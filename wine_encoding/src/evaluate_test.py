"""Explicit final test evaluation of an already selected model. No fitting/tuning."""
import argparse
import json
from pathlib import Path
import numpy as np
from .cv import metrics
from .data import ROOT, load_report, read_part
from .predict import load_model
from .train import prediction_audit, error_groups


def evaluate_test(data_dir=ROOT / 'outputs', model_dir=None, output=None):
    data = Path(data_dir)
    model_dir = Path(model_dir or data / 'model_combined')
    out = Path(output or model_dir / 'test_evaluation')
    report = load_report(data)
    bundle = load_model(model_dir / 'ridge_combined.joblib')
    if bundle['provenance'] != report['provenance']:
        raise ValueError('Model and data provenance differ')
    frame = read_part(report, 'test')
    pred = bundle['pipeline'].predict(frame)
    baseline = bundle['baseline'].predict(np.zeros((len(frame), 1)))
    audit = prediction_audit(frame, np.load(data / 'row_ids_test.npy'), pred, baseline, bundle['training_reviews'])
    clean = ~audit.review_matches_train
    summary = {'test_evaluated': True, 'alpha': bundle['alpha'],
               'test': metrics(frame.points, pred), 'baseline': metrics(frame.points, baseline),
               'test_without_train_review_overlap': metrics(frame.points[clean], pred[clean]),
               'baseline_without_train_review_overlap': metrics(frame.points[clean], baseline[clean]),
               'review_overlap_rows': int(audit.review_matches_train.sum()),
               'provenance': report['provenance'],
               'holdout_history': 'Seed-42 holdout was previously observed; not a pristine test.'}
    if out.exists():
        raise FileExistsError(f'Test evaluation output already exists: {out}')
    out.mkdir(parents=True)
    audit.to_csv(out / 'test_predictions.csv', index=False, encoding='utf-8-sig')
    error_groups(audit).to_csv(out / 'errors_by_group.csv', index=False, encoding='utf-8-sig')
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default=str(ROOT / 'outputs'))
    parser.add_argument('--model-dir')
    parser.add_argument('--output')
    args = parser.parse_args()
    print(json.dumps(evaluate_test(args.data_dir, args.model_dir, args.output), indent=2))


if __name__ == '__main__':
    main()
