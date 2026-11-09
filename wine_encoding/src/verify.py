"""Verify locked artifacts, provenance, row ordering and train-only encoders."""
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from .data import ROOT, load_report, locked_parts
from .encoding import SOURCE_COLUMNS, normalize, with_missing_flags


def verify(data_dir=ROOT / 'outputs'):
    out = Path(data_dir)
    report = load_report(out)
    raw, parts = locked_parts(report['config'])
    bundle = joblib.load(out / 'encoder.joblib')
    if bundle.get('schema_version') != report['schema_version'] or bundle.get('provenance') != report['provenance']:
        raise ValueError('Encoder/report provenance mismatch')
    manifest = pd.read_csv(out / 'split_manifest.csv')
    assert manifest.source_row_id.is_unique
    assert len(manifest) == report['eligible_rows'] == sum(map(len, parts.values()))
    assert manifest.groupby('title_group')['split'].nunique().eq(1).all()
    assert report['rows'] == len(raw)
    assert report['excluded_rows'] == len(raw) - len(manifest)
    coverage = pd.read_csv(out / 'column_coverage.csv')
    assert set(coverage.column) == set(SOURCE_COLUMNS)
    for name, part in parts.items():
        ids = np.load(out / f'row_ids_{name}.npy')
        np.testing.assert_array_equal(ids, part.index)
        np.testing.assert_array_equal(np.load(out / f'y_{name}.npy'), part.points.to_numpy(dtype=np.float32))
        stored_manifest = manifest[manifest.split.eq(name)]
        np.testing.assert_array_equal(stored_manifest.source_row_id, ids)
        np.testing.assert_array_equal(stored_manifest.title_group, part.title_clean)
        sample = part.iloc[:10]
        diagnostic = sparse.csr_matrix(bundle['preprocessor'].transform(
            with_missing_flags(normalize(sample[SOURCE_COLUMNS]))), dtype=np.float32)
        expected = {profile: diagnostic[:, cols] for profile, cols in bundle['profiles'].items()}
        expected['combined'] = sparse.csr_matrix(bundle['combined'].transform(sample))
        for profile, encoded in expected.items():
            saved = sparse.load_npz(out / profile / f'X_{name}.npz')
            assert saved.shape == (len(part), report['profiles'][profile])
            assert np.isfinite(saved.data).all()
            assert len(pd.read_csv(out / profile / 'features.csv')) == saved.shape[1]
            diff = saved[:len(sample)] - encoded
            assert not diff.nnz or np.max(np.abs(diff.data)) < 1e-6
    train = normalize(parts['train'][SOURCE_COLUMNS])
    for col in ('price', 'vintage_year', 'price_original', 'log_price'):
        median = bundle['preprocessor'].named_transformers_[col].named_steps['impute'].statistics_[0]
        assert np.isclose(median, train[col].median())
    combined = bundle['combined']
    transformed = combined.named_steps['inputs'].transform(parts['train'])
    learned = combined.named_steps['features'].named_transformers_['numeric'].named_steps['impute'].statistics_
    np.testing.assert_allclose(learned, transformed[['log_price', 'vintage_year']].median())
    print('PASS: locked split/order, provenance, train medians, finite matrices and reload parity.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default=str(ROOT / 'outputs'))
    verify(parser.parse_args().data_dir)


if __name__ == '__main__':
    main()
