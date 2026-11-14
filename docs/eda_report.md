# Báo cáo EDA: thông tin sản phẩm và review

Cập nhật theo hướng phân tích dữ liệu là trọng tâm. Mô hình đã huấn luyện và đánh giá test ngày 13/11/2026; EDA không chọn lại mô hình.

- [Báo cáo EDA đầy đủ tự sinh](../outputs/eda/REPORT.md): câu hỏi, hình, bảng, kết quả, hàm ý và giới hạn; mọi phân tích chi tiết dùng train.
- [Câu hỏi → bằng chứng → diễn giải](../outputs/eda/QUESTION_MAP.md).
- [Notebook EDA](../notebooks/03_eda.ipynb): chạy bằng kernel mới sau khi sinh báo cáo thống kê.
- [Thống kê giá–điểm](../outputs/analysis/REPORT.md): Spearman trên trung vị nhóm title train, CI bootstrap và p-value xấp xỉ; khám phá sau EDA.
- [Báo cáo mô hình bổ sung](../outputs/model_report/REPORT.md): metric tính từ dự đoán lưu sẵn.

## Phạm vi

Audit schema/missing dùng cleaned; giá, điểm, metadata và từ vựng dùng train. Validation/test chỉ đọc description trong EDA để audit trùng chuỗi; báo cáo mô hình đọc dự đoán đã có riêng. Bảng train có missing price bằng 0 vì đã chọn mẫu có giá, không phải nguồn đầy đủ.

## Tái lập

```powershell
python src/create_eda_plots.py
python -m src.analyze_associations
```

Dữ liệu gốc, cleaned và split không đổi. Bảng/hình và Markdown được sinh từ cùng kết quả code; không sửa số liệu bằng tay. Từng báo cáo có summary.json ghi checksum, phiên bản và phạm vi. Hệ số thống kê không phải nhân quả, từ phổ biến không phải mức ảnh hưởng, chỉ mô hình kết hợp chưa chứng minh đóng góp riêng của review. Giữ lịch sử holdout từng được quan sát và giới hạn near-duplicate.
