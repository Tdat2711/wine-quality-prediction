"""Regression checks for the shared, descriptive notebook plots."""

import importlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import create_eda_plots as plots


class EdaPlotTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_import_does_not_read_csv_draw_or_export_figures(self):
        with (
            patch.object(pd, "read_csv", side_effect=AssertionError("CSV read during import")),
            patch.object(plt, "figure", side_effect=AssertionError("Figure created during import")),
            patch.object(Figure, "savefig", side_effect=AssertionError("Figure exported during import")),
        ):
            importlib.reload(plots)

    def test_display_window_does_not_remove_source_rows(self):
        source = pd.DataFrame(
            {"price": [10.0, 25.0, 300.0, 500.0], "points": [85, 88, 92, 90]}
        )
        before = source.copy(deep=True)
        distribution = plots.plot_price_distribution(source)
        scatter = plots.plot_price_points(source)
        pd.testing.assert_frame_equal(source, before)
        self.assertEqual(sum(bar.get_height() for bar in distribution.axes[0].patches), 3)
        self.assertIn("1 bản ghi trên khung", distribution.texts[0].get_text())
        self.assertEqual(len(scatter.axes[0].collections[0].get_offsets()), 4)
        self.assertIn("3 điểm nằm trong khung", scatter.texts[0].get_text())

    def test_invalid_observed_samples_fail_instead_of_silently_dropping_rows(self):
        invalid = [
            pd.DataFrame({"price": [], "points": []}),
            pd.DataFrame({"price": [20.0]}),
            pd.DataFrame({"price": [np.nan], "points": [88]}),
            pd.DataFrame({"price": pd.Series([pd.NA], dtype="Float64"), "points": [88]}),
            pd.DataFrame({"price": [0.0], "points": [88]}),
            pd.DataFrame({"price": [-1.0], "points": [88]}),
            pd.DataFrame({"price": [np.inf], "points": [88]}),
            pd.DataFrame({"price": [20.0], "points": [np.nan]}),
            pd.DataFrame({"price": [20.0], "points": pd.Series([pd.NA], dtype="Int64")}),
            pd.DataFrame({"price": [20.0], "points": [101]}),
        ]
        for source in invalid:
            with self.subTest(source=source.to_dict()):
                with self.assertRaises(ValueError):
                    plots.plot_price_distribution(source)


if __name__ == "__main__":
    unittest.main()
