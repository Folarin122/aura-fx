from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

from data.ingestion.oanda_client import OandaClient


class HistoricalDownloader:
    def __init__(self):
        self.client = OandaClient()

    def download_candles(
        self,
        instrument="EUR_USD",
        granularity="H1",
        total_candles=5000,
        batch_size=500,
    ):
        all_frames = []
        end_time = None

        remaining = total_candles

        while remaining > 0:
            count = min(batch_size, remaining)

            params = {
                "granularity": granularity,
                "count": count,
                "price": "MBA",
            }

            if end_time is not None:
                params["to"] = end_time

            url = (
                f"{self.client.base_url.rstrip('/')}/v3/instruments/"
                f"{instrument}/candles"
            )

            response = self.client.session.get(
                url,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            payload = response.json()

            rows = []

            for candle in payload["candles"]:
                if not candle["complete"]:
                    continue

                rows.append(
                    {
                        "time": candle["time"],
                        "volume": candle["volume"],
                        "mid_open": float(candle["mid"]["o"]),
                        "mid_high": float(candle["mid"]["h"]),
                        "mid_low": float(candle["mid"]["l"]),
                        "mid_close": float(candle["mid"]["c"]),
                        "bid_close": float(candle["bid"]["c"]),
                        "ask_close": float(candle["ask"]["c"]),
                    }
                )

            frame = pd.DataFrame(rows)

            if frame.empty:
                break

            frame["time"] = pd.to_datetime(
                frame["time"],
                utc=True,
            )

            frame["spread"] = (
                frame["ask_close"]
                - frame["bid_close"]
            )

            all_frames.append(frame)

            earliest_time = frame["time"].min()

            end_time = earliest_time.isoformat()

            remaining -= len(frame)

            print(
                f"Downloaded {total_candles - remaining} "
                f"of {total_candles} candles"
            )

        if not all_frames:
            return pd.DataFrame()

        data = pd.concat(
            all_frames,
            ignore_index=True,
        )

        data = data.drop_duplicates(
            subset=["time"]
        )

        data = data.sort_values(
            "time"
        )

        data = data.reset_index(
            drop=True
        )

        return data


if __name__ == "__main__":
    downloader = HistoricalDownloader()

    data = downloader.download_candles(
        instrument="EUR_USD",
        granularity="H1",
        total_candles=5000,
    )

    output_dir = Path("data/processed")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / "EUR_USD_H1_5000.csv"
    )

    data.to_csv(
        output_file,
        index=False,
    )

    print()
    print(f"Saved {len(data)} rows")
    print(f"File: {output_file}")