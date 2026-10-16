# Roadmap dự án — Tuần 5 đến tuần 10

## Tuần 5 đến trước buổi đánh giá tiến trình thứ Tư tuần 6

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Chốt câu hỏi hai tầng. Tự viết code chia các chai có giá thành bốn khoảng theo tứ phân vị; xuất bảng số chai, giá trung vị và `points` trung vị, viết 2–3 nhận xét có số liệu. Tự làm slide và trình bày phần giá–điểm; nhận slide đã làm của từng người để ghép và kiểm tra mạch chung. |
| Đạt | Cleaning pipeline và cleaning log đã có, không làm lại. Từ dữ liệu sạch, lập bảng quy tắc chọn mẫu: số chai có/thiếu giá và số chai có nhãn `points`. Tạo bảng trước/sau cleaning với số dòng, duplicate và hai giá sửa để tự trình bày quyết định xử lý dữ liệu. |
| Đô | Viết code tạo hai hình: phân bố `price` và quan hệ giá–điểm. Đưa hai hình lên slide; mỗi hình ghi số mẫu, trục/đơn vị và một kết luận mà mình tự trình bày. |
| Dương | Viết phần giới thiệu theo bối cảnh → vấn đề → câu hỏi → hướng giải quyết. Tự tính bảng trung bình, trung vị, tứ phân vị của `points` và `price`, tạo một hình phân bố `points`; dùng chúng để trình bày mục tiêu, ý nghĩa thực tế và giới hạn của điểm review. |
| Dũng | Lập bảng ý nghĩa, tỷ lệ thiếu và số nhóm của `price`, `country`, `province`, `variety`, `vintage_year`. Làm một slide giải thích bốn cấu hình dự kiến và tự trình bày; ghi rõ chưa có metric mô hình. |

## Tuần 6 — Tiếp tục sau buổi đánh giá tiến trình

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Ghi góp ý của giảng viên và sửa câu hỏi nghiên cứu nếu cần. Trên các chai có giá quan sát, tạo split/holdout mới theo nhóm tên chai, không dùng lại holdout seed 42 từng chạy thử; công bố số dòng từng tập. Trên train, lập bảng `points` trung vị theo khoảng giá trong 2–3 quốc gia đủ mẫu. |
| Đạt | Dựa trên bảng chọn mẫu tuần 5, tự so sánh `points` trung vị và tỷ lệ các quốc gia phổ biến giữa nhóm có giá với nhóm thiếu giá. Viết nhận xét sơ bộ về khả năng mẫu chỉ có giá không đại diện cho toàn bộ dữ liệu. |
| Đô | Chuyển hai hình giá–điểm đã làm thành code chạy lại; sau khi có split mới, dùng tập train để thêm một hình so sánh trong các nhóm đủ mẫu và sửa hình theo góp ý. |
| Dương | Từ thống kê mô tả và góp ý, viết một trang câu chuyện dữ liệu: điều đã quan sát, câu hỏi còn mở và giới hạn; tách rõ phát hiện sơ bộ với giả thuyết sẽ kiểm định sau. |
| Dũng | Trên tập train sau split, tự lập bảng cho các quốc gia và giống nho phổ biến: số chai, giá trung vị, `points` trung vị. Ghi nhóm nào quá ít mẫu và đề xuất metadata đáng phân tích sâu ở tuần 7. |

## Tuần 7 — Trực quan hóa và phân tích khám phá

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Từ bảng thăm dò tuần 6, viết phần EDA riêng: trên tập train, tính số mẫu và điểm trung vị theo bốn khoảng giá cho các quốc gia đủ mẫu; đối chiếu xu hướng chung với từng quốc gia và giải thích điểm giống/khác. |
| Đạt | Viết script xuất thành phần train/validation/test theo khoảng giá và quốc gia, kèm kiểm tra không trùng nhóm tên chai giữa các tập. Dùng báo cáo này để giải thích mẫu nào được dùng cho EDA và mô hình. |
| Đô | Hoàn thiện hai hình cốt lõi của mình trên tập train về phân bố giá và quan hệ giá–điểm. Rà nhãn, trục/đơn vị và số mẫu của các hình nhóm chọn đưa vào báo cáo; không làm lại hình mà thành viên khác phụ trách. |
| Dương | Viết mạch EDA nối các phân tích của nhóm: dữ liệu gồm những gì, giá liên hệ với điểm ra sao, metadata gợi ra câu hỏi gì. Tách rõ quan sát và giả thuyết, không suy diễn nhân quả. |
| Dũng | Mở rộng bảng metadata tuần 6 trên tập train: so sánh `points` giữa các giống nho đủ mẫu trong cùng khoảng giá, rồi làm 1–2 hình. Ghi rõ nhóm nào quá ít mẫu để tránh diễn giải sai. |

## Tuần 8 — Kiểm định và hoàn thiện câu chuyện dữ liệu

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Trên tập train, tự kiểm tra giả thuyết về mối liên hệ giữa giá và `points`: nêu giả thuyết, chọn thước đo phù hợp, tính kết quả, tạo một hình minh họa đơn giản và viết kết luận kèm độ lớn quan hệ. |
| Đạt | Kiểm định nhận xét sơ bộ từ tuần 6: điểm review của nhóm có giá và nhóm thiếu giá khác nhau đến mức nào. Ghi phép kiểm định, số mẫu, độ lớn chênh lệch, khoảng tin cậy và giới hạn; tự tạo một hình so sánh hai nhóm. Chỉ dùng nhóm có giá thuộc train cho so sánh, không đọc nhãn validation/test để điều chỉnh mô hình. |
| Đô | Chọn phát hiện kiểm định quan trọng nhất của nhóm và tự tạo một hình giải thích phát hiện đó, ghi rõ số mẫu và khoảng tin cậy khi có. Chọn thêm 1–2 hình do Khánh, Đạt hoặc Dương tự làm để chuẩn hóa cho báo cáo; không phải tạo lại toàn bộ hình kiểm định. |
| Dương | Trên tập train, chọn trước hai nhóm metadata đủ mẫu để so sánh điểm review. Nêu giả thuyết, phép kiểm định và giả định; tự tạo một hình so sánh và báo cáo độ lớn khác biệt, khoảng tin cậy, điều không thể suy ra từ kết quả. |
| Dũng | Nhận kết quả kiểm định từ Khánh, Đạt và Dương; lập một bảng chung ghi giả thuyết, số mẫu, phương pháp, độ lớn kết quả và giới hạn. Tạo notebook chạy lại bảng này từ kết quả của từng người và kiểm tra lại ít nhất một phép tính; không phải tự thiết kế cả ba phép kiểm định. |

## Tuần 9 — So sánh mô hình hồi quy hai tầng

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Trên split đã chốt, tự xây `Dummy` và mô hình chỉ giá; thiết lập cách chọn `alpha` bằng GroupKFold chỉ trên train và cùng một grid để Dũng dùng cho các mô hình Ridge còn lại. Xuất dự đoán cùng MAE/RMSE/R² trên validation; kiểm tra cùng mẫu, cùng metric và preprocessing chỉ học từ train. |
| Đạt | Viết bước chuẩn bị dữ liệu dùng chung: chọn chai có giá quan sát, xử lý năm thiếu và mã hóa metadata từ train. Viết test kiểm tra split không chồng nhóm chai và không fit preprocessing trên validation/test. |
| Đô | Từ dự đoán validation, tự tạo hai hình điểm thật–điểm dự đoán và phân bố sai số, cùng bảng sai số theo khoảng giá. Viết nhận xét mô hình sai ở nhóm nào. |
| Dương | Nhận dự đoán của Khánh và Dũng, kiểm tra bốn cấu hình dùng cùng các chai validation rồi ghép bảng MAE/RMSE/R². Tính chênh lệch MAE giữa chỉ giá và kết hợp trên cùng mẫu; viết ý nghĩa thực tế và giới hạn của điểm review. |
| Dũng | Dùng split và cách chọn `alpha` do Khánh chốt, cùng bước preprocessing chung của Đạt, để cấu hình và chạy hai mô hình Ridge: chỉ metadata và kết hợp. Xuất dự đoán theo mã dòng và MAE/RMSE/R² trên validation để Dương ghép bảng; chưa mở test cuối và không phải tự xây lại preprocessing. |

## Tuần 10 — Đánh giá cuối và hoàn thiện bài nộp

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Chốt bốn cấu hình theo validation và kiểm tra lệnh đánh giá trước khi Dũng mở test. Sau khi có metric test, tự tính và giải thích chênh lệch MAE giữa chỉ giá và kết hợp; ghép code, báo cáo và phần trình bày kết quả hai tầng. |
| Đạt | Chạy lại pipeline từ dữ liệu gốc, đối chiếu số dòng, checksum và split/holdout mới. Viết phần nguồn dữ liệu, cleaning và khả năng tái lập cho báo cáo cuối. |
| Đô | Sau khi có kết quả test hợp lệ, cập nhật hình so sánh điểm thật–dự đoán và sai số theo nhóm. Hoàn thiện hình, chú thích và phần trực quan hóa trong báo cáo. |
| Dương | Viết phần tổng hợp EDA, kiểm định, ý nghĩa của chênh lệch sai số, bias, đạo đức khi diễn giải điểm review và giới hạn. Chuẩn bị lời giải thích “đã có điểm thật thì dự đoán để làm gì?”. |
| Dũng | Sau khi Khánh khóa cấu hình và duyệt lệnh, chạy một đợt đánh giá test cho cả bốn mô hình; xuất bảng MAE/RMSE/R² và dự đoán để nhóm phân tích. Lưu model, cấu hình và lệnh chạy lại cho bài nộp. |
