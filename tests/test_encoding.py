"""Self-contained regression tests: no generated artifacts or real-data training required."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd
from scipy import sparse

from src.split_data import create_splits
from wine_encoding.src.combined import CombinedInputs, INPUT_COLUMNS, build_encoder, build_pipeline
from wine_encoding.src.cv import connected_groups, cross_validate, metrics
from wine_encoding.src.data import provenance, read_source_csv, normalized_reviews
from wine_encoding.src.encoding import SOURCE_COLUMNS, resolve_source_path
from wine_encoding.src.predict import predict, load_model
from wine_encoding.src.prepare import prepare
from wine_encoding.src.train import train
from wine_encoding.src.verify import verify
from wine_encoding.src.verify_model import verify_model
from wine_encoding.src.evaluate_test import evaluate_test


def fixture_frame():
    rows = []
    for i in range(120):
        high = i % 2 == 0
        rows.append(dict(country='France' if high else 'US', designation='Reserve', province='Region',
                         region_1='Region One', region_2='Region Two', taster_name='Reviewer',
                         taster_twitter_handle='@reviewer', variety='Red', winery=f'Winery {i % 3}',
                         price=np.nan if i == 119 else float(10 + i % 20),
                         vintage_year=np.nan if i % 9 == 0 else float(2000 + i % 20),
                         price_original=float(10 + i % 20), log_price=np.log1p(10 + i % 20),
                         is_non_informative_review=False, price_was_missing=i == 119,
                         price_was_corrected=False,
                         description=('ripe berry vanilla excellent' if high else 'tart acid green simple') + f' item{i}',
                         title=f'Wine Title {i}', points=94 if high else 82))
    return pd.DataFrame(rows)[SOURCE_COLUMNS]


class EncodingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        source = cls.root / 'source.csv'
        fixture_frame().to_csv(source, index=False)
        raw = pd.read_csv(source)
        cls.parts = create_splits(raw)
        splits = cls.root / 'splits'
        splits.mkdir()
        # Include an exact train/validation review duplicate while retaining the locked assignments.
        raw.loc[cls.parts['val'].index[0], 'description'] = cls.parts['train'].description.iloc[0]
        raw.to_csv(source, index=False)
        cls.parts = create_splits(raw)
        for name, part in cls.parts.items():
            part.to_csv(splits / f'{name}.csv', index=False)
        cls.config = dict(source=str(source), split_dir=str(splits), output=str(cls.root / 'outputs'),
                          category_min_frequency=2, category_max_categories=20,
                          description_max_features=100, title_max_features=30, cv_folds=5)
        cls.before = provenance(cls.config)
        with contextlib.redirect_stdout(io.StringIO()):
            cls.report = prepare(cls.config)
            reads = []
            def training_read(path, *args, **kwargs):
                reads.append(Path(path).stem)
                if Path(path).stem not in ('train', 'val'):
                    raise AssertionError('Training attempted to load source/test data')
                return read_source_csv(path, *args, **kwargs)
            with patch('wine_encoding.src.data.read_source_csv', side_effect=training_read):
                cls.summary = train(cls.config['output'])
            cls.training_reads = reads
        cls.out = Path(cls.config['output'])
        cls.bundle = load_model(cls.out / 'model_combined/ridge_combined.joblib')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_end_to_end_artifacts_preserve_sources_and_split_order(self):
        self.assertEqual(provenance(self.config), self.before)
        self.assertEqual(self.report['rows'], 120)
        self.assertEqual(self.report['eligible_rows'], 119)
        self.assertEqual(self.report['excluded_rows'], 1)
        with contextlib.redirect_stdout(io.StringIO()):
            verify(self.out)
            verify_model(self.out)
        for name, stored in [('train', 'train'), ('validation', 'val'), ('test', 'test')]:
            np.testing.assert_array_equal(np.load(self.out / f'row_ids_{name}.npy'), self.parts[stored].index)
        self.assertEqual(self.training_reads, ['train', 'val'])
        self.assertFalse(self.summary['test_evaluated'])
        self.assertFalse((self.out / 'model_combined/test_evaluation').exists())

    def test_missing_or_modified_split_fails_before_output(self):
        config = dict(self.config, output=str(self.root / 'should_not_exist'))
        path = Path(config['split_dir']) / 'val.csv'
        original = path.read_bytes()
        try:
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                prepare(config)
            path.write_bytes(original)
            changed = pd.read_csv(path)
            changed.loc[0, 'points'] += 1
            changed.to_csv(path, index=False)
            with self.assertRaises(AssertionError):
                prepare(config)
            self.assertFalse(Path(config['output']).exists())
        finally:
            path.write_bytes(original)

    def test_missing_input_never_falls_back_and_does_not_write(self):
        target = self.root / 'missing-input-output.csv'
        with self.assertRaises(FileNotFoundError):
            resolve_source_path(self.root / 'nonexistent.csv')
        with self.assertRaises(FileNotFoundError):
            predict(self.root / 'nonexistent.csv', self.out / 'model_combined/ridge_combined.joblib', target)
        self.assertFalse(target.exists())
        # An explicit base directory wins over the current working directory.
        self.assertEqual(resolve_source_path('source.csv', relative_to=self.root), self.root / 'source.csv')

    def test_raw_csv_prediction_and_reload_parity(self):
        sample = self.parts['val'][INPUT_COLUMNS].head(4)
        input_path, output_path = self.root / 'new.csv', self.root / 'predictions.csv'
        sample.to_csv(input_path, index=False)
        result = predict(input_path, self.out / 'model_combined/ridge_combined.joblib', output_path)
        expected = self.bundle['pipeline'].predict(sample)
        np.testing.assert_allclose(result.points_predicted, expected, atol=1e-10, rtol=0)
        self.assertTrue(np.isfinite(result.points_predicted).all())
        self.assertEqual(len(result), len(sample))
        reloaded = joblib.load(self.out / 'model_combined/ridge_combined.joblib')
        np.testing.assert_allclose(reloaded['pipeline'].predict(sample), expected, rtol=0, atol=1e-10)

    def test_unused_fields_and_targets_are_ignored(self):
        raw = self.parts['val'].head(5).copy()
        expected = self.bundle['pipeline'].predict(raw)
        for col in set(raw.columns) - set(INPUT_COLUMNS):
            raw[col] = 'invalid unused data'
        np.testing.assert_allclose(self.bundle['pipeline'].predict(raw), expected, rtol=0, atol=1e-10)

    def test_valid_missing_and_unknown_inputs_and_invalid_values(self):
        sample = self.parts['val'][INPUT_COLUMNS].head(2).copy()
        sample['country'] = '__UNSEEN__'
        sample['price'] = np.nan
        sample['vintage_year'] = np.nan
        sample['description'] = ''
        self.assertTrue(np.isfinite(self.bundle['pipeline'].predict(sample)).all())
        prepared = CombinedInputs().transform(sample)
        self.assertTrue(prepared.description.eq('').all())
        text = self.bundle['pipeline'].named_steps['encode'].named_steps['features'].named_transformers_['description']
        self.assertEqual(text.transform(prepared.description).nnz, 0)
        for value in [0, -1, np.inf, 'not a number']:
            bad = sample.copy()
            bad['price'] = value
            with self.subTest(price=value), self.assertRaises(ValueError):
                self.bundle['pipeline'].predict(bad)
        for value in [np.inf, 'invalid year']:
            bad = sample.copy()
            bad['vintage_year'] = value
            with self.assertRaises(ValueError):
                self.bundle['pipeline'].predict(bad)
        with self.assertRaises(ValueError):
            self.bundle['pipeline'].predict(sample.drop(columns='description'))

    def test_review_signal_affects_features_and_predictions(self):
        raw = fixture_frame().iloc[:40].copy()
        raw['country'] = 'France'
        raw['price'] = 20.0
        raw['vintage_year'] = 2010.0
        pipeline = build_pipeline(self.config, 0.1).fit(raw, raw.points)
        samples = pd.concat([raw.iloc[[0]], raw.iloc[[0]]], ignore_index=True)
        samples['description'] = ['ripe berry vanilla excellent', 'tart acid green simple']
        encoded = sparse.csr_matrix(pipeline.named_steps['encode'].transform(samples))
        self.assertGreater((encoded[0] - encoded[1]).nnz, 0)
        predictions = pipeline.predict(samples)
        self.assertGreater(predictions[0] - predictions[1], 1)

    def test_cv_transitive_groups_and_empty_reviews(self):
        frame = pd.DataFrame({'title': ['A', 'A', 'B', 'C', 'D'],
                              'description': ['one', 'two', 'two', '', '']})
        groups = connected_groups(frame)
        self.assertEqual(groups[0], groups[2])
        self.assertNotEqual(groups[3], groups[4])
        manifest = pd.read_csv(self.out / 'model_combined/cv_manifest.csv')
        self.assertTrue(manifest.groupby('cv_group').fold.nunique().eq(1).all())

    def test_fold_preprocessing_uses_only_fold_training_rows(self):
        raw = fixture_frame().dropna(subset=['price']).iloc[:45].copy()
        # Unique tokens occur twice inside each title/review-connected pair.
        for i in range(0, 44, 2):
            raw.loc[raw.index[i:i+2], 'description'] = f'not good wine specialtoken{i}'
        encoders = []
        def capture(config):
            encoder = build_encoder(config)
            encoders.append(encoder)
            return encoder
        with patch('wine_encoding.src.cv.build_encoder', side_effect=capture), contextlib.redirect_stdout(io.StringIO()):
            _, _, _, assignments = cross_validate(raw, self.config, [1.0], 5)
        for fold, encoder in enumerate(encoders):
            mask = assignments.fold.to_numpy() != fold
            prepared = CombinedInputs().transform(raw.iloc[np.flatnonzero(mask)])
            features = encoder.named_steps['features']
            learned = features.named_transformers_['numeric'].named_steps['impute'].statistics_
            np.testing.assert_allclose(learned, prepared[['log_price', 'vintage_year']].median())
            category = features.named_transformers_['category']
            for col, learned_values in zip(['country', 'province', 'variety'], category.categories_):
                self.assertEqual(set(learned_values), set(prepared[col]))
            text = features.named_transformers_['description']
            self.assertIn('not', text.vocabulary_)
            self.assertIn('not good', text.vocabulary_)
            train_tokens = set(' '.join(prepared.description).split())
            heldout_tokens = set(' '.join(raw.iloc[np.flatnonzero(~mask)].description).split()) - train_tokens
            self.assertTrue(heldout_tokens.isdisjoint(text.vocabulary_))

    def test_overlap_metrics_recomputed_and_cv_winner(self):
        saved = pd.read_csv(self.out / 'model_combined/validation_predictions.csv')
        self.assertEqual(self.summary['review_overlap_rows'], 1)
        clean = saved[~saved.review_matches_train]
        actual = metrics(clean.points_actual, clean.points_predicted)
        expected_metrics = self.summary['validation_without_train_review_overlap']
        self.assertEqual(actual['n'], expected_metrics['n'])
        for key in ('MAE', 'RMSE', 'R2'):
            self.assertAlmostEqual(actual[key], expected_metrics[key], places=10)
        scores = pd.read_csv(self.out / 'model_combined/cv_summary.csv')
        expected = scores.sort_values(['MAE', 'RMSE', 'alpha']).iloc[0].alpha
        self.assertEqual(expected, self.summary['selected_alpha'])

    def test_provenance_mismatch_rejected(self):
        path = Path(self.config['source'])
        original = path.read_bytes()
        try:
            path.write_bytes(original + b'\n')
            with self.assertRaisesRegex(ValueError, 'changed'):
                train(self.out)
        finally:
            path.write_bytes(original)

    def test_explicit_test_evaluation_uses_fixture_only_and_never_refits(self):
        # This evaluates synthetic fixture data, never the repository's holdout.
        target = self.root / 'fixture-test-evaluation'
        with patch('sklearn.pipeline.Pipeline.fit', side_effect=AssertionError('Must not refit')):
            summary = evaluate_test(self.out, output=target)
        self.assertTrue(summary['test_evaluated'])
        self.assertEqual(summary['test']['n'], len(self.parts['test']))
        with self.assertRaises(FileExistsError):
            evaluate_test(self.out, output=target)
        with self.assertRaisesRegex(ValueError, 'version-2 combined'):
            old = self.root / 'old-model.joblib'
            joblib.dump({'profile': 'product'}, old)
            load_model(old)


if __name__ == '__main__':
    unittest.main()
