"""Reproducible cleaning pipeline for the Wine Reviews 130k dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import sys

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.clean_consistency import enforce_consistency
from src.clean_duplicates import find_possible_logical_duplicates, remove_duplicates
from src.handle_missing_values import handle_missing_values
from src.handle_outliers_and_noise import process_dataset
from src.validate_cleaned_data import sha256_file, validate_cleaned_dataset
from src.cleaning_report import snapshot, write_report


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
    stages = [snapshot(df, 'raw')]

    print(f"Dataset gốc: {df.shape}")

    before = df
    df, report = handle_missing_values(df)
    stages.append(snapshot(df, 'missing', before))
    overall_report["missing"] = report
    df.to_csv(INTERIM_MISSING_PATH, index=False)
    print(f"[1/4] Missing values: {df.shape}")

    before = df
    df, report = enforce_consistency(df)
    stages.append(snapshot(df, 'consistency', before))
    overall_report["consistency"] = report
    df.to_csv(INTERIM_CONSISTENCY_PATH, index=False)
    print(f"[2/4] Consistency: {df.shape}")

    before = df
    df, report = remove_duplicates(df)
    stages.append(snapshot(df, 'duplicates', before))
    overall_report["duplicates"] = report
    candidates = find_possible_logical_duplicates(df)
    candidates.to_csv(POSSIBLE_DUPLICATES_PATH, index=False)
    df.to_csv(INTERIM_DUPLICATES_PATH, index=False)
    print(f"[3/4] Exact duplicates: {df.shape}")
    print(f"      Possible logical duplicates: {POSSIBLE_DUPLICATES_PATH}")

    before = df
    df, report = process_dataset(df)
    stages.append(snapshot(df, 'outliers_noise', before))
    overall_report["outliers_and_noise"] = report
    df.to_csv(INTERIM_OUTLIERS_PATH, index=False)
    print(f"[4/4] Outliers and noise: {df.shape}")

    raw_hash_after = sha256_file(RAW_DATA_PATH)
    if raw_hash_before != raw_hash_after:
        raise AssertionError("Dataset gốc đã thay đổi trong lúc chạy pipeline.")

    validation = validate_cleaned_dataset(raw, df, raw_hash_after)
    df.to_csv(CLEANED_DATA_PATH, index=False)
    write_report(pd.DataFrame(stages), overall_report, RAW_DATA_PATH, CLEANED_DATA_PATH)

    print(f"Hoàn tất cleaning: {df.shape}")
    print(
        "Mẫu đủ điều kiện cho split (có giá quan sát): "
        f"{validation['model_eligible_rows']:,} dòng"
    )
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
