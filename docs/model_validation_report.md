# Kết quả mô hình kết hợp — validation

Cập nhật: [báo cáo bổ sung từ dự đoán đã lưu](../outputs/model_report/REPORT.md) cung cấp ngưỡng sai số và trường hợp minh họa, không fit lại. Phân tích thống kê khám phá ở [báo cáo giá–điểm](../outputs/analysis/REPORT.md). Các câu “chưa đánh giá/chưa kiểm định” bên dưới thuộc mốc lịch sử 09/11/2026.

Đánh giá test riêng đã hoàn thành ngày 13/11/2026; xem [báo cáo test](model_test_report.md). Các nội dung bên dưới mô tả trạng thái tại lần validation ngày 09/11/2026.

Lần chạy ngày 09/11/2026. Model metadata + TF-IDF review → Ridge; không đánh giá test trong lần chạy này.

## Dữ liệu và phương pháp

- Train: 78,106 dòng; validation: 16,745 dòng; 3,332 feature.
- Giữ split seed 42 đã khóa; chỉ mã hóa 111.593 dòng có giá quan sát và points, 8.395 dòng thiếu giá giữ trong nguồn để audit.
- CV 5 fold trên train: nhóm liên thông cùng title chuẩn hóa hoặc cùng review chuẩn hóa không rỗng; encoder fit riêng từng fold.
- Chọn alpha bằng MAE CV trung bình, hòa thì RMSE rồi alpha nhỏ hơn. Pipeline cuối chỉ fit train.
- Đầu vào: price → log1p, vintage_year, country, province, variety, description. Không dùng title, người chấm hay cột audit làm predictor.

## CV trên train

| Alpha | MAE trung bình | RMSE trung bình | R² trung bình |
|---:|---:|---:|---:|
| 0.1 | 1.212195 | 1.541469 | 0.753289 |
| 1 | 1.209300 | 1.538228 | 0.754326 |
| 10 | 1.239437 | 1.579239 | 0.741051 |
| 100 | 1.460298 | 1.853999 | 0.643110 |
| 1000 | 1.766425 | 2.225007 | 0.485990 |

Alpha được chọn: **1**.

## Validation

| Mô hình / mẫu đánh giá | n | MAE | RMSE | R² |
|---|---:|---:|---:|---:|
| Baseline trung bình train | 16,745 | 2.527950 | 3.082118 | -0.000005 |
| Ridge kết hợp | 16,745 | 1.203588 | 1.532724 | 0.752696 |
| Baseline, không trùng review train | 16,739 | 2.527671 | 3.081715 | -0.000005 |
| Ridge, không trùng review train | 16,739 | 1.203535 | 1.532636 | 0.752660 |

- Có 6 dòng validation trùng review chuẩn hóa với train; giữ nguyên file split, chỉ loại khỏi phép tính phụ. Không dùng kết quả phụ để tuning.
- Có 9 dự đoán validation ngoài khoảng điểm train; không cắt hoặc làm tròn trước khi tính metric.

## Kiểm chứng và tái lập

- Toàn bộ 29 unittest pass, gồm fixture tự tạo artifact, tách nhóm CV, học preprocessing trong fold, sai input và parity sau lưu/load.
- Prepare, verify, CV/train, verify_model, preview, transform và predict được chạy trên dữ liệu thật. Lệnh evaluate_test chỉ được kiểm thử bằng fixture giả lập; chưa chạy trên holdout thật.
- Nguồn và ba CSV split giữ nguyên checksum trước/sau. Artifact đầy đủ được sinh tại `wine_encoding/outputs/model_combined/` (gitignored).

| Nguồn | SHA-256 theo byte |
|---|---|
| source | `e84affec87e91e1e0c0175b1cefafe6ff31373ff15180ecded34739ef43c0461` |
| train | `25e9690c1878ffb739326bd7bfde295d46090061849f2a199e0c3cde20d798ef` |
| validation | `e87a5ca9aa61460d3d3eeb258f1cfd8a549041cf3ad29233597ee7246274253c` |
| test | `c807506ac14bfedfb6e08f36471e299b9c849636bf891f5634544851a8506d6e` |

Môi trường đã dùng: numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1, joblib 1.6.0, matplotlib 3.11.2.

## Giới hạn

- Seed-42 holdout đã từng được quan sát trước đây; không khẳng định test nguyên vẹn về lịch sử hoặc zero leakage.
- Audit chỉ phát hiện review trùng chính xác sau lowercase/trim/gộp khoảng trắng; chưa phát hiện near-duplicate.
- Mô hình cần review đã tồn tại và ước lượng điểm đánh giá, không đo chất lượng khách quan trước review.
- So với baseline trung bình không chứng minh mức lợi ích riêng do thêm review; chưa có thí nghiệm đối chứng metadata-only cùng thiết kế.
- Chưa đánh giá test, chưa chạy kiểm định thống kê chính thức; không suy luận nhân quả từ hệ số.
