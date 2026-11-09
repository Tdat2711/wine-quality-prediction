"""Verify combined pipeline, CV grouping/selection and validation metrics."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .cv import connected_groups, metrics
from .data import ROOT, load_report, read_part, normalized_reviews, review_matches
from .predict import load_model


def verify_model(data_dir=ROOT / 'outputs', model_dir=None):
    data = Path(data_dir)
    out = Path(model_dir or data / 'model_combined')
    report = load_report(data)
    summary = json.loads((out / 'summary.json').read_text(encoding='utf-8'))
    bundle = load_model(out / 'ridge_combined.joblib')
    assert bundle['provenance'] == report['provenance'] == summary['provenance']
    training, validation = read_part(report, 'train'), read_part(report, 'validation')
    saved = pd.read_csv(out / 'validation_predictions.csv')
    np.testing.assert_array_equal(saved.source_row_id, np.load(data / 'row_ids_validation.npy'))
    np.testing.assert_array_equal(saved.points_actual, validation.points)
    pred = bundle['pipeline'].predict(validation)
    np.testing.assert_allclose(pred, saved.points_predicted, rtol=0, atol=1e-10)
    for key in ('MAE', 'RMSE', 'R2'):
        assert np.isclose(metrics(validation.points, pred)[key], summary['validation'][key])
    matched = review_matches(validation, normalized_reviews(training.description))
    np.testing.assert_array_equal(matched, saved.review_matches_train)
    assert int(matched.sum()) == summary['review_overlap_rows']
    clean_metrics = metrics(validation.points[~matched], pred[~matched])
    assert clean_metrics['n'] == summary['validation_without_train_review_overlap']['n']
    for key in ('MAE', 'RMSE', 'R2'):
        assert (clean_metrics[key] is None and summary['validation_without_train_review_overlap'][key] is None) or np.isclose(
            clean_metrics[key], summary['validation_without_train_review_overlap'][key])
    scores = pd.read_csv(out / 'cv_metrics.csv')
    means = scores[scores.model.eq('Ridge')].groupby('alpha')[['MAE', 'RMSE']].mean().reset_index()
    winner = means.sort_values(['MAE', 'RMSE', 'alpha']).iloc[0].alpha
    assert winner == summary['selected_alpha'] == bundle['alpha']
    folds = pd.read_csv(out / 'cv_manifest.csv')
    np.testing.assert_array_equal(folds.source_row_id, np.load(data / 'row_ids_train.npy'))
    np.testing.assert_array_equal(folds.cv_group, connected_groups(training))
    assert folds.groupby('cv_group').fold.nunique().eq(1).all()
    sample = validation.head(20).copy()
    modified = sample.copy()
    for col in ('title', 'taster_name', 'taster_twitter_handle', 'winery', 'designation',
                'region_1', 'region_2', 'price_original', 'log_price', 'points', 'is_non_informative_review'):
        modified[col] = 'unused value'
    np.testing.assert_allclose(bundle['pipeline'].predict(sample), bundle['pipeline'].predict(modified), rtol=0, atol=1e-10)
    assert not summary['test_evaluated']
    print('PASS: combined raw inference, independent validation metrics, grouped CV selection and unused-field independence.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default=str(ROOT / 'outputs'))
    parser.add_argument('--model-dir')
    args = parser.parse_args()
    verify_model(args.data_dir, args.model_dir)


if __name__ == '__main__':
    main()
