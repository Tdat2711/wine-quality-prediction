# Roadmap dự án — Tuần 5 đến tuần 10

Buổi thứ Tư tuần 6 là **đánh giá tiến trình**, không phải bảo vệ mô hình cuối. Nhóm dùng **một notebook chung** `notebooks/02_eda.ipynb` làm nguồn minh chứng; theo yêu cầu ngày 21/10/2026, có thêm PowerPoint hỗ trợ trình bày. Mỗi người tự tạo và nộp một notebook phần việc trong `notebooks/w5_progress_parts/`; các file này được giữ để chạy lại và ghi nhận đóng góp. Khánh tạo khung notebook chung từ sớm, tích hợp dần các cell cần trình bày và kiểm tra bản cuối; không làm thay phần phân tích của thành viên khác. Không để nhiều người cùng sửa trực tiếp notebook chung.

Mỗi notebook cá nhân cần nêu mục tiêu, đọc cùng `data/processed/wine_cleaned_final.csv`, chứa code tạo lại bảng/hình, kết quả, 2–3 nhận xét và giới hạn. Không làm sạch dữ liệu lần nữa hoặc chỉ nộp ảnh chụp kết quả. Nếu split chưa được xác nhận, phân tích trên mẫu có giá chỉ là **khám phá sơ bộ**; không chạy kiểm định/hồi quy để công bố metric. Không dùng test set trước bước đánh giá cuối.

## Tuần 5 đến trước buổi đánh giá tiến trình thứ Tư tuần 6

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Chốt câu hỏi hai tầng. Trong `01_khanh_price_tiers.ipynb`, chia các chai có giá thành bốn khoảng theo tứ phân vị; xuất bảng số chai, giá trung vị và `points` trung vị, viết 2–3 nhận xét có số liệu. Tạo khung `02_eda.ipynb`, nhận các notebook cá nhân, tích hợp phần cần trình bày và kiểm tra mạch chung; không làm thay phân tích của người khác. Chốt quy tắc split để Đạt thực hiện. |
| Đạt | Cleaning pipeline và cleaning log đã có, không làm lại. Trong `02_dat_data_split.ipynb`, tóm tắt số chai có/thiếu giá và số chai có nhãn `points` bằng một bảng ngắn; bắt đầu split mẫu có giá theo nhóm `title` chuẩn hóa, ghi số dòng từng tập và kiểm tra không chồng nhóm. Nếu chưa xác nhận kịp, hoàn tất ở tuần 6; không trình bày lại báo cáo cleaning chi tiết. |
| Đô | Trong `03_do_eda_plots.ipynb`, tạo đúng hai hình: phân bố `price` và quan hệ giá–điểm. Mỗi hình có số mẫu, trục/đơn vị và nhận xét để tự trình bày; không làm hình hồi quy hoặc hình của người khác. |
| Dương | Trong `04_duong_story_stats.ipynb`, viết bối cảnh → vấn đề → câu hỏi và giả thuyết về liên hệ giá–điểm; giải thích điểm review không phải chất lượng khách quan. Chỉ khi split đã được xác nhận, có thể kiểm tra Spearman sơ bộ trên train, báo số mẫu, hệ số, p-value và giới hạn diễn giải. |
| Dũng | Trong `05_dung_baseline.ipynb`, giải thích ý nghĩa bốn cấu hình dự kiến. Chỉ khi split đã được xác nhận, có thể fit `DummyRegressor` và `LinearRegression` chỉ dùng `log_price` trên train, so MAE validation trên cùng mẫu; ghi rõ đây là kết quả thử, không phải mô hình cuối. Chuyển khảo sát metadata chi tiết sang tuần 6. |

Năm notebook cá nhân đặt trong `notebooks/w5_progress_parts/`. **Đầu ra bắt buộc trước thứ Tư** là notebook chung có câu hỏi, bảng chọn mẫu, bảng bốn khoảng giá, hai biểu đồ và nhận xét đã kiểm tra. Kiểm định/hồi quy thử chỉ đưa vào nếu split và phép tính đã được kiểm tra trước khi chốt notebook tối thứ Ba; nếu chưa có, ghi rõ “chưa có kết quả”, không ước lượng số liệu. PowerPoint tóm tắt kết quả; mở `02_eda.ipynb` khi cần đối chiếu code và số liệu.

## Tuần 6 — Tiếp tục sau buổi đánh giá tiến trình

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Ghi góp ý của giảng viên và sửa câu hỏi nghiên cứu nếu cần. Đã duyệt bộ split theo nhóm tên rượu, giữ seed 42 ngày 21/10/2026; giữ ghi nhận holdout này từng được thử, không khẳng định test chưa từng được quan sát. Trên train, lập bảng `points` trung vị theo khoảng giá trong 2–3 quốc gia đủ mẫu; không làm lại bảng bốn khoảng giá chung đã nộp. |
| Đạt | Hoàn tất split theo nhóm `title` nếu chưa xong, lưu quy tắc/seed và số dòng từng tập; kiểm tra không chồng nhóm. Tự so sánh `points` trung vị và tỷ lệ các quốc gia phổ biến giữa nhóm có giá và nhóm thiếu giá; nhận xét khả năng mẫu có giá không đại diện toàn bộ dữ liệu. |
| Đô | Sửa hai hình cốt lõi theo góp ý và chạy lại trên train sau khi split đã khóa; thêm một hình so sánh trong nhóm đủ mẫu, không vẽ lại hình của thành viên khác. |
| Dương | Từ thống kê mô tả và góp ý, viết một trang câu chuyện dữ liệu: điều đã quan sát, câu hỏi còn mở và giới hạn. Hoàn tất/kiểm tra kết quả Spearman sơ bộ nếu tuần trước chưa có; tách rõ phát hiện sơ bộ với kiểm định chính thức tuần 8. |
| Dũng | Trên train sau split, lập bảng cho các quốc gia và giống nho phổ biến: số chai, giá trung vị, `points` trung vị; ghi nhóm quá ít mẫu. Hoàn tất/kiểm tra thử nghiệm chỉ giá nếu tuần trước chưa có; không coi kết quả thử là so sánh bốn cấu hình tuần 9. |

## Tuần 7 — Trực quan hóa và phân tích khám phá

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Từ bảng thăm dò tuần 6, mở rộng phần EDA trên train cho các quốc gia đủ mẫu; đối chiếu xu hướng giá–điểm chung với từng quốc gia và giải thích điểm giống/khác, không tạo lại bảng chung tuần 5. |
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
| Khánh | Trên split đã chốt, xây lại `Dummy` và mô hình chỉ giá **chính thức** bằng giao thức chung; thiết lập cách chọn `alpha` bằng GroupKFold chỉ trên train và cùng một grid để Dũng dùng cho các mô hình Ridge còn lại. Xuất dự đoán cùng MAE/RMSE/R² trên validation; không dùng kết quả `LinearRegression` thử tuần 5–6 làm kết quả cuối. |
| Đạt | Viết bước chuẩn bị dữ liệu dùng chung: chọn chai có giá quan sát, xử lý năm thiếu và mã hóa metadata từ train. Viết test kiểm tra split không chồng nhóm chai và không fit preprocessing trên validation/test. |
| Đô | Từ dự đoán validation, tự tạo hai hình điểm thật–điểm dự đoán và phân bố sai số, cùng bảng sai số theo khoảng giá. Viết nhận xét mô hình sai ở nhóm nào. |
| Dương | Nhận dự đoán của Khánh và Dũng, kiểm tra bốn cấu hình dùng cùng các chai validation rồi ghép bảng MAE/RMSE/R². Tính chênh lệch MAE giữa chỉ giá và kết hợp trên cùng mẫu; viết ý nghĩa thực tế và giới hạn của điểm review. |
| Dũng | Dùng split và cách chọn `alpha` do Khánh chốt, cùng bước preprocessing chung của Đạt, để cấu hình và chạy hai mô hình Ridge: chỉ metadata và kết hợp. Xuất dự đoán theo mã dòng và MAE/RMSE/R² trên validation để Dương ghép bảng; chưa mở test cuối và không phải tự xây lại preprocessing. |

## Tuần 10 — Đánh giá cuối và hoàn thiện bài nộp

| Người phụ trách | Nhiệm vụ |
|---|---|
| Khánh | Chốt bốn cấu hình theo validation và kiểm tra lệnh đánh giá trước khi Dũng mở test. Sau khi có metric test, tự tính và giải thích chênh lệch MAE giữa chỉ giá và kết hợp; ghép code, báo cáo và phần trình bày kết quả hai tầng. |
| Đạt | Chạy lại pipeline từ dữ liệu gốc, đối chiếu số dòng, checksum và split/holdout seed 42 đã chốt, kèm lịch sử sử dụng. Viết phần nguồn dữ liệu, cleaning và khả năng tái lập cho báo cáo cuối. |
| Đô | Sau khi có kết quả test hợp lệ, cập nhật hình so sánh điểm thật–dự đoán và sai số theo nhóm. Hoàn thiện hình, chú thích và phần trực quan hóa trong báo cáo. |
| Dương | Viết phần tổng hợp EDA, kiểm định, ý nghĩa của chênh lệch sai số, bias, đạo đức khi diễn giải điểm review và giới hạn. Chuẩn bị lời giải thích “đã có điểm thật thì dự đoán để làm gì?”. |
| Dũng | Sau khi Khánh khóa cấu hình và duyệt lệnh, chạy một đợt đánh giá test cho cả bốn mô hình; xuất bảng MAE/RMSE/R² và dự đoán để nhóm phân tích. Lưu model, cấu hình và lệnh chạy lại cho bài nộp. |
