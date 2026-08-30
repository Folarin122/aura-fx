from pathlib import Path

import pandas as pd


class MarketDataValidator:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.data = pd.read_csv(
            self.filepath,
            parse_dates=["time"],
        )

    def run_checks(self):
        print("AURA FX Data Validation")
        print("=" * 40)

        self.check_rows()
        self.check_duplicates()
        self.check_missing_values()
        self.check_ohlc_integrity()
        self.check_spreads()
        self.check_time_order()

        print("=" * 40)
        print("Validation complete.")

    def check_rows(self):
        print(f"Rows: {len(self.data)}")

    def check_duplicates(self):
        duplicates = self.data.duplicated(
            subset=["time"]
        ).sum()

        print(f"Duplicate timestamps: {duplicates}")

    def check_missing_values(self):
        missing = self.data.isna().sum().sum()

        print(f"Missing values: {missing}")

    def check_ohlc_integrity(self):
        invalid = self.data[
            (self.data["mid_high"] < self.data["mid_low"])
            | (self.data["mid_open"] > self.data["mid_high"])
            | (self.data["mid_open"] < self.data["mid_low"])
            | (self.data["mid_close"] > self.data["mid_high"])
            | (self.data["mid_close"] < self.data["mid_low"])
        ]

        print(f"Invalid OHLC candles: {len(invalid)}")

    def check_spreads(self):
        negative_spreads = (
            self.data["spread"] < 0
        ).sum()

        zero_spreads = (
            self.data["spread"] == 0
        ).sum()

        print(f"Negative spreads: {negative_spreads}")
        print(f"Zero spreads: {zero_spreads}")

        print(
            f"Average spread: "
            f"{self.data['spread'].mean():.6f}"
        )

        print(
            f"Maximum spread: "
            f"{self.data['spread'].max():.6f}"
        )

    def check_time_order(self):
        ordered = self.data["time"].is_monotonic_increasing

        print(f"Chronological order: {ordered}")


if __name__ == "__main__":
    validator = MarketDataValidator(
        "data/processed/EUR_USD_H1_5000.csv"
    )

    validator.run_checks()
    