# Cấu trúc dự án

## 1. Nguyên tắc

Repository được tổ chức theo chức năng và luồng dữ liệu, không theo tên thành viên. Cách này giúp:

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
│   └── 01_outliers_and_noise.ipynb
├── reports/
│   └── figures/
├── src/
├── tests/
├── frontend/                         # Legacy
├── services/prediction-service/      # Legacy
├── requirements.txt
└── README.md
```

Phần cleaning có cấu trúc tương đối rõ. Phần EDA, inference và modeling chưa có đầy đủ module, artifact và test.

## 3. Cấu trúc mục tiêu đến cuối kỳ

```text
wine-quality-prediction/
├── data/
│   ├── raw/                          # Dữ liệu gốc bất biến
│   ├── interim/                      # Bước cleaning trung gian
│   └── processed/
│       ├── wine_cleaned_final.csv
│       └── model_ready.*             # Chỉ tạo nếu cần lưu artifact này
├── docs/
│   ├── ROADMAP_W5_W10.md
│   ├── TEAM_WORKFLOW.md
│   ├── PROJECT_STRUCTURE.md
│   ├── data_dictionary.md
│   └── model_card.md                 # Tạo trong tuần 7–9
├── notebooks/
│   ├── 00_data_understanding.ipynb
│   ├── 01_outliers_and_noise.ipynb
│   ├── 02_eda.ipynb
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
│   ├── train.py                      # Train/CV entry point
│   └── evaluate.py                   # Evaluation có kiểm soát
├── tests/
│   ├── test_cleaning.py
│   ├── test_features.py
│   └── test_split.py
├── frontend/                         # Legacy cho đến khi đạt web gate
├── services/                         # Legacy cho đến khi đạt web gate
├── requirements.txt
└── README.md
```

Các file chưa tồn tại trong cây mục tiêu là định hướng triển khai, không phải tính năng hiện có. Chỉ tạo file khi task tương ứng bắt đầu và có owner/reviewer.

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
          preprocessing + feature pipeline
                     │
              ┌──────┴──────┐
              ▼             ▼
       CV/validation     EDA/inference
              │             │
              └──────┬──────┘
                     ▼
              locked final model
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
- Split indices hoặc ID ổn định phải được lưu/tái tạo bằng seed và quy tắc đã khóa.
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

Sau khi model freeze, nhóm chọn một trong hai hướng:

1. Không làm web: giữ legacy ngoài phạm vi và nộp sản phẩm data/model/report.
2. Làm web: thay toàn bộ input schema và prediction flow bằng pipeline Wine Reviews 130k đã khóa.

## 8. Web gate

Chỉ bắt đầu web/API khi đồng thời đạt các điều kiện:

- Cleaning và modeling pipeline chạy end-to-end từ project root.
- Automated tests liên quan đều pass.
- Có model artifact chứa preprocessing và model.
- Báo cáo hoàn thành tối thiểu khoảng 70%.
- Có validation metrics và error analysis.
- Không làm chậm deadline model freeze tuần 9.

Nếu thiếu một điều kiện, ưu tiên tiếp tục phần data/model/report.

## 9. Cách xác định ownership mà không dùng thư mục cá nhân

- Task ID và owner nằm trong [ROADMAP_W5_W10.md](ROADMAP_W5_W10.md).
- Tên branch chứa task ID.
- Pull request ghi owner, reviewer và đầu ra.
- Báo cáo có mục contributors nếu cần ghi đóng góp học thuật.
- Git history dùng để xem thay đổi cụ thể, không dùng vị trí thư mục để suy ra đóng góp.

Cách tổ chức này vẫn ghi nhận rõ công sức từng người nhưng tránh phân mảnh pipeline.
