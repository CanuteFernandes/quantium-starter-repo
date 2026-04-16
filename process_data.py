from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = BASE_DIR / "output.csv"


def main() -> None:
    csv_files = sorted(DATA_DIR.glob("daily_sales_data_*.csv"))
    if not csv_files:
        raise FileNotFoundError("No input CSV files found in data directory.")

    frames = [pd.read_csv(file) for file in csv_files]
    combined = pd.concat(frames, ignore_index=True)

    pink = combined[combined["product"].str.lower() == "pink morsel"].copy()

    pink["price"] = pink["price"].str.replace("$", "", regex=False).astype(float)
    pink["quantity"] = pink["quantity"].astype(float)
    pink["Sales"] = pink["price"] * pink["quantity"]

    result = pink[["Sales", "date", "region"]].rename(
        columns={"date": "Date", "region": "Region"}
    )

    result = result.sort_values(["Date", "Region"]).reset_index(drop=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print(f"Wrote {len(result)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
