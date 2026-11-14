"""Meaningful fixture checks for additive analysis; never fit the real model."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.pipeline import Pipeline
from src.analyze_associations import grouped_observations, association, run as association_run
from src.cleaning_report import snapshot
from src.create_eda_plots import content_unigrams
from src.reporting import ROOT, output_directory
from wine_encoding.src.report_results import summarize_predictions, select_cases, run as report_run
from wine_encoding.src.explain_features import examples
from wine_encoding.src.combined import build_pipeline, feature_names


class AnalysisReportTests(unittest.TestCase):
    def test_normalized_title_medians_and_source_preserved(self):
        frame = pd.DataFrame({'title': [' Same! ', 'same', 'other'],
                              'price': [10., 30., 40.], 'points': [80., 90., 95.]})
        before = frame.copy(deep=True)
        groups = grouped_observations(frame).set_index('title_group')
        self.assertEqual(groups.loc['same', 'price'], 20.)
        self.assertEqual(groups.loc['same', 'points'], 85.)
        self.assertEqual(groups.loc['same', 'rows'], 2)
        pd.testing.assert_frame_equal(frame, before)

    def test_bootstrap_reproducible_and_constant_or_small_is_insufficient(self):
        groups = pd.DataFrame({'price': np.arange(30), 'points': np.arange(30) % 7})
        a = association(groups, repetitions=30)
        self.assertEqual(a, association(groups, repetitions=30))
        self.assertEqual(a['status'], 'ok')
        self.assertLessEqual(a['ci_low'], a['ci_high'])
        for data in [groups.head(2), groups.assign(points=88)]:
            result = association(data, repetitions=10)
            self.assertEqual(result['status'], 'insufficient_data')
            self.assertIsNone(result['rho'])

    def test_association_only_reads_given_train_and_records_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'train.csv'
            pd.DataFrame({'title': ['a', 'b', 'c'], 'price': [10, 20, 30],
                          'points': [85, 87, 90]}).to_csv(path, index=False)
            before = path.read_bytes()
            read = pd.read_csv
            def train_only(source, **kwargs):
                self.assertEqual(Path(source), path)
                return read(source, **kwargs)
            with patch('src.analyze_associations.pd.read_csv', side_effect=train_only), \
                    contextlib.redirect_stdout(io.StringIO()):
                association_run(path, Path(tmp) / 'report', repetitions=20)
            info = json.loads((Path(tmp) / 'report/summary.json').read_text(encoding='utf-8'))
            self.assertIn(str(path.resolve()), info['inputs'])
            self.assertEqual(before, path.read_bytes())

    def test_content_words_keep_negation_minimum_documents_and_empty_input(self):
        frame = pd.Series(['the not berry berry', 'not citrus', 'berry without acidity'])
        before = frame.copy()
        words = content_unigrams(frame, min_documents=2).set_index('term')
        self.assertIn('not', words.index)
        self.assertNotIn('the', words.index)
        self.assertNotIn('citrus', words.index)
        self.assertEqual(words.loc['berry', 'documents'], 2)
        self.assertEqual(words.loc['berry', 'occurrences'], 3)
        pd.testing.assert_series_equal(frame, before)
        self.assertTrue(content_unigrams(pd.Series(['the and']), 1).empty)
        self.assertTrue(content_unigrams(pd.Series(dtype=str), 1).empty)

    def predictions(self):
        return pd.DataFrame({'source_row_id': [3, 1, 2, 4], 'points_actual': [88., 88., 88., 88.],
                             'points_predicted': [87., 86., 85., 84.], 'points_baseline': [80.] * 4})

    def test_tolerance_includes_boundaries_and_residual_direction(self):
        row, groups = summarize_predictions(self.predictions(), 'fixture')
        self.assertEqual(row['within_1_points_pct'], 25.)
        self.assertEqual(row['within_2_points_pct'], 50.)
        self.assertEqual(row['within_3_points_pct'], 75.)
        self.assertEqual(groups.set_index('band').loc['86–89', 'mean_residual'], 2.5)
        self.assertEqual(groups.set_index('band').loc['≥95', 'n'], 0)

    def test_invalid_predictions_rejected(self):
        good = self.predictions()
        for data in [good.head(0), good.assign(source_row_id=[1, 1, 2, 3]),
                     good.assign(points_predicted=[np.inf, 0, 0, 0]),
                     good.assign(points_actual=[np.nan, 88, 88, 88]),
                     good.assign(source_row_id=[.5, 1, 2, 3])]:
            with self.assertRaises(ValueError):
                summarize_predictions(data, 'bad')

    def test_cases_tie_break_and_row_identity_validation(self):
        predictions = self.predictions().assign(points_predicted=87.)
        validation = pd.DataFrame({'points': [88.] * 4, 'price': [20.] * 4,
                                   'country': ['A'] * 4, 'variety': ['B'] * 4,
                                   'description': ['example'] * 4})
        ids = predictions.source_row_id.to_numpy()
        cases = select_cases(predictions, validation, ids)
        self.assertEqual(cases.source_row_id.tolist(), [1, 2, 3, 1, 2, 3])
        with self.assertRaises(ValueError):
            select_cases(predictions, validation, ids[::-1])

    def test_output_guard_prevents_protected_directory_and_input_overwrite(self):
        for target in [ROOT, ROOT / 'data/processed', ROOT / 'wine_encoding/outputs/new_report']:
            with self.assertRaises(ValueError):
                output_directory(target)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                output_directory(tmp, [Path(tmp) / 'predictions.csv'])

    def test_cleaning_snapshot_distinguishes_missing_placeholders_and_flags(self):
        frame = pd.DataFrame({'price': [20., np.nan], 'country': ['Unknown', None],
                              'is_non_informative_review': [True, False]})
        result = snapshot(frame, 'fixture')
        self.assertEqual(result['missing_cells'], 2)
        self.assertEqual(result['placeholder_cells'], 1)
        self.assertEqual(result['short_review_flags'], 1)
        self.assertIsNone(snapshot(frame.head(1), 'removed', frame)['changed_cells_existing_columns'])

    def test_feature_examples_transform_only_and_sparse_parity(self):
        train = pd.DataFrame({'price': [10., 20., 30., 40.], 'vintage_year': [2001., np.nan, 2010., 2012.],
                              'country': ['A', 'A', 'A', 'B'], 'province': ['R'] * 4,
                              'variety': ['Red'] * 4, 'description': ['not berry wine'] * 4})
        config = {'category_min_frequency': 2, 'category_max_categories': 20,
                  'description_max_features': 30}
        pipeline = build_pipeline(config, 1).fit(train, [85, 87, 89, 91])
        encoder = pipeline.named_steps['encode']
        expected = encoder.transform(train.head(3)).tocsr()
        names = feature_names(encoder)
        with patch.object(Pipeline, 'fit', side_effect=AssertionError('must not fit')), \
                patch.object(csr_matrix, 'toarray', side_effect=AssertionError('must stay sparse')):
            raw, numeric, active, dims = examples({'pipeline': pipeline}, train)
        self.assertEqual(dims['empty_review_nonzero'], 0)
        self.assertEqual(dims['nonzero'], expected.nnz)
        for row in active.itertuples():
            self.assertAlmostEqual(row.value, expected[row.example, np.where(names == row.feature_name)[0][0]])


if __name__ == '__main__':
    unittest.main()
