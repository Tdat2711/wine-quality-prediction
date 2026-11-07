# Số hóa dữ liệu rượu để chuẩn bị mô hình

Project có tiền xử lý đủ 19 cột và huấn luyện **baseline + Ridge** dự đoán `points`.
Kết quả hiện tại là kết quả validation; chưa đánh giá mô hình trên test.
Tệp nguồn `../wine_cleaned_final.csv` được đọc nguyên trạng, không bị ghi đè.

## Chạy

Mở PowerShell tại thư mục project:

```powershell
python -m pip install -r requirements.txt
python -m src.prepare --config config.json
python -m src.verify
```

Đường dẫn input/output trong config được tính từ vị trí `config.json`.
Lần chạy lại sẽ thay thế các đầu ra cùng tên trong `outputs/`.

## Đủ 19 thuộc tính được xử lý như thế nào?

| Cột | Chuyển đổi | Bộ đầu vào |
|---|---|---|
| country | One-hot, gom nhóm hiếm | product, review, all |
| designation | One-hot, gom nhóm hiếm | product, review, all |
| province | One-hot, gom nhóm hiếm | product, review, all |
| region_1 | One-hot, gom nhóm hiếm | product, review, all |
| region_2 | One-hot, giữ nhãn Unknown/Not applicable riêng nếu đủ tần suất | product, review, all |
| variety | One-hot, gom nhóm hiếm | product, review, all |
| winery | One-hot, gom nhóm hiếm | product, review, all |
| price | Điền trung vị train + StandardScaler; thêm cờ thiếu | product, review, all |
| vintage_year | Điền trung vị train + StandardScaler; thêm cờ thiếu | product, review, all |
| description | TF-IDF unigram/bigram, tối đa 3.000 đặc trưng | review, all |
| taster_name | One-hot, gom nhóm hiếm | review, all |
| is_non_informative_review | False/True thành 0/1 | review, all |
| title | TF-IDF tối đa 1.000 đặc trưng; đồng thời dùng chia nhóm | all |
| taster_twitter_handle | One-hot, gom nhóm hiếm | all |
| price_original | Điền trung vị train + StandardScaler; thêm cờ thiếu | all |
| log_price | Điền trung vị train + StandardScaler; thêm cờ thiếu | all |
| price_was_missing | False/True thành 0/1 | all |
| price_was_corrected | False/True thành 0/1 | all |
| points | Số float32, lưu riêng thành y | Đáp án, không bao giờ vào X |

`all` là thư mục `all_attributes_audit`. Không xóa cột nào khỏi nguồn.
19 cột nguồn được biểu diễn bằng 18 cột đầu vào đã mở rộng + đáp án y.
Không mã hóa chữ tùy ý thành 1, 2, 3. Các nhóm dưới 20 mẫu train được gom hiếm;
mỗi thuộc tính phân loại có tối đa 256 cột. Cấu hình có thể thay đổi.
Không bảo toàn riêng từng tên hiếm hoặc từng từ: đó là giảm chiều có chủ đích.
Category lạ được đưa vào nhóm hiếm nếu encoder đã có nhóm đó, nếu không thì thành
toàn 0 trong khối của thuộc tính. Từ chưa gặp bị TF-IDF bỏ qua.

## Chọn bộ nào để làm mô hình?

- **product**: dùng thông tin sản phẩm để dự đoán điểm trước khi có review.
  Giả định có thông tin giá/niên vụ hoặc giá trị thiếu và các danh mục sản phẩm.
- **review**: thêm description, người chấm và cờ chất lượng review. Đây là bài toán
  ước lượng điểm từ review đã có, có giả định biết người chấm; không so sánh như thể
  nó giải quyết đúng cùng tình huống với product.
- **all_attributes_audit**: số hóa toàn bộ để đối chiếu hoặc thử nghiệm có kiểm soát.
  **Không lấy nguyên bộ này làm mô hình mặc định**: có cột audit, thông tin lặp về giá,
  tên rượu, danh tính người chấm và văn bản review. Chúng có thể không tồn tại khi sử dụng.
  Các cột nguồn xử lý giá không tự động là rò rỉ đích points, nhưng cần xét tính khả dụng.

## Chia dữ liệu và chống rò rỉ

Giữ toàn bộ dòng có points, kể cả 8.395 dòng thiếu giá: giá là đầu vào, không phải đáp án.
Chia theo nhóm title đã chuẩn hóa Unicode, hoa/thường và khoảng trắng, seed 42.
Tỷ lệ khoảng 70/15/15 theo nhóm; tỷ lệ số dòng có thể khác một chút.
Không có cùng title chuẩn hóa ở nhiều tập. Cách này không bảo đảm nhận diện cùng
một rượu nếu tên khác nhau, và không bảo đảm tách theo winery.

Trong thư mục ban đầu không có các split cũ, nên project tạo split mới, không tuyên bố
tái tạo các số 78.106/16.745/16.742 trong ảnh. Nếu đã có split được duyệt, cần dùng
lại đúng row ID/split đó thay vì so kết quả giữa hai cách chia.

Trung vị, scaler, nhóm hiếm, vocabulary và IDF chỉ fit trên train.
Validation/test chỉ transform. `points` được tách trước khi fit encoder.
Chưa sửa lại các quyết định làm sạch trong CSV nguồn; không thể loại bỏ rò rỉ có thể
đã phát sinh trong lịch sử làm sạch khi chưa có code/dữ liệu trước đó.

Khi tuning bằng cross-validation, cần fit lại tiền xử lý trong từng fold từ dữ liệu
chưa mã hóa, không dùng nguyên X_train đã mã hóa bằng toàn train cho CV. Các file
hiện tại phù hợp luồng train -> chọn trên validation -> đánh giá test cuối cùng.
Không xem test để chọn đặc trưng hoặc tham số.

## Đầu ra

```text
outputs/
  encoder.joblib             # encoder đã fit trên train và chỉ số cột từng bộ
  report.json                # số dòng, feature, missing, seed, hash nguồn
  column_coverage.csv        # chứng minh đủ 19 cột có vai trò
  split_manifest.csv         # source_row_id (0-based), title_group, split
  y_train.npy / y_validation.npy / y_test.npy
  row_ids_train.npy / row_ids_validation.npy / row_ids_test.npy
  product/                  # bộ thông tin sản phẩm
  review/                   # bộ có review
  all_attributes_audit/     # bản đầy đủ để đối chiếu
    X_train.npz / X_validation.npz / X_test.npz
    features.csv            # thứ tự cột tương ứng ma trận X
    sample_5_rows.csv        # 5 dòng đầu train, đọc để minh họa
```

`X` là ma trận thưa CSR float32: mọi giá trị đều là số, không có NaN/inf sau xử lý.
Không xuất toàn bộ thành CSV đặc vì TF-IDF/one-hot có hàng nghìn cột và phần lớn là 0.
`source_row_id` không phải feature. X, y và row_ids cùng split có cùng thứ tự hàng.

```python
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

X_train = load_npz('outputs/product/X_train.npz')
y_train = np.load('outputs/y_train.npy')
features = pd.read_csv('outputs/product/features.csv')
print(X_train.shape, y_train.shape)
# Truyền X_train, y_train vào mô hình ở bước tiếp theo.
# Các mô hình cần dense phải xử lý cẩn thận bộ nhớ; không toarray toàn bộ review.
```

## Mã hóa dữ liệu mới

```powershell
python -m src.transform --input du_lieu_moi.csv --profile product --output outputs/new_product.npz
```

Chạy thử bằng hai dòng minh họa (không phải dữ liệu kiểm định độc lập):

```powershell
python -m src.transform --input examples/new_wines.csv --profile product --output outputs/example_new_product.npz
```

Product chỉ cần đủ 9 cột sản phẩm trong bảng, không cần points, review hay cột audit.
Review cần thêm description, taster_name, is_non_informative_review.
Chấp nhận ô thiếu numeric, nhưng không chấp nhận giá trị chữ sai kiểu hay cờ không hợp lệ.
Output giữ nguyên thứ tự dòng input và dùng đúng số/thứ tự feature đã học.
Lệnh này không tính điểm: muốn có điểm còn cần mô hình dự đoán đã huấn luyện.
Chỉ load joblib do bạn tạo và tin cậy.

## Huấn luyện baseline và Ridge

```powershell
python -m src.train
python -m src.verify_model
```

Lệnh train dùng bộ `product` gồm 996 feature (từ 9 cột sản phẩm và cờ thiếu),
không dùng nội dung review, người chấm hay target làm feature. Baseline luôn dự đoán
trung bình points của train. Ridge dùng solver LSQR, tol=1e-8, max_iter=10000.
Chọn alpha trong [0.1, 1, 10, 100, 1000] bằng MAE validation thấp nhất;
nếu bằng nhau dùng RMSE. Không mở ma trận test trong lệnh train.
Mô hình được lưu vẫn chỉ fit trên train, chưa fit lại bằng train+validation.

Đầu ra trong `outputs/model_product/`:

- `RESULTS.md`, `summary.json`: kết quả và giới hạn.
- `metrics.csv`: MAE/RMSE/R² trên train và validation của tất cả cấu hình.
- `validation_predictions.csv`: điểm thật, điểm dự đoán và sai số từng dòng.
- `errors_by_group.csv`, `largest_errors.csv`: kiểm tra nhóm dự đoán kém.
- `ridge_coefficients.csv`: hệ số; không diễn giải như tác động nhân quả.
- `validation_diagnostics.png`: điểm thật–dự đoán, phần dư và phân phối phần dư.
- `ridge_product.joblib`: mô hình kèm encoder để dự đoán dữ liệu mới.

Không cắt điểm hay làm tròn dự đoán trước khi đánh giá. Đây là hồi quy tuyến tính,
có thể trả về điểm ngoài khoảng quan sát; sai số và R² không phải phần trăm accuracy.

## Dự đoán từ CSV mới

```powershell
python -m src.predict --input examples/new_wines.csv
```

CSV cần 9 cột sản phẩm, không cần points. Kết quả mặc định:
`outputs/model_product/new_predictions.csv`, thêm `points_predicted` và cờ
`prediction_outside_train_target_range`. Hai dòng example chỉ minh họa cách gọi,
không có nhãn thật nên không dùng để đánh giá độ chính xác.
Không điền số dự đoán vào points thực tế.

Các lệnh đọc CSV bỏ khoảng trắng ở đầu/cuối tên cột, không sửa tệp nguồn.
Train kiểm tra hash nguồn; chỉ chấp nhận khác biệt khoảng trắng trước tên cột đầu
nếu loại đúng khoảng trắng đó khôi phục hash cũ, chứng minh phần dữ liệu không đổi.
Thay đổi khác phải số hóa lại trước khi train.
