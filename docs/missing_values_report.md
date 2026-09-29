# Báo cáo xử lý missing values — Dương

## Phạm vi

- Nguồn: `data/raw/winemag-data-130k-v2.csv`.
- Đầu ra: `data/interim/01_missing_handled.csv`.
- Code tái lập: `src/handle_missing_values.py`.
- Chỉ xử lý 9 cột có giá trị thiếu. Không xóa dòng, không xử lý duplicate,
  khoảng trắng, kiểu dữ liệu hoặc outlier.

## Nguyên tắc xử lý

1. Giữ nguyên 129.971 dòng và thứ tự 14 cột.
2. Chỉ suy luận giá trị phân loại khi dữ liệu quan sát cho thấy ánh xạ một-một.
3. Với trường tùy chọn không thể suy luận, dùng nhãn rõ nghĩa thay vì xóa dòng.
4. Điền `price` bằng trung vị phân cấp và chỉ dùng nhóm có ít nhất 5 giá hợp lệ.
   Không dùng `points` trong phép điền để tránh rò rỉ biến mục tiêu tiềm năng.
5. Phân biệt `Not applicable` và `Unknown` ở `region_2`.

## Kết quả

| Cột | Missing trước | Cách xử lý | Missing sau |
|---|---:|---|---:|
| `country` | 63 | 32 từ ánh xạ duy nhất theo `winery`; 31 `Unknown` | 0 |
| `designation` | 37.465 | `Not specified` | 0 |
| `price` | 8.996 | Trung vị `country+variety` 8.892; `variety` 47; `country` 57 | 0 |
| `province` | 63 | 12 từ ánh xạ duy nhất theo `winery`; 51 `Unknown` | 0 |
| `region_1` | 21.247 | `Unknown` | 0 |
| `region_2` | 79.460 | 75.436 `Not applicable`; 4.024 `Unknown` | 0 |
| `taster_name` | 26.244 | `Unknown` | 0 |
| `taster_twitter_handle` | 31.213 | `Not provided` | 0 |
| `variety` | 1 | `Petite Sirah` từ mô tả có cụm “Petite Syrah” | 0 |

## Kiểm tra sau xử lý

- Kích thước vẫn là **129.971 dòng × 14 cột**.
- Tổng missing trong 9 cột được giao là **0**.
- Không có cột nào ngoài 9 cột được giao bị thay đổi.
- Các giá trị `price` đã có sẵn, gồm giá trị cao nhất 3.300 USD, được giữ nguyên để
  nhóm phụ trách outlier đánh giá riêng.

## Chạy lại

```powershell
python src/handle_missing_values.py
```

Có thể dùng `--input` và `--output` để áp dụng cùng logic lên file trung gian sau
khi nhóm hợp nhất các bước cleaning.
