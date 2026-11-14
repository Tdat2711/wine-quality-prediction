"""Illustrate the saved encoder on three TRAIN rows without refitting/densifying."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from src.reporting import ROOT, metadata, output_directory, write_json, markdown_table
from .combined import INPUT_COLUMNS, NUMERIC_COLUMNS, CATEGORY_COLUMNS, feature_names
from .data import load_report, read_part
from .predict import load_model


def examples(bundle, train):
    encoder = bundle['pipeline'].named_steps['encode']
    raw = train.head(3)[INPUT_COLUMNS].copy()
    prepared = encoder.named_steps['inputs'].transform(raw)
    columns = encoder.named_steps['features']
    numeric_pipe = columns.named_transformers_['numeric']
    imputed = numeric_pipe.named_steps['impute'].transform(prepared[NUMERIC_COLUMNS])
    scaled = numeric_pipe.named_steps['scale'].transform(imputed)
    names = feature_names(encoder)
    matrix = encoder.transform(raw).tocsr()
    numeric, active = [], []
    for i in range(len(raw)):
        for j, col in enumerate(NUMERIC_COLUMNS):
            numeric.append({'example': i, 'feature': col,
                            'raw': raw.iloc[i]['price' if col == 'log_price' else col],
                            'prepared': prepared.iloc[i][col], 'imputed': imputed[i, j], 'scaled': scaled[i, j]})
        row = matrix.getrow(i)
        for index, value in zip(row.indices, row.data):
            active.append({'example': i, 'feature_name': names[index], 'value': value})
    categories = columns.named_transformers_['category']
    probes = prepared.head(1).copy()
    for col in CATEGORY_COLUMNS:
        known = set(categories.categories_[CATEGORY_COLUMNS.index(col)])
        unknown = '__UNSEEN_DEMO__'
        while unknown in known:
            unknown += '_'
        probes[col] = unknown
    unknown_matrix = categories.transform(probes[CATEGORY_COLUMNS]).tocsr()
    empty_text = columns.named_transformers_['description'].transform([''])
    dimensions = {'rows': matrix.shape[0], 'features': matrix.shape[1], 'nonzero': matrix.nnz,
                  'unknown_category_nonzero': unknown_matrix.nnz, 'empty_review_nonzero': empty_text.nnz}
    return raw, pd.DataFrame(numeric), pd.DataFrame(active), dimensions


def run(data_dir=ROOT / 'wine_encoding/outputs', output_dir=ROOT / 'outputs/feature_examples'):
    data = Path(data_dir)
    report = load_report(data)
    model_path = data / 'model_combined/ridge_combined.joblib'
    paths = [model_path, data / 'report.json', Path(report['provenance']['train']['path'])]
    info = metadata(paths, 'first three train rows; saved encoder; no fit', seed=None)
    bundle = load_model(model_path)
    if bundle['provenance'] != report['provenance']:
        raise ValueError('Saved model and train provenance differ')
    raw, numeric, active, dimensions = examples(bundle, read_part(report, 'train'))
    encoder = bundle['pipeline'].named_steps['encode']
    probe = raw.head(1).assign(price=np.nan, vintage_year=np.nan)
    probe_prepared = encoder.named_steps['inputs'].transform(probe)
    numeric_pipe = encoder.named_steps['features'].named_transformers_['numeric']
    probe_imputed = numeric_pipe.named_steps['impute'].transform(probe_prepared[NUMERIC_COLUMNS])
    probe_scaled = numeric_pipe.named_steps['scale'].transform(probe_imputed)
    probe_table = pd.DataFrame({'feature': NUMERIC_COLUMNS, 'raw_missing': [True, True],
                                'imputed_train_median': probe_imputed[0], 'scaled': probe_scaled[0]})
    out = output_directory(output_dir, paths)
    raw.to_csv(out / 'raw_examples.csv', index=False)
    numeric.to_csv(out / 'numeric_steps.csv', index=False)
    active.to_csv(out / 'active_features.csv', index=False)
    probe_table.to_csv(out / 'missing_numeric_probe.csv', index=False)
    write_json(out / 'summary.json', {**info, 'dimensions': dimensions})
    text = ['# Minh họa đặc trưng từ pipeline đã lưu', '',
            'Ba dòng đầu train, không học lại encoder. Chỉ xuất phần tử khác 0 của ma trận sparse.', '',
            markdown_table(raw), '', '## Giá và niên vụ', '', markdown_table(numeric.round(6)), '',
            '`prepared` là log1p(price) hoặc năm gốc; `imputed` dùng trung vị train; '
            '`scaled` dùng trung bình/độ lệch chuẩn train. Không dùng đồng thời giá gốc và log giá.', '',
            '**Probe tổng hợp:** sao chép dòng train đầu rồi đặt giá/năm thiếu để minh họa imputer; '
            'đây không phải một quan trắc train mới hoặc bằng chứng hiệu năng cho giá thiếu.', '',
            markdown_table(probe_table.round(6)), '',
            '## Metadata và văn bản', '',
            'One-hot ánh xạ quốc gia/vùng/giống nho thành cột số; nhóm hiếm học trên train. '
            'Nhãn mới vào nhóm hiếm nếu có, nếu không khối tương ứng bằng 0. '
            'Review dùng TF-IDF unigram/bigram, giữ stopword và phủ định. Từ chưa biết bị bỏ qua. '
            'Đây là biểu diễn mô hình, khác bảng tần suất mô tả trong EDA.', '',
            f'Kích thước ví dụ: {dimensions["rows"]} × {dimensions["features"]}; '
            f'{dimensions["nonzero"]} phần tử khác 0. Probe nhãn chưa thấy: '
            f'{dimensions["unknown_category_nonzero"]} phần tử khác 0 trong khối category; '
            f'probe review rỗng: {dimensions["empty_review_nonzero"]} phần tử khác 0.', '',
            'Tên và giá trị từng đặc trưng hoạt động nằm trong `active_features.csv`; '
            'không thể so sánh độ lớn hệ số giữa các loại đặc trưng như tác động nhân quả.', '',
            '**Tái lập:** `python -m wine_encoding.src.explain_features`; checksum/phiên bản/phạm vi tại `summary.json`.', '']
    (out / 'REPORT.md').write_text('\n'.join(text), encoding='utf-8')
    print(dimensions)
    return dimensions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', default=str(ROOT / 'outputs/feature_examples'))
    args = parser.parse_args()
    run(output_dir=args.output_dir)


if __name__ == '__main__':
    main()
