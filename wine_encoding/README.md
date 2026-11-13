# Metadata + review → Ridge

Module dùng split đã khóa của repo. Model mặc định là `combined`; ba profile `product`, `review`, `all_attributes_audit` được giữ để đối chiếu encoding và không phải mô hình chính.

## Chạy từ repository root

Dùng môi trường hiện có, hoặc cài dependency gốc bằng `python -m pip install -r requirements.txt`.

```powershell
python src/split_data.py
python -m wine_encoding.src.prepare
python -m wine_encoding.src.verify
python -m wine_encoding.src.train
python -m wine_encoding.src.verify_model
python -m wine_encoding.src.preview
python -m wine_encoding.src.transform --input wine_encoding/examples/new_wines.csv
python -m wine_encoding.src.predict --input wine_encoding/examples/new_wines.csv
python -m unittest discover -s tests -v
```

`prepare --config <file>` nhận config JSON; `source`, `split_dir`, `output` tính từ thư mục config. Mọi đường dẫn CLI tính từ thư mục chạy. Sai đường dẫn báo lỗi, không tự tìm dataset khác. Các lệnh `verify`, `train`, `verify_model` hỗ trợ `--data-dir`; train hỗ trợ `--output`, verify_model hỗ trợ `--model-dir`.

## Mẫu và split bất biến

Nguồn mặc định: `data/processed/wine_cleaned_final.csv`, 119.988 dòng. Mẫu có giá quan sát và points: 111.593 dòng; 8.395 dòng thiếu giá vẫn giữ trong nguồn để audit. Chỉ mã hóa mẫu trong split đã khóa: train 78.106, validation 16.745, test 16.742.

Prepare tái tạo split bằng module chung rồi so sánh cả nội dung và thứ tự với `data/processed/splits/{train,val,test}.csv`. Thiếu hoặc lệch split thì dừng trước khi xuất. Không tự chia lại hay ghi split. `source_row_id` là vị trí 0-based trong CSV nguồn; tên `val` được xuất thành `validation`. Manifest chỉ chứa các dòng đủ điều kiện. Báo cáo phân biệt tổng nguồn, eligible và excluded, lưu đường dẫn tuyệt đối cùng checksum nguồn/split. Di chuyển nguồn cần prepare/train lại.

Test chỉ transform bằng encoder fit trên train; không tính metric hay thống kê nhãn test trong prepare/train. Train chỉ đọc CSV train/val; kiểm tra toàn vẹn các nguồn bằng checksum không dùng nhãn test để chọn cấu hình.

## Đầu vào và pipeline chính

CSV dự đoán cần đúng sáu cột (có thể có thêm cột không dùng):

| Cột | Xử lý |
|---|---|
| `price` | `log1p`, điền trung vị train, StandardScaler |
| `vintage_year` | Điền trung vị train, StandardScaler |
| `country`, `province`, `variety` | Nhãn thiếu, one-hot; min_frequency=20, max_categories=256 |
| `description` | TF-IDF unigram/bigram, min_df=2, tối đa 3.000 feature, sublinear TF |

Numeric thiếu được chấp nhận khi dự đoán; chữ sai kiểu, số vô hạn và giá không dương bị từ chối. Category mới được gom vào nhóm hiếm nếu có, nếu không thành khối 0. Review thiếu/trống thành vector văn bản 0. Giữ stopword và từ phủ định; từ lạ bị bỏ qua. Tập fit cần có từ xuất hiện ít nhất hai dòng; nếu vocabulary rỗng thì báo lỗi, không train mô hình văn bản giả.

Không cần points, title, người chấm hay cột audit. Không dùng title, winery, designation, region_1/2, taster hoặc cờ audit làm predictor chính. Log giá được tính từ price trong pipeline, không tin cột log_price truyền vào. Không dùng đồng thời giá gốc và log giá.

## CV và đánh giá validation

- 5 fold trên train, nhóm là thành phần liên thông của title chuẩn hóa hoặc review chuẩn hóa không rỗng; chuỗi rỗng không nối nhóm.
- Fit encoder riêng trong từng fold; dùng lại encoder giữa các alpha chỉ bên trong cùng fold.
- Lưới alpha mặc định `[0.1, 1, 10, 100, 1000]`; chọn MAE CV trung bình thấp nhất, hòa thì RMSE, rồi alpha nhỏ hơn.
- Ridge LSQR, tol=1e-8, max_iter=10000; từ chối nếu chạm giới hạn lặp.
- Pipeline cuối chỉ fit train, chưa refit train+validation. Baseline là trung bình train. Validation không chọn lại alpha.
- Báo MAE/RMSE/R² tổng thể và riêng các dòng không trùng review train. Hiện có 6 dòng validation trùng review train; giữ nguyên chúng trong file split và báo cờ từng dòng.

Chuẩn hóa review để audit: chữ thường, trim, gộp khoảng trắng, bỏ chuỗi rỗng. Không phát hiện near-duplicate/semantic duplicate. Giữ lịch sử seed-42 holdout từng được quan sát; không tuyên bố test mới hoàn toàn hoặc zero leakage.

## Artifact và tương thích

```text
outputs/
  report.json, encoder.joblib, split_manifest.csv, column_coverage.csv
  row_ids_{train,validation,test}.npy, y_{train,validation,test}.npy
  combined/, product/, review/, all_attributes_audit/
    features.csv, sample_5_rows.csv, X_{train,validation,test}.npz
  model_combined/
    ridge_combined.joblib          # Pipeline raw inputs → preprocessing → Ridge
    summary.json, RESULTS.md
    cv_metrics.csv, cv_summary.csv, cv_manifest.csv
    metrics.csv, validation_predictions.csv, errors_by_group.csv
    largest_errors.csv, ridge_coefficients.csv, validation_diagnostics.png
    new_predictions.csv
```

Ma trận CSR; không densify toàn bộ dữ liệu. Bộ combined độc lập với encoder của các trường audit; train CV trực tiếp trên dữ liệu chưa mã hóa. Ba bộ cũ vẫn chuẩn hóa/one-hot/TF-IDF 19 cột theo thiết kế ban đầu, points tách thành y; chỉ dùng chúng trong thử nghiệm có kiểm soát.

Artifact schema version 2. Encoder/model cũ cần tái tạo; model product không tự động thay thế combined. Chuẩn bị lại encoding yêu cầu train lại model; verify so checksum nguồn/split để phát hiện thay đổi. Chỉ load joblib do bạn tạo và tin cậy. Các lệnh tái sinh ghi đè artifact cùng tên, không sửa dữ liệu nguồn/split.

Predict giữ nguyên thứ tự dòng, thêm `points_predicted` và `prediction_outside_train_target_range`. Không ép dự đoán trong 80–100, không làm tròn/cắt điểm khi đánh giá.

## Đánh giá test tách riêng — đã chạy ngày 13/11/2026

Đã chạy bằng mô hình khóa alpha = 1: MAE **1,208998**, RMSE **1,542601**, R² **0,751284** trên 16.742 dòng test. Xem [báo cáo test](../docs/model_test_report.md). Lệnh đã dùng (không chạy lại vào thư mục đã có):

```powershell
python -m wine_encoding.src.evaluate_test
```

Lệnh chỉ load model và đánh giá, không fit/tuning; xuất vào `model_combined/test_evaluation/` và từ chối ghi đè thư mục đã có. Báo tổng thể và tập không trùng review train. Không sửa mô hình theo kết quả test.

## Giới hạn

Mô hình cần review đã tồn tại và ước lượng điểm của người đánh giá, không đo chất lượng khách quan trước review. Chưa có đối chứng để kết luận phần cải thiện riêng do review. Hệ số không thể hiện nhân quả; cần xem số mẫu khi đọc sai số theo nhóm. Chưa thực hiện kiểm định thống kê chính thức.
