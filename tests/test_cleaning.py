from pathlib import Path
import sys
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clean_consistency import enforce_consistency
from clean_duplicates import find_possible_logical_duplicates, remove_duplicates
from handle_missing_values import handle_missing_values
from handle_outliers_and_noise import process_dataset


class CleaningTests(unittest.TestCase):
    def test_missing_price_is_preserved_without_cross_row_inference(self):
        source = pd.DataFrame(
            {
                "country": ["France", None],
                "designation": [None, None],
                "price": [20.0, None],
                "province": ["Bordeaux", None],
                "region_1": [None, None],
                "region_2": [None, None],
                "taster_name": ["A", None],
                "taster_twitter_handle": [None, None],
                "variety": ["Merlot", None],
                "winery": ["Same", "Same"],
                "description": ["review", "review"],
            }
        )
        cleaned, report = handle_missing_values(source)
        self.assertTrue(pd.isna(cleaned.loc[1, "price"]))
        self.assertEqual(cleaned.loc[1, "country"], "Unknown")
        self.assertEqual(cleaned.loc[1, "province"], "Unknown")
        self.assertEqual(report["price_left_missing"], 1)

    def test_country_code_us_is_preserved(self):
        source = pd.DataFrame({"country": ["US", " Us ", "France"]})
        cleaned, report = enforce_consistency(source)
        self.assertEqual(cleaned["country"].tolist(), ["US", "US", "France"])
        self.assertEqual(report["country_values_standardized"], 1)

    def test_only_exact_duplicates_are_removed(self):
        source = pd.DataFrame(
            {
                "Unnamed: 0": [0, 1, 2],
                "description": ["same", "same", "same"],
                "taster_name": ["A", "A", "A"],
                "title": ["Wine 1", "Wine 1", "Wine 2"],
                "price": [10.0, 10.0, 20.0],
            }
        )
        cleaned, report = remove_duplicates(source)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(report["exact_duplicates_removed"], 1)
        self.assertEqual(report["possible_logical_duplicate_groups"], 1)
        self.assertEqual(report["possible_logical_duplicate_rows"], 2)
        candidates = find_possible_logical_duplicates(cleaned)
        self.assertEqual(len(candidates), 2)

    def test_luxury_prices_are_retained_and_known_typos_are_audited(self):
        source = pd.DataFrame(
            {
                "title": [
                    "Luxury 2010 Wine",
                    "Blair 2013 Roger Rose Vineyard Chardonnay (Arroyo Seco)",
                    "Château les Ormes Sorbet 2013 Médoc",
                ],
                "description": ["A sufficiently detailed tasting note here"] * 3,
                "price": [2500.0, 2013.0, 3300.0],
            }
        )
        cleaned, report = process_dataset(source)
        self.assertIn(2500.0, cleaned["price"].tolist())
        self.assertEqual(cleaned["price_was_corrected"].sum(), 2)
        self.assertEqual(report["corrections"]["blair_2013"], 1)
        self.assertEqual(report["corrections"]["chateau_ormes_sorbet"], 1)

    def test_outlier_step_does_not_mark_missing_price_as_corrected(self):
        source = pd.DataFrame(
            {
                "title": ["Unknown wine", "Known wine"],
                "description": ["A tasting review", "Another tasting review"],
                "price": [float("nan"), 20.0],
            }
        )
        cleaned, _ = process_dataset(source)
        self.assertTrue(bool(cleaned.loc[0, "price_was_missing"]))
        self.assertFalse(bool(cleaned.loc[0, "price_was_corrected"]))
        self.assertTrue(pd.isna(cleaned.loc[0, "log_price"]))


if __name__ == "__main__":
    unittest.main()
