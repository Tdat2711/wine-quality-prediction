# Báo cáo chọn mẫu và chia train/validation/test

**Phần việc:** Nguyễn Khắc Tuấn Đạt — chọn mẫu và chia dữ liệu theo nhóm tên chai.

Notebook chạy lại: [02_dat_data_split.ipynb](../notebooks/w5_progress_parts/02_dat_data_split.ipynb).
Đầu vào là `data/processed/wine_cleaned_final.csv` từ pipeline chung; bước này không chạy lại cleaning.

## 1. Chọn mẫu

| Nhóm dữ liệu | Số dòng |
|---|---:|
| Toàn bộ cleaned data | 119.988 |
| Có nhãn mục tiêu `points` | 119.988 |
| Có giá quan sát `price` | 111.593 |
| Thiếu giá, giữ lại để audit | 8.395 |
| Đủ cả giá và điểm để chia tập | 111.593 |

Thống kê và biểu đồ có/thiếu giá dùng toàn bộ cleaned data. Chỉ sau bước thống kê mới chọn mẫu bằng `dropna(subset=['price', 'points'])`. Không điền giá thiếu và không sửa file cleaned gốc. Các trường metadata, kể cả `vintage_year`, được giữ nguyên; năm thiếu không làm dòng bị loại ở bước này.

SHA-256 của cleaned data sau chuẩn hóa xuống dòng CRLF thành LF:

```text
e2a8a1d3c2e3ce127beea391a44b1c7dc42dc1fec0d12df0f2415314e60e35a6
```

## 2. Cách chia và đầu ra

- Chuẩn hóa `title` bằng chữ thường, bỏ khoảng trắng đầu/cuối, gộp khoảng trắng và bỏ dấu câu theo hàm `normalize_title` trong notebook.
- Dùng hai bước `GroupShuffleSplit`: khoảng 70% nhóm cho train, rồi chia phần còn lại thành validation/test với tỷ lệ nhóm 50/50.
- Khánh chốt seed **42 ngày 21/10/2026** ở cả hai bước cho bộ split hiện tại. Tỷ lệ theo số dòng có thể lệch nhẹ vì mỗi nhóm tên chai có số dòng khác nhau.
- `log_price = log1p(price)` là phép biến đổi cố định; không fit encoder, imputer, scaler hoặc mô hình ở bước này.

| File trong `data/processed/splits/` | Số dòng | Số nhóm `title_clean` | Thiếu giá | Thiếu điểm |
|---|---:|---:|---:|---:|
| `train.csv` | 78.106 | 77.437 | 0 | 0 |
| `val.csv` | 16.745 | 16.594 | 0 | 0 |
| `test.csv` | 16.742 | 16.594 | 0 | 0 |

Cả ba giao nhóm train–validation, train–test và validation–test đều bằng **0**. Tổng các tập là **111.593 dòng**; mọi dòng đủ điều kiện được giữ đúng một lần. Hai hiệu chỉnh giá 33 USD và 35 USD cùng các cột audit được bảo toàn.

## 3. Chạy lại và kiểm tra

Chọn kernel Python của `.venv`, rồi Restart Kernel và Run All. Notebook hỗ trợ chạy từ project root, `notebooks/` hoặc `notebooks/w5_progress_parts/`; các CSV được xuất về cùng thư mục trong project.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_split.py -v
```

Notebook đã chạy thành công từ kernel mới, ba cell code theo thứ tự 1–2–3. Bốn kiểm thử split kiểm tra không thiếu giá/điểm, bảo toàn toàn bộ bản ghi đủ điều kiện, không chồng nhóm và tính đúng `log_price`. Cả bốn đều đạt. Raw data và cleaned data không thay đổi.

## 4. Giới hạn và trạng thái

Mẫu có giá chỉ chiếm khoảng 93% cleaned data, có thể không đại diện toàn bộ dữ liệu. Không suy ra các phân phối giống nhau chỉ từ tỷ lệ chia hoặc số mẫu. Không tính thống kê phân phối điểm của test, chạy metric mô hình hay chọn cấu hình theo test trong lần sửa này.

**Quyết định ngày 21/10/2026:** Khánh giữ seed **42**, chốt bộ split có giá. Phần chọn mẫu/split của Đạt đã hoàn thành; Spearman và mô hình chưa thực hiện, dành cho buổi sau.

**Lịch sử và giới hạn:** EDA đã xem toàn mẫu có giá và dự án có ghi nhận holdout seed 42 từng được thử. Giữ seed 42 không xác nhận test hoàn toàn chưa từng được quan sát. Giữ lịch sử này khi diễn giải kết quả; không đổi seed để chọn kết quả thuận lợi và không tuning theo test.
