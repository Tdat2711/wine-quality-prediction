# Báo Cáo Nhiệm Vụ Tiền Xử Lý Dữ Liệu: Nhất Quán & Trùng Lặp

**Người thực hiện:** Nguyễn Khắc Tuấn Đạt  
**Giai đoạn:** Data Cleaning (Bước 2 & Bước 3 trong Pipeline)  
**Tập dữ liệu:** Wine Reviews (`winemag-data-130k-v2.csv`)

---

## 1. Tổng quan nhiệm vụ
Nhiệm vụ này tập trung vào việc chuẩn hóa định dạng văn bản để đảm bảo tính đồng nhất (Consistency) và phát hiện, loại bỏ các bản ghi trùng lặp (Duplicates) nhằm nâng cao chất lượng tập dữ liệu trước khi đưa vào mô hình học máy. Đầu vào của giai đoạn này là tập dữ liệu đã được xử lý giá trị khuyết thiếu (Missing Values).

## 2. Chi tiết triển khai

### Nhiệm vụ 2.1: Đảm bảo tính nhất quán (Data Consistency)
* **File mã nguồn:** `src/clean_consistency.py`
* **File kết quả (Interim):** `data/interim/02_consistency_handled.csv`
* **Các thao tác xử lý:**
  - **Chuẩn hóa khoảng trắng:** Tự động quét toàn bộ các cột định dạng văn bản (string/object). Loại bỏ các khoảng trắng thừa ở đầu/cuối chuỗi (`strip`) và thay thế các khoảng trắng kép liên tiếp ở giữa thành một khoảng trắng duy nhất.
  - **Đồng bộ định dạng Null:** Chuyển đổi các giá trị chuỗi dạng `'nan'` (do lỗi parse dữ liệu) về lại định dạng `pd.NA` chuẩn của thư viện Pandas.
  - **Chuẩn hóa Quốc gia (Country):** Ép kiểu viết hoa chữ cái đầu (Title Case) cho toàn bộ dữ liệu trong cột `country`.
  - **Chuẩn hóa Twitter Handle:** Khôi phục tính nhất quán cho cột `taster_twitter_handle` bằng cách tự động gắn thêm ký tự `@` vào trước các tài khoản bị thiếu, đồng thời bỏ qua các giá trị "Unknown" hoặc "Not provided".

### Nhiệm vụ 2.2: Xử lý dữ liệu trùng lặp (Data Deduplication)
* **File mã nguồn:** `src/clean_duplicates.py`
* **File kết quả (Interim):** `data/interim/03_duplicates_handled.csv`
* **Các thao tác xử lý:**
  - **Loại bỏ ID hệ thống:** Xóa bỏ cột `Unnamed: 0` (đóng vai trò như index ID ẩn). Bước này mang tính chất quyết định vì nếu giữ nguyên, mỗi dòng sẽ là một ID độc nhất, khiến hệ thống không thể phát hiện trùng lặp.
  - **Xóa trùng lặp Logic (Logical Duplicates):** Thay vì chỉ xóa các dòng giống nhau 100%, hệ thống định nghĩa trùng lặp dựa trên logic thực tế: Nếu hai bản ghi có cùng một bài đánh giá (`description`) và cùng một người đánh giá (`taster_name`), bản ghi đó sẽ bị coi là lặp lại do lỗi crawl dữ liệu và bị xóa (chỉ giữ lại bản ghi đầu tiên).

## 3. Tích hợp Pipeline
Các module trên đã được đóng gói thành hàm độc lập (Modular) và tích hợp thành công vào file điều phối trung tâm `src/pipeline.py`. Dữ liệu truyền tải an toàn, không bị biến đổi cấu trúc ngoài ý muốn và có hệ thống ghi nhận log (report) số lượng bản ghi bị tác động tại mỗi chốt chặn.