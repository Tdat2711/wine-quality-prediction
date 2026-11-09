# Báo cáo chọn mẫu và chia train/validation/test

Notebook: [02_data_split.ipynb](../notebooks/02_data_split.ipynb). Module dùng chung: [split_data.py](../src/split_data.py).

## 1. Chọn mẫu

Đầu vào `data/processed/wine_cleaned_final.csv`, không làm sạch lần nữa ở bước split. Một dòng là một review.

| Nhóm | Số bản ghi |
|---|---:|
| Cleaned data | 119.988 |
| Có points | 119.988 |
| Có giá quan sát, đủ điều kiện split | 111.593 |
| Thiếu giá, giữ trong cleaned data để audit | 8.395 |

Chọn bằng `dropna(subset=['price', 'points'])`; không loại vì thiếu niên vụ, không điền giá. Review train không có chuỗi trống; module giữ nguyên mẫu đã khóa, không thêm bộ lọc văn bản làm thay đổi phân bố bản ghi.

SHA-256 cleaned data sau chuẩn hóa CRLF thành LF: `e2a8a1d3c2e3ce127beea391a44b1c7dc42dc1fec0d12df0f2415314e60e35a6`.

## 2. Quy tắc và kết quả split

- Giữ nguyên hàm chuẩn hóa title đã dùng: chữ thường, trim, gộp khoảng trắng, bỏ ký tự theo biểu thức chính quy trong module.
- Hai bước GroupShuffleSplit: 70% nhóm cho train; phần còn lại chia đôi cho validation/test. Seed **42** ở cả hai bước.
- `log_price = log1p(price)` là biến đổi cố định, không fit preprocessing trong split.
- Lệnh mặc định tái tạo trong bộ nhớ và đối chiếu cả thứ tự bản ghi với file hiện có; `--write` chỉ tạo file chưa có, không ghi đè split đang tồn tại.

| File | Số dòng | Số nhóm title_clean | Thiếu price | Thiếu points |
|---|---:|---:|---:|---:|
| train.csv | 78.106 | 77.437 | 0 | 0 |
| val.csv | 16.745 | 16.594 | 0 | 0 |
| test.csv | 16.742 | 16.594 | 0 | 0 |

Giao nhóm title của cả ba cặp bằng 0. Tổng 111.593 dòng, mỗi dòng đủ điều kiện xuất hiện đúng một lần. Các cột audit và hai hiệu chỉnh giá vẫn được giữ.

## 3. Audit review trùng giữa các tập

Chuyển chữ thường, trim và gộp khoảng trắng; bỏ chuỗi rỗng khỏi phép giao. Không dùng nhãn holdout để điều chỉnh phương pháp.

| Cặp tập | Số chuỗi review phân biệt dùng chung |
|---|---:|
| train–validation | 6 |
| train–test | 5 |
| validation–test | 1 |

Đây là số chuỗi theo từng cặp, không phải số dòng bị trùng hay tổng số chuỗi duy nhất trên toàn bộ split. Không kiểm tra tương đồng ngữ nghĩa hoặc review gần trùng. Kết quả không thay đổi split. Luồng mô hình kết hợp giữ mọi dòng, báo metric validation tổng thể và riêng tập không trùng review train (loại 6 dòng khỏi phép tính phụ, không sửa file split). Không dùng kết quả phụ để tuning. Test có 5 dòng trùng review train; hiện chưa tính metric test. CV trên train nối nhóm cùng title hoặc cùng review không rỗng để tránh chúng qua ranh giới fold.

Bảng tái tạo: [review_overlap.csv](../outputs/eda/tables/review_overlap.csv).

## 4. Chạy lại

Từ project root, dùng môi trường theo README:

```powershell
python src/split_data.py
python -m unittest discover -s tests -p test_split.py -v
```

Notebook mới chạy cùng module, kiểm tra số dòng, nhóm, giá/nhãn thiếu và trùng review. Không fit encoder/imputer/scaler/TF-IDF, không tính metric test.

## 5. Lịch sử và giới hạn

Split seed 42 được chốt ngày **21/10/2026**. EDA trước đây đã xem toàn mẫu có giá và holdout 42 từng được thử; không khẳng định test hoàn toàn chưa được quan sát. Giữ lịch sử này khi diễn giải; không đổi seed để chọn kết quả thuận lợi và không tuning theo test.

Mẫu có giá có thể khác nhóm thiếu giá. Không suy ra phân phối các tập giống nhau chỉ từ tỷ lệ chia. Cách nhóm theo title hạn chế chồng tên rượu nhưng chưa ngăn mọi trùng lặp văn bản.
