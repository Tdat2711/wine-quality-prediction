# Demo ước lượng điểm review

## Đầu vào và ý nghĩa

Mô hình cần sáu cột `price`, `vintage_year`, `country`, `province`, `variety`, `description`. Không cần `points`, title hoặc người chấm. Review là lời đánh giá đã tồn tại; kết quả là ước lượng điểm người đánh giá, không phải chất lượng khách quan trước review.

Xem [CSV ví dụ](../wine_encoding/examples/new_wines.csv) và [minh họa đặc trưng](../outputs/feature_examples/REPORT.md).

## Chạy bằng pipeline đã lưu

Từ thư mục gốc, dùng môi trường Python của dự án:

```powershell
python -m wine_encoding.src.predict --input wine_encoding/examples/new_wines.csv --output outputs/demo/new_predictions.csv
```

Lệnh đọc pipeline hiện có và xuất một file mới ngoài thư mục artifact gốc; không huấn luyện hoặc đánh giá lại test. Thiếu model thì xem hướng dẫn artifact trong README; không chạy prepare/train chỉ để xem báo cáo.

## Đọc kết quả

- Thứ tự dòng và cột đầu vào được giữ; thêm `points_predicted` và `prediction_outside_train_target_range`.
- Giá/năm thiếu được điền bằng trung vị train; giá không dương, chữ trong cột số hoặc số vô hạn bị từ chối.
- Category mới vào nhóm hiếm nếu nhóm đó đã học trên train; nếu không, khối one-hot tương ứng bằng 0. Đây không phải hiểu biết mới về category.
- Review thiếu/rỗng thành vector văn bản 0; mô hình vẫn có thể dựa vào metadata nhưng không có đánh giá riêng bảo đảm hiệu năng trong trường hợp này.
- Cờ ngoài khoảng điểm train là thông tin cảnh báo, không tự cắt hoặc làm tròn dự đoán. Ví dụ trình bày có thể làm tròn để đọc, còn metric dùng số gốc.
- File ví dụ không có nhãn thật, do đó không tính accuracy/MAE từ demo. Đọc [báo cáo đánh giá](../outputs/model_report/REPORT.md) cho số liệu kiểm chứng.

## Giới hạn

Dataset không đại diện toàn bộ thị trường; hiệu năng tổng thể không bảo đảm cho mỗi quốc gia hoặc review mới. Chưa có thí nghiệm metadata-only để đo lợi ích riêng của review. Không suy luận tác động nhân quả từ hệ số Ridge.
