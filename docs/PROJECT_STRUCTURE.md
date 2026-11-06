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
| `tests/` | Kiểm tra cleaning, split, lựa chọn mẫu và EDA |

## Luồng chạy hiện có

1. `python src/pipeline.py`: raw → interim → cleaned, kèm validation.
2. `python src/split_data.py`: tái tạo split trong bộ nhớ, so sánh file hiện có; không ghi đè.
3. `python src/split_data.py --write`: chỉ tạo split chưa tồn tại, từ chối nếu file đã có không khớp.
4. `python src/create_eda_plots.py`: cleaned dùng cho audit, train dùng cho phân tích chi tiết; review holdout chỉ dùng audit trùng văn bản.
5. Mở notebook theo thứ tự; notebook outlier giải thích các quyết định cleaning, không phải bước xử lý bổ sung ngoài pipeline.
6. `python -m unittest discover -s tests -v`: kiểm tra các quy tắc đang triển khai.

Logic split đã được chuyển từ notebook phần việc sang module chung; notebook mới chỉ kiểm tra, không xuất lại CSV. Các nội dung bảng khoảng giá, hình giá–điểm, bối cảnh và chuẩn bị mô hình được tích hợp trong notebook chức năng và README.

## Giai đoạn mô hình dự kiến

Giá và niên vụ → xử lý số; quốc gia/vùng/giống nho → one-hot; review → TF-IDF unigram/bigram. Ghép thành ma trận đưa vào Ridge để dự đoán `points`. Mọi bộ xử lý học từ dữ liệu chỉ fit trên train.

Chưa có module huấn luyện, đánh giá, dự đoán, model artifact hay metric. Chỉ thêm các thành phần này khi triển khai thực tế; không tạo file rỗng. Khi có, pipeline lưu phải bao gồm cả preprocessing và Ridge; output đánh giá phải có mã bản ghi, điểm thật/dự đoán và split sử dụng. CV theo nhóm trên train, validation để khóa cấu hình, test đánh giá cuối.

Giữ lịch sử holdout và báo cáo review trùng. Không thay split hoặc tuning theo test để chọn kết quả thuận lợi. Không sửa dữ liệu raw hoặc chép bản dữ liệu/model riêng theo người thực hiện.
