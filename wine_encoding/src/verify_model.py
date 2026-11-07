"""Verify saved model against validation predictions and raw-data inference."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from .encoding import read_source_csv
from .transform import prepare_new_frame


def main():
    root = Path(__file__).resolve().parents[1]
    out = root / 'outputs/model_product'
    report = json.loads((root / 'outputs/report.json').read_text(encoding='utf-8'))
    summary = json.loads((out / 'summary.json').read_text(encoding='utf-8'))
    bundle = joblib.load(out / 'ridge_product.joblib')
    saved = pd.read_csv(out / 'validation_predictions.csv')
    y = saved.points_actual.to_numpy()
    pred = saved.points_predicted.to_numpy()
    assert np.isclose(mean_absolute_error(y, pred), summary['validation']['MAE'])
    assert np.isclose(np.sqrt(mean_squared_error(y, pred)), summary['validation']['RMSE'])
    assert np.isclose(r2_score(y, pred), summary['validation']['R2'])
    all_metrics = pd.read_csv(out / 'metrics.csv')
    ridge_val = all_metrics[(all_metrics.split == 'validation') & all_metrics.alpha.notna()]
    winner = ridge_val.sort_values(['MAE', 'RMSE']).iloc[0]
    assert winner.model == summary['selected_model']
    raw = read_source_csv(report['source'], relative_to=root).iloc[saved.source_row_id.iloc[:100]].copy()
    def predict_raw(frame):
        prepared = prepare_new_frame(frame, 'product')
        x = sparse.csr_matrix(bundle['preprocessor'].transform(prepared), dtype=np.float64)
        return bundle['model'].predict(x[:, bundle['feature_indices']])
    reproduced = predict_raw(raw)
    np.testing.assert_allclose(reproduced, pred[:100], atol=1e-8)
    # Target and unused review fields cannot influence product predictions.
    modified = raw.copy()
    modified['points'] = -999
    modified['description'] = 'completely different review'
    modified['title'] = 'different title'
    modified['price_original'] = 9999
    np.testing.assert_allclose(predict_raw(modified), reproduced, atol=1e-8)
    assert 'points' not in bundle['feature_names']
    assert not summary['test_evaluated']
    print('PASS: independent validation metrics, alpha selection, saved model/raw CSV parity,')
    print('target and unused-field independence. Test metrics not evaluated.')


if __name__ == '__main__':
    main()
