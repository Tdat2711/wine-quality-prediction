"""Handle only missing values in the Wine Reviews dataset.

This module intentionally does not remove duplicates, trim text, change data
types, or treat outliers. Those concerns belong to the other cleaning tasks.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "winemag-data-130k-v2.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "wine_missing_values_handled.csv"
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


def _fill_from_unambiguous_mapping(
    df: pd.DataFrame, source: str, target: str
) -> int:
    """Fill target from source only when the observed mapping is one-to-one."""
    observed = df.dropna(subset=[source, target])[[source, target]]
    if observed.empty:
        return 0

    mappings = observed.groupby(source, sort=False)[target].agg(
        lambda values: tuple(pd.unique(values))
    )
    unique_mapping = {
        key: values[0] for key, values in mappings.items() if len(values) == 1
    }

    missing = df[target].isna() & df[source].notna()
    inferred = df.loc[missing, source].map(unique_mapping)
    fill_index = inferred[inferred.notna()].index
    df.loc[fill_index, target] = inferred.loc[fill_index]
    return len(fill_index)


def _fill_price_with_hierarchical_medians(
    df: pd.DataFrame, minimum_group_size: int = 5
) -> dict[str, int]:
    """Impute price with robust medians without using the prediction target.

    The hierarchy is country+variety, variety, country, then global median.
    Small groups are skipped to avoid using an unstable single observation.
    """
    counts: dict[str, int] = {}
    hierarchy: Iterable[tuple[list[str], str]] = (
        (["country", "variety"], "country+variety"),
        (["variety"], "variety"),
        (["country"], "country"),
    )

    for keys, label in hierarchy:
        grouped = df.groupby(keys, dropna=False)["price"]
        group_median = grouped.transform("median")
        group_count = grouped.transform("count")
        eligible = (
            df["price"].isna()
            & group_median.notna()
            & group_count.ge(minimum_group_size)
        )
        df.loc[eligible, "price"] = group_median.loc[eligible]
        counts[label] = int(eligible.sum())

    remaining = df["price"].isna()
    global_median = df["price"].median()
    if pd.isna(global_median):
        raise ValueError("Cannot impute price because the column has no valid values.")
    df.loc[remaining, "price"] = global_median
    counts["global"] = int(remaining.sum())
    return counts


def handle_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Return a copy with the nine audited missing-value columns handled."""
    missing_required = [column for column in MISSING_COLUMNS if column not in df]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    cleaned = df.copy(deep=True)
    report: dict[str, int] = {}

    # Geographic values: infer only from wineries that always have one value.
    report["country_inferred_from_winery"] = _fill_from_unambiguous_mapping(
        cleaned, "winery", "country"
    )
    report["province_inferred_from_winery"] = _fill_from_unambiguous_mapping(
        cleaned, "winery", "province"
    )
    report["country_set_unknown"] = int(cleaned["country"].isna().sum())
    report["province_set_unknown"] = int(cleaned["province"].isna().sum())
    cleaned["country"] = cleaned["country"].fillna("Unknown")
    cleaned["province"] = cleaned["province"].fillna("Unknown")

    # Optional labels are not safely reconstructable from other columns.
    report["designation_set_not_specified"] = int(
        cleaned["designation"].isna().sum()
    )
    cleaned["designation"] = cleaned["designation"].fillna("Not specified")

    report.update(
        {
            f"price_imputed_{key}": value
            for key, value in _fill_price_with_hierarchical_medians(cleaned).items()
        }
    )

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

    # Try one-to-one mappings first so this remains safe on future data versions.
    report["taster_name_inferred_from_handle"] = _fill_from_unambiguous_mapping(
        cleaned, "taster_twitter_handle", "taster_name"
    )
    report["twitter_handle_inferred_from_name"] = _fill_from_unambiguous_mapping(
        cleaned, "taster_name", "taster_twitter_handle"
    )
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

    remaining_missing = cleaned.loc[:, MISSING_COLUMNS].isna().sum()
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
    print("Remaining missing values in audited columns: 0")
    for key, value in report.items():
        print(f"- {key}: {value:,}")


if __name__ == "__main__":
    main()
