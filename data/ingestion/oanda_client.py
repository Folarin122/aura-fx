import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


class OandaClient:
    def __init__(self):
        self.token = os.getenv("OANDA_API_TOKEN")

        self.base_url = os.getenv(
            "OANDA_BASE_URL",
            "https://api-fxpractice.oanda.com",
        )

        if not self.token:
            raise ValueError(
                "OANDA_API_TOKEN was not found in the .env file."
            )

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token.strip()}",
                "Content-Type": "application/json",
            }
        )

    def get_candles(
        self,
        instrument="EUR_USD",
        granularity="H1",
        count=500,
    ):
        url = (
            f"{self.base_url.rstrip('/')}/v3/instruments/"
            f"{instrument}/candles"
        )

        params = {
            "granularity": granularity,
            "count": count,
            "price": "MBA",
        }

        response = self.session.get(
            url,
            params=params,
            timeout=30,
        )

        if response.status_code != 200:
            print("OANDA status:", response.status_code)
            print("OANDA response:", response.text)

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

        dataframe = pd.DataFrame(rows)

        if not dataframe.empty:
            dataframe["time"] = pd.to_datetime(
                dataframe["time"],
                utc=True,
            )

            dataframe["spread"] = (
                dataframe["ask_close"]
                - dataframe["bid_close"]
            )

        return dataframe