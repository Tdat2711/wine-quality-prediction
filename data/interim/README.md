# Interim data

Thư mục này chứa các file CSV trung gian do `python src/pipeline.py` tạo ra sau từng bước làm sạch dữ liệu.

- Không chỉnh sửa các file CSV trung gian bằng tay.
- Các file CSV không được đưa lên GitHub vì có dung lượng lớn và có thể tái tạo từ dataset raw.
- Chạy pipeline từ thư mục gốc của project để tạo lại các file trung gian.

Các đầu ra trung gian hiện gồm:

1. `01_missing_handled.csv`
2. `02_consistency_handled.csv`
3. `03_duplicates_handled.csv`
4. `04_outliers_noise_handled.csv`
