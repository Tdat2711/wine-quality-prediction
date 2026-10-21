# EDA sơ bộ: Phân bố giá và quan hệ giá–điểm review

## Phạm vi và nguồn

Hai hình do Đô thực hiện, được hoàn thiện cách trình bày và tích hợp vào notebook
tiến trình của Khánh. Đây là thống kê mô tả trên toàn mẫu có giá, không phải EDA riêng trên train;
chưa phải kết quả kiểm định hoặc đánh giá mô hình.

- Đầu vào: data/processed/wine_cleaned_final.csv; không chạy lại cleaning ở bước này.
- Toàn bộ dữ liệu sạch: **119.988 bản ghi review**.
- Có giá quan sát: **111.593 bản ghi**; thiếu giá: **8.395 bản ghi**.
- Một dòng là một bản ghi review; cùng tên rượu có thể có nhiều review.
- Không điền giá thiếu và không xóa giá cao để vẽ hình.

Bản notebook cá nhân duy nhất:
[03_do_eda_plots.ipynb](../notebooks/w5_progress_parts/03_do_eda_plots.ipynb).
Bản trình bày:
[02_eda.ipynb](../notebooks/02_eda.ipynb).
Hai notebook dùng chung hàm vẽ trong
[src/create_eda_plots.py](../src/create_eda_plots.py).

## Hình 1 — Phân bố giá

[Ảnh xuất PNG](../outputs/eda_plots/fig1_price_distribution.png).

- Histogram 100 bins trong khung 0–300 USD; trục trái là số bản ghi review.
- KDE được tính trên toàn mẫu có giá, với trục mật độ riêng bên phải.
- Các vạch dọc đánh dấu giá trung vị và trung bình của toàn mẫu.
- Giá nhỏ nhất 4 USD, trung vị 25 USD, trung bình khoảng 35,6 USD, tối đa 2.500 USD.
- Có **310 bản ghi giá trên 300 USD**, khoảng **0,28%** mẫu có giá; chúng vẫn được giữ.
- Chú thích nằm dưới hình, không che các cột hoặc điểm.

Phân bố giá lệch phải. Nhóm dự kiến dùng log1p(price) cho cấu hình chỉ giá theo
giao thức dự án. Đây là lựa chọn biểu diễn đặc trưng, không phải yêu cầu bắt buộc
cho mọi thuật toán chỉ vì biến giá có phân bố lệch.

## Hình 2 — Quan hệ giá và điểm review

[Ảnh xuất PNG](../outputs/eda_plots/fig2_price_vs_points.png).

- Toàn mẫu: 111.593 bản ghi có giá.
- Lấy mẫu tối đa 15.000 bản ghi với seed 42 để giảm chồng lấp; seed này chỉ dùng vẽ hình.
- Trục X là giá USD, khung 0–300; trục Y là điểm review, thang 80–100.
- Màu thể hiện điểm review. Chú thích phân biệt toàn mẫu, số được lấy mẫu và số điểm
  thực sự nằm trong khung; số trong khung được tính lại mỗi lần chạy.
- Không fit đường hồi quy, chạy kiểm định hoặc đọc các file split.

Giá và điểm có xu hướng đồng biến trong biểu đồ, nhưng cùng mức giá vẫn có nhiều
mức điểm khác nhau. Toàn mẫu còn **16 bản ghi giá trên 100 USD nhưng điểm dưới 85**;
không diễn giải xu hướng thành quy luật tuyệt đối.

**Câu hỏi tiếp theo:** metadata như quốc gia, giống nho, vùng và niên vụ có giúp
giảm sai số dự đoán ngoài thông tin giá hay không? Hai hình hiện tại chưa chứng minh
giá trị dự đoán bổ sung này. Cần so sánh mô hình trên cùng mẫu và validation sau khi
split đã chốt.

## Giới hạn

Mẫu có giá có thể khác nhóm thiếu giá; dữ liệu review không đại diện toàn bộ thị trường.
Điểm review phụ thuộc người chấm, không phải thước đo chất lượng khách quan.
Các quốc gia, vùng và giống nho có thể liên quan đồng thời tới cả giá và điểm.
Quan hệ quan sát không chứng minh giá cao gây ra điểm cao.
Split seed 42 đã chốt ngày 21/10/2026; bước tiếp theo chạy lại EDA trên train theo roadmap.

## Chạy lại

Chọn kernel môi trường dự án, Restart Kernel và Run All rồi lưu notebook.
Cài môi trường theo README trước khi chạy. Notebook hỗ trợ project root,
thư mục notebooks và thư mục notebooks/w5_progress_parts.

Lệnh xuất hai PNG hiện có từ project root được giữ nguyên:

~~~powershell
python src/create_eda_plots.py
~~~

Ảnh được tạo lại tại outputs/eda_plots/ với tên fig1_price_distribution.png và
fig2_price_vs_points.png (300 DPI). Có thể chỉ định --input hoặc --output-dir;
khi import module vào notebook, module không tự đọc CSV, ghi ảnh hoặc đổi backend.

Các notebook riêng của Khánh và Dũng được giữ nguyên để ghi nhận đóng góp.
Bối cảnh, giả thuyết và câu chuyện dữ liệu của
[Dương](../notebooks/w5_progress_parts/04_duong_story_stats.ipynb) đã được hiệu chỉnh
theo dữ liệu sạch và tích hợp vào notebook chung. Notebook riêng tính lại mẫu và
thống kê giá từ code; tên nguồn Wine Reviews 130k không được dùng làm cỡ mẫu sạch.
Phần chọn mẫu/split của Đạt đã hoàn thành, seed 42 được chốt ngày 21/10/2026.
Spearman của Dương trên train và thử mô hình dành cho buổi sau. Chưa công bố MAE, RMSE, R² hoặc kết quả
kiểm định trong bản EDA sơ bộ này.
