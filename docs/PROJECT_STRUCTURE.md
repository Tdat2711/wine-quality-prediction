# Cấu trúc dự án

## 1. Nguyên tắc

Repository được tổ chức theo chức năng và luồng dữ liệu, không tách pipeline thành thư mục cá nhân. Riêng notebook phần việc trước buổi đánh giá tiến trình được giữ chung trong một thư mục để ghi nhận đóng góp; notebook báo cáo vẫn là một file tích hợp. Cách này giúp:

- Người khác tìm đúng loại artifact mà không cần biết ai tạo.
- Code, dữ liệu và báo cáo có thể tích hợp liên tục.
- Tránh năm phiên bản pipeline rời rạc trong năm thư mục cá nhân.
- Ownership được theo dõi bằng task ID, branch, pull request và roadmap.

## 2. Cấu trúc hiện tại

```text
wine-quality-prediction/
├── data/
│   ├── raw/
│   │   └── winemag-data-130k-v2.csv
│   ├── interim/
│   │   ├── 01_missing_handled.csv
│   │   ├── 02_consistency_handled.csv
│   │   ├── 03_duplicates_handled.csv
│   │   └── 04_outliers_noise_handled.csv
│   └── processed/
│       └── wine_cleaned_final.csv
├── docs/
├── notebooks/
│   ├── 00_data_understanding.ipynb
│   ├── 01_outliers_and_noise.ipynb
│   ├── 02_eda.ipynb                 # Khung báo cáo tiến trình, chưa có kết quả phân tích của nhóm
│   └── w5_progress_parts/
│       └── README.md                # Quy tắc nộp notebook cá nhân; chưa có năm file phần việc
├── src/
├── tests/
├── frontend/                         # Legacy
├── services/prediction-service/      # Legacy
├── requirements.txt
└── README.md
```

Cleaning đã được điều chỉnh để giữ giá thiếu. `02_eda.ipynb` hiện chỉ là khung; các notebook cá nhân sẽ được thêm khi từng người thực hiện nhiệm vụ. Phần EDA, inference và modeling phục vụ so sánh Dummy / chỉ giá / chỉ metadata / kết hợp **chưa có kết quả chính thức**; không dùng prototype classifier cũ.

## 3. Cấu trúc mục tiêu đến cuối kỳ

```text
wine-quality-prediction/
├── data/
│   ├── raw/                          # Dữ liệu gốc bất biến
│   ├── interim/                      # Bước cleaning trung gian
│   └── processed/
│       ├── wine_cleaned_final.csv
│       ├── split_assignments.csv
│       └── split_manifest.json
├── docs/
│   ├── ROADMAP_W5_W10.md
│   ├── TEAM_WORKFLOW.md
│   ├── PROJECT_STRUCTURE.md
│   ├── data_dictionary.md
│   └── model_card.md                 # Tạo sau khi có kết quả mô hình
├── notebooks/
│   ├── 00_data_understanding.ipynb
│   ├── 01_outliers_and_noise.ipynb
│   ├── 02_eda.ipynb                 # Một notebook dùng để trình bày thứ Tư tuần 6
│   ├── w5_progress_parts/           # Notebook cá nhân, giữ lại để chạy lại và xem đóng góp
│   │   ├── 01_khanh_price_tiers.ipynb
│   │   ├── 02_dat_data_split.ipynb
│   │   ├── 03_do_eda_plots.ipynb
│   │   ├── 04_duong_story_stats.ipynb
│   │   └── 05_dung_baseline.ipynb
│   ├── 03_statistical_inference.ipynb
│   └── 04_error_analysis.ipynb
├── reports/
│   ├── figures/
│   ├── metrics/                      # CV, validation và test metrics
│   └── final_report.md
├── models/                            # Pipeline model đã khóa và metadata
├── src/
│   ├── pipeline.py                   # Cleaning entry point hiện tại
│   ├── features.py                   # Feature/preprocessing dùng chung
│   ├── split_data.py                 # Split reproducible
│   ├── train.py                      # Validation sơ bộ / train-only CV và freeze
│   └── evaluate.py                   # Một đợt test cho bốn cấu hình đã khóa
├── tests/
│   ├── test_cleaning.py
│   ├── test_features.py
│   └── test_split.py
├── frontend/                         # Legacy cho đến khi đạt web gate
├── services/                         # Legacy cho đến khi đạt web gate
├── requirements.txt
└── README.md
```

Các file chưa tồn tại trong cây mục tiêu là định hướng triển khai, không phải tính năng hiện có. Chỉ tạo notebook cá nhân khi người phụ trách bắt đầu task; không tạo năm file rỗng. `02_eda.ipynb` là nơi Khánh tích hợp các cell đã kiểm tra, không sao chép năm lần phần nạp dữ liệu.

## 4. Trách nhiệm từng thư mục

| Thư mục | Được đặt | Không được đặt |
|---|---|---|
| `data/raw/` | Dataset gốc đã xác minh | File đã sửa, output notebook, bản sao tùy ý |
| `data/interim/` | Output trung gian có thể tái tạo | Kết quả cuối duy nhất hoặc file sửa tay |
| `data/processed/` | Cleaned/model-ready data có schema rõ | Model, figures hoặc báo cáo |
| `docs/` | Quy tắc, audit, data dictionary, model card | Notebook hoặc code thực thi chính |
| `notebooks/` | EDA, inference và error analysis | Logic production duy nhất, model binary |
| `reports/figures/` | Hình cuối được tạo từ code | Screenshot tạm hoặc hình không có nguồn |
| `reports/metrics/` | Bảng CV/validation/test có metadata | Model binary hoặc dữ liệu raw |
| `models/` | Pipeline model đã khóa và metadata | Các thử nghiệm không còn dùng |
| `src/` | Code tái sử dụng và entry point | Dữ liệu, hình hoặc kết quả thủ công |
| `tests/` | Unit/integration tests nhỏ, ổn định | Notebook phân tích hoặc dataset lớn |
| `frontend/`, `services/` | Chỉ dùng lại sau web gate | Kết quả chính khi schema còn không khớp |

## 5. Luồng dữ liệu và artifact

```text
data/raw/winemag-data-130k-v2.csv
        │
        ▼
src/pipeline.py
        │
        ├── data/interim/*.csv
        ├── docs/possible_logical_duplicates.csv
        └── data/processed/wine_cleaned_final.csv
                     │
                     ▼
             split train/val/test
                     │
                     ▼
          train-fitted preprocessing + feature pipeline
                     │
              ┌──────┴──────┐
              ▼             ▼
       CV/validation     EDA/inference trên train
              │             │
              └──────┬──────┘
                     ▼
              four locked comparison arms
                     │
              ┌──────┴────────┐
              ▼               ▼
       test metrics       report/figures
```

### Metadata tối thiểu cho experiment

Mỗi kết quả model cần ghi:

- Commit/version của code.
- Dataset/checksum hoặc định danh data version.
- Feature set và target.
- Seed và phương pháp split.
- Model/hyperparameter.
- Metric trên CV/validation hoặc test.
- Thời điểm chạy và người thực hiện.

## 6. Quy tắc tạo model-ready data

- Không ghi đè `wine_cleaned_final.csv`.
- Ưu tiên để preprocessing nằm trong scikit-learn pipeline thay vì xuất nhiều CSV đã encode.
- Nếu cần lưu `model_ready`, phải có script tái tạo và schema đi kèm.
- Không lưu một bản model-ready riêng cho mỗi thành viên.
- Split assignments được lưu với row ID và title-group; kiểm tra hash của cleaned data trước khi train/evaluate.
- Không fit encoder/imputer/scaler trước khi chia dữ liệu.

## 7. Xử lý thành phần legacy

Các thành phần sau hiện không khớp bài toán chính:

- `src/train_model.py` dùng target `quality` và classifier.
- `frontend/` nhập 11 chỉ số hóa lý.
- `services/prediction-service/` mong đợi model/class probability theo bài toán cũ.

Trong giai đoạn tuần 5–8:

- Không sử dụng chúng để huấn luyện hoặc báo cáo kết quả.
- Không xóa nếu chưa có quyết định chung vì chúng vẫn thể hiện prototype trước đây.
- Gắn nhãn legacy rõ trong README và tài liệu.

Hướng hai tầng không yêu cầu web. Nếu nhóm quyết định làm web thành task riêng về sau, phải thay toàn bộ input schema và prediction flow bằng pipeline Wine Reviews 130k đã khóa.

## 8. Web gate (ngoài phạm vi bắt buộc)

Chỉ bắt đầu web/API khi đồng thời đạt các điều kiện:

- Cleaning và modeling pipeline chạy end-to-end từ project root.
- Automated tests liên quan đều pass.
- Có model artifact chứa preprocessing và model.
- Báo cáo hoàn thành tối thiểu khoảng 70%.
- Có validation metrics và error analysis.
- Không làm chậm các nhiệm vụ phân tích và mô hình trong roadmap.

Nếu thiếu một điều kiện, ưu tiên tiếp tục phần data/model/report; không đưa web vào gate báo cáo tuần 6.

## 9. Cách xác định ownership

- Người phụ trách và nhiệm vụ nằm trong [ROADMAP_W5_W10.md](ROADMAP_W5_W10.md); task ID, nếu dùng, được tạo trong issue/branch.
- Tên branch chứa task ID khi nhóm dùng issue để theo dõi.
- Pull request ghi owner, reviewer và đầu ra.
- Báo cáo có mục contributors nếu cần ghi đóng góp học thuật.
- Git history dùng để xem thay đổi cụ thể, không dùng vị trí thư mục để suy ra đóng góp.
- `notebooks/w5_progress_parts/` chỉ là nơi nộp năm notebook phần việc; tên file và Git history cho biết người phụ trách, nhưng không tạo năm bản pipeline dữ liệu riêng.

Cách tổ chức này vẫn ghi nhận rõ công sức từng người nhưng tránh phân mảnh pipeline.
