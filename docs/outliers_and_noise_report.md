# Báo cáo Outlier & Noise — Wine Reviews 130k

**Phạm vi**: Bước 4 của pipeline cleaning, chạy sau missing values, consistency và exact duplicates.

**Đầu vào**: `data/interim/03_duplicates_handled.csv` — 119.988 dòng × 13 cột.

**Đầu ra chính thức**: `data/processed/wine_cleaned_final.csv` — 119.988 dòng × 19 cột.

**Code**: `src/handle_outliers_and_noise.py`

**Notebook**: `notebooks/01_outliers_and_noise.ipynb`

## 1. Mục tiêu

- Phân biệt outlier tự nhiên với dấu hiệu nhập liệu sai.
- Không tự động xóa rượu giá cao hoặc rượu đạt điểm cực trị.
- Làm sạch nhiễu văn bản có quy tắc rõ ràng.
- Tạo các biến phục vụ phân tích, đồng thời giữ khả năng truy vết mọi hiệu chỉnh.

## 2. Đánh giá giá trị `price`

Sau ba bước cleaning trước, **8.395 dòng vẫn thiếu `price`**. Các thống kê giá dưới đây chỉ tính trên 111.593 dòng có giá quan sát:

| Chỉ số | Giá trị |
|---|---:|
| Dòng có giá hợp lệ | 111.593 |
| Dòng thiếu giá được giữ | 8.395 |
| Q1 / Median / Q3 | 17 / 25 / 42 USD |
| IQR | 25 USD |
| Ngưỡng IQR 1,5 | 79,5 USD |
| Giá trị vượt ngưỡng IQR | 6.869 |
| Giá trị vượt ngưỡng IQR 3,0 | 2.574 |
| Giá trên 500 USD | 91 |
| Giá trên 1.000 USD | 14 |
| Giá lớn nhất sau xử lý | 2.500 USD |

IQR chỉ được dùng để phát hiện. Các mức giá cao có thể phản ánh phân khúc rượu xa xỉ hợp lệ nên pipeline giữ lại toàn bộ 6.869 giá trị vượt ngưỡng.

## 3. Hai giá trị được hiệu chỉnh có lưu vết

| Sản phẩm | Giá gốc | Giá sau hiệu chỉnh |
|---|---:|---:|
| Blair 2013 Roger Rose Vineyard Chardonnay | 2.013 USD | 35 USD |
| Château les Ormes Sorbet 2013 Médoc | 3.300 USD | 33 USD |

Hai trường hợp có dấu hiệu mạnh của lỗi nhập liệu. Giá sau hiệu chỉnh là giả định có căn cứ, chưa phải giá thị trường được xác minh tuyệt đối. Pipeline giữ giá cũ trong `price_original`, đánh dấu bằng `price_was_corrected` và phân biệt các dòng thiếu giá bằng `price_was_missing`.

## 4. `points` và outlier đa biến

- `points` vẫn nằm trong khoảng 80–100.
- Giữ đủ 19 bản ghi đạt 100 điểm và 397 bản ghi đạt 80 điểm.
- Có 7 trường hợp giá từ 100 USD nhưng điểm không quá 83; các dòng này được giữ vì chưa có bằng chứng là lỗi.
- Có 2 trường hợp giá quan sát không quá 15 USD nhưng đạt ít nhất 94 điểm; đây chỉ là trường hợp đáng xem xét thêm, không phải lỗi kỹ thuật hoặc bằng chứng chắc chắn rằng sản phẩm "đáng tiền".

## 5. Xử lý noise và transformation

- Giải mã HTML entities, thay non-breaking space và loại khoảng trắng đầu/cuối trong `description` và `title`.
- Gắn cờ 39 review dưới 10 từ bằng `is_non_informative_review`; không xóa dòng vì metadata vẫn có thể hữu ích.
- Trích xuất 115.660 giá trị `vintage_year`; tiêu đề NV/Non-Vintage và năm không đủ tin cậy được để thiếu.
- Tạo `log_price = log1p(price)` cho giá quan sát; giá thiếu vẫn thiếu. Skewness trên các giá quan sát giảm từ khoảng 17,96 xuống 0,66 mà không xóa rượu cao cấp.

## 6. Bằng chứng validation

- Dataset cuối: 119.988 dòng × 19 cột.
- Các cột gốc ngoài `price` không còn missing; `price` giữ 8.395 missing.
- Duplicate hoàn toàn: 0.
- Hai hiệu chỉnh giá có đầy đủ giá gốc và cờ truy vết.
- Giá cao nhất hợp lệ 2.500 USD và 19 rượu đạt 100 điểm vẫn được giữ.
- SHA-256 của raw vẫn là `52af2643c8ac29f010f0cc629dfbdda1c74aa0f332d11762af9ef3de4e567ac9`.

## 7. Hạn chế

- Hai giá hiệu chỉnh vẫn là giả định có lưu vết.
- Ngưỡng review dưới 10 từ chỉ là quy tắc gắn cờ, chưa chứng minh mọi review ngắn đều vô ích.
- `vintage_year` thiếu là hợp lệ khi tiêu đề không chứa niên vụ đáng tin cậy.
- Các thao tác encoding, scaling và feature selection cho mô hình không thuộc phạm vi cleaning này.
