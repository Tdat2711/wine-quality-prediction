"""Select alpha by grouped training CV; evaluate only on validation."""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor

from .combined import INPUT_COLUMNS, build_pipeline, check_convergence, feature_names
from .cv import cross_validate, metrics
from .data import ROOT, SCHEMA_VERSION, load_report, normalized_reviews, read_part, review_matches
from .plot_model import render_diagnostics


def error_groups(audit):
    rows = []
    dimensions = {col: audit[col] for col in ('country', 'variety')}
    dimensions['actual_points_band'] = pd.cut(audit.points_actual, [-np.inf, 85, 89, 94, np.inf],
                                              labels=['<=85', '86-89', '90-94', '>=95'])
    for dimension, keys in dimensions.items():
        for key, group in audit.groupby(keys, dropna=False, observed=True):
            residual = group.points_actual - group.points_predicted
            rows.append({'dimension': dimension, 'group': str(key),
                         **metrics(group.points_actual, group.points_predicted),
                         'mean_residual': float(residual.mean())})
    return pd.DataFrame(rows)


def prediction_audit(frame, ids, pred, baseline, training_reviews):
    audit = frame[['title', 'country', 'variety', 'price', 'vintage_year']].copy()
    audit.insert(0, 'source_row_id', ids)
    audit['points_actual'] = frame.points.to_numpy(dtype=float)
    audit['points_predicted'] = pred
    audit['points_baseline'] = baseline
    audit['review_matches_train'] = review_matches(frame, training_reviews).to_numpy()
    audit['residual_actual_minus_predicted'] = audit.points_actual - pred
    audit['absolute_error'] = audit.residual_actual_minus_predicted.abs()
    audit['squared_error'] = audit.residual_actual_minus_predicted ** 2
    return audit


def train(data_dir=ROOT / 'outputs', output=None, alphas=(0.1, 1, 10, 100, 1000)):
    alphas = sorted(set(alphas))
    if not alphas or any(not np.isfinite(a) or a <= 0 for a in alphas):
        raise ValueError('Alphas must be finite positive values')
    data = Path(data_dir).resolve()
    report = load_report(data)
    config = report['config']
    frames = {name: read_part(report, name) for name in ('train', 'validation')}
    ids = {name: np.load(data / f'row_ids_{name}.npy') for name in frames}
    for name, frame in frames.items():
        if len(ids[name]) != len(frame):
            raise ValueError(f'Row ID mismatch: {name}')
        if not np.isfinite(frame.points.to_numpy(dtype=float)).all():
            raise ValueError(f'Invalid targets: {name}')
    training, validation = frames['train'], frames['validation']
    alpha, scores, means, folds = cross_validate(training, config, alphas, config.get('cv_folds', 5))
    # Selection finishes before validation labels are used to compute any metrics.
    pipeline = build_pipeline(config, alpha)
    pipeline.fit(training, training.points)
    check_convergence(pipeline.named_steps['ridge'])
    baseline = DummyRegressor(strategy='mean').fit(np.zeros((len(training), 1)), training.points)
    training_reviews = normalized_reviews(training.description).tolist()
    pred = pipeline.predict(validation)
    baseline_pred = baseline.predict(np.zeros((len(validation), 1)))
    audit = prediction_audit(validation, ids['validation'], pred, baseline_pred, training_reviews)
    clean = ~audit.review_matches_train
    names = feature_names(pipeline.named_steps['encode'])
    summary = {'schema_version': SCHEMA_VERSION, 'profile': 'combined', 'target': 'points',
               'train_rows': len(training), 'validation_rows': len(validation), 'features': len(names),
               'selected_alpha': alpha, 'alphas': alphas, 'cv_folds': config.get('cv_folds', 5),
               'selection_rule': 'lowest mean grouped train CV MAE; tie-break RMSE, alpha',
               'validation': metrics(validation.points, pred),
               'baseline_validation': metrics(validation.points, baseline_pred),
               'validation_without_train_review_overlap': metrics(validation.points[clean], pred[clean]),
               'baseline_without_train_review_overlap': metrics(validation.points[clean], baseline_pred[clean]),
               'review_overlap_rows': int(audit.review_matches_train.sum()),
               'test_evaluated': False, 'fit_on': 'train only', 'provenance': report['provenance'],
               'holdout_history': 'Seed-42 holdout has previously been observed; not a pristine test.'}
    lo, hi = float(training.points.min()), float(training.points.max())
    summary['validation_predictions_outside_train_range'] = int(((pred < lo) | (pred > hi)).sum())
    out = Path(output or data / 'model_combined').resolve()
    out.mkdir(parents=True, exist_ok=True)
    scores.to_csv(out / 'cv_metrics.csv', index=False)
    means.to_csv(out / 'cv_summary.csv', index=False)
    folds.insert(0, 'source_row_id', ids['train'])
    folds.to_csv(out / 'cv_manifest.csv', index=False)
    audit.to_csv(out / 'validation_predictions.csv', index=False, encoding='utf-8-sig')
    audit.nlargest(20, 'absolute_error').to_csv(out / 'largest_errors.csv', index=False, encoding='utf-8-sig')
    error_groups(audit).to_csv(out / 'errors_by_group.csv', index=False, encoding='utf-8-sig')
    rows = []
    for split, frame in frames.items():
        for name, predicted in [('Ridge', pipeline.predict(frame)),
                                ('Baseline_mean', baseline.predict(np.zeros((len(frame), 1))))]:
            rows.append({'model': name, 'split': split, **metrics(frame.points, predicted)})
    pd.DataFrame(rows).to_csv(out / 'metrics.csv', index=False)
    pd.DataFrame({'feature_name': names, 'coefficient': pipeline.named_steps['ridge'].coef_}).to_csv(
        out / 'ridge_coefficients.csv', index=False, encoding='utf-8-sig')
    bundle = {'schema_version': SCHEMA_VERSION, 'profile': 'combined', 'pipeline': pipeline,
              'baseline': baseline, 'input_columns': INPUT_COLUMNS, 'feature_names': list(names),
              'alpha': alpha, 'config': config, 'cv_summary': means.to_dict(orient='records'),
              'train_target_range': [lo, hi], 'training_reviews': sorted(set(training_reviews) - {''}),
              'provenance': report['provenance']}
    joblib.dump(bundle, out / 'ridge_combined.joblib', compress=3)
    np.testing.assert_allclose(joblib.load(out / 'ridge_combined.joblib')['pipeline'].predict(validation.head(10)),
                               pred[:10], rtol=0, atol=1e-10)
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    render_diagnostics(audit, alpha, summary['validation']['MAE'], summary['validation']['RMSE'], out)
    lines = ['# Metadata + review -> Ridge: validation', '',
             f'- Train: {len(training):,}; validation: {len(validation):,}; features: {len(names):,}.',
             f'- Alpha selected by grouped train CV: {alpha:g}. Pipeline fitted on train only.',
             f'- Validation metrics: {summary["validation"]}',
             f'- Baseline metrics: {summary["baseline_validation"]}',
             f'- Review matches with train: {summary["review_overlap_rows"]}.',
             f'- Validation excluding matching reviews: {summary["validation_without_train_review_overlap"]}',
             '- Test metrics have not been evaluated by this run.', '',
             '## Limits', '',
             '- Requires an existing review; does not predict quality before review availability.',
             '- Exact normalized review overlap is reported; near duplicates are not detected.',
             '- Seed-42 holdout was observed previously. No claim of a pristine test or zero leakage.',
             '- No experiment here establishes the incremental benefit of adding review text.',
             '- Predictions are not clipped or rounded; coefficients are not causal effects.', '']
    (out / 'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default=str(ROOT / 'outputs'))
    parser.add_argument('--output')
    parser.add_argument('--alphas', type=float, nargs='+', default=[0.1, 1, 10, 100, 1000])
    args = parser.parse_args()
    train(args.data_dir, args.output, args.alphas)


if __name__ == '__main__':
    main()
