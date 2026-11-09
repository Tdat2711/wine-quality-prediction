"""Train baseline + Ridge using train/validation only; never read test files."""
import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from .encoding import read_source_csv, resolve_source_path
from .plot_model import render_diagnostics


def metrics(y, pred):
    if not np.isfinite(pred).all():
        raise ValueError('Non-finite predictions')
    return {'MAE': float(mean_absolute_error(y, pred)),
            'RMSE': float(np.sqrt(mean_squared_error(y, pred))),
            'R2': float(r2_score(y, pred))}


def main():
    module_root = Path(__file__).resolve().parents[1]
    default_data_dir = str(module_root / 'outputs')
    default_output = str(module_root / 'outputs' / 'model_product')
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default=default_data_dir)
    parser.add_argument('--output', default=default_output)
    parser.add_argument('--alphas', type=float, nargs='+', default=[0.1, 1, 10, 100, 1000])
    args = parser.parse_args()
    if not args.alphas or any(not np.isfinite(a) or a <= 0 for a in args.alphas):
        raise ValueError('Alphas must be finite positive values')
    data = Path(args.data_dir).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = json.loads((data / 'report.json').read_text(encoding='utf-8'))
    source = resolve_source_path(report['source'], relative_to=data.parent)
    source_bytes = source.read_bytes()
    current_sha = hashlib.sha256(source_bytes).hexdigest()
    header_whitespace_only = False
    if current_sha != report['sha256']:
        # Accept only a byte-identical original after stripping whitespace before
        # the first header. Any other change requires regenerating encoded data.
        header_whitespace_only = (
            hashlib.sha256(source_bytes.lstrip(b' \t')).hexdigest() == report['sha256'])
        if not header_whitespace_only:
            raise ValueError('Source changed since encoding; regenerate encoded data first')
        print('Source differs only by leading whitespace before first header; row bytes unchanged.', flush=True)
    raw = read_source_csv(source)
    features = pd.read_csv(data / 'product/features.csv')
    arrays = {}
    # Deliberately do not load y_test/X_test or use test metrics for selection.
    for split in ['train', 'validation']:
        x = sparse.load_npz(data / 'product' / f'X_{split}.npz').astype(np.float64)
        y = np.load(data / f'y_{split}.npy').astype(np.float64)
        ids = np.load(data / f'row_ids_{split}.npy')
        if x.shape != (len(y), len(features)) or len(ids) != len(y):
            raise ValueError(f'X/y/features mismatch: {split}')
        np.testing.assert_array_equal(y, raw.points.iloc[ids].to_numpy(dtype=float))
        if not np.isfinite(x.data).all() or not np.isfinite(y).all():
            raise ValueError(f'Non-finite input: {split}')
        arrays[split] = (x, y, ids)
    x_train, y_train, _ = arrays['train']
    x_val, y_val, ids_val = arrays['validation']
    rows = []
    predictions = {}
    baseline = DummyRegressor(strategy='mean').fit(x_train, y_train)
    candidates = [('Baseline_mean', None, baseline)]
    candidates.extend((f'Ridge_alpha_{a:g}', a,
                       Ridge(alpha=a, solver='lsqr', tol=1e-8, max_iter=10000))
                      for a in sorted(set(args.alphas)))
    best = None
    for name, alpha, model in candidates:
        if alpha is not None:
            model.fit(x_train, y_train)
            if model.n_iter_ is not None and np.max(model.n_iter_) >= 10000:
                raise RuntimeError(f'{name}: iteration limit; cannot trust fit')
        for split in ['train', 'validation']:
            x, y, _ = arrays[split]
            pred = model.predict(x)
            rows.append({'model': name, 'alpha': alpha, 'split': split, **metrics(y, pred)})
            if split == 'validation':
                predictions[name] = pred
        val = rows[-1]
        print(f'{name}: validation MAE={val["MAE"]:.4f}, RMSE={val["RMSE"]:.4f}, '
              f'R2={val["R2"]:.4f}', flush=True)
        if alpha is not None and (best is None or
                (val['MAE'], val['RMSE']) < (best['MAE'], best['RMSE'])):
            best = {**val, 'estimator': model}
    comparison = pd.DataFrame(rows)
    comparison.to_csv(out / 'metrics.csv', index=False, encoding='utf-8-sig')
    best_name = best['model']
    pred = predictions[best_name]
    residual = y_val - pred
    baseline_mae = metrics(y_val, predictions['Baseline_mean'])['MAE']
    improvement = (baseline_mae - best['MAE']) / baseline_mae * 100
    outside_count = int(((pred < y_train.min()) | (pred > y_train.max())).sum())
    audit = raw.iloc[ids_val][['title', 'country', 'variety', 'price', 'vintage_year']].copy()
    audit.insert(0, 'source_row_id', ids_val)
    audit['points_actual'] = y_val
    audit['points_predicted'] = pred
    audit['points_baseline'] = predictions['Baseline_mean']
    audit['residual_actual_minus_predicted'] = residual
    audit['absolute_error'] = np.abs(residual)
    audit['squared_error'] = residual ** 2
    audit.to_csv(out / 'validation_predictions.csv', index=False, encoding='utf-8-sig')
    audit.nlargest(20, 'absolute_error').to_csv(out / 'largest_errors.csv', index=False,
                                              encoding='utf-8-sig')
    groups = []
    for col in ['country', 'variety']:
        for key, g in audit.groupby(col, dropna=False):
            groups.append({'dimension': col, 'group': str(key), 'n': len(g),
                           'MAE': float(g.absolute_error.mean()),
                           'RMSE': float(np.sqrt(g.squared_error.mean())),
                           'mean_residual': float(g.residual_actual_minus_predicted.mean())})
    score_bands = pd.cut(audit.points_actual, [-np.inf, 85, 89, 94, np.inf],
                        labels=['<=85', '86-89', '90-94', '>=95'])
    for key, g in audit.groupby(score_bands, observed=True):
        groups.append({'dimension': 'actual_points_band', 'group': str(key), 'n': len(g),
                       'MAE': float(g.absolute_error.mean()),
                       'RMSE': float(np.sqrt(g.squared_error.mean())),
                       'mean_residual': float(g.residual_actual_minus_predicted.mean())})
    group_frame = pd.DataFrame(groups)
    group_frame.to_csv(out / 'errors_by_group.csv', index=False, encoding='utf-8-sig')
    coef = features.copy()
    coef['coefficient'] = best['estimator'].coef_
    coef['absolute_coefficient'] = np.abs(coef.coefficient)
    coef.sort_values('absolute_coefficient', ascending=False).to_csv(
        out / 'ridge_coefficients.csv', index=False, encoding='utf-8-sig')
    encoder = joblib.load(data / 'encoder.joblib')
    model_bundle = {'model': best['estimator'], 'baseline': baseline,
                    'preprocessor': encoder['preprocessor'],
                    'feature_indices': encoder['profiles']['product'],
                    'feature_names': features.feature_name.tolist(),
                    'profile': 'product', 'target': 'points', 'alpha': best['alpha'],
                    'source_sha256': report['sha256'],
                    'train_target_range': [float(y_train.min()), float(y_train.max())]}
    joblib.dump(model_bundle, out / 'ridge_product.joblib', compress=3)
    loaded = joblib.load(out / 'ridge_product.joblib')
    np.testing.assert_allclose(loaded['model'].predict(x_val[:10]), pred[:10], atol=1e-10)
    # Independent arithmetic check of headline metrics.
    assert np.isclose(best['MAE'], np.abs(residual).mean())
    assert np.isclose(best['RMSE'], np.sqrt(np.mean(residual ** 2)))
    render_diagnostics(audit, best['alpha'], best['MAE'], best['RMSE'], out)
    # Only train and validation counts enter this model report.
    summary = {'profile': 'product', 'target': 'points', 'features': len(features),
               'train_rows': len(y_train), 'validation_rows': len(y_val),
               'selection_rule': 'lowest validation MAE; tie-break RMSE',
               'alphas': sorted(set(args.alphas)), 'selected_model': best_name,
               'selected_alpha': best['alpha'], 'validation': metrics(y_val, pred),
               'baseline_validation': metrics(y_val, predictions['Baseline_mean']),
               'mae_improvement_percent': improvement, 'test_evaluated': False,
               'validation_predictions_outside_train_range': outside_count,
               'intercept': float(best['estimator'].intercept_),
               'source_current_sha256': current_sha,
               'source_header_whitespace_only_change': header_whitespace_only,
               'prediction_min': float(pred.min()), 'prediction_max': float(pred.max())}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Kết quả baseline và Ridge — validation', '',
             f'- Train: {len(y_train):,} dòng; validation: {len(y_val):,} dòng; {len(features)} đầu vào số.',
             f'- Chọn {best_name} theo MAE validation thấp nhất trong lưới alpha đã định.',
             f'- Baseline MAE: {baseline_mae:.4f}; Ridge MAE: {best["MAE"]:.4f}.',
             f'- MAE giảm {improvement:.2f}% so với baseline.',
             f'- Ridge RMSE: {best["RMSE"]:.4f}; R²: {best["R2"]:.4f}.',
             '- Chưa tính chỉ số dự đoán trên test. Đây là kết quả chọn mô hình, chưa là kết quả cuối.', '',
             '## Giới hạn', '',
             '- Đầu vào là thông tin sản phẩm; không dùng review, người chấm hoặc points làm feature.',
             '- Chia theo tên rượu, không phải theo winery hay thời gian.',
             '- Dữ liệu đầu vào đã làm sạch trước project; chưa kiểm chứng được toàn bộ lịch sử xử lý.',
             '- Hệ số là liên hệ có điều kiện trong mô hình, không chứng minh nhân quả.',
             '- Có thể dự đoán số thập phân hoặc ngoài khoảng điểm train; không làm tròn/cắt điểm khi tính metrics.',
             '- Cần kiểm tra sai số ở nhóm ít mẫu và ở hai đầu thang điểm trước khi sử dụng.', '',
             f'- Có {outside_count}/{len(y_val)} dự đoán ngoài khoảng điểm train; lớn nhất {pred.max():.2f}.',
             '- Đây là mô hình thử nghiệm; chưa phù hợp để tự động đưa ra điểm chất lượng thực tế.', '',
             '## Đầu ra', '',
             '- metrics.csv: cả train và validation cho từng cấu hình.',
             '- validation_predictions.csv: điểm thật, dự đoán, baseline và sai số từng dòng.',
             '- errors_by_group.csv: sai số theo quốc gia, giống nho và khoảng điểm; luôn xem n.',
             '- largest_errors.csv: 20 trường hợp sai số lớn nhất.',
             '- ridge_coefficients.csv: hệ số trên feature đã mã hóa/chuẩn hóa.',
             '- validation_diagnostics.png: biểu đồ kiểm tra mô hình.',
             '- ridge_product.joblib: mô hình + encoder để dự đoán dữ liệu mới.', '']
    (out / 'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Selected {best_name}; MAE improvement {improvement:.2f}%; test untouched.', flush=True)


if __name__ == '__main__':
    main()
