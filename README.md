# Wine Reviews 130k — Data Cleaning and Analysis

Dự án sử dụng bộ **Wine Reviews 130k** gồm 129.971 bài đánh giá rượu, với thông tin về điểm số (`points`), giá, quốc gia, vùng, giống nho, nhà sản xuất, người đánh giá và nội dung review. Đây là dữ liệu review/metadata, không phải bộ dữ liệu 11 chỉ số hóa lý.

## Nguồn dữ liệu

- Nguồn: [Kaggle — Wine Reviews](https://www.kaggle.com/datasets/zynicide/wine-reviews)
- File raw: `data/raw/winemag-data-130k-v2.csv`
- Giấy phép công bố trên Kaggle: CC BY-NC-SA 4.0
- SHA-256 raw: `52af2643c8ac29f010f0cc629dfbdda1c74aa0f332d11762af9ef3de4e567ac9`

## Pipeline cleaning

```text
raw → missing values → consistency → exact duplicates
    → outlier/noise handling → final validation
```

Chạy từ thư mục project:

```powershell
python src/pipeline.py
```

Kết quả chính được tạo tại `data/processed/wine_cleaned_final.csv`. Các file trong `data/interim` chỉ dùng để audit và có thể tái tạo. Danh sách các bản ghi có khả năng trùng logic được xuất tại `docs/possible_logical_duplicates.csv` để nhóm xem xét thủ công.

`wine_ready_for_ML.csv` là đầu ra thử nghiệm cũ và không được dùng để huấn luyện chính thức. Quy trình ML phải chia train/test trước khi fit imputer, scaler hoặc SMOTE.
