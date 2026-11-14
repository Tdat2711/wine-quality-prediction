# Minh họa đặc trưng từ pipeline đã lưu

Ba dòng đầu train, không học lại encoder. Chỉ xuất phần tử khác 0 của ma trận sparse.

| price | vintage_year | country | province | variety | description |
| --- | --- | --- | --- | --- | --- |
| 14.0 | 2013.0 | US | Oregon | Pinot Gris | Tart and snappy, the flavors of lime flesh and rind dominate. Some green pineapple pokes through, with crisp acidity underscoring the flavors. The wine was all stainless-steel fermented. |
| 13.0 | 2013.0 | US | Michigan | Riesling | Pineapple rind, lemon pith and orange blossom start off the aromas. The palate is a bit more opulent, with notes of honey-drizzled guava and mango giving way to a slightly astringent, semidry finish. |
| 65.0 | 2012.0 | US | Oregon | Pinot Noir | Much like the regular bottling from 2012, this comes across as rather rough and tannic, with rustic, earthy, herbal characteristics. Nonetheless, if you think of it as a pleasantly unfussy country wine, it's a good companion to a hearty winter stew. |

## Giá và niên vụ

| example | feature | raw | prepared | imputed | scaled |
| --- | --- | --- | --- | --- | --- |
| 0 | log_price | 14.0 | 2.70805 | 2.70805 | -1.020688 |
| 0 | vintage_year | 2013.0 | 2013.0 | 2013.0 | 0.657329 |
| 1 | log_price | 13.0 | 2.639057 | 2.639057 | -1.12885 |
| 1 | vintage_year | 2013.0 | 2013.0 | 2013.0 | 0.657329 |
| 2 | log_price | 65.0 | 4.189655 | 4.189655 | 1.302069 |
| 2 | vintage_year | 2012.0 | 2012.0 | 2012.0 | 0.377147 |

`prepared` là log1p(price) hoặc năm gốc; `imputed` dùng trung vị train; `scaled` dùng trung bình/độ lệch chuẩn train. Không dùng đồng thời giá gốc và log giá.

**Probe tổng hợp:** sao chép dòng train đầu rồi đặt giá/năm thiếu để minh họa imputer; đây không phải một quan trắc train mới hoặc bằng chứng hiệu năng cho giá thiếu.

| feature | raw_missing | imputed_train_median | scaled |
| --- | --- | --- | --- |
| log_price | True | 3.258097 | -0.158363 |
| vintage_year | True | 2011.0 | 0.096966 |

## Metadata và văn bản

One-hot ánh xạ quốc gia/vùng/giống nho thành cột số; nhóm hiếm học trên train. Nhãn mới vào nhóm hiếm nếu có, nếu không khối tương ứng bằng 0. Review dùng TF-IDF unigram/bigram, giữ stopword và phủ định. Từ chưa biết bị bỏ qua. Đây là biểu diễn mô hình, khác bảng tần suất mô tả trong EDA.

Kích thước ví dụ: 3 × 3332; 123 phần tử khác 0. Probe nhãn chưa thấy: 3 phần tử khác 0 trong khối category; probe review rỗng: 0 phần tử khác 0.

Tên và giá trị từng đặc trưng hoạt động nằm trong `active_features.csv`; không thể so sánh độ lớn hệ số giữa các loại đặc trưng như tác động nhân quả.

**Tái lập:** `python -m wine_encoding.src.explain_features`; checksum/phiên bản/phạm vi tại `summary.json`.
