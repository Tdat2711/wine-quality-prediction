# Phân tích và dự đoán điểm đánh giá rượu từ giá và thông tin sản phẩm

Dự án khoa học dữ liệu dùng **Wine Reviews 130k** để trả lời: **giá giúp dự đoán điểm review `points` đến đâu, và metadata bổ sung được bao nhiêu?** Mô hình là công cụ so sánh các nguồn thông tin; dự đoán không thay thế điểm review đã có và không đo "chất lượng khách quan".


## 1. Câu hỏi nghiên cứu

Dự án tập trung trả lời ba câu hỏi:

1. Chỉ biết giá, mô hình dự đoán `points` tốt hơn một dự đoán ngây thơ bao nhiêu?
2. Thêm `country`, `province`, `variety`, `vintage_year` có giảm sai số so với chỉ giá không?
3. Mô hình còn sai ở nhóm giá, quốc gia, giống nho hoặc người đánh giá nào?

Bốn cấu hình dùng **cùng một mẫu và split**: `Dummy`, `price_only`, `metadata_only`, `combined`. Chênh lệch MAE giữa `price_only` và `combined` đo **giá trị dự đoán bổ sung** của metadata, không phải quan hệ nhân quả.

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
| Missing values | Đã xử lý theo hướng mới | Giữ giá thiếu để không biến giá ước tính thành giá quan sát |
| Consistency và duplicates | Đã xử lý | Xóa duplicate hoàn toàn; giữ và xuất các trường hợp nghi trùng logic để audit |
| Outlier và noise | Đã xử lý bước đầu | Giữ phân khúc giá cao; hai lỗi giá đã được hiệu chỉnh có lưu dấu |
| Automated tests | Đã có bước đầu | Hiện tập trung vào một số quy tắc cleaning quan trọng |
| EDA và inference | Chưa hoàn thành | Sẽ triển khai theo câu hỏi hai tầng trong roadmap |
| Modeling chính thức | Chưa bắt đầu | Chưa có split, pipeline so sánh hoặc metric chính thức |
| Báo cáo tiến trình | Đang chuẩn bị | Buổi thứ Tư tuần 6 dùng một notebook chung, chưa có kết quả mô hình chính thức |

Đầu ra cleaning là `data/processed/wine_cleaned_final.csv`, gồm **119.988 dòng và 19 cột**. Có **8.395 dòng thiếu giá** sau loại duplicate; **111.593 dòng** có giá quan sát được, dự kiến đủ điều kiện cho thí nghiệm chính. Dữ liệu raw có 8.996 giá thiếu. Nhóm chưa chạy so sánh mô hình, validation hoặc test chính thức.

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
| Numerical | `price`, `log_price`, `vintage_year` | Giá dùng `log1p(price)`; năm là metadata |
| Categorical | `country`, `province`, `region_1`, `region_2`, `variety`, `winery`, `designation` | Metadata; cần xử lý missing và cardinality |
| Text | `title`, `description` | Dùng cho audit/EDA; chưa đưa vào baseline chính |
| Reviewer metadata | `taster_name`, `taster_twitter_handle` | Dùng để phân tích bias; không dùng làm feature chính nếu chưa có lập luận hợp lý |
| Audit fields | `price_original`, `price_was_missing`, `price_was_corrected`, `is_non_informative_review` | Theo dõi quyết định cleaning; không dùng làm predictor |

Định nghĩa đầy đủ của từng cột nằm trong [Data Dictionary](docs/data_dictionary.md). Dữ liệu trong `data/raw/` là bất biến: mọi biến đổi phải được thực hiện bằng code và ghi sang `data/interim/` hoặc `data/processed/`.

## 5. Pipeline dự án

```text
Raw data
   ↓
Missing-value handling (giữ price thiếu)
   ↓
Consistency normalization
   ↓
Exact-duplicate removal
   ↓
Outlier/noise audit
   ↓
Final validation
   ↓
Chọn chai có giá quan sát, chia train/validation/test theo nhóm title
   ↓
Feature engineering
   ↓
Dummy / chỉ giá / chỉ metadata / kết hợp (cùng mẫu)
   ↓
Evaluation, bias analysis and reporting
```

Hiện chỉ có entry point cho cleaning. Các bước từ chia dữ liệu đến kết quả mô hình là kế hoạch trong [lộ trình tuần 5–10](docs/ROADMAP_W5_W10.md), chưa được triển khai.

## 6. Cấu trúc repository hiện tại

```text
wine-quality-prediction/
├── data/
│   ├── raw/                    # Dữ liệu gốc, không chỉnh sửa
│   ├── interim/                # Kết quả trung gian có thể tái tạo
│   └── processed/              # Dữ liệu sạch dùng cho phân tích
├── docs/                       # Audit, data dictionary và tài liệu quản lý
├── notebooks/                  # Phân tích khám phá có thứ tự thực hiện
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

Hiện có notebook tìm hiểu dữ liệu và cleaning, cùng khung `notebooks/02_eda.ipynb` cho buổi đánh giá tiến trình. Mỗi thành viên sẽ nộp notebook phần việc trong `notebooks/w5_progress_parts/`; Khánh chọn và tích hợp các cell đã kiểm tra vào một notebook chung để trình bày. Các notebook inference và phân tích sai số được làm ở giai đoạn sau; `src/train_model.py` cũ không dùng cho kết quả cuối.

## 8. Quy ước modeling đã chốt

- **Bài toán:** regression với target `points`.
- **Metric chính:** Mean Absolute Error (MAE).
- **Metric phụ:** Root Mean Squared Error (RMSE) và \(R^2\).
- **Mẫu so sánh:** chỉ dòng có giá quan sát được; dòng thiếu giá vẫn giữ trong cleaned data để audit.
- **Split dự kiến:** xấp xỉ 70% train, 15% validation, 15% test; seed sẽ được khóa khi bắt đầu thí nghiệm, nhóm theo `title` đã chuẩn hóa để tránh cùng tên chai nằm ở hai tập.
- **Bốn cấu hình:** `DummyRegressor`, Ridge chỉ `log_price`, Ridge chỉ metadata, Ridge kết hợp; cùng mẫu, split và metric.
- **Metadata chính:** `country`, `province`, `variety`, `vintage_year`. Không dùng nguyên văn review/title, người chấm hay audit fields làm predictor.
- Imputer, encoder, scaler và mọi bước học từ dữ liệu chỉ được fit trên train.
- Validation là kết quả sơ bộ; train-only GroupKFold chọn `alpha` từ cùng grid cho ba cấu hình Ridge.
- Test set chỉ dùng trong một đợt sau khi model freeze; không tuning theo test.
- `description`, `title` và thông tin người đánh giá không được đưa vào baseline chính.

## 9. Kết quả

### Kết quả đã xác nhận

- Raw data giữ nguyên và được kiểm tra bằng SHA-256.
- Cleaning pipeline tạo 119.988 dòng và 19 cột; 8.395 dòng thiếu giá được giữ lại.
- Không còn duplicate hoàn toàn trên các cột dữ liệu gốc.
- Điểm tối đa 100 và phân khúc rượu giá cao được giữ lại.
- Hai lỗi nhập giá đã biết được sửa và đánh dấu bằng audit fields.
- Các test cleaning hiện có chạy thành công tại thời điểm cập nhật tài liệu.

### Kết quả mô hình chưa có

Nhóm chưa công bố MAE, RMSE hoặc \(R^2\) cho hướng hai tầng. Mọi bảng validation và test trong roadmap là **đầu ra dự kiến**, không phải kết quả hiện có.

## 10. Thành viên và trách nhiệm chính

| Thành viên | Trách nhiệm chính |
|---|---|
| **Khánh** — nhóm trưởng | Điều phối câu hỏi nghiên cứu, phân tích giá–điểm, chốt và duyệt split, xây baseline hồi quy chính thức, tích hợp kết quả |
| **Đạt** | Cleaning, chuẩn bị mẫu và triển khai/kiểm soát split, chuẩn bị dữ liệu cùng preprocessing dùng chung cho mô hình |
| **Đô** | EDA, trực quan hóa và phân tích sai số mô hình |
| **Dương** | Kể câu chuyện dữ liệu, thống kê và kiểm định, diễn giải kết quả, bias, ethics và giới hạn |
| **Dũng** | Khảo sát metadata, thử baseline chỉ giá ở giai đoạn tiến trình nếu đủ điều kiện, xây mô hình chỉ metadata và mô hình kết hợp, đánh giá mô hình cuối |

Nhiệm vụ cụ thể và người phụ trách từng giai đoạn được ghi tại [Roadmap tuần 5–10](docs/ROADMAP_W5_W10.md). Cách chọn reviewer, giao đầu ra và review code nằm trong [Team Workflow](docs/TEAM_WORKFLOW.md).

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

Tuần 5–10 trong [roadmap](docs/ROADMAP_W5_W10.md) là tiến độ thực tế của nhóm, không trùng số tuần in trên slide của học phần 15 tuần. Buổi đánh giá tiến trình thứ Tư tuần 6 dùng một notebook chung, tập trung vào câu hỏi dự án và phân tích khám phá giá–điểm; cleaning chỉ được tóm tắt vì đã báo cáo trước. Split có thể bắt đầu trước buổi đánh giá và hoàn tất ở tuần 6. Kiểm định/hồi quy thử chỉ trình bày nếu đã kiểm tra đúng trên train/validation; kiểm định chính thức ở tuần 8, so sánh bốn mô hình ở tuần 9 và đánh giá test cuối ở tuần 10.
