from collections import Counter
from itertools import combinations
from pathlib import Path
import unittest

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class SplitArtifactTests(unittest.TestCase):
    """Check the exported data used by every downstream model."""

    @classmethod
    def setUpClass(cls):
        cls.source = pd.read_csv(ROOT / "data/processed/wine_cleaned_final.csv")
        cls.expected = cls.source.dropna(subset=["price", "points"])
        cls.parts = {
            name: pd.read_csv(ROOT / f"data/processed/splits/{name}.csv")
            for name in ("train", "val", "test")
        }
        cls.exported = pd.concat(cls.parts.values(), ignore_index=True)

    def test_model_rows_have_observed_price_and_target(self):
        for name, part in self.parts.items():
            with self.subTest(split=name):
                self.assertFalse(part[["price", "points", "log_price"]].isna().any().any())
                self.assertFalse(part["price_was_missing"].any())
                self.assertTrue(part["price"].gt(0).all())

    def test_exports_preserve_exactly_the_eligible_cleaned_records(self):
        self.assertEqual(len(self.exported), len(self.expected))
        self.assertTrue(set(self.source.columns).issubset(self.exported.columns))
        # log_price is recomputed from the observed price; its numeric accuracy
        # is checked separately to allow harmless floating-point differences.
        columns = [column for column in self.source if column != "log_price"]
        expected = Counter(
            pd.util.hash_pandas_object(self.expected[columns], index=False)
        )
        actual = Counter(
            pd.util.hash_pandas_object(self.exported[columns], index=False)
        )
        self.assertEqual(actual, expected, "Split exports lost, duplicated or changed source records.")

    def test_title_groups_do_not_cross_split_boundaries(self):
        title_groups = {
            name: set(
                part["title"].str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
            )
            for name, part in self.parts.items()
        }
        stored_groups = {
            name: set(part["title_clean"]) for name, part in self.parts.items()
        }
        for left, right in combinations(self.parts, 2):
            with self.subTest(left=left, right=right):
                self.assertFalse(title_groups[left] & title_groups[right])
                self.assertFalse(stored_groups[left] & stored_groups[right])

    def test_log_price_matches_the_observed_price(self):
        self.assertTrue(np.isfinite(self.exported["log_price"]).all())
        np.testing.assert_allclose(
            self.exported["log_price"],
            np.log1p(self.exported["price"]),
            rtol=1e-12,
            atol=1e-12,
        )


if __name__ == "__main__":
    unittest.main()
