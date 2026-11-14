"""Additive reports from saved predictions. Never train or load a fitted estimator."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.reporting import ROOT, metadata, output_directory, write_json, markdown_table
from .data import load_report, read_part

BANDS = ['≤85', '86–89', '90–94', '≥95']


def validate_predictions(frame):
    columns = ['source_row_id', 'points_actual', 'points_predicted', 'points_baseline']
    missing = set(columns) - set(frame)
    if missing:
        raise ValueError(f'Missing prediction columns: {sorted(missing)}')
    if frame.empty:
        raise ValueError('Predictions must not be empty')
    numeric = frame[columns].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(numeric.to_numpy()).all():
        raise ValueError('Predictions and row IDs must be finite')
    ids = numeric.source_row_id
    if ids.duplicated().any() or ids.lt(0).any() or ids.ne(np.floor(ids)).any():
        raise ValueError('source_row_id must be unique nonnegative integers')
    return numeric


def summarize_predictions(frame, split):
    values = validate_predictions(frame)
    y, pred, baseline = (values[c].to_numpy() for c in
                         ('points_actual', 'points_predicted', 'points_baseline'))
    error = np.abs(y - pred)
    baseline_mae = mean_absolute_error(y, baseline)
    row = {'split': split, 'n': len(y), 'MAE': mean_absolute_error(y, pred),
           'RMSE': np.sqrt(mean_squared_error(y, pred)),
           'R2': r2_score(y, pred) if len(y) > 1 else None,
           'baseline_MAE': baseline_mae,
           'baseline_RMSE': np.sqrt(mean_squared_error(y, baseline)),
           'baseline_R2': r2_score(y, baseline) if len(y) > 1 else None,
           'MAE_reduction_pct': 100 * (baseline_mae - error.mean()) / baseline_mae if baseline_mae else None}
    for k in (1, 2, 3):
        row[f'within_{k}_points_pct'] = float(100 * (error <= k).mean())
    groups = []
    bands = pd.cut(y, [-np.inf, 85, 89, 94, np.inf], labels=BANDS)
    for band in BANDS:
        mask = bands == band
        groups.append({'split': split, 'band': band, 'n': int(mask.sum()),
                       'MAE': float(error[mask].mean()) if mask.any() else None,
                       'mean_residual': float((y[mask] - pred[mask]).mean()) if mask.any() else None})
    return row, pd.DataFrame(groups)


def select_cases(predictions, validation, row_ids):
    validate_predictions(predictions)
    if len(validation) != len(row_ids) or len(predictions) != len(row_ids):
        raise ValueError('Validation row count differs from saved manifest')
    if not np.array_equal(predictions.source_row_id, row_ids):
        raise ValueError('Validation IDs do not match saved manifest order')
    if not np.array_equal(predictions.points_actual, validation.points):
        raise ValueError('Validation targets differ from saved predictions')
    result = predictions[['source_row_id', 'points_actual', 'points_predicted']].copy()
    for col in ('price', 'country', 'variety', 'description'):
        result[col] = validation[col].to_numpy()
    result['absolute_error'] = (result.points_actual - result.points_predicted).abs()
    small = result.sort_values(['absolute_error', 'source_row_id']).head(3).assign(selection='smallest_error')
    large = result.sort_values(['absolute_error', 'source_row_id'], ascending=[False, True]).head(3).assign(selection='largest_error')
    return pd.concat([small, large], ignore_index=True)


def render(groups, scores, out):
    for split, group in groups.groupby('split', sort=False):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
        labels = [f'{r.band}\nn={r.n:,}' for r in group.itertuples()]
        axes[0].bar(labels, group.MAE, color='#285C76')
        axes[0].set(ylabel='MAE (điểm)', title='Sai số tuyệt đối trung bình')
        axes[1].bar(labels, group.mean_residual, color='#722F37')
        axes[1].axhline(0, color='black', linewidth=.8)
        axes[1].set(ylabel='Điểm thật − dự đoán', title='Residual trung bình')
        fig.suptitle(f'{split}: theo khoảng điểm thật; nguồn: errors_by_band.csv')
        fig.tight_layout()
        fig.savefig(out / f'{split}_errors_by_band.png', dpi=160, bbox_inches='tight')
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(3)
    for i, row in scores.iterrows():
        bars = ax.bar(x + (i - .5) * .35, [row[f'within_{k}_points_pct'] for k in (1, 2, 3)],
                      width=.35, label=f'{row["split"]} (n={int(row["n"]):,})')
        ax.bar_label(bars, fmt='%.1f%%', fontsize=8, padding=2)
    ax.set(xticks=x, xticklabels=['±1 điểm', '±2 điểm', '±3 điểm'], ylim=(0, 105),
           ylabel='Tỷ lệ dự đoán (%)', title='Tỷ lệ trong ngưỡng sai số; nguồn: metrics.csv')
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / 'tolerance_rates.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def run(data_dir=ROOT / 'wine_encoding/outputs', output_dir=ROOT / 'outputs/model_report'):
    data = Path(data_dir)
    model = data / 'model_combined'
    paths = [model / 'validation_predictions.csv', model / 'test_evaluation/test_predictions.csv',
             model / 'summary.json', model / 'test_evaluation/summary.json', data / 'row_ids_validation.npy']
    report = load_report(data)
    paths.extend([data / 'report.json', Path(report['provenance']['validation']['path'])])
    info = metadata(paths, 'saved validation/test predictions; no fitting; post-evaluation descriptive metrics')
    frames = {name: pd.read_csv(paths[i]) for i, name in enumerate(('validation', 'test'))}
    records, groups = [], []
    for split, frame in frames.items():
        row, band = summarize_predictions(frame, split)
        original = json.loads((model / ('summary.json' if split == 'validation'
                                        else 'test_evaluation/summary.json')).read_text(encoding='utf-8'))
        if original['provenance'] != report['provenance']:
            raise ValueError(f'{split} prediction provenance differs from data')
        for key in ('MAE', 'RMSE', 'R2'):
            if not np.isclose(row[key], original[split][key], rtol=0, atol=1e-10):
                raise ValueError(f'{split} saved {key} differs from recomputed metric')
        if len(frame) != original[split]['n']:
            raise ValueError(f'{split} row count differs from summary')
        records.append(row)
        groups.append(band)
    cases = select_cases(frames['validation'], read_part(report, 'validation'), np.load(paths[4]))
    scores, grouped = pd.DataFrame(records), pd.concat(groups, ignore_index=True)
    out = output_directory(output_dir, paths)
    scores.to_csv(out / 'metrics.csv', index=False)
    grouped.to_csv(out / 'errors_by_band.csv', index=False)
    cases.to_csv(out / 'validation_cases.csv', index=False)
    write_json(out / 'summary.json', info)
    render(grouped, scores, out)
    interpretations = []
    for row in scores.itertuples():
        subset = grouped[(grouped.split == row.split) & grouped.n.gt(0)]
        hardest = subset.sort_values(['MAE', 'band'], ascending=[False, True]).iloc[0]
        reduction = (f'giảm {row.MAE_reduction_pct:.2f}% so baseline' if pd.notna(row.MAE_reduction_pct)
                     else 'mức giảm MAE không xác định vì baseline MAE bằng 0')
        interpretations.append(f'**{row.split}:** MAE {row.MAE:.3f} điểm, {reduction}; '
                               f'{row.within_2_points_pct:.2f}% dự đoán trong ±2 điểm. '
                               f'Nhóm sai số lớn nhất {hardest.band}: MAE {hardest.MAE:.3f}, '
                               f'n={int(hardest.n):,}, residual trung bình {hardest.mean_residual:.3f}.')
    text = ['# Đánh giá bổ sung từ dự đoán đã lưu', '',
            '**Câu hỏi:** mô hình sai bao nhiêu điểm, nhóm nào khó và những trường hợp nào minh họa giới hạn?', '',
            markdown_table(scores.round(6)), '', '![Ngưỡng sai số](tolerance_rates.png)', '',
            '\n\n'.join(interpretations), '',
            'Các tỷ lệ ±1/2/3 điểm tính cả biên, là thống kê bổ sung sau đánh giá; không phải accuracy phân loại '
            'hoặc tiêu chí chọn mô hình. Không cắt/làm tròn dự đoán trước tính metric.', '',
            markdown_table(grouped.round(6)), '',
            '![Validation theo nhóm](validation_errors_by_band.png)', '',
            '![Test theo nhóm](test_errors_by_band.png)', '',
            'Residual = điểm thật − dự đoán; số dương là dự đoán thấp. Nhóm theo điểm thật chỉ dùng '
            'đánh giá hồi cứu, chưa biết nhóm này khi dự đoán review mới. Xem số mẫu trước khi so sánh.', '',
            '## Trường hợp minh họa trên validation', '',
            'Chọn ba sai số nhỏ nhất và ba lớn nhất; hòa theo source_row_id tăng dần. '
            'Các trường hợp không đại diện toàn bộ dữ liệu và không chứng minh nguyên nhân sai số.', '',
            markdown_table(cases.round(6)), '',
            '**Giới hạn:** holdout từng được quan sát; audit mới kiểm tra trùng văn bản chính xác, '
            'chưa kiểm tra near-duplicate. Cần review đã có; không dự đoán chất lượng khách quan. '
            'Chưa có metadata-only để đo lợi ích riêng của review. Không điều chỉnh mô hình theo kết quả này.', '',
            '**Tái lập:** `python -m wine_encoding.src.report_results`. Các bảng CSV là nguồn số liệu; '
            'checksum, phiên bản và phạm vi nằm trong `summary.json`.', '']
    (out / 'REPORT.md').write_text('\n'.join(text), encoding='utf-8')
    print(scores.to_string(index=False))
    return scores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', default=str(ROOT / 'outputs/model_report'))
    args = parser.parse_args()
    run(output_dir=args.output_dir)


if __name__ == '__main__':
    main()
