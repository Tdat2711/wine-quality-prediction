"""Handle outliers and noise in the Wine Reviews dataset.

This module addresses:
1. Outliers in `price`:
   - Distinguishes valid luxury wines (natural outliers) from data entry errors.
   - Corrects verified data entry errors (Blair 2013 and Chateau les Ormes Sorbet).
   - Generates `log_price` transformation for machine learning algorithms.
2. Noise in text and metadata:
   - Cleans HTML entities (&amp;, &eacute;, etc.) and non-breaking spaces (\xa0).
   - Flags non-informative reviews (< 10 words, e.g. importer notes).
   - Extracts clean vintage years while ignoring brand foundation years for Non-Vintage (NV) wines.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "winemag-data-130k-v2.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "interim" / "04_outliers_noise_handled.csv"
)


def detect_price_outliers(df: pd.DataFrame) -> dict[str, Any]:
    """Calculate descriptive statistics and Tukey IQR thresholds for price."""
    prices = df["price"].dropna()
    q1 = float(prices.quantile(0.25))
    q3 = float(prices.quantile(0.75))
    iqr = q3 - q1

    mild_upper = q3 + 1.5 * iqr
    extreme_upper = q3 + 3.0 * iqr

    mild_outliers = int((prices > mild_upper).sum())
    extreme_outliers = int((prices > extreme_upper).sum())

    return {
        "valid_count": len(prices),
        "missing_count": int(df["price"].isna().sum()),
        "mean": float(prices.mean()),
        "median": float(prices.median()),
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "mild_threshold": mild_upper,
        "extreme_threshold": extreme_upper,
        "mild_outliers_count": mild_outliers,
        "mild_outliers_pct": float(mild_outliers / len(prices) * 100),
        "extreme_outliers_count": extreme_outliers,
        "extreme_outliers_pct": float(extreme_outliers / len(prices) * 100),
        "over_500_count": int((prices > 500).sum()),
        "over_1000_count": int((prices > 1000).sum()),
        "skewness_raw": float(prices.skew()),
    }


def clean_text_noise(text: Any) -> str:
    """Unescape HTML entities and replace non-breaking spaces."""
    if not isinstance(text, str):
        return ""
    cleaned = html.unescape(text)
    cleaned = cleaned.replace("\xa0", " ")
    return cleaned.strip()


def extract_clean_vintage(title: Any) -> float:
    """Extract vintage harvest year while filtering foundation years for NV wines."""
    if not isinstance(title, str):
        return np.nan

    # Check for Non-Vintage labels
    if re.search(r"\b(NV|Non-Vintage)\b", title, re.IGNORECASE):
        return np.nan

    match = re.search(r"\b(19\d\d|20[0-2]\d)\b", title)
    if match:
        year = int(match.group(1))
        # Keep realistic harvest vintages (1980 - 2021)
        if 1980 <= year <= 2021:
            return float(year)
    return np.nan


def correct_data_entry_errors(df: pd.DataFrame) -> dict[str, int]:
    """Correct verified typos and field misplacements in price."""
    changes = {"blair_2013": 0, "chateau_ormes_sorbet": 0}

    # Case 1: Blair 2013 Chardonnay mistakenly typed vintage 2013 as price
    mask_blair = (
        df["title"].str.contains("Blair 2013 Roger Rose Vineyard", na=False)
        & (df["price"] == 2013.0)
    )
    if mask_blair.any():
        df.loc[mask_blair, "price"] = 35.0
        changes["blair_2013"] = int(mask_blair.sum())

    # Case 2: Chateau les Ormes Sorbet 2013 (Cru Bourgeois) mistyped 3300.0 instead of 33.0
    mask_ormes = (
        df["title"].str.contains("Château les Ormes Sorbet 2013", na=False)
        & (df["price"] == 3300.0)
    )
    if mask_ormes.any():
        df.loc[mask_ormes, "price"] = 33.0
        changes["chateau_ormes_sorbet"] = int(mask_ormes.sum())

    return changes


def process_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Execute complete outlier and noise handling pipeline."""
    result = df.copy()
    stats: dict[str, Any] = {}

    # 1. Price stats before cleaning
    stats["price_stats_before"] = detect_price_outliers(result)

    # 2. Text noise cleanup
    for col in ["description", "title"]:
        if col in result.columns:
            result[col] = result[col].apply(clean_text_noise)

    # 3. Flag non-informative short reviews (< 10 words)
    if "description" in result.columns:
        result["is_non_informative_review"] = result["description"].apply(
            lambda x: len(x.split()) < 10
        )
        stats["short_reviews_flagged"] = int(
            result["is_non_informative_review"].sum()
        )

    # 4. Extract clean vintage year
    if "title" in result.columns:
        result["vintage_year"] = result["title"].apply(extract_clean_vintage)
        stats["vintages_extracted"] = int(result["vintage_year"].notna().sum())

    # 5. Preserve original prices and audit verified corrections.
    result["price_original"] = result["price"]
    stats["corrections"] = correct_data_entry_errors(result)
    result["price_was_corrected"] = result["price"].ne(result["price_original"])

    # 6. Apply Log Transform for Machine Learning
    result["log_price"] = np.log1p(result["price"])
    stats["skewness_after_log"] = float(result["log_price"].dropna().skew())

    return result, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Handle outliers and noise in the Wine Reviews dataset."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to input raw or formatted CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to output interim CSV file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Reading dataset from: {args.input}")
    df = pd.read_csv(args.input)

    print(f"Dataset shape: {df.shape}")
    cleaned_df, stats = process_dataset(df)

    p_before = stats["price_stats_before"]
    print("\n--- OUTLIER AUDIT (PRICE) ---")
    print(f"Valid prices: {p_before['valid_count']:,}")
    print(f"Q1: {p_before['q1']:.1f}$, Median: {p_before['median']:.1f}$, Q3: {p_before['q3']:.1f}$")
    print(f"Mild Outliers (> {p_before['mild_threshold']:.1f}$): {p_before['mild_outliers_count']:,} ({p_before['mild_outliers_pct']:.2f}%)")
    print(f"Extreme Outliers (> {p_before['extreme_threshold']:.1f}$): {p_before['extreme_outliers_count']:,} ({p_before['extreme_outliers_pct']:.2f}%)")
    print(f"Wines > 1000$: {p_before['over_1000_count']} bottles (retained as valid luxury segment)")

    print("\n--- ACTIONS APPLIED ---")
    print(f"Corrected data entry errors: {stats['corrections']}")
    print(f"Flagged non-informative short reviews: {stats['short_reviews_flagged']}")
    print(f"Extracted clean vintage years: {stats['vintages_extracted']:,}")
    print(f"Price skewness reduced: {p_before['skewness_raw']:.2f} -> {stats['skewness_after_log']:.2f} via log1p")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"\nSaved processed data to: {args.output}")
    print(f"Final shape: {cleaned_df.shape}")


if __name__ == "__main__":
    main()
