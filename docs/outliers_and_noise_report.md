# Báo cáo chuyên sâu: Phát hiện và Xử lý Outlier & Noise — Wine Reviews 130k

**Người phụ trách**: Thành viên nhóm phụ trách Outlier & Noise  
**Tập dữ liệu**: `data/raw/winemag-data-130k-v2.csv` (129.971 dòng × 14 cột)  
**Tài liệu liên quan**: `docs/data_audit.md`, `docs/cleaning_log.csv`, `notebooks/02_outliers_and_noise.ipynb`

---

## 1. Mục tiêu và Phạm vi

Báo cáo này tập trung vào hai vấn đề cốt lõi trong giai đoạn Làm sạch Dữ liệu (Data Cleaning):
1. **Outliers (Giá trị ngoại lai)**: Nhận diện, phân loại giữa ngoại lai tự nhiên hợp lệ (Natural Outliers) và ngoại lai do lỗi nhập liệu (Artificial Outliers); xây dựng chiến lược xử lý không làm mất mát thông tin quan trọng.
2. **Noise (Dữ liệu nhiễu)**: Phát hiện và khử các thành phần dữ liệu không mang giá trị thông tin, ký tự lỗi bảng mã (encoding artifacts), văn bản rác và lỗi logic trích xuất metadata (Vintage Year).

---

## 2. Phân tích Chi tiết Outliers (Giá trị ngoại lai)

### 2.1. Cột `price` (Biến liên tục có độ lệch phải lớn)

#### Thống kê định lượng:
* **Số dòng hợp lệ**: 120.975 dòng (8.996 dòng missing).
* **Min**: 4.0 USD | **Max**: 3.300.0 USD
* **Q1 (25%)**: 17.0 USD | **Median (50%)**: 25.0 USD | **Q3 (75%)**: 42.0 USD | **Mean**: 35.36 USD | **Std**: 41.02 USD
* **Khoảng tứ phân vị (IQR)**: $IQR = Q3 - Q1 = 25.0$ USD

#### Phát hiện theo quy tắc Tukey Boxplot:
* **Ngoại lai nhẹ (*Mild Outliers* > Q3 + 1.5 × IQR = 79.5 USD)**:
  * Số lượng: **7.241 dòng** (~5,99% số chai có giá).
* **Ngoại lai cực đoan (*Extreme Outliers* > Q3 + 3.0 × IQR = 117.0 USD)**:
  * Số lượng: **2.676 dòng** (~2,21%).
* **Phân khúc giá siêu cao**:
  * Giá > 500 USD: **91 chai**
  * Giá > 1.000 USD: **14 chai**

#### Phân loại và Đánh giá bản chất:

##### A. Nhóm Outlier tự nhiên hợp lệ (Natural / Domain Outliers)
Đối chiếu danh sách các chai có giá > 1.000 USD với kiến thức chuyên ngành rượu vang (Domain Knowledge):
* Dòng 98380: `Domaine du Comte Liger-Belair 2010 La Romanée` (2.500 USD, 96 điểm) — Dòng Grand Cru độc quyền cực kỳ đắt giá tại Burgundy (Pháp).
* Dòng 15840: `Château Pétrus 2014 Pomerol` (2.500 USD, 96 điểm) & Dòng 65352 (2.000 USD, 97 điểm) — Vang huyền thoại đắt đỏ nhất vùng Bordeaux.
* Dòng 1558: `Château Margaux 2009 Margaux` (1.900 USD, 98 điểm).
* Dòng 111755: `Château Cheval Blanc 2010 Saint-Émilion` (1.500 USD, 100 điểm tuyệt đối).
* Dòng 111753: `Château Lafite Rothschild 2010 Pauillac` (1.500 USD, 100 điểm tuyệt đối).

> **Kết luận**: Các mức giá từ vài trăm đến hàng ngàn USD phản ánh đúng phân khúc rượu vang xa xỉ (Luxury Segment). Việc xóa bỏ các dòng này một cách máy móc theo ngưỡng IQR ($> 79.5\$$) sẽ xóa mất hơn 7.200 chai rượu và làm mất đi toàn bộ đặc trưng phân khúc cao cấp của thị trường. **Bắt buộc phải giữ lại**.

##### B. Nhóm Outlier do lỗi nhập liệu (Artificial Outliers / Data Entry Errors)
* **Trường hợp 1 (Dòng 120391)**: `Blair 2013 Roger Rose Vineyard Chardonnay (Arroyo Seco)`
  * Cột `price` ghi nhận: **2.013.0 USD** (trong khi điểm số là 91).
  * Niên vụ trong tên chai: **2013**.
  * **Nguyên nhân**: Người nhập liệu đã gõ nhầm năm sản xuất `2013` vào ô giá! Trên thực tế, các chai Chardonnay dòng Roger Rose Vineyard của hãng Blair tại California chỉ có giá niêm yết từ $35 – $45 USD.
  * **Hành động**: Hiệu chỉnh giá về giá thực tế (~35 USD) hoặc giá trung vị của hãng Blair.
* **Trường hợp 2 (Dòng 80290)**: `Château les Ormes Sorbet 2013 Médoc`
  * Cột `price` ghi nhận: **3.300.0 USD** (Chai đắt nhất toàn bộ dataset, điểm đánh giá chỉ đạt 88 điểm).
  * Phân hạng: Đây là dòng Cru Bourgeois của vùng Médoc (Bordeaux). Các chai khác cùng hãng này trong dataset (dòng 93726 điểm 87, dòng 102412 điểm 86) đều là vang phổ thông với giá thị trường dao động $30 – $35 USD.
  * **Nguyên nhân**: Lỗi định dạng dấu chấm thập phân ($33.00 \rightarrow 3300$) hoặc gõ thừa hai chữ số 0.
  * **Hành động**: Hiệu chỉnh giá về 33.0 USD.

---

### 2.2. Cột `points` (Điểm đánh giá)
* Dữ liệu phân phối nghiêm ngặt từ 80 đến 100, không có giá trị ngoài miền xác định.
* Phân phối hình chuông tiệm cận chuẩn (Mean = 88.45, Std = 3.04).
* Có 19 chai đạt điểm tối đa 100 và 397 chai điểm 80. Cả hai nhóm đều là điểm hợp lệ do các chuyên gia thẩm định rượu của Wine Enthusiast chấm.

---

### 2.3. Outlier Đa biến (Bivariate Outliers: `points` vs `price`)
Khi phân tích tương quan giữa Giá và Điểm số:
1. **Giá cao nhưng điểm thấp** (Giá $\ge 100$ USD nhưng điểm $\le 83$): Có **7 chai**.
   * Dòng 74798: `Marqués de Murrieta 1978 Castillo Ygay Gran Reserva Especial` (225 USD, 83 điểm).
   * Dòng 23910: `Chateau Margene 2009 Beau Melange Red` (150 USD, 82 điểm).
   * Dòng 11369: `Espectacle 2010 René Isabelle Christopher...` (130 USD, 81 điểm).
   * *Đánh giá*: Đây là những chai vang lâu năm hoặc đắt tiền nhưng hương vị không được lòng chuyên gia, phản ánh sự đa dạng cảm quan, không phải lỗi kỹ thuật.
2. **Giá siêu rẻ nhưng điểm rất cao** (Giá $\le 15$ USD nhưng điểm $\ge 94$): Có **2 chai**.
   * Dòng 19136: `Osborne NV Pedro Ximenez 1827 Sweet Sherry` (14 USD, 94 điểm).
   * Dòng 23974: `Quinta dos Murças 2011 Assobio Red` (13 USD, 94 điểm).
   * *Đánh giá*: Đây là các ứng viên tiêu biểu cho nhãn "Best Buy" (rượu ngon vượt trội so với tầm giá).

---

## 3. Phân tích Chi tiết Noise (Dữ liệu nhiễu)

### 3.1. Nhiễu Văn bản (Text Noise)
* **Ký tự thực thể HTML (HTML Entities)**: Phát hiện 7 dòng chứa các chuỗi như `&amp;`, `&#\d+;`. Cần unescape về ký tự gốc.
* **Khoảng trắng không ngắt (Non-breaking space `\xa0`)**: Phát hiện 2 dòng trong `description` và 9.532 dòng trong `taster_twitter_handle`. Cần thay thế bằng dấu cách thông thường và `strip()`.
* **Đánh giá siêu ngắn / Rác thông tin (Non-informative reviews)**: Có 39 bài đánh giá dưới 10 từ.
  * Điển hình (Dòng 9483): `Imported by Bluewater Wine Company.` (5 từ). Đây là thông tin đơn vị nhập khẩu bị dính vào cột nhận xét hương vị, hoàn toàn không có giá trị phân tích cảm quan cho các mô hình NLP.
  * *Hành động*: Tạo cờ `is_non_informative_review` (True/False) để bộ lọc NLP có thể loại bỏ khi trích xuất đặc trưng từ bài viết.
* **Trùng lặp nội dung mô tả giữa các chai khác nhau**: Có 72 dòng chia sẻ câu mô tả giống hệt nhau dù tên chai khác nhau (do sao chép đánh giá chung cho một series sản phẩm).

### 3.2. Nhiễu logic trích xuất Niên vụ (Vintage Year Noise trong `title`)
* Khi dùng biểu thức chính quy (Regex) trích xuất năm 4 chữ số từ `title`:
  * Xuất hiện 173 chai có năm < 1980, thậm chí từ thế kỷ 19 (1872, 1887, 1898...).
  * **Phát hiện**: Dòng 339 `Cavas Hill NV 1887 Rosado Sparkling` (1887 là năm thành lập nhà làm vang Cavas Hill, không phải năm sản xuất); Dòng 2135 `Codorníu NV Reserva Cuvée Barcelona 1872` (1872 là năm sáng lập). Rượu thực chất là loại **NV** (*Non-Vintage* - vang không niên vụ).
  * **Hành động**: Xây dựng thuật toán trích xuất có kiểm tra cờ `NV` / `Non-Vintage`. Nếu là vang NV thì gán `vintage_year = NaN` hoặc `'NV'`.

---

## 4. Chiến lược và Giải pháp đề xuất cho Nhóm

### Cho Phân tích Khám phá (EDA):
1. **Sửa 2 điểm lỗi nhập liệu cụ thể**:
   * Dòng 120391 (Blair 2013): Sửa `price = 35.0`.
   * Dòng 80290 (Château les Ormes Sorbet 2013): Sửa `price = 33.0`.
2. **Giữ nguyên toàn bộ các chai giá cao hợp lệ** để không làm sai lệch bức tranh toàn cảnh về phân khúc rượu vang thế giới.

### Cho Huấn luyện Mô hình Machine Learning (ML):
1. **Phép biến đổi Log Transform**:
   Áp dụng công thức:
   $$\text{log\_price} = \ln(\text{price} + 1)$$
   * Giúp kéo đuôi phân phối lệch phải (skewness từ $18.0$ giảm xuống chỉ còn khoảng $0.6$), đưa biến giá về phân phối gần chuẩn.
   * Giảm thiểu hoàn toàn tác động tiêu cực của các giá trị ngoại lai cực đoan lên các mô hình hồi quy (Linear Regression, Ridge, Neural Networks) mà không cần phải vứt bỏ bất kỳ dòng dữ liệu nào.
2. **Đối với mô hình Cây quyết định (Random Forest, Gradient Boosting, XGBoost)**:
   * Các thuật toán này phân chia ngưỡng (split) theo thứ tự giá trị nên vốn dĩ có tính đề kháng tự nhiên rất cao với outlier đơn biến.
