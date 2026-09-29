"""Reproducible cleaning pipeline for the Wine Reviews 130k dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from clean_consistency import enforce_consistency
from clean_duplicates import find_possible_logical_duplicates, remove_duplicates
from handle_missing_values import handle_missing_values
from handle_outliers_and_noise import process_dataset
from validate_cleaned_data import sha256_file, validate_cleaned_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "winemag-data-130k-v2.csv"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

INTERIM_MISSING_PATH = INTERIM_DIR / "01_missing_handled.csv"
INTERIM_CONSISTENCY_PATH = INTERIM_DIR / "02_consistency_handled.csv"
INTERIM_DUPLICATES_PATH = INTERIM_DIR / "03_duplicates_handled.csv"
INTERIM_OUTLIERS_PATH = INTERIM_DIR / "04_outliers_noise_handled.csv"
CLEANED_DATA_PATH = PROCESSED_DIR / "wine_cleaned_final.csv"
POSSIBLE_DUPLICATES_PATH = PROJECT_ROOT / "docs" / "possible_logical_duplicates.csv"


def _print_report(report: dict[str, Any], prefix: str = "") -> None:
    for key, value in report.items():
        label = f"{prefix}{key}"
        if isinstance(value, dict):
            _print_report(value, prefix=f"{label}.")
        else:
            print(f"  - {label}: {value}")


def run_cleaning_stage() -> pd.DataFrame:
    """Run all approved cleaning stages and validate the final dataset."""
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy dataset gốc: {RAW_DATA_PATH}")

    raw_hash_before = sha256_file(RAW_DATA_PATH)
    raw = pd.read_csv(RAW_DATA_PATH)
    df = raw.copy(deep=True)
    overall_report: dict[str, Any] = {}

    print(f"Dataset gốc: {df.shape}")

    df, report = handle_missing_values(df)
    overall_report["missing"] = report
    df.to_csv(INTERIM_MISSING_PATH, index=False)
    print(f"[1/4] Missing values: {df.shape}")

    df, report = enforce_consistency(df)
    overall_report["consistency"] = report
    df.to_csv(INTERIM_CONSISTENCY_PATH, index=False)
    print(f"[2/4] Consistency: {df.shape}")

    df, report = remove_duplicates(df)
    overall_report["duplicates"] = report
    candidates = find_possible_logical_duplicates(df)
    candidates.to_csv(POSSIBLE_DUPLICATES_PATH, index=False)
    df.to_csv(INTERIM_DUPLICATES_PATH, index=False)
    print(f"[3/4] Exact duplicates: {df.shape}")
    print(f"      Possible logical duplicates: {POSSIBLE_DUPLICATES_PATH}")

    df, report = process_dataset(df)
    overall_report["outliers_and_noise"] = report
    df.to_csv(INTERIM_OUTLIERS_PATH, index=False)
    print(f"[4/4] Outliers and noise: {df.shape}")

    raw_hash_after = sha256_file(RAW_DATA_PATH)
    if raw_hash_before != raw_hash_after:
        raise AssertionError("Dataset gốc đã thay đổi trong lúc chạy pipeline.")

    validation = validate_cleaned_dataset(raw, df, raw_hash_after)
    df.to_csv(CLEANED_DATA_PATH, index=False)

    print(f"Hoàn tất cleaning: {df.shape}")
    print(f"Đầu ra: {CLEANED_DATA_PATH}")
    print("Báo cáo:")
    _print_report(overall_report)
    print("Final validation:")
    _print_report(validation)
    return df


def run_data_pipeline() -> pd.DataFrame:
    """Run cleaning only; ML preprocessing belongs to a separate workflow."""
    return run_cleaning_stage()


if __name__ == "__main__":
    run_data_pipeline()
