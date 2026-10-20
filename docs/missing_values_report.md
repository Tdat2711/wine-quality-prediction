# Báo cáo xử lý missing values — phiên bản thí nghiệm hai tầng

## Phạm vi

- Nguồn: `data/raw/winemag-data-130k-v2.csv`.
- Đầu ra: `data/interim/01_missing_handled.csv`.
- Code tái lập: `src/handle_missing_values.py`.
- Chỉ xử lý 9 cột có giá trị thiếu. Không xóa dòng, không xử lý duplicate,
  khoảng trắng, kiểu dữ liệu hoặc outlier.

## Nguyên tắc xử lý

1. Giữ nguyên 129.971 dòng và thứ tự 14 cột.
2. Không học ánh xạ giữa các dòng trước khi chia train/validation/test; trường thiếu được gắn nhãn rõ nghĩa.
3. Giữ nguyên `price` thiếu. Thí nghiệm chính dùng cùng mẫu có giá quan sát ở cả bốn cấu hình; không biến giá ước tính thành giá thật.
4. Các phép suy luận từ một dòng riêng lẻ có bằng chứng trực tiếp (một `variety` từ `description`) vẫn được lưu dấu.
5. Phân biệt `Not applicable` và `Unknown` ở `region_2`.

## Kết quả

| Cột | Missing trước | Cách xử lý | Missing sau |
|---|---:|---|---:|
| `country` | 63 | 63 `Unknown`; không dùng ánh xạ winery từ toàn bộ dữ liệu | 0 |
| `designation` | 37.465 | `Not specified` | 0 |
| `price` | 8.996 | Giữ thiếu để audit; lọc khỏi thí nghiệm chính sau duplicate removal | 8.996 |
| `province` | 63 | 63 `Unknown`; không dùng ánh xạ winery từ toàn bộ dữ liệu | 0 |
| `region_1` | 21.247 | `Unknown` | 0 |
| `region_2` | 79.460 | 75.404 `Not applicable`; 4.056 `Unknown` | 0 |
| `taster_name` | 26.244 | `Unknown` | 0 |
| `taster_twitter_handle` | 31.213 | `Not provided` | 0 |
| `variety` | 1 | `Petite Sirah` từ mô tả có cụm “Petite Syrah” | 0 |

## Kiểm tra sau xử lý

- Kích thước vẫn là **129.971 dòng × 14 cột**.
- Chỉ còn **8.996 giá thiếu** ở bước này; sau loại duplicate còn **8.395** trên 119.988 dòng.
- Mẫu so sánh có giá quan sát gồm **111.593 dòng**; bốn cấu hình mô hình dùng đúng mẫu này.
- Không có cột nào ngoài 9 cột được giao bị thay đổi.
- Các giá trị `price` đã có sẵn, gồm giá trị cao nhất 3.300 USD, được giữ nguyên để
  nhóm phụ trách outlier đánh giá riêng.

## Chạy lại

```powershell
python src/handle_missing_values.py
```

Có thể dùng `--input` và `--output` để áp dụng cùng logic lên file trung gian sau
khi nhóm hợp nhất các bước cleaning.
