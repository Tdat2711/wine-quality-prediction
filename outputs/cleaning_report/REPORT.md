# Bằng chứng làm sạch trước/sau

| stage | rows | columns | missing_cells | missing_price | exact_duplicate_rows_excluding_export_index | placeholder_cells | removed_rows | changed_cells_existing_columns | added_columns | short_review_flags | price_correction_flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw | 129971 | 14 | 204752 | 8996 | 9983 | 0 | 0 | 0.0 | 0 | 0 | 0 |
| missing | 129971 | 14 | 8996 | 8996 | 9983 | 195755 | 0 | 195756.0 | 0 | 0 | 0 |
| consistency | 129971 | 14 | 8996 | 8996 | 9983 | 195755 | 0 | 42992.0 | 0 | 0 | 0 |
| duplicates | 119988 | 13 | 8395 | 8395 | 0 | 181805 | 9983 | không căn chỉnh | 0 | 0 | 0 |
| outliers_noise | 119988 | 19 | 29513 | 8395 | 0 | 181805 | 0 | 2.0 | 6 | 39 | 2 |

Các dòng được tái tạo bằng hàm cleaning thuần trong bộ nhớ và đối chiếu cleaned hiện có. Không ghi lại raw, interim hoặc cleaned. Missing thật khác placeholder. Duplicate không tính chỉ mục CSV.

`changed_cells_existing_columns` chỉ so các ô cùng vị trí khi không xóa dòng; bước duplicate báo số dòng xóa riêng. Cột mới và cờ được đếm riêng, không cộng vào số ô sửa.

Tổng missing cuối có thể tăng vì thêm vintage_year, price_original và log_price; đây không phải dữ liệu gốc trở nên kém đầy đủ. Xem missing_by_column.csv để phân biệt cột gốc/cột mới.

| scope | column | missing | rows |
| --- | --- | --- | --- |
| raw | Unnamed: 0 | 0 | 129971 |
| raw | country | 63 | 129971 |
| raw | description | 0 | 129971 |
| raw | designation | 37465 | 129971 |
| raw | points | 0 | 129971 |
| raw | price | 8996 | 129971 |
| raw | province | 63 | 129971 |
| raw | region_1 | 21247 | 129971 |
| raw | region_2 | 79460 | 129971 |
| raw | taster_name | 26244 | 129971 |
| raw | taster_twitter_handle | 31213 | 129971 |
| raw | title | 0 | 129971 |
| raw | variety | 1 | 129971 |
| raw | winery | 0 | 129971 |
| cleaned | country | 0 | 119988 |
| cleaned | description | 0 | 119988 |
| cleaned | designation | 0 | 119988 |
| cleaned | points | 0 | 119988 |
| cleaned | price | 8395 | 119988 |
| cleaned | province | 0 | 119988 |
| cleaned | region_1 | 0 | 119988 |
| cleaned | region_2 | 0 | 119988 |
| cleaned | taster_name | 0 | 119988 |
| cleaned | taster_twitter_handle | 0 | 119988 |
| cleaned | title | 0 | 119988 |
| cleaned | variety | 0 | 119988 |
| cleaned | winery | 0 | 119988 |
| cleaned | is_non_informative_review | 0 | 119988 |
| cleaned | vintage_year | 4328 | 119988 |
| cleaned | price_was_missing | 0 | 119988 |
| cleaned | price_original | 8395 | 119988 |
| cleaned | price_was_corrected | 0 | 119988 |
| cleaned | log_price | 8395 | 119988 |

**Quyết định:** giữ giá thiếu để audit; chỉ dùng dòng có giá cho thí nghiệm hiện tại. Giữ giá cao hợp lệ; hai hiệu chỉnh giá là giả định có lưu vết, không phải giá thị trường đã xác minh. `is_non_informative_review` là tên cột lịch sử cho cờ độ dài dưới 10 từ, không chứng minh review vô ích.

**Phạm vi:** audit cleaning lịch sử trên toàn bộ dữ liệu; phân tích chi tiết hiện hành dùng train. Không coi số lượng cờ là số lỗi chắc chắn.

**Tái lập:** `python -m src.cleaning_report`. Các hành động chi tiết, checksum và phiên bản nằm trong `summary.json`; bảng gốc là `stages.csv`.
