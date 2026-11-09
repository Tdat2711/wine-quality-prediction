"""Encode new data using the fitted encoder, without refitting."""
import argparse
from pathlib import Path
import joblib
import numpy as np
from scipy import sparse
from .data import SCHEMA_VERSION
from .combined import CombinedInputs
from .encoding import normalize, with_missing_flags, read_source_csv


def prepare_new_frame(raw, profile):
    """Validate profile inputs and supply placeholders for unused source fields."""
    from .encoding import PRODUCT, REVIEW, CATEGORICAL, FLAGS, NUMERIC, TEXT
    if profile == 'combined':
        return CombinedInputs().transform(raw)
    if profile not in ('product', 'review', 'all_attributes_audit'):
        raise ValueError(f'Unknown profile: {profile}')
    raw = raw.copy()
    required = PRODUCT if profile == 'product' else REVIEW if profile == 'review' else (
        CATEGORICAL + FLAGS + NUMERIC + TEXT)
    missing = set(required) - set(raw.columns)
    if missing:
        raise ValueError(f'Missing inputs for {profile}: {sorted(missing)}')
    for col in set(CATEGORICAL + FLAGS + NUMERIC + TEXT) - set(raw.columns):
        raw[col] = False if col in FLAGS else np.nan if col in NUMERIC else ''
    return with_missing_flags(normalize(raw.drop(columns='points', errors='ignore')))


def main():
    module_root = Path(__file__).resolve().parents[1]
    default_encoder = str(module_root / 'outputs' / 'encoder.joblib')
    default_output = str(module_root / 'outputs' / 'new_data.npz')
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--encoder', default=default_encoder)
    parser.add_argument('--profile', choices=['combined', 'product', 'review', 'all_attributes_audit'],
                        default='combined')
    parser.add_argument('--output', default=default_output)
    args = parser.parse_args()
    raw = read_source_csv(args.input)
    bundle = joblib.load(args.encoder)
    if bundle.get('schema_version') != SCHEMA_VERSION:
        raise ValueError('Incompatible encoder; rerun prepare')
    if args.profile == 'combined':
        matrix = sparse.csr_matrix(bundle['combined'].transform(raw))
    else:
        normalized = prepare_new_frame(raw, args.profile)
        matrix = sparse.csr_matrix(bundle['preprocessor'].transform(normalized), dtype=np.float32)
        matrix = matrix[:, bundle['profiles'][args.profile]].tocsr()
    if not np.isfinite(matrix.data).all():
        raise ValueError('Non-finite encoded values')
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    sparse.save_npz(output, matrix)
    print(f'Saved {matrix.shape} to {output}; input row order preserved; no refit.')


if __name__ == '__main__':
    main()
