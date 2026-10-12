# Wine Quality Prediction

Dự án khoa học dữ liệu sử dụng bộ **Wine Reviews 130k** để nghiên cứu các yếu tố liên hệ với điểm đánh giá rượu và xây dựng mô hình hồi quy dự đoán `points` từ giá cùng các metadata phù hợp.


## 1. Câu hỏi nghiên cứu

Dự án tập trung trả lời ba câu hỏi:

1. Những đặc trưng nào có quan hệ đáng chú ý với điểm đánh giá `points`?
2. Có thể dự đoán `points` từ `price` và metadata của rượu chính xác đến mức nào?
3. Sai số của mô hình có khác nhau giữa quốc gia, giống nho và các phân khúc giá hay không?

## 2. Mục tiêu và phạm vi

### Mục tiêu chính

- Audit, làm sạch và kiểm tra chất lượng dữ liệu theo một pipeline có thể chạy lại.
- Thực hiện exploratory data analysis (EDA) và trực quan hóa các quan hệ quan trọng.
- Sử dụng statistical inference để kiểm tra các giả thuyết có ý nghĩa với bài toán.
- Xây dựng feature engineering và preprocessing không gây data leakage.
- Huấn luyện, so sánh và đánh giá các mô hình hồi quy.
- Phân tích residual, bias, ethics và giới hạn sử dụng kết quả.
- Tạo báo cáo và slide có đủ bằng chứng để bảo vệ cuối kỳ.

### Ngoài phạm vi chính hiện tại

- Web, API và deployment không phải ưu tiên từ tuần 5 đến tuần 10.
- Không sử dụng deep learning, Spark hoặc cloud nếu pipeline dữ liệu và báo cáo chưa hoàn tất.
- Không biến `points` thành bài toán classification trong pipeline chính.

## 3. Trạng thái dự án

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Data audit | Đã hoàn thành | Có báo cáo và data dictionary |
| Cleaning pipeline | Tương đối hoàn chỉnh | Chạy được từ raw tới cleaned data |
| Missing values | Đã xử lý | Các quyết định được ghi trong báo cáo và cleaning log |
| Consistency và duplicates | Đã xử lý | Xóa duplicate hoàn toàn; giữ và xuất các trường hợp nghi trùng logic để audit |
| Outlier và noise | Đã xử lý bước đầu | Giữ phân khúc giá cao; hai lỗi giá đã được hiệu chỉnh có lưu dấu |
| Automated tests | Đã có bước đầu | Hiện tập trung vào một số quy tắc cleaning quan trọng |
| EDA và inference | Đang thực hiện | Chưa có kết luận cuối |
| Modeling chính thức | Chưa hoàn thành | Chưa có metric test chính thức |
| Báo cáo và slide | Chưa hoàn thành | Thực hiện từ tuần 8 đến tuần 10 |

Đầu ra cleaning hiện tại là `data/processed/wine_cleaned_final.csv`, gồm **119.988 dòng và 18 cột**. Các metric mô hình sẽ chỉ được công bố sau khi pipeline modeling hoàn chỉnh và test set được mở đúng một lần ở tuần 9.

`src/train_model.py`, `frontend/` và `services/prediction-service/` là **legacy prototype**: các thành phần này đang giả định target `quality` và 11 thuộc tính hóa lý, nên không được xem là pipeline hoạt động của dự án Wine Reviews 130k.

## 4. Dữ liệu

- Nguồn: [Kaggle — Wine Reviews](https://www.kaggle.com/datasets/zynicide/wine-reviews)
- File gốc: `data/raw/winemag-data-130k-v2.csv`
- File sạch: `data/processed/wine_cleaned_final.csv`
- Giấy phép được công bố trên Kaggle: CC BY-NC-SA 4.0
- SHA-256 file raw đã audit: `52af2643c8ac29f010f0cc629dfbdda1c74aa0f332d11762af9ef3de4e567ac9`

### Nhóm biến

| Nhóm | Các cột tiêu biểu | Vai trò dự kiến |
|---|---|---|
| Target | `points` | Điểm cần dự đoán |
| Numerical | `price`, `log_price`, `vintage_year` | EDA, inference và modeling |
| Categorical | `country`, `province`, `region_1`, `region_2`, `variety`, `winery`, `designation` | Metadata; cần xử lý missing và cardinality |
| Text | `title`, `description` | Dùng cho audit/EDA; chưa đưa vào baseline chính |
| Reviewer metadata | `taster_name`, `taster_twitter_handle` | Dùng để phân tích bias; không dùng làm feature chính nếu chưa có lập luận hợp lý |
| Audit fields | `price_original`, `price_was_corrected`, `is_non_informative_review` | Theo dõi quyết định cleaning |

Định nghĩa đầy đủ của từng cột nằm trong [Data Dictionary](docs/data_dictionary.md). Dữ liệu trong `data/raw/` là bất biến: mọi biến đổi phải được thực hiện bằng code và ghi sang `data/interim/` hoặc `data/processed/`.

## 5. Pipeline dự án

```text
Raw data
   ↓
Missing-value handling
   ↓
Consistency normalization
   ↓
Exact-duplicate removal
   ↓
Outlier/noise audit
   ↓
Final validation
   ↓
Train/validation/test split
   ↓
Feature engineering
   ↓
Regression models
   ↓
Evaluation, bias analysis and reporting
```

Năm bước đầu đã có trong cleaning pipeline. Các bước từ chia dữ liệu đến đánh giá mô hình được triển khai theo [lộ trình tuần 5–10](docs/ROADMAP_W5_W10.md).

## 6. Cấu trúc repository hiện tại

```text
wine-quality-prediction/
├── data/
│   ├── raw/                    # Dữ liệu gốc, không chỉnh sửa
│   ├── interim/                # Kết quả trung gian có thể tái tạo
│   └── processed/              # Dữ liệu sạch dùng cho phân tích
├── docs/                       # Audit, data dictionary và tài liệu quản lý
├── notebooks/                  # Phân tích khám phá có thứ tự thực hiện
├── reports/
│   └── figures/                # Hình ảnh dùng trong báo cáo/slide
├── src/                        # Code pipeline có thể tái sử dụng
├── tests/                      # Automated tests
├── frontend/                   # Legacy prototype, chưa thuộc pipeline chính
├── services/                   # Legacy prediction service
├── requirements.txt
└── README.md
```

Không chia repository thành thư mục riêng cho Khánh, Đạt, Đô, Dương và Dũng. File được tổ chức theo chức năng; người chịu trách nhiệm được quản lý trong roadmap, issue, branch và pull request. Xem [Project Structure](docs/PROJECT_STRUCTURE.md) để biết cấu trúc mục tiêu và vị trí các artifact sắp được tạo.

## 7. Cài đặt và chạy lại

Các lệnh dưới đây được chạy từ thư mục gốc của repository.

### Yêu cầu

- Python 3.10 trở lên.
- Git.
- Dữ liệu raw đúng tên và checksum nêu ở phần dữ liệu.

### Thiết lập môi trường

```powershell
git clone <repository-url>
cd wine-quality-prediction
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Trên macOS/Linux, kích hoạt môi trường bằng `source .venv/bin/activate`.

### Chạy cleaning pipeline

```powershell
python src/pipeline.py
```

Pipeline tạo lại các file trung gian, file cleaned cuối và danh sách các trường hợp nghi trùng logic. Pipeline đồng thời kiểm tra checksum raw, schema, missing values, duplicate, miền `points` và các quyết định xử lý giá.

### Chạy test

```powershell
python -m unittest discover -s tests
```

### Mở notebook

```powershell
jupyter notebook
```

Sau đó chạy notebook theo tiền tố số trong `notebooks/`. Chưa có lệnh train/evaluate chính thức trong README vì modeling pipeline mới đang được xây dựng; không sử dụng `src/train_model.py` cho kết quả cuối.

## 8. Quy ước modeling đã chốt

- **Bài toán:** regression với target `points`.
- **Metric chính:** Mean Absolute Error (MAE).
- **Metric phụ:** Root Mean Squared Error (RMSE) và \(R^2\).
- **Split:** 70% train, 15% validation, 15% test với random seed cố định và phân tầng theo khoảng `points` nếu khả thi.
- **Baseline:** `DummyRegressor`, `LinearRegression` và `Ridge`.
- Imputer, encoder, scaler và mọi bước học từ dữ liệu chỉ được fit trên train.
- Validation/CV dùng để lựa chọn feature, mô hình và hyperparameter.
- Test set được khóa đến tuần 9 và chỉ dùng một lần để báo cáo kết quả cuối.
- `description`, `title` và thông tin người đánh giá không được đưa vào baseline chính.

## 9. Kết quả

### Kết quả đã xác nhận

- Raw data giữ nguyên và được kiểm tra bằng SHA-256.
- Cleaning pipeline tạo 119.988 dòng và 18 cột.
- Không còn duplicate hoàn toàn trên các cột dữ liệu gốc.
- Điểm tối đa 100 và phân khúc rượu giá cao được giữ lại.
- Hai lỗi nhập giá đã biết được sửa và đánh dấu bằng audit fields.
- Các test cleaning hiện có chạy thành công tại thời điểm cập nhật tài liệu.

### Kết quả chưa có

Nhóm chưa công bố MAE, RMSE hoặc \(R^2\) vì pipeline modeling và đánh giá test chưa hoàn tất. Bảng kết quả chính thức sẽ được thêm sau model freeze ở tuần 9; không sử dụng số liệu giả định để điền trước.

## 10. Thành viên và trách nhiệm chính

| Thành viên | Trách nhiệm chính |
|---|---|
| **Khánh** — nhóm trưởng | Chốt phạm vi, baseline hồi quy, tích hợp pipeline, QA và reproducibility |
| **Đạt** | Data pipeline, validation và model-ready dataset |
| **Đô** | EDA, trực quan hóa và error analysis |
| **Dương** | Statistical inference, ethics, bias và limitations |
| **Dũng** | Feature engineering, modeling và evaluation |

Nhiệm vụ, reviewer, đầu ra và điều kiện hoàn thành của từng tuần được ghi tại [Roadmap tuần 5–10](docs/ROADMAP_W5_W10.md). Quy trình phối hợp nằm trong [Team Workflow](docs/TEAM_WORKFLOW.md).

## 11. Tài liệu dự án

- [Data audit](docs/data_audit.md)
- [Data dictionary](docs/data_dictionary.md)
- [Missing-values report](docs/missing_values_report.md)
- [Consistency và duplicate report](docs/report_dat_consistency_duplicates.md)
- [Outlier và noise report](docs/outliers_and_noise_report.md)
- [Roadmap tuần 5–10](docs/ROADMAP_W5_W10.md)
- [Team workflow](docs/TEAM_WORKFLOW.md)
- [Project structure](docs/PROJECT_STRUCTURE.md)

## 12. Hạn chế, bias và đạo đức

- `points` phản ánh đánh giá chủ quan và có thể phụ thuộc vào người chấm.
- Quốc gia, vùng, giống nho, winery và các khoảng giá có phân bố không đồng đều.
- Tương quan giữa giá và điểm không chứng minh rằng giá cao gây ra chất lượng cao.
- Dữ liệu chỉ bao phủ các sản phẩm được chọn để review, không đại diện cho toàn bộ thị trường rượu.
- Không trình bày dự đoán như một thước đo chất lượng khách quan tuyệt đối hoặc khuyến nghị mua hàng chắc chắn.
- Tên người đánh giá chỉ phục vụ audit/bias analysis, trừ khi nhóm có bằng chứng rõ ràng để sử dụng hợp lệ trong mô hình.

## 13. Khả năng tái lập

- Không chỉnh sửa trực tiếp file raw.
- Kiểm tra checksum raw trước và sau cleaning.
- Dùng seed cố định cho split, CV và mô hình có tính ngẫu nhiên.
- Lưu cấu hình split và metric cùng kết quả thực nghiệm.
- Notebook phải chạy lại từ đầu không lỗi trước khi merge.
- Logic dùng chung phải được chuyển từ notebook sang `src/` và có test phù hợp.
- Mọi kết quả trong báo cáo phải truy ngược được tới code, dữ liệu và artifact đã version hóa.

## 14. Tiến độ

Hiện tại là **tuần thực tế thứ 5**; cuối tuần này nhóm hoàn thành kiến thức đến Regression Analysis. Lộ trình chi tiết từ tuần 5 đến tuần 10, bao gồm nhiệm vụ cân bằng cho năm thành viên, nằm trong [docs/ROADMAP_W5_W10.md](docs/ROADMAP_W5_W10.md).
