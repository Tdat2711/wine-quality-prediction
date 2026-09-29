"""Acceptance checks for the cleaned Wine Reviews dataset."""

from __future__ import annotations

from pathlib import Path
import hashlib

import pandas as pd


EXPECTED_RAW_SHA256 = (
    "52af2643c8ac29f010f0cc629dfbdda1c74aa0f332d11762af9ef3de4e567ac9"
)
REQUIRED_DERIVED_COLUMNS = {
    "price_original",
    "price_was_corrected",
    "log_price",
    "vintage_year",
    "is_non_informative_review",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_cleaned_dataset(
    raw: pd.DataFrame,
    cleaned: pd.DataFrame,
    raw_sha256: str,
) -> dict[str, int | str]:
    errors: list[str] = []
    base_columns = [column for column in raw.columns if column != "Unnamed: 0"]

    if raw_sha256 != EXPECTED_RAW_SHA256:
        errors.append("SHA-256 của dataset raw không khớp bản đã audit.")
    if "Unnamed: 0" in cleaned.columns:
        errors.append("Cột chỉ mục Unnamed: 0 vẫn còn trong dữ liệu sạch.")

    missing_columns = set(base_columns).difference(cleaned.columns)
    if missing_columns:
        errors.append(f"Thiếu cột gốc: {sorted(missing_columns)}")

    missing_derived = REQUIRED_DERIVED_COLUMNS.difference(cleaned.columns)
    if missing_derived:
        errors.append(f"Thiếu cột dẫn xuất: {sorted(missing_derived)}")

    if not missing_columns:
        missing_base = int(cleaned[base_columns].isna().sum().sum())
        if missing_base:
            errors.append(f"Còn {missing_base} ô thiếu trong các cột gốc.")

    exact_duplicates = int(cleaned[base_columns].duplicated().sum()) if not missing_columns else -1
    if exact_duplicates > 0:
        errors.append(f"Còn {exact_duplicates} duplicate hoàn toàn.")

    if "country" in cleaned.columns and int((cleaned["country"] == "Us").sum()):
        errors.append("Còn giá trị quốc gia 'Us'; giá trị chuẩn phải là 'US'.")

    if "points" in cleaned.columns:
        raw_max_points = int(raw["points"].max())
        cleaned_max_points = int(cleaned["points"].max())
        if cleaned_max_points != raw_max_points:
            errors.append(
                f"Điểm tối đa thay đổi từ {raw_max_points} thành {cleaned_max_points}."
            )

    if "price" in cleaned.columns and float(cleaned["price"].max()) <= 79.5:
        errors.append("Phân khúc rượu giá cao đã bị loại khỏi dữ liệu.")

    if "price_was_corrected" in cleaned.columns:
        corrected_prices = int(cleaned["price_was_corrected"].sum())
        if corrected_prices != 2:
            errors.append(
                f"Kỳ vọng 2 lỗi giá được đánh dấu, thực tế có {corrected_prices}."
            )
    else:
        corrected_prices = -1

    if errors:
        raise AssertionError("Final validation failed:\n- " + "\n- ".join(errors))

    return {
        "raw_sha256": raw_sha256,
        "rows": len(cleaned),
        "columns": len(cleaned.columns),
        "exact_duplicates": exact_duplicates,
        "corrected_prices": corrected_prices,
        "max_points": int(cleaned["points"].max()),
        "max_price": int(cleaned["price"].max()),
    }
