# Báo cáo EDA: thông tin sản phẩm và review

Notebook chính: [03_eda.ipynb](../notebooks/03_eda.ipynb). Logic và lệnh tạo bảng/hình: [create_eda_plots.py](../src/create_eda_plots.py).

## Phạm vi và phương pháp

Audit schema/missing dùng 119.988 review cleaned, trong đó 111.593 có giá và 8.395 thiếu giá. Mọi thống kê chi tiết về điểm, giá, metadata và nội dung review dùng **78.106 bản ghi train**. Không fit mô hình hoặc TF-IDF; chưa chạy kiểm định chính thức. Holdout chỉ được đọc cột review để audit trùng văn bản.

## Quan sát trên train

- Điểm trung bình 88,42, độ lệch chuẩn 3,10, phạm vi 80–100.
- Giá trung vị 25 USD, trung bình 35,66 USD, tối đa 2.500 USD. Giữ toàn đuôi giá cao; hình giá gốc và log1p dùng cùng mẫu.
- Các khoảng giá theo tứ phân vị train: đến 17 USD, trên 17–25, trên 25–42 và trên 42 USD. Điểm trung vị tương ứng 86, 88, 89, 91. Giá bằng mốc được xếp vào khoảng kết thúc ở mốc đó; số mẫu không bắt buộc bằng nhau vì nhiều giá bằng nhau.
- Review dài trung vị 40 từ; 29 review dưới 10 từ; không có review trống trên train. Cờ review ít thông tin không đồng nghĩa mọi review ngắn đều vô ích.
- Quốc gia/vùng/giống nho có số mẫu khác nhau. Bảng lưu mọi nhóm và số giá thiếu; boxplot chỉ so sánh tối đa 10 nhóm đông nhất đạt 100 dòng, không dùng nhãn placeholder.
- Tần suất unigram/bigram dùng CountVectorizer trên train, giữ stopword và từ phủ định. Từ chức năng phổ biến có thể chiếm đầu bảng; không diễn giải thành từ khen/chê hoặc ảnh hưởng đến điểm.

## Bảng và hình

| Nội dung | Bảng | Hình |
|---|---|---|
| Audit | [Missing](../outputs/eda/tables/audit_missing.csv), [mẫu](../outputs/eda/tables/sample_counts.csv) | — |
| Điểm | [Thống kê số](../outputs/eda/tables/numeric_summary.csv) | [Phân bố điểm](../outputs/eda/figures/01_points_distribution.png) |
| Giá | [Khoảng giá](../outputs/eda/tables/price_tiers.csv) | [Phân bố giá](../outputs/eda/figures/02_price_distribution.png), [giá–điểm](../outputs/eda/figures/03_price_points.png) |
| Quốc gia | [Bảng nhóm](../outputs/eda/tables/groups_country.csv) | [Boxplot](../outputs/eda/figures/04_country_points.png) |
| Vùng | [Bảng nhóm](../outputs/eda/tables/groups_province.csv) | [Boxplot](../outputs/eda/figures/04_province_points.png) |
| Giống nho | [Bảng nhóm](../outputs/eda/tables/groups_variety.csv) | [Boxplot](../outputs/eda/figures/04_variety_points.png) |
| Review | [Tóm tắt](../outputs/eda/tables/review_summary.csv) | [Độ dài](../outputs/eda/figures/05_review_length.png) |
| Từ/cụm từ | [Unigram](../outputs/eda/tables/unigrams.csv), [bigram](../outputs/eda/tables/bigrams.csv) | [Unigram](../outputs/eda/figures/06_unigrams.png), [bigram](../outputs/eda/figures/06_bigrams.png) |
| Trùng review | [Giao review](../outputs/eda/tables/review_overlap.csv) | — |

Scatter chỉ hiển thị tối đa 15.000 bản ghi lấy mẫu seed 42 trên trục giá log, không cắt mất đuôi giá cao; bảng thống kê dùng toàn train. Số giá thiếu trong các bảng nhóm train bằng 0 vì train đã chọn mẫu có giá, không phải bằng chứng dữ liệu nguồn đầy đủ.

## Giới hạn và bước tiếp theo

Xu hướng giữa các khoảng giá không chứng minh nhân quả. Khác biệt nhóm chưa được kiểm định, có thể gắn với giá, người chấm hoặc cơ chế tuyển chọn review. Không coi bảng điểm là xếp hạng chất lượng hoặc khuyến nghị mua chắc chắn.

Review trùng chuẩn hóa giữa train–validation là 6 chuỗi, train–test 5, validation–test 1; cần thống nhất xử lý trước modeling. Không thay split trong EDA. EDA trước đây đã xem toàn mẫu và holdout seed 42 từng được thử; giữ lịch sử này khi diễn giải test về sau.

Bước tiếp theo là kiểm định theo giả thuyết đã chốt và triển khai mô hình kết hợp: metadata + TF-IDF → Ridge. Preprocessing chỉ fit trên train; CV theo nhóm, validation để chốt cấu hình và test đánh giá cuối. Hiện chưa có MAE/RMSE/R² hay bằng chứng lợi ích dự đoán tăng thêm của review.

## Chạy lại

```powershell
python src/create_eda_plots.py
```

Hoặc Restart Kernel và Run All notebook EDA. Mọi bảng/hình ghi vào `outputs/eda/`, không sửa dữ liệu gốc hoặc split. Có thể dùng `--output-dir` để xuất vào thư mục khác.
