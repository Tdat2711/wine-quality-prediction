"""Reproduce the locked title-group split without fitting preprocessing."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/processed/wine_cleaned_final.csv"
SPLIT_DIR = ROOT / "data/processed/splits"
SEED = 42


def normalize_title(text):
    """Keep the exact normalization used to create the locked split."""
    if pd.isna(text):
        return "unknown"
    text = re.sub(r"\s+", " ", str(text).lower().strip())
    return re.sub(r"[^\w\s\(\)\-\']", "", text).strip()


def create_splits(source: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return the original seed-42 70/15/15 group assignment in memory."""
    eligible = source.dropna(subset=["price", "points"]).copy()
    if eligible.empty or not eligible["price"].gt(0).all():
        raise ValueError("Mẫu phải có giá quan sát dương và nhãn points.")
    if eligible["price_was_missing"].any():
        raise ValueError("Mẫu có giá ước tính thay vì giá quan sát.")
    eligible["title_clean"] = eligible["title"].map(normalize_title)
    eligible["log_price"] = np.log1p(eligible["price"])
    outer = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=SEED)
    train_idx, temp_idx = next(outer.split(eligible, groups=eligible["title_clean"]))
    temp = eligible.iloc[temp_idx]
    inner = GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=SEED)
    val_idx, test_idx = next(inner.split(temp, groups=temp["title_clean"]))
    return {"train": eligible.iloc[train_idx].copy(),
            "val": temp.iloc[val_idx].copy(), "test": temp.iloc[test_idx].copy()}


def check_existing_splits(parts, directory=SPLIT_DIR):
    """Fail if recomputation differs; never silently replace an existing split."""
    for name, expected in parts.items():
        stored = pd.read_csv(Path(directory) / f"{name}.csv")
        pd.testing.assert_frame_equal(
            expected.reset_index(drop=True), stored, check_dtype=False,
            check_exact=False, rtol=1e-12, atol=1e-12,
        )


def review_overlap(parts):
    """Count shared nonempty review texts; do not inspect held-out labels."""
    texts = {}
    for name, part in parts.items():
        normalized = part["description"].fillna("").str.lower().str.strip()
        normalized = normalized.str.replace(r"\s+", " ", regex=True)
        texts[name] = set(normalized[normalized.ne("")])
    rows = []
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        shared = texts[left] & texts[right]
        rows.append({"left": left, "right": right, "shared_unique_reviews": len(shared)})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Xuất split nếu chưa có; kiểm tra nếu đã có.")
    args = parser.parse_args()
    parts = create_splits(pd.read_csv(DATA_PATH))
    if args.write:
        # Check all existing files before any write. Existing bytes are preserved.
        existing = {n: p for n, p in parts.items() if (SPLIT_DIR / f"{n}.csv").exists()}
        check_existing_splits(existing)
        SPLIT_DIR.mkdir(parents=True, exist_ok=True)
        for name, part in parts.items():
            target = SPLIT_DIR / f"{name}.csv"
            if not target.exists():
                part.to_csv(target, index=False, encoding="utf-8", lineterminator="\n")
    else:
        check_existing_splits(parts)
    print({name: len(part) for name, part in parts.items()})
    print(review_overlap(parts).to_string(index=False))


if __name__ == "__main__":
    main()
