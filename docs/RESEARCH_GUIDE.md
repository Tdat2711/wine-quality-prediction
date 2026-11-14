# Hướng dẫn đọc và hoàn thiện câu chuyện nghiên cứu

## Mục tiêu

Phân tích giá, xuất xứ, giống nho và nội dung review liên hệ với điểm người đánh giá; dùng Ridge kết hợp hiện có để minh họa khả năng ước lượng điểm. Không coi điểm review là phép đo chất lượng khách quan hoặc đưa ra khuyến nghị mua hàng chắc chắn.

## Bốn câu hỏi và bằng chứng

| Câu hỏi | Nơi đọc kết quả | Ý nghĩa và giới hạn |
|---|---|---|
| Giá liên hệ với điểm ra sao? | [EDA](../outputs/eda/REPORT.md), [Spearman](../outputs/analysis/REPORT.md) | Phân biệt xu hướng mô tả, tương quan nhóm và nhân quả; log không được chứng minh tăng hiệu năng |
| Metadata khác nhau thế nào? | Bảng groups và hình 04/07 trong [EDA](../outputs/eda/REPORT.md) | So cả giá, điểm, số mẫu và khoảng tứ phân vị; không xếp hạng chất lượng |
| Review có đặc điểm gì? | Bảng tần suất gốc, bảng lọc bổ sung và độ dài theo điểm trong EDA | Tần suất không phải sentiment hoặc tác động; review ngắn không mặc định vô ích |
| Mô hình còn sai ở đâu? | [Báo cáo đánh giá](../outputs/model_report/REPORT.md) | Đọc baseline, MAE/RMSE, tỷ lệ trong ngưỡng, số mẫu và trường hợp validation |

[Bảng câu hỏi → bằng chứng → phát hiện → quyết định/hàm ý → giới hạn](../outputs/eda/QUESTION_MAP.md) được sinh bằng code cùng EDA. Không phải phát hiện nào cũng dẫn tới thay đổi mô hình.

## Phân biệt ba loại kết quả

1. **Mô tả:** histogram, boxplot, trung vị theo khoảng giá và tần suất từ cho biết dữ liệu train trông như thế nào.
2. **Thống kê khám phá:** Spearman giữa trung vị giá/điểm mỗi nhóm title, p-value hai phía xấp xỉ và CI bootstrap. Được bổ sung sau EDA, không đăng ký trước; nhóm có thể còn phụ thuộc qua winery/người chấm. Không kết luận nhân quả từ p-value.
3. **Dự đoán:** metric từ dự đoán validation/test đã lưu. Ngưỡng ±1/2/3 điểm là cách diễn giải sau đánh giá; không dùng để chọn lại mô hình. R² không phải tỷ lệ dự đoán đúng.

## Trình tự chạy từ artifact hiện có

```powershell
python src/split_data.py
python -m src.cleaning_report
python src/create_eda_plots.py
python -m src.analyze_associations
python -m wine_encoding.src.report_results
python -m wine_encoding.src.explain_features
python -m wine_encoding.src.verify_model
python -m unittest discover -s tests -v
```

Sau đó Restart Kernel/Run All bốn notebook theo thứ tự 00–03, hoặc chạy `python scripts/verify_notebooks.py` bằng môi trường dự án. Notebook EDA đọc báo cáo thống kê đã tạo và kiểm tra checksum train.

Các lệnh báo cáo không tạo lại model. Thiếu dữ liệu/artifact thì dừng và báo đường dẫn; không tự huấn luyện. Luồng prepare/train là luồng tạo thí nghiệm độc lập, có thể ghi lại artifact, không cần cho đợt hoàn thiện này.

## Cách dùng báo cáo

- Bảng CSV là nguồn số liệu; Markdown và hình sinh từ cùng bảng.
- Mỗi thư mục báo cáo có `summary.json` ghi checksum đầu vào, phiên bản, seed và phạm vi. Từ điển dữ liệu giải thích các tên cột lịch sử.
- Báo cáo cleaning thuộc audit toàn mẫu lịch sử; phân tích chi tiết mới chỉ dùng train. Dòng thiếu giá được giữ trong cleaned, không thuộc mẫu mô hình hiện tại.
- [Báo cáo validation](model_validation_report.md) lưu trạng thái ngày 09/11/2026; [báo cáo test](model_test_report.md) lưu kết quả ngày 13/11/2026. Chú thích lịch sử không được hiểu là trạng thái hiện tại.
- Holdout từng được quan sát; audit trùng chính xác không phát hiện near-duplicate. Giữ công bố này khi thuyết trình.

## Trách nhiệm nội dung

TV1 tổng hợp câu hỏi, kết luận và trạng thái tài liệu; TV2 kiểm chứng cleaning; TV3 EDA và thống kê; TV4 giải thích đặc trưng và demo; TV5 sai số và tái lập. Mỗi người viết phần chuyên môn của mình. TV2–TV4 kiểm tra ranh giới cleaning/preprocessing; TV3–TV5 đối chiếu số liệu và diễn giải.

Sau khi chạy notebook và báo cáo, dùng `python scripts/verify_reports.py` để kiểm tra checksum bảo vệ, provenance báo cáo, trạng thái notebook và liên kết Markdown cục bộ. Kết quả lưu trong `outputs/quality/verification.json`.
