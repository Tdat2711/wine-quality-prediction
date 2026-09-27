# Data Dictionary — Wine Reviews 130k

Nguồn dữ liệu: `data/raw/winemag-data-130k-v2.csv`  
Kích thước khi audit: **129.971 dòng × 14 cột**  
Các con số dưới đây được tính trên file raw và chưa qua làm sạch.

| Tên cột | Ý nghĩa | Kiểu dữ liệu thực tế | Unique (không tính null) | Missing | Ghi chú |
|---|---|---:|---:|---:|---|
| `Unnamed: 0` | Chỉ mục dòng được lưu kèm khi xuất CSV | `int64` | 129.971 | 0 | Cột đầu không có tên trong file gốc; giá trị 0–129.970 và duy nhất. Chưa xóa. |
| `country` | Quốc gia sản xuất rượu | chuỗi | 43 | 63 | Biến phân loại; cần thống nhất cách xử lý missing. |
| `description` | Nội dung đánh giá rượu | chuỗi | 119.955 | 0 | Văn bản tự do; phát hiện 1 giá trị có khoảng trắng đầu/cuối. |
| `designation` | Tên dòng rượu hoặc tên do nhà sản xuất đặt | chuỗi | 37.979 | 37.465 | Missing nhiều; có 5 giá trị có khoảng trắng đầu/cuối. |
| `points` | Điểm đánh giá | `int64` | 21 | 0 | Khoảng thực tế 80–100. |
| `price` | Giá chai rượu (USD) | `float64` | 390 | 8.996 | Khoảng 4–3.300; trung vị 25. Cần đánh giá outlier trước khi xử lý. |
| `province` | Tỉnh, bang hoặc vùng sản xuất cấp cao | chuỗi | 425 | 63 | Missing khớp về số lượng với `country`, nhưng cần kiểm tra theo dòng. |
| `region_1` | Vùng sản xuất cấp chi tiết thứ nhất | chuỗi | 1.229 | 21.247 | Có 4 giá trị có khoảng trắng đầu/cuối. |
| `region_2` | Vùng sản xuất cấp chi tiết thứ hai | chuỗi | 17 | 79.460 | Cột thiếu nhiều nhất, khoảng 61,14%. |
| `taster_name` | Tên người đánh giá | chuỗi | 19 | 26.244 | Cần xem quan hệ với tài khoản Twitter. |
| `taster_twitter_handle` | Tài khoản Twitter của người đánh giá | chuỗi | 15 | 31.213 | Có 9.532 giá trị có khoảng trắng đầu/cuối. |
| `title` | Tiêu đề của bài đánh giá/chai rượu | chuỗi | 118.840 | 0 | Có 14 giá trị có khoảng trắng đầu/cuối. |
| `variety` | Giống nho hoặc loại phối trộn | chuỗi | 707 | 1 | Có 4 giá trị có khoảng trắng đầu/cuối. |
| `winery` | Nhà sản xuất/rượu vang | chuỗi | 16.757 | 0 | Có 17 giá trị có khoảng trắng; 27 nhóm chỉ khác cách viết hoa/thường. |

## Quy ước

- `Missing` là số ô rỗng mà pandas đọc thành `NaN`.
- `Unique` không tính giá trị rỗng.
- Kiểu “chuỗi” có thể hiển thị là `object` hoặc `str` tùy phiên bản pandas; ý nghĩa dữ liệu không đổi.
- Data dictionary này chỉ mô tả dữ liệu. Mọi quyết định sửa/xóa phải được ghi vào cleaning log.
