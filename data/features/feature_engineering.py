from pathlib import Path

import numpy as np
import pandas as pd


class FeatureEngineer:
    def __init__(self, filepath):
        self.filepath = Path(filepath)

        self.data = pd.read_csv(
            self.filepath,
            parse_dates=["time"],
        )

        self.data = self.data.sort_values("time").reset_index(drop=True)

    def add_returns(self):
        self.data["return_1"] = self.data["mid_close"].pct_change()

        self.data["log_return"] = np.log(
            self.data["mid_close"]
            / self.data["mid_close"].shift(1)
        )

    def add_moving_averages(self):
        self.data["sma_10"] = (
            self.data["mid_close"]
            .rolling(10)
            .mean()
        )

        self.data["sma_20"] = (
            self.data["mid_close"]
            .rolling(20)
            .mean()
        )

        self.data["sma_50"] = (
            self.data["mid_close"]
            .rolling(50)
            .mean()
        )

        self.data["ema_20"] = (
            self.data["mid_close"]
            .ewm(span=20, adjust=False)
            .mean()
        )

    def add_momentum(self):
        self.data["momentum_5"] = (
            self.data["mid_close"]
            - self.data["mid_close"].shift(5)
        )

        self.data["momentum_20"] = (
            self.data["mid_close"]
            - self.data["mid_close"].shift(20)
        )

    def add_volatility(self):
        self.data["volatility_20"] = (
            self.data["return_1"]
            .rolling(20)
            .std()
        )

    def add_rsi(self, period=14):
        delta = self.data["mid_close"].diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        self.data["rsi_14"] = (
            100 - (100 / (1 + rs))
        )

    def add_atr(self, period=14):
        high_low = (
            self.data["mid_high"]
            - self.data["mid_low"]
        )

        high_close = (
            self.data["mid_high"]
            - self.data["mid_close"].shift(1)
        ).abs()

        low_close = (
            self.data["mid_low"]
            - self.data["mid_close"].shift(1)
        ).abs()

        true_range = pd.concat(
            [
                high_low,
                high_close,
                low_close,
            ],
            axis=1,
        ).max(axis=1)

        self.data["atr_14"] = (
            true_range
            .rolling(period)
            .mean()
        )

    def add_time_features(self):
        self.data["hour"] = self.data["time"].dt.hour

        self.data["day_of_week"] = (
            self.data["time"].dt.dayofweek
        )

    def add_spread_features(self):
        self.data["spread_rolling_mean_20"] = (
            self.data["spread"]
            .rolling(20)
            .mean()
        )

        self.data["spread_vs_average"] = (
            self.data["spread"]
            / self.data["spread_rolling_mean_20"]
        )

    def create_target(self):
        self.data["future_return_1"] = (
            self.data["mid_close"].shift(-1)
            / self.data["mid_close"]
            - 1
        )

        self.data["target_up"] = (
            self.data["future_return_1"] > 0
        ).astype(int)

    def build(self):
        self.add_returns()
        self.add_moving_averages()
        self.add_momentum()
        self.add_volatility()
        self.add_rsi()
        self.add_atr()
        self.add_time_features()
        self.add_spread_features()
        self.create_target()

        self.data = self.data.dropna().reset_index(drop=True)

        return self.data


if __name__ == "__main__":
    engineer = FeatureEngineer(
        "data/processed/EUR_USD_H1_5000.csv"
    )

    data = engineer.build()

    output_file = Path(
        "data/processed/EUR_USD_H1_features.csv"
    )

    data.to_csv(
        output_file,
        index=False,
    )

    print()
    print("AURA FX Feature Engineering")
    print("=" * 40)
    print(f"Rows: {len(data)}")
    print(f"Columns: {len(data.columns)}")
    print()
    print(data.tail())
    print()
    print(f"Saved to: {output_file}")
    