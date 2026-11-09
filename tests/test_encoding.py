"""Tests for wine encoding, preprocessing pipelines, and model evaluation."""

import unittest
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from scipy import sparse

from wine_encoding.src.encoding import (
    SOURCE_COLUMNS,
    PRODUCT,
    REVIEW,
    CATEGORICAL,
    NUMERIC,
    FLAGS,
    TEXT,
    normalize,
    with_missing_flags,
    read_source_csv,
    resolve_source_path,
)
from wine_encoding.src.transform import prepare_new_frame


class WineEncodingIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.encoding_dir = cls.repo_root / "wine_encoding"
        cls.outputs_dir = cls.encoding_dir / "outputs"
        cls.report_file = cls.outputs_dir / "report.json"
        
        with cls.report_file.open("r", encoding="utf-8") as f:
            cls.report = json.load(f)

    def test_source_data_exists_and_matches_checksum(self):
        source_path = resolve_source_path(self.report["source"], relative_to=self.encoding_dir)
        self.assertTrue(source_path.is_file(), f"Source data file not found: {source_path}")
        
        # Verify schema
        df = read_source_csv(source_path)
        self.assertEqual(len(df), self.report["rows"])
        self.assertEqual(set(df.columns), set(SOURCE_COLUMNS))

    def test_encoder_bundle_integrity(self):
        bundle_path = self.outputs_dir / "encoder.joblib"
        self.assertTrue(bundle_path.is_file())
        bundle = joblib.load(bundle_path)
        
        self.assertIn("preprocessor", bundle)
        self.assertIn("profiles", bundle)
        self.assertIn("product", bundle["profiles"])
        self.assertIn("review", bundle["profiles"])
        self.assertIn("all_attributes_audit", bundle["profiles"])

    def test_group_separation_and_split_integrity(self):
        manifest_path = self.outputs_dir / "split_manifest.csv"
        self.assertTrue(manifest_path.is_file())
        manifest = pd.read_csv(manifest_path)
        
        # Zero group leakage across splits
        splits_per_group = manifest.groupby("title_group")["split"].nunique()
        self.assertTrue((splits_per_group == 1).all(), "Detected title group crossing split boundaries!")

    def test_model_product_prediction_reproducibility(self):
        model_path = self.outputs_dir / "model_product" / "ridge_product.joblib"
        self.assertTrue(model_path.is_file())
        bundle = joblib.load(model_path)
        
        test_samples = pd.DataFrame([
            {
                "country": "US",
                "designation": "Reserve",
                "province": "California",
                "region_1": "Napa Valley",
                "region_2": "Napa",
                "variety": "Cabernet Sauvignon",
                "winery": "Example Winery",
                "price": 75.0,
                "vintage_year": 2018.0,
            }
        ])
        
        prepared = prepare_new_frame(test_samples, "product")
        x = sparse.csr_matrix(bundle["preprocessor"].transform(prepared), dtype=np.float64)
        x_selected = x[:, bundle["feature_indices"]]
        pred = bundle["model"].predict(x_selected)
        
        self.assertEqual(len(pred), 1)
        self.assertTrue(np.isfinite(pred[0]))
        # Realistic wine score
        self.assertGreaterEqual(pred[0], 80.0)
        self.assertLessEqual(pred[0], 100.0)


if __name__ == "__main__":
    unittest.main()
