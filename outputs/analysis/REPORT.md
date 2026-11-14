# Giá và điểm — phân tích thống kê khám phá

**Câu hỏi:** giá và điểm có quan hệ đơn điệu ở cấp nhóm title trên train không?

Mỗi title chuẩn hóa đóng góp một cặp trung vị giá–điểm; đây không phải định danh chai rượu duy nhất.

| groups | bootstrap_repetitions | seed | status | rho | p_value_approx | ci_low | ci_high | valid_bootstrap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 77437 | 2000 | 42 | ok | 0.6157651448603431 | 0.0 | 0.6110206411877455 | 0.6202161585632493 | 2000 |

Spearman hai phía; p-value xấp xỉ, ngưỡng tham khảo 0,05. Khoảng tin cậy percentile 95% từ 2000 bootstrap nhóm title, seed 42. Giá và log giá giữ cùng thứ hạng, không kiểm định hai lần.

**Diễn giải:** rho = 0.6158; khoảng tin cậy [0.6110, 0.6202]. Độ lớn hệ số mô tả quan hệ đơn điệu, không phải mức tăng điểm khi tăng giá.

**Giới hạn:** phân tích sau EDA, không phải giả thuyết đăng ký trước; chưa kiểm soát quốc gia, giống nho, winery hoặc người chấm. Các nhóm có thể còn phụ thuộc, làm p-value/CI lạc quan. P-value rất nhỏ có thể do cỡ mẫu lớn; giá trị 0 trong file là giới hạn số thực, không phải xác suất đúng bằng 0. Chỉ đại diện các review train có giá quan sát; không suy luận nhân quả.

**Tái lập:** `python -m src.analyze_associations`; số liệu lấy từ `price_points_spearman.csv`; phiên bản, checksum và phạm vi tại `summary.json`.
