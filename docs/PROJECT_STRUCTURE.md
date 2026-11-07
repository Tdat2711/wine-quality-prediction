# Cấu trúc và quy trình repository

Repository tổ chức theo chức năng, dùng chung một pipeline cleaning, một bộ split và một notebook EDA chính. Không có phân công theo thành viên hoặc lịch tuần học.

## Thư mục và trách nhiệm

| Vị trí | Nội dung |
|---|---|
| `data/raw/` | Dataset nguồn bất biến |
| `data/interim/` | CSV trung gian từ pipeline cleaning |
| `data/processed/` | Cleaned data và `splits/train.csv`, `val.csv`, `test.csv` |
| `notebooks/` | `00_data_understanding.ipynb`, `01_outliers_and_noise.ipynb`, `02_data_split.ipynb`, `03_eda.ipynb` |
| `src/` | Các module cleaning hiện có, `pipeline.py`, `split_data.py`, `create_eda_plots.py` |
| `outputs/eda/figures/` | Hình PNG được tạo lại bằng code |
| `outputs/eda/tables/` | Bảng mô tả và audit CSV |
| `docs/` | Audit, dictionary, quyết định cleaning, báo cáo split và EDA |
| `tests/` | Kiểm tra cleaning, split, lựa chọn mẫu, EDA và encoding |
| `wine_encoding/` | Module tiền xử lý, số hóa dữ liệu (product/review/all), huấn luyện baseline + Ridge, đánh giá và suy luận |
| `wine_encoding/outputs/` | Artifact tiền xử lý (`encoder.joblib`), ma trận đặc trưng `X_*.npz`, model `ridge_product.joblib`, báo cáo đánh giá |

## Luồng chạy hiện có

1. `python src/pipeline.py`: raw → interim → cleaned, kèm validation (`data/processed/wine_cleaned_final.csv`).
2. `python src/split_data.py`: tái tạo split trong bộ nhớ, so sánh file hiện có; không ghi đè.
3. `python src/split_data.py --write`: chỉ tạo split chưa tồn tại, từ chối nếu file đã có không khớp.
4. `python src/create_eda_plots.py`: cleaned dùng cho audit, train dùng cho phân tích chi tiết; review holdout chỉ dùng audit trùng văn bản.
5. Mở notebook theo thứ tự; notebook outlier giải thích các quyết định cleaning, không phải bước xử lý bổ sung ngoài pipeline.
6. `python -m unittest discover -s tests -v`: kiểm tra các quy tắc đang triển khai (bao gồm kiểm thử làm sạch, chia tập, EDA và encoding).

Logic split đã được chuyển từ notebook phần việc sang module chung; notebook mới chỉ kiểm tra, không xuất lại CSV. Các nội dung bảng khoảng giá, hình giá–điểm, bối cảnh và chuẩn bị mô hình được tích hợp trong notebook chức năng và README.

## Module tiền xử lý và mô hình hóa (`wine_encoding`)

Đã tích hợp module `wine_encoding` chuẩn hóa 19 thuộc tính theo thiết kế:
- **Tiền xử lý số**: Giá, niên vụ, log_price được điền trung vị train + chuẩn hóa thang đo (StandardScaler) kèm cờ thiếu ổn định.
- **Biến phân loại**: One-hot encoder với gom nhóm tần suất thấp (`category_min_frequency=20`, tối đa 256 nhóm/cột).
- **Văn bản**: TF-IDF unigram/bigram cho description (tối đa 3.000 features) và title (tối đa 1.000 features).
- **Bộ đặc trưng đa tầng**:
  - `product`: thông tin sản phẩm (giá, vùng, giống nho, winery, vintage).
  - `review`: bổ sung thêm mô tả cảm quan và người đánh giá.
  - `all_attributes_audit`: số hóa toàn bộ để đối chiếu audit.
- **Chống rò rỉ (Zero Leakage)**: Mọi scaler, imputer, vocabulary và nhóm hiếm chỉ fit trên tập train; validation/test chỉ transform.
- **Mô hình**: Baseline (DummyRegressor) + Ridge Regression chọn siêu tham số alpha tốt nhất trên tập validation.
- **Cách chạy**:
  - Kiểm tra tính toàn vẹn: `python -m wine_encoding.src.verify` và `python -m wine_encoding.src.verify_model`
  - Huấn luyện / Tái sinh ma trận: `python -m wine_encoding.src.prepare` và `python -m wine_encoding.src.train`
  - Dự đoán dữ liệu mới: `python -m wine_encoding.src.predict --input wine_encoding/examples/new_wines.csv`

Giữ lịch sử holdout và báo cáo review trùng. Không thay split hoặc tuning theo test để chọn kết quả thuận lợi. Không sửa dữ liệu raw hoặc chép bản dữ liệu/model riêng theo người thực hiện.
