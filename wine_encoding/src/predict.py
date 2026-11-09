"""Predict from six raw metadata/review columns using the saved complete pipeline."""
import argparse
from pathlib import Path
import joblib
import numpy as np
from .data import ROOT, SCHEMA_VERSION
from .encoding import read_source_csv


def load_model(path):
    bundle = joblib.load(path)
    if bundle.get('schema_version') != SCHEMA_VERSION or bundle.get('profile') != 'combined':
        raise ValueError('Expected a version-2 combined model; rerun train')
    return bundle


def predict(input_path, model_path=ROOT / 'outputs/model_combined/ridge_combined.joblib',
            output_path=ROOT / 'outputs/model_combined/new_predictions.csv'):
    raw = read_source_csv(input_path)
    if 'points_predicted' in raw:
        raise ValueError('Input already contains points_predicted')
    bundle = load_model(model_path)
    pred = bundle['pipeline'].predict(raw)
    if not np.isfinite(pred).all():
        raise ValueError('Non-finite predictions')
    result = raw.copy()
    result['points_predicted'] = pred
    lo, hi = bundle['train_target_range']
    result['prediction_outside_train_target_range'] = (pred < lo) | (pred > hi)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out, index=False, encoding='utf-8-sig')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--model', default=str(ROOT / 'outputs/model_combined/ridge_combined.joblib'))
    parser.add_argument('--output', default=str(ROOT / 'outputs/model_combined/new_predictions.csv'))
    args = parser.parse_args()
    result = predict(args.input, args.model, args.output)
    print(result.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
