# Báo cáo audit ban đầu — Wine Reviews 130k

## Phạm vi

Báo cáo được tạo từ `data/raw/winemag-data-130k-v2.csv`. Đây là bước kiểm tra trước khi chia nhiệm vụ làm sạch; không có dữ liệu nào bị sửa hoặc xóa.

## Tổng quan

- Kích thước: **129.971 dòng × 14 cột**.
- Cột số: `Unnamed: 0`, `points`, `price`.
- Cột văn bản/phân loại: 11 cột còn lại.
- `points` nằm trong khoảng 80–100.
- `price` có 120.975 giá trị hợp lệ, trung vị 25 USD, trung bình 35,36 USD và tối đa 3.300 USD.

## Vấn đề đã xác nhận

### 1. Cột chỉ mục CSV

`Unnamed: 0` là cột đầu không có tên trong file CSV gốc. Cột có 129.971 giá trị duy nhất, liên tục từ 0 đến 129.970. Đây nhiều khả năng là chỉ mục được lưu khi xuất CSV, nhưng báo cáo chưa tự động xóa cột này.

### 2. Giá trị thiếu

| Cột | Số missing | Tỷ lệ |
|---|---:|---:|
| `region_2` | 79.460 | 61,14% |
| `designation` | 37.465 | 28,83% |
| `taster_twitter_handle` | 31.213 | 24,02% |
| `taster_name` | 26.244 | 20,19% |
| `region_1` | 21.247 | 16,35% |
| `price` | 8.996 | 6,92% |
| `country` | 63 | 0,05% |
| `province` | 63 | 0,05% |
| `variety` | 1 | dưới 0,01% |

Năm cột `Unnamed: 0`, `description`, `points`, `title`, `winery` không có missing.

### 3. Bản ghi trùng

- So sánh toàn bộ 14 cột: **0** dòng trùng, vì `Unnamed: 0` là duy nhất.
- Bỏ `Unnamed: 0` khỏi phép so sánh: **9.983** dòng được đánh dấu là bản sao xuất hiện sau.

Con số 9.983 là kết quả audit, chưa phải số dòng chắc chắn sẽ xóa. Nhóm cần xác định duplicate theo mục tiêu phân tích và kiểm tra các trường hợp có cùng nội dung đánh giá.

### 4. Khoảng trắng ở dữ liệu văn bản

Phát hiện giá trị có khoảng trắng đầu/cuối ở: `taster_twitter_handle` (9.532), `winery` (17), `title` (14), `designation` (5), `region_1` (4), `variety` (4), `description` (1). Các cột văn bản còn lại không có dấu hiệu này.

## Trường hợp cần nhóm xem xét

### 1. Giá trị giá rất cao

`price` có Q1 = 17, trung vị = 25, Q3 = 42 và giá trị tối đa = 3.300 USD. Độ lệch lớn cho thấy phân phối lệch phải và có ứng viên outlier. Giá cao có thể là chai rượu hợp lệ, nên không được tự động xóa chỉ vì vượt ngưỡng thống kê.

### 2. Không nhất quán chữ hoa/thường

Sau khi bỏ khoảng trắng và so sánh không phân biệt hoa/thường, phát hiện **27 nhóm** tên `winery` có nhiều cách viết. Không phát hiện nhóm tương tự ở `country`, `province`, `region_1`, `region_2` và `variety`. Cần xem từng nhóm trước khi chuẩn hóa để tránh gộp nhầm tên riêng.

### 3. Quan hệ giữa các cột

- `country` và `province` cùng thiếu 63 giá trị, nhưng cần đối chiếu theo dòng trước khi kết luận chúng luôn thiếu cùng nhau.
- `taster_name` và `taster_twitter_handle` có mức missing khác nhau; không nên điền một cột chỉ dựa vào cột kia nếu chưa kiểm tra ánh xạ.
- `region_2` thiếu 61,14%; quyết định giữ, bỏ hoặc gắn nhãn “Unknown/Not applicable” phụ thuộc mục tiêu EDA/modeling.

## Kết luận

Audit đã xác định các nhóm công việc cho giai đoạn cleaning: missing values, duplicate, consistency văn bản, outlier giá và quyết định xử lý cột chỉ mục. Tất cả đang ở trạng thái **Chờ nhóm thống nhất** trong `cleaning_log.csv`.
