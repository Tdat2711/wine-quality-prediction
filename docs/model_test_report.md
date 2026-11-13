# Kết quả đánh giá cuối trên test

Ngày đánh giá: **13/11/2026**. Dùng pipeline metadata + TF-IDF review → Ridge đã lưu, **alpha = 1**, fit trên train. Chỉ load và dự đoán; không fit lại, không tuning, không thay đổi preprocessing hoặc split.

## Kết quả

| Mô hình / mẫu | n | MAE | RMSE | R² |
|---|---:|---:|---:|---:|
| Baseline trung bình train — test | 16.742 | 2,531205 | 3,093160 | -0,000004 |
| Ridge — test | 16.742 | 1,208998 | 1,542601 | 0,751284 |
| Baseline — test không trùng review train | 16.737 | 2,531279 | 3,093268 | -0,000004 |
| Ridge — test không trùng review train | 16.737 | 1,208922 | 1,542574 | 0,751310 |
| Ridge — validation, đối chiếu lần chạy trước | 16.745 | 1,203588 | 1,532724 | 0,752696 |

MAE test giảm **52,24%** so với baseline trung bình train. MAE test cao hơn validation khoảng **0,0054 điểm**; RMSE cao hơn khoảng **0,0099 điểm**. Kết quả gần nhau trên hai tập, nhưng không phải bằng chứng mô hình sẽ đạt cùng hiệu năng trên dữ liệu triển khai khác phân bố. R² không phải tỷ lệ dự đoán đúng.

Có **5 dòng test trùng review chuẩn hóa với train**; metric phụ sau khi bỏ các dòng này gần như không đổi. Giữ nguyên toàn bộ file split. Kiểm tra chỉ phát hiện trùng chính xác sau lowercase/trim/gộp khoảng trắng, chưa phát hiện near-duplicate.

## Sai số theo khoảng điểm thật

Residual được tính bằng điểm thật trừ điểm dự đoán; số dương nghĩa là mô hình dự đoán thấp hơn thực tế.

| Khoảng điểm thật | n | MAE | Residual trung bình |
|---|---:|---:|---:|
| ≤85 | 2.957 | 1,419391 | -1,088631 |
| 86–89 | 7.521 | 1,040557 | -0,217127 |
| 90–94 | 5.928 | 1,265200 | 0,697544 |
| ≥95 | 336 | 2,136192 | 1,983015 |

Trong các khoảng trên, nhóm ≥95 có MAE cao nhất và thường được dự đoán thấp; nhóm ≤85 thường được dự đoán cao. Mẫu điểm rất cao nhỏ hơn các nhóm còn lại. Không dùng các phát hiện test này để chỉnh lại mô hình trong lần đánh giá cuối hiện tại.

Có **6 dự đoán test ngoài khoảng 80–100**. Không cắt hoặc làm tròn dự đoán trước khi tính metric.

## Đầu ra và kiểm tra

Lệnh đã chạy từ repo root trong môi trường hiện có:

```powershell
.\.venv\Scripts\python.exe -m wine_encoding.src.evaluate_test
```

Đầu ra tại `wine_encoding/outputs/model_combined/test_evaluation/` (artifact được gitignore):

- `summary.json`: metric, alpha và provenance.
- `test_predictions.csv`: điểm thật, dự đoán Ridge/baseline, sai số và cờ trùng review theo từng dòng.
- `errors_by_group.csv`: metric theo quốc gia, giống nho và khoảng điểm thật.

Đã đối chiếu 16.742 dòng, source_row_id duy nhất, tính lại MAE/RMSE/R² từ CSV dự đoán khớp summary trong sai số 1e-12. SHA-256 của nguồn và ba split sau đánh giá khớp provenance đã lưu. Lệnh kiểm tra provenance thành công trước khi đánh giá. Không chạy lại train.

`model_combined/summary.json` và `RESULTS.md` ở cấp model vẫn mô tả lần train/validation trước đó; trạng thái đánh giá test mới nằm trong `test_evaluation/summary.json` và báo cáo này.

## Giới hạn

- Holdout seed 42 từng được quan sát trong lịch sử; không gọi đây là test chưa từng được xem hoặc khẳng định zero leakage.
- Mô hình cần review đã tồn tại và ước lượng điểm người đánh giá, không đo chất lượng khách quan trước khi có review.
- Chưa có đối chứng metadata-only để đo lợi ích riêng của review; hệ số không chứng minh nhân quả.
- Kiểm định thống kê chính thức là hạng mục riêng, chưa được thực hiện bởi bước đánh giá này.

Phần đánh giá test của mô hình đã hoàn thành. Cấu hình hiện tại được giữ nguyên sau khi xem kết quả.
