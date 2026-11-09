"""Integration checks on the saved files and encoder."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from .encoding import normalize, with_missing_flags, read_source_csv


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'outputs'
    report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
    bundle = joblib.load(output / 'encoder.joblib')
    frame = read_source_csv(report['source'], relative_to=root)
    manifest = pd.read_csv(output / 'split_manifest.csv')
    if not manifest.groupby('title_group')['split'].nunique().eq(1).all():
        raise AssertionError('Title group overlap')
    coverage = pd.read_csv(output / 'column_coverage.csv')
    assert len(coverage) == 19 and set(coverage.column) == set(frame.columns)
    assert coverage.loc[coverage.column.eq('points'), 'encoded_feature_count'].iloc[0] == 0
    train_ids = np.load(output / 'row_ids_train.npy')
    train = normalize(frame.iloc[train_ids])
    for col in ['price', 'vintage_year', 'price_original', 'log_price']:
        actual = bundle['preprocessor'].named_transformers_[col].named_steps['impute'].statistics_[0]
        assert np.isclose(actual, train[col].median()), f'Non-train median: {col}'
    for split in ['train', 'validation', 'test']:
        y = np.load(output / f'y_{split}.npy')
        ids = np.load(output / f'row_ids_{split}.npy')
        np.testing.assert_array_equal(y, frame.points.iloc[ids].to_numpy(dtype=np.float32))
        for profile, columns in bundle['profiles'].items():
            x = sparse.load_npz(output / profile / f'X_{split}.npz')
            assert x.shape == (len(y), len(columns))
            assert np.isfinite(x.data).all()
    # Reloaded artifact must reproduce output, and tolerate unseen categories/missing numbers.
    sample = normalize(frame.iloc[train_ids[:3]])
    transformed = sparse.csr_matrix(bundle['preprocessor'].transform(with_missing_flags(sample)), dtype=np.float32)
    for profile, columns in bundle['profiles'].items():
        saved = sparse.load_npz(output / profile / 'X_train.npz')[:3]
        diff = saved - transformed[:, columns]
        assert diff.nnz == 0 or np.abs(diff.data).max() < 1e-6
    sample.loc[sample.index[0], 'country'] = '__NEVER_SEEN_COUNTRY__'
    sample.loc[sample.index[0], ['price', 'vintage_year']] = np.nan
    unseen = bundle['preprocessor'].transform(with_missing_flags(sample))
    assert np.isfinite(unseen.data).all()
    print('PASS: 19-column coverage, group separation, train-only medians, X/y alignment,')
    print('finite matrices, reload consistency, unseen categories and missing numeric inputs.')


if __name__ == '__main__':
    main()
