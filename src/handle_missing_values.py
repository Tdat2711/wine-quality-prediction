"""Handle only missing values in the Wine Reviews dataset.

This module intentionally does not remove duplicates, trim text, change data
types, or treat outliers. Those concerns belong to the other cleaning tasks.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "winemag-data-130k-v2.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "interim" / "01_missing_handled.csv"
)

MISSING_COLUMNS = (
    "country",
    "designation",
    "price",
    "province",
    "region_1",
    "region_2",
    "taster_name",
    "taster_twitter_handle",
    "variety",
)


def handle_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Handle labels deterministically; preserve missing observed prices."""
    missing_required = [column for column in MISSING_COLUMNS if column not in df]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    cleaned = df.copy(deep=True)
    report: dict[str, int] = {}

    # Never learn cross-row mappings before the train/validation/test split.
    report["country_set_unknown"] = int(cleaned["country"].isna().sum())
    report["province_set_unknown"] = int(cleaned["province"].isna().sum())
    cleaned["country"] = cleaned["country"].fillna("Unknown")
    cleaned["province"] = cleaned["province"].fillna("Unknown")

    # Optional labels are not safely reconstructable from other columns.
    report["designation_set_not_specified"] = int(
        cleaned["designation"].isna().sum()
    )
    cleaned["designation"] = cleaned["designation"].fillna("Not specified")

    report["price_left_missing"] = int(cleaned["price"].isna().sum())

    report["region_1_set_unknown"] = int(cleaned["region_1"].isna().sum())
    cleaned["region_1"] = cleaned["region_1"].fillna("Unknown")

    region_2_missing = cleaned["region_2"].isna()
    not_applicable = (
        region_2_missing
        & cleaned["country"].ne("US")
        & cleaned["country"].ne("Unknown")
    )
    unknown_region_2 = region_2_missing & ~not_applicable
    report["region_2_set_not_applicable"] = int(not_applicable.sum())
    report["region_2_set_unknown"] = int(unknown_region_2.sum())
    cleaned.loc[not_applicable, "region_2"] = "Not applicable"
    cleaned.loc[unknown_region_2, "region_2"] = "Unknown"

    report["taster_name_set_unknown"] = int(cleaned["taster_name"].isna().sum())
    report["twitter_handle_set_not_provided"] = int(
        cleaned["taster_twitter_handle"].isna().sum()
    )
    cleaned["taster_name"] = cleaned["taster_name"].fillna("Unknown")
    cleaned["taster_twitter_handle"] = cleaned["taster_twitter_handle"].fillna(
        "Not provided"
    )

    # The only missing variety explicitly names Petite Syrah in its review.
    missing_variety = cleaned["variety"].isna()
    review_text = cleaned["description"].fillna("")
    petite_sirah = missing_variety & review_text.str.contains(
        r"\bPetite Syrah\b", case=False, regex=True
    )
    cleaned.loc[petite_sirah, "variety"] = "Petite Sirah"
    report["variety_inferred_from_description"] = int(petite_sirah.sum())
    report["variety_set_unknown"] = int(cleaned["variety"].isna().sum())
    cleaned["variety"] = cleaned["variety"].fillna("Unknown")

    remaining_missing = cleaned.loc[:, [c for c in MISSING_COLUMNS if c != "price"]].isna().sum()
    if int(remaining_missing.sum()) != 0:
        raise AssertionError(
            f"Missing values remain after processing: {remaining_missing.to_dict()}"
        )

    return cleaned, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Handle missing values without changing other cleaning concerns."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = pd.read_csv(args.input)
    original_columns = source.columns.tolist()
    original_rows = len(source)

    cleaned, report = handle_missing_values(source)

    if cleaned.columns.tolist() != original_columns:
        raise AssertionError("Column names or order changed during missing-value handling.")
    if len(cleaned) != original_rows:
        raise AssertionError("Row count changed during missing-value handling.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False)

    print(f"Saved {len(cleaned):,} rows x {len(cleaned.columns)} columns to {args.output}")
    print(f"Remaining missing prices (preserved): {cleaned['price'].isna().sum():,}")
    for key, value in report.items():
        print(f"- {key}: {value:,}")


if __name__ == "__main__":
    main()
