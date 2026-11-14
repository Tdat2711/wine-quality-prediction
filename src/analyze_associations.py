"""Exploratory title-level price/points association; TRAIN only, no model fit."""
import argparse
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from src.reporting import ROOT, metadata, output_directory, write_json, markdown_table
from src.split_data import normalize_title


def grouped_observations(train):
    required = {'title', 'price', 'points'}
    if not required.issubset(train):
        raise ValueError(f'Missing columns: {sorted(required - set(train))}')
    values = train[['price', 'points']].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(values.to_numpy()).all() or not values.price.gt(0).all():
        raise ValueError('Expected finite points and positive observed prices')
    values['title_group'] = train.title.map(normalize_title)
    if values.title_group.eq('').any() or train.title.isna().any():
        raise ValueError('Missing title cannot define an independent analysis group')
    return values.groupby('title_group', sort=True).agg(
        price=('price', 'median'), points=('points', 'median'), rows=('price', 'size')).reset_index()


def association(groups, repetitions=2000, seed=42):
    if repetitions < 2:
        raise ValueError('Bootstrap needs at least two repetitions')
    result = {'groups': len(groups), 'bootstrap_repetitions': repetitions, 'seed': seed,
              'status': 'insufficient_data', 'rho': None, 'p_value_approx': None,
              'ci_low': None, 'ci_high': None, 'valid_bootstrap': 0}
    if len(groups) < 3 or groups.price.nunique() < 2 or groups.points.nunique() < 2:
        return result
    x, y = groups.price.to_numpy(), groups.points.to_numpy()
    rho, p = spearmanr(x, y, alternative='two-sided')
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(repetitions):
        idx = rng.integers(0, len(groups), len(groups))
        if np.unique(x[idx]).size < 2 or np.unique(y[idx]).size < 2:
            continue
        samples.append(float(spearmanr(x[idx], y[idx]).statistic))
    result.update(rho=float(rho), p_value_approx=float(p), valid_bootstrap=len(samples))
    if len(samples) >= max(2, int(0.9 * repetitions)):
        low, high = np.percentile(samples, [2.5, 97.5])
        result.update(status='ok', ci_low=float(low), ci_high=float(high))
    return result


def run(train_path=ROOT / 'data/processed/splits/train.csv', output_dir=ROOT / 'outputs/analysis',
        repetitions=2000, seed=42):
    info = metadata([train_path], 'train; median price and points per normalized title', seed)
    groups = grouped_observations(pd.read_csv(train_path))
    result = association(groups, repetitions, seed)
    out = output_directory(output_dir, [train_path])
    groups.to_csv(out / 'title_groups.csv', index=False)
    table = pd.DataFrame([result])
    table.to_csv(out / 'price_points_spearman.csv', index=False)
    write_json(out / 'summary.json', {**info, 'result': result})
    report = ['# Giá và điểm — phân tích thống kê khám phá', '',
              '**Câu hỏi:** giá và điểm có quan hệ đơn điệu ở cấp nhóm title trên train không?', '',
              'Mỗi title chuẩn hóa đóng góp một cặp trung vị giá–điểm; đây không phải định danh chai rượu duy nhất.', '',
              markdown_table(table), '',
              'Spearman hai phía; p-value xấp xỉ, ngưỡng tham khảo 0,05. Khoảng tin cậy percentile 95% '
              f'từ {repetitions} bootstrap nhóm title, seed {seed}. Giá và log giá giữ cùng thứ hạng, không kiểm định hai lần.', '',
              '**Diễn giải:** ' + (f'rho = {result["rho"]:.4f}; khoảng tin cậy '
              f'[{result["ci_low"]:.4f}, {result["ci_high"]:.4f}]. '
              'Độ lớn hệ số mô tả quan hệ đơn điệu, không phải mức tăng điểm khi tăng giá.'
              if result['status'] == 'ok' else 'Không đủ điều kiện để kết luận; không báo ý nghĩa thống kê.'), '',
              '**Giới hạn:** phân tích sau EDA, không phải giả thuyết đăng ký trước; chưa kiểm soát quốc gia, '
              'giống nho, winery hoặc người chấm. Các nhóm có thể còn phụ thuộc, làm p-value/CI lạc quan. '
              'P-value rất nhỏ có thể do cỡ mẫu lớn; giá trị 0 trong file là giới hạn số thực, không phải xác suất đúng bằng 0. '
              'Chỉ đại diện các review train có giá quan sát; không suy luận nhân quả.', '',
              '**Tái lập:** `python -m src.analyze_associations`; số liệu lấy từ '
              '`price_points_spearman.csv`; phiên bản, checksum và phạm vi tại `summary.json`.', '']
    (out / 'REPORT.md').write_text('\n'.join(report), encoding='utf-8')
    print(table.to_string(index=False))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=str, default=str(ROOT / 'outputs/analysis'))
    args = parser.parse_args()
    run(output_dir=args.output_dir)


if __name__ == '__main__':
    main()
