"""Predict product points from a raw CSV using saved training transformations."""
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from .transform import prepare_new_frame
from .encoding import read_source_csv


def main():
    module_root = Path(__file__).resolve().parents[1]
    default_model = str(module_root / 'outputs' / 'model_product' / 'ridge_product.joblib')
    default_output = str(module_root / 'outputs' / 'model_product' / 'new_predictions.csv')
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--model', default=default_model)
    parser.add_argument('--output', default=default_output)
    args = parser.parse_args()
    model_path = Path(args.model)
    if not model_path.is_file() and (module_root / args.model).is_file():
        model_path = module_root / args.model
    bundle = joblib.load(model_path)
    raw = read_source_csv(args.input, relative_to=module_root)
    normalized = prepare_new_frame(raw, bundle['profile'])
    x = sparse.csr_matrix(bundle['preprocessor'].transform(normalized), dtype=np.float64)
    x = x[:, bundle['feature_indices']]
    if x.shape[1] != len(bundle['feature_names']):
        raise ValueError('Feature mismatch')
    pred = bundle['model'].predict(x)
    if not np.isfinite(pred).all():
        raise ValueError('Non-finite predictions')
    if 'points_predicted' in raw:
        raise ValueError('Input already contains points_predicted; choose a raw input file')
    raw['points_predicted'] = pred
    lo, hi = bundle['train_target_range']
    raw['prediction_outside_train_target_range'] = (pred < lo) | (pred > hi)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out, index=False, encoding='utf-8-sig')
    print(f'Saved {len(raw)} predictions to {out}; no fit/refit.')
    print(raw.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
