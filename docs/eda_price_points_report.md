# Báo Cáo EDA: Phân Tích Phân Bố Giá & Mối Quan Hệ Giá – Điểm

Tài liệu này ghi lại chi tiết quá trình đọc dữ liệu định hướng từ các tài liệu/hình ảnh dự án, phương pháp luận thực hiện, mã nguồn trực quan hóa và các kết luận thống kê rút ra từ 2 biểu đồ EDA chính: **Phân bố `price`** và **Quan hệ `price` – `points`**.

---

## 1. Bối Cảnh Và Định Hướng Đề Tài (Từ Tài Liệu & Ảnh Yêu Cầu)

Theo định hướng nghiên cứu mới của dự án **Wine Quality Prediction** (từ tập dữ liệu Wine Reviews 130k):
- **Mục tiêu cốt lõi**: Khảo sát xem *giá (`price`) giải thích điểm review (`points`) được đến đâu*, và *các trường thông tin sản phẩm (metadata: quốc gia, giống nho, niên vụ, vùng sản xuất...) có bổ sung giá trị dự đoán vượt ngoài giá hay không*.
- **Cách tiếp cận câu chuyện (Storytelling qua biểu đồ)**:
  1. Biểu đồ phân bố giá: Hiểu đặc tính dữ liệu giá, mức độ lệch và định hướng tiền xử lý (vd: log transform).
  2. Biểu đồ giá – điểm: Đánh giá mối quan hệ thực tế giữa giá và điểm. Liệu giá cao có chắc chắn điểm cao? Giá đơn thuần có đủ để làm tính năng dự đoán duy nhất không?
- **Nguyên tắc xử lý dữ liệu sạch**:
  - Dữ liệu sau pipeline làm sạch có tổng cộng **119,988** dòng.
  - Trong đó có **8,395** dòng bị thiếu giá (`price_was_missing == True`). Theo quy tắc mới, không tự ý điền giá trung vị/trung bình cho các mẫu thiếu giá để tránh làm sai lệch quan hệ tự nhiên.
  - Phân tích EDA cho các quan hệ liên quan đến giá được thực hiện trên tập mẫu quan sát thực tế: **$N = 111,593$** mẫu.

---

## 2. Chi Tiết Thực Hiện & Phương Pháp Trực Quan Hóa

Mã nguồn thực thi được đặt tại file [`src/create_eda_plots.py`](../src/create_eda_plots.py), chỉ tập trung tạo 2 hình ảnh độc lập độ nét cao (300 DPI) lưu tại thư mục [`outputs/eda_plots/`](../outputs/eda_plots/):

### 2.1. Hình 1: Phân bố `price` (`fig1_price_distribution.png`)
- **Vị trí file**: `outputs/eda_plots/fig1_price_distribution.png`
- **Phương pháp trực quan**:
  - Biểu đồ phân bố tần suất (**Histogram**) với 100 bins trong khoảng giá 0–300 USD.
  - Đường ước lượng mật độ hạt nhân (**KDE - Kernel Density Estimation**) để nhìn rõ dáng phân bố liên tục.
  - Vạch mốc giá trị **Trung vị (Median)** và **Trung bình (Mean)**.
- **Thông số kỹ thuật & Đơn vị**:
  - Số lượng mẫu phân tích: $N = 111,593$ mẫu (loại trừ $8,395$ mẫu thiếu giá).
  - Trục hoành ($X$): Giá rượu (Đơn vị: USD, giới hạn hiển thị 0 – 300 USD để trực quan hóa rõ vùng mật độ cao).
  - Trục tung ($Y$): Số lượng mẫu rượu quan sát (Đơn vị: Chai).
- **Thống kê cơ bản**:
  - Giá trị nhỏ nhất: $4 USD.
  - Giá trị lớn nhất: $2,500 USD.
  - Trung vị (Median): **$25 USD**.
  - Trung bình (Mean): **$35.6 USD**.
- **Kết luận rút ra**:
  > Phân bố giá của bộ dữ liệu bị **lệch phải rất mạnh (right-skewed)**. Phần lớn rượu vang tập trung ở phân khúc phổ thông ($\le 25\text{ USD}$), trong khi một lượng nhỏ rượu cao cấp có giá từ vài trăm đến hàng ngàn USD kéo giá trị trung bình lên $35.6\text{ USD}$.
  > 
  > **Khuyến nghị kỹ thuật**: Không nên đưa biến `price` trực tiếp ở thang đo tuyến tính vào các thuật toán hồi quy vì các giá trị ngoại lai lớn sẽ gây méo trọng số. Cần áp dụng phép biến đổi logarit: $\text{log}(1 + \text{price})$ hoặc phân khúc giá thành các bin hạng mục.

---

### 2.2. Hình 2: Quan hệ Giá – Điểm (`fig2_price_vs_points.png`)
- **Vị trí file**: `outputs/eda_plots/fig2_price_vs_points.png`
- **Phương pháp trực quan**:
  - Biểu đồ phân tán (**Scatter plot**) thể hiện phân bố đồng thời giữa `price` và `points`. Để tránh hiện tượng chen chúc/chồng lấn điểm (overplotting), biểu đồ lấy mẫu ngẫu nhiên $15,000$ điểm đại diện với độ trong suốt $\alpha = 0.35$ và dải màu theo thang điểm.
  - Không vẽ đường hồi quy/kiểm định mô hình để giữ đúng tính chất phân tích khám phá mô tả ban đầu (EDA).
- **Thông số kỹ thuật & Đơn vị**:
  - Số lượng mẫu: $N = 111,593$ mẫu.
  - Trục hoành ($X$): Giá rượu (Đơn vị: USD, từ 0 đến 300 USD).
  - Trục tung ($Y$): Điểm đánh giá chất lượng của chuyên gia (Đơn vị: Points, dải điểm chuẩn của Wine Enthusiast từ 80 đến 100 điểm).
- **Kết luận rút ra**:
  > 1. Có xu hướng đồng biến: Rượu giá cao hầu như không có điểm thấp (< 85).
  > 2. Tuy nhiên, **độ phân tán là rất lớn**: Ở cùng một mức giá (ví dụ $20–$50 USD), điểm số dao động từ 80 đến tận 95+ điểm.
  > 3. **Ý nghĩa cốt lõi cho đề tài**: *Giá tiền một mình nó CHƯA ĐỦ để giải thích điểm review của một chai rượu*. Kết quả này đặt nền móng lý giải vì sao nhóm nghiên cứu cần bước tiếp theo: đưa thêm **metadata** (quốc gia, giống nho, vùng trồng nho, niên vụ) để kiểm chứng liệu thông tin sản phẩm có giúp giải thích phần chênh lệch điểm số này hay không.

---

## 3. Cấu Trúc Các Tệp Tin Liên Quan Đã Được Cập Nhật

Cấu trúc lưu trữ hiện tại như sau:

```text
wine-quality-prediction/
├── docs/
│   ├── eda_price_points_report.md          <-- [File này] Báo cáo chi tiết phương pháp & kết luận
│   └── ...
├── notebooks/
│   ├── 03_do_eda_plots.ipynb               <-- Notebook EDA chính của thành viên Đô
│   └── w5_progress_parts/
│       └── 03_do_eda_plots.ipynb           <-- Bản sao trong thư mục phần việc tuần 5
├── outputs/
│   └── eda_plots/                          <-- Thư mục chứa 2 ảnh xuất ra (300 DPI)
│       ├── fig1_price_distribution.png
│       └── fig2_price_vs_points.png
└── src/
    └── create_eda_plots.py                 <-- Script Python tạo 2 hình
```

---

## 4. Hướng Dẫn Chạy Lại Script

Nếu có cập nhật dữ liệu sạch mới trong tương lai và muốn vẽ lại 2 biểu đồ, chạy lệnh:

```bash
# Đứng tại thư mục wine-quality-prediction:
python src/create_eda_plots.py
```
Hai hình ảnh sẽ tự động được làm mới tại `outputs/eda_plots/`.
