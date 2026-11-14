"""Evidence for cleaning: pure replay in memory, never rewrite source datasets."""
import argparse
import numpy as np
import pandas as pd
from src.clean_consistency import enforce_consistency
from src.clean_duplicates import remove_duplicates
from src.handle_missing_values import handle_missing_values
from src.handle_outliers_and_noise import process_dataset
from src.reporting import ROOT, metadata, output_directory, write_json, markdown_table


def snapshot(frame, stage, before=None):
    content = frame.drop(columns=['Unnamed: 0'], errors='ignore')
    labels = ('Unknown', 'Not specified', 'Not applicable', 'Not provided')
    changed = 0
    if before is not None:
        if len(frame) != len(before):
            changed = None  # Row deletion is counted separately, not aligned by reset index.
        else:
            for col in before.columns.intersection(frame.columns):
                a, b = before[col].reset_index(drop=True), frame[col].reset_index(drop=True)
                same = (a.eq(b) | (a.isna() & b.isna())).fillna(False)
                changed += int((~same).sum())
    return {'stage': stage, 'rows': len(frame), 'columns': len(frame.columns),
            'missing_cells': int(frame.isna().sum().sum()),
            'missing_price': int(frame.price.isna().sum()),
            'exact_duplicate_rows_excluding_export_index': int(content.duplicated().sum()),
            'placeholder_cells': int(frame.isin(labels).sum().sum()),
            'removed_rows': 0 if before is None else len(before) - len(frame),
            'changed_cells_existing_columns': changed,
            'added_columns': 0 if before is None else len(frame.columns.difference(before.columns)),
            'short_review_flags': int(frame.get('is_non_informative_review', pd.Series(dtype=bool)).sum()),
            'price_correction_flags': int(frame.get('price_was_corrected', pd.Series(dtype=bool)).sum())}


def replay(raw):
    frame = raw.copy(deep=True)
    rows, actions = [snapshot(frame, 'raw')], {}
    for name, transform in [('missing', handle_missing_values), ('consistency', enforce_consistency),
                            ('duplicates', remove_duplicates), ('outliers_noise', process_dataset)]:
        before = frame
        frame, action = transform(frame)
        rows.append(snapshot(frame, name, before))
        actions[name] = action
    return frame, pd.DataFrame(rows), actions


def write_report(stages, actions, raw_path, cleaned_path, output_dir=ROOT / 'outputs/cleaning_report'):
    info = metadata([raw_path, cleaned_path], 'historical full-data cleaning audit; not train EDA')
    out = output_directory(output_dir, [raw_path, cleaned_path])
    stages.to_csv(out / 'stages.csv', index=False)
    missing = []
    for scope, path in [('raw', raw_path), ('cleaned', cleaned_path)]:
        source = pd.read_csv(path)
        for col in source:
            missing.append({'scope': scope, 'column': col, 'missing': int(source[col].isna().sum()),
                            'rows': len(source)})
    missing = pd.DataFrame(missing)
    missing.to_csv(out / 'missing_by_column.csv', index=False)
    write_json(out / 'summary.json', {**info, 'actions': actions,
                                    'stages': stages.replace({np.nan: None}).to_dict(orient='records')})
    report = ['# Bằng chứng làm sạch trước/sau', '', markdown_table(stages.fillna('không căn chỉnh')), '',
              'Các dòng được tái tạo bằng hàm cleaning thuần trong bộ nhớ và đối chiếu cleaned hiện có. '
              'Không ghi lại raw, interim hoặc cleaned. Missing thật khác placeholder. Duplicate không tính chỉ mục CSV.', '',
              '`changed_cells_existing_columns` chỉ so các ô cùng vị trí khi không xóa dòng; '
              'bước duplicate báo số dòng xóa riêng. Cột mới và cờ được đếm riêng, không cộng vào số ô sửa.', '',
              'Tổng missing cuối có thể tăng vì thêm vintage_year, price_original và log_price; '
              'đây không phải dữ liệu gốc trở nên kém đầy đủ. Xem missing_by_column.csv để phân biệt cột gốc/cột mới.', '',
              markdown_table(missing), '',
              '**Quyết định:** giữ giá thiếu để audit; chỉ dùng dòng có giá cho thí nghiệm hiện tại. '
              'Giữ giá cao hợp lệ; hai hiệu chỉnh giá là giả định có lưu vết, không phải giá thị trường đã xác minh. '
              '`is_non_informative_review` là tên cột lịch sử cho cờ độ dài dưới 10 từ, không chứng minh review vô ích.', '',
              '**Phạm vi:** audit cleaning lịch sử trên toàn bộ dữ liệu; phân tích chi tiết hiện hành dùng train. '
              'Không coi số lượng cờ là số lỗi chắc chắn.', '',
              '**Tái lập:** `python -m src.cleaning_report`. Các hành động chi tiết, checksum và phiên bản nằm trong '
              '`summary.json`; bảng gốc là `stages.csv`.', '']
    (out / 'REPORT.md').write_text('\n'.join(report), encoding='utf-8')


def run(output_dir=ROOT / 'outputs/cleaning_report'):
    raw_path = ROOT / 'data/raw/winemag-data-130k-v2.csv'
    cleaned_path = ROOT / 'data/processed/wine_cleaned_final.csv'
    frame, stages, actions = replay(pd.read_csv(raw_path))
    stored = pd.read_csv(cleaned_path)
    pd.testing.assert_frame_equal(frame.reset_index(drop=True), stored, check_dtype=False,
                                  check_exact=False, rtol=1e-12, atol=1e-12)
    write_report(stages, actions, raw_path, cleaned_path, output_dir)
    print(stages.to_string(index=False))
    return stages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', default=str(ROOT / 'outputs/cleaning_report'))
    args = parser.parse_args()
    run(args.output_dir)


if __name__ == '__main__':
    main()
