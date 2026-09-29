from pathlib import Path
import sys
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clean_consistency import enforce_consistency
from clean_duplicates import find_possible_logical_duplicates, remove_duplicates
from handle_outliers_and_noise import process_dataset


class CleaningTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
