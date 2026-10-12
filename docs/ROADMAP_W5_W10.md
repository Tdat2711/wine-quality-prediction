# Roadmap dự án — Tuần 5 đến tuần 10

## 1. Bối cảnh và mục tiêu cuối kỳ

Hiện tại là tuần thực tế thứ 5. Cuối tuần này, nhóm đã học đến nội dung Regression Analysis trong bộ slide mười tuần đầu. Cleaning pipeline đã tương đối hoàn chỉnh; phần còn thiếu là EDA có hệ thống, statistical inference, feature engineering, modeling, error/bias analysis và báo cáo cuối.

Mục tiêu cuối kỳ là một quy trình có thể tái lập để dự đoán `points` trên bộ Wine Reviews 130k, kèm theo:

- Dữ liệu model-ready và phương pháp chia dữ liệu cố định.
- Baseline và ít nhất một mô hình mạnh hơn được so sánh công bằng.
- MAE là metric chính; RMSE và \(R^2\) là metric phụ.
- Phân tích residual và sai số theo nhóm dữ liệu.
- Báo cáo về bias, ethics và limitations.
- README, báo cáo, slide và code có thể chạy lại.

Web/API chỉ được xem xét sau khi các đầu ra trên hoàn thành.

## 2. Vai trò ổn định

| Thành viên | Vai trò chính | Vai trò hỗ trợ |
|---|---|---|
| Khánh | Nhóm trưởng, data split, regression baseline, integration | QA, điều phối deadline và reproducibility |
| Đạt | Data pipeline, validation, model-ready data | Test và kiểm tra leakage |
| Đô | EDA, visualization, error analysis | Chuẩn hóa hình ảnh báo cáo |
| Dương | Statistical inference, ethics, bias | Viết phương pháp và limitations |
| Dũng | Feature engineering, modeling, evaluation | Model serialization và metrics |

Vai trò chính không có nghĩa một người sở hữu riêng một thư mục. Mỗi đầu ra có một người thực hiện và một reviewer khác người thực hiện.

## 3. Tuần 5 — Khóa bài toán và tạo baseline

**Mục tiêu tuần:** chuyển từ dữ liệu sạch sang thiết kế thí nghiệm ML rõ ràng.

| ID | Người làm | Người review | Nhiệm vụ | Đầu ra | Phụ thuộc | Điều kiện hoàn thành |
|---|---|---|---|---|---|---|
| W5-K1 | Khánh | Dương | Chốt experimental protocol, trực tiếp tạo split 70/15/15 và chạy Linear Regression baseline | `src/split_data.py` hoặc notebook split có thể tái tạo; bảng metric Linear | Cleaning pipeline | Target là `points`; seed và indices tái tạo được; không overlap; preprocessing chỉ fit train; có MAE/RMSE/\(R^2\) trên validation |
| W5-Da1 | Đạt | Khánh | Kiểm tra schema, missing, duplicate và xác định cột model-ready | Báo cáo validation và đặc tả feature ban đầu | Cleaning pipeline | Có số dòng/cột, danh sách feature được dùng/loại và lý do |
| W5-Do1 | Đô | Dũng | EDA `points`, `price`, `log_price`, quốc gia và variety | `notebooks/02_eda.ipynb` và hình nháp | File cleaned | Notebook chạy từ đầu; mỗi biểu đồ có tiêu đề, trục và kết luận |
| W5-Du1 | Dương | Đạt | Đánh giá missingness còn lại, đặt câu hỏi và giả thuyết thống kê | Phần inference plan trong báo cáo tuần | W5-Da1 | Có ít nhất ba giả thuyết, biến, kiểm định dự kiến và giả định |
| W5-Dg1 | Dũng | Đô | Xây Dummy và Ridge baseline, sau đó ghép kết quả với Linear baseline của Khánh | Notebook/script baseline và bảng so sánh validation | W5-K1, W5-Da1 | Cùng split và preprocessing; báo cáo MAE/RMSE/\(R^2\); chưa đọc test |

**Deadline:** cuối tuần 5.

**Gate cuối tuần:** toàn nhóm thống nhất feature ban đầu, split protocol và baseline. Nếu gate chưa đạt, không bắt đầu tuning.

## 4. Tuần 6 — Feature engineering, inference và so sánh mô hình

**Mục tiêu tuần:** tạo pipeline preprocessing đúng và thu bằng chứng phân tích.

| ID | Người làm | Người review | Nhiệm vụ | Đầu ra | Phụ thuộc | Điều kiện hoàn thành |
|---|---|---|---|---|---|---|
| W6-K1 | Khánh | Đạt | Trực tiếp tích hợp preprocessing và Linear/Ridge bằng `Pipeline`/`ColumnTransformer`; chạy khung CV chung | Module/khung experiment dùng chung và bảng CV Linear/Ridge | W5-K1, W5-Da1 | Không fit preprocessing ngoài train; mọi model dùng cùng folds/seed; lệnh chạy được từ project root |
| W6-Da1 | Đạt | Dương | Xử lý categorical cardinality, rare categories, missing indicator và đặc trưng giá/vintage | Module feature engineering và data validation | W5-Da1 | Transformation xác định rõ; không dùng target để tạo feature |
| W6-Do1 | Đô | Khánh | Hoàn thiện tối thiểu năm biểu đồ trả lời câu hỏi nghiên cứu | Hình trong `reports/figures/` và caption | W5-Do1 | Hình đọc được, thống nhất style, có insight và không lặp ý |
| W6-Du1 | Dương | Đô | Thực hiện tối thiểu ba phân tích/kiểm định thống kê | `notebooks/03_statistical_inference.ipynb` | W5-Du1 | Kiểm tra giả định, effect size/CI khi phù hợp, không chỉ báo p-value |
| W6-Dg1 | Dũng | Khánh | So sánh Linear/Ridge với các regressor cây phù hợp | Bảng CV và thời gian chạy | W6-K1, W6-Da1 | Có mean/std CV, cùng metric và cùng dữ liệu; chưa dùng test |

**Deadline:** cuối tuần 6.

**Gate cuối tuần:** có pipeline không leakage, năm biểu đồ đạt chuẩn, ba phân tích thống kê và bảng CV công bằng.

### Mốc kiểm tra thứ Tư và thuyết trình thứ Năm

Do có buổi kiểm tra vào thứ Tư và thuyết trình vào thứ Năm tuần sau, nhóm áp dụng lịch rút gọn sau:

- Hoàn thành toàn bộ gate tuần 5 trước cuối tuần này.
- Hoàn thành phần cốt lõi tuần 6 trước tối thứ Ba: năm biểu đồ, 1–2 kiểm định thống kê, preprocessing pipeline và CV cho các baseline.
- Khóa số liệu và slide vào tối thứ Ba; thứ Tư chỉ kiểm tra, ghi nhận góp ý và sửa lỗi nhỏ.
- Không mở test set, không tuning sâu và không làm web trước buổi thuyết trình.

Phần kỹ thuật Khánh phải trực tiếp trình bày trong buổi kiểm tra gồm:

1. Cách tạo split 70/15/15 và kiểm tra không overlap.
2. Vì sao preprocessing chỉ được fit trên train.
3. Cách xây Linear Regression baseline.
4. Kết quả MAE, RMSE và \(R^2\) trên validation.
5. Cách tích hợp preprocessing và model trong một pipeline tái lập được.

## 5. Tuần 7 — Tuning, error analysis và chọn mô hình

**Mục tiêu tuần:** chọn mô hình bằng validation/CV, đồng thời hiểu mô hình sai ở đâu.

| ID | Người làm | Người review | Nhiệm vụ | Đầu ra | Phụ thuộc | Điều kiện hoàn thành |
|---|---|---|---|---|---|---|
| W7-K1 | Khánh | Dũng | Chạy feature-group ablation, chủ trì model review và lập decision record | Bảng ablation và quyết định mô hình | Kết quả tuần 6 | So sánh ít nhất price-only, metadata-only và combined; quyết định dựa trên metric, độ ổn định, khả năng giải thích và chi phí chạy |
| W7-Da1 | Đạt | Khánh | Audit data leakage, split overlap và reproducibility | Leakage checklist và test bổ sung | W6-K1 | Không có record overlap; cùng seed tái tạo cùng split/kết quả trong tolerance |
| W7-Do1 | Đô | Dương | Phân tích residual và sai số theo country, variety và price band | `notebooks/04_error_analysis.ipynb` và hình | Prediction validation | Có residual distribution, actual-vs-predicted và group error table |
| W7-Du1 | Dương | Đạt | Phân tích bias/ethics và soạn model card bản đầu | Model card draft | W7-Do1 | Nêu intended use, excluded use, subgroup risks và limitations |
| W7-Dg1 | Dũng | Đô | Tuning có giới hạn cho tối đa hai model tốt nhất | Kết quả search và model candidate | W6-Dg1 | Search space được ghi lại; lựa chọn bằng CV/validation; không dùng test |

**Deadline:** cuối tuần 7.

**Gate cuối tuần:** chỉ còn một model chính và một baseline đối chứng; test set vẫn bị khóa.

## 6. Tuần 8 — Tích hợp end-to-end và viết báo cáo

**Mục tiêu tuần:** một thành viên khác có thể chạy lại toàn bộ quy trình mà không cần sửa code thủ công.

| ID | Người làm | Người review | Nhiệm vụ | Đầu ra | Phụ thuộc | Điều kiện hoàn thành |
|---|---|---|---|---|---|---|
| W8-K1 | Khánh | Đạt | Ghép entry point end-to-end và hướng dẫn reproducibility | Lệnh train/evaluate nội bộ và runbook | Model tuần 7 | Chạy từ project root; đường dẫn không phụ thuộc máy cá nhân |
| W8-Da1 | Đạt | Dũng | Viết test cho schema, preprocessing và split | Test suite mở rộng | W7-Da1 | Test bắt lỗi thiếu cột, leakage/overlap và transformation sai cơ bản |
| W8-Do1 | Đô | Khánh | Chuẩn hóa figures, caption và phần EDA/results | Bộ figures gần cuối | Tuần 6–7 | File có tên nhất quán, đủ độ phân giải, mỗi hình có nguồn dữ liệu |
| W8-Du1 | Dương | Đô | Viết data, method, inference, ethics và limitations | Báo cáo đạt khoảng 70% | Các phân tích trước | Mỗi claim quan trọng có số liệu, bảng hoặc hình hỗ trợ |
| W8-Dg1 | Dũng | Dương | Hoàn thiện train/evaluate, lưu pipeline và metadata | Model artifact candidate và metrics validation | Model tuần 7 | Artifact chứa preprocessing + model; có phiên bản, seed và feature list |

**Deadline:** cuối tuần 8.

**Gate cuối tuần:** clone sạch hoặc môi trường mới chạy được pipeline; báo cáo đạt tối thiểu 70%. Chỉ khi gate đạt mới được dành thời gian cho web.

## 7. Tuần 9 — Đánh giá test một lần và model freeze

**Mục tiêu tuần:** tạo kết quả cuối không thiên lệch và khóa artifact.

| ID | Người làm | Người review | Nhiệm vụ | Đầu ra | Phụ thuộc | Điều kiện hoàn thành |
|---|---|---|---|---|---|---|
| W9-K1 | Khánh | Dương | Tạo experiment manifest, xác nhận checklist rồi cho phép mở test đúng một lần; đóng gói model freeze | Manifest, biên bản test evaluation và version freeze | Gate tuần 8 | Ghi checksum, commit, config, feature list, thời điểm và người chạy; không tuning sau test |
| W9-Da1 | Đạt | Đô | Audit dữ liệu, split và checksum cuối | Final data audit | W8-Da1 | Kích thước split, schema và checksum khớp cấu hình đã khóa |
| W9-Do1 | Đô | Dũng | Tạo biểu đồ test/residual cuối và thay hình nháp | Figures cuối | Test predictions | Không cherry-pick subgroup để làm đẹp kết quả; caption đúng metric |
| W9-Du1 | Dương | Khánh | Hoàn thiện model card, ethics, bias và limitations | Model card/report hoàn chỉnh | W9-Da1, W9-Do1 | Nêu rõ rủi ro tổng quát hóa và giới hạn dữ liệu |
| W9-Dg1 | Dũng | Đạt | Chạy evaluation test và xuất MAE/RMSE/\(R^2\), group metrics | Metrics JSON/CSV và bảng kết quả | W9-K1 | Chỉ một lần; artifact/model/config khớp bản đã chọn tuần 7–8 |

**Deadline:** cuối tuần 9.

**Gate cuối tuần:** model, dữ liệu, metrics, báo cáo và hình được khóa; README được cập nhật bằng số liệu thật.

## 8. Tuần 10 — Hoàn thiện bài nộp và bảo vệ

**Mục tiêu tuần:** nộp một sản phẩm nhất quán và mọi thành viên đều giải thích được phần của mình.

| ID | Người làm | Người review | Nhiệm vụ | Đầu ra | Phụ thuộc | Điều kiện hoàn thành |
|---|---|---|---|---|---|---|
| W10-K1 | Khánh | Cả nhóm | Code freeze, tích hợp bài nộp, mở và kết thúc hai buổi rehearsal | Release candidate và checklist nộp | Gate tuần 9 | Repo sạch, lệnh chạy đúng, không còn placeholder hoặc kết quả mâu thuẫn |
| W10-Da1 | Đạt | Dương | Chuẩn bị phần data source, audit, cleaning và validation | Phần trình bày dữ liệu | Final report | Trình bày được quyết định missing/duplicate/outlier và bằng chứng |
| W10-Do1 | Đô | Khánh | Chuẩn bị phần EDA, figures và error analysis | Phần trình bày phân tích | Figures cuối | Mỗi hình trả lời một câu hỏi; không đọc số liệu rời rạc |
| W10-Du1 | Dương | Đạt | Chuẩn bị inference, bias, ethics và limitations | Phần trình bày đánh giá trách nhiệm | Model card cuối | Phân biệt correlation/causation và nêu phạm vi sử dụng |
| W10-Dg1 | Dũng | Đô | Chuẩn bị modeling, metrics và giải thích lựa chọn model | Phần trình bày mô hình | Metrics cuối | Giải thích baseline, CV, MAE/RMSE/\(R^2\) và test protocol |

**Deadline:** trước hạn nộp chính thức; rehearsal thứ hai phải hoàn thành trước buổi bảo vệ ít nhất một ngày.

## 9. Definition of Done chung

Một nhiệm vụ chỉ được chuyển sang `Done` khi:

1. Đầu ra nằm đúng thư mục và không phụ thuộc đường dẫn máy cá nhân.
2. Code/notebook chạy lại từ đầu không lỗi.
3. Có kết luận ngắn, không chỉ có code hoặc biểu đồ.
4. Có reviewer khác người thực hiện xác nhận.
5. Test liên quan đã chạy thành công.
6. README hoặc tài liệu liên quan được cập nhật nếu giao diện chạy thay đổi.
7. Không sử dụng test set ngoài quy trình tuần 9.

## 10. Theo dõi tiến độ

Trong mỗi buổi họp tuần, nhóm cập nhật bảng sau trong issue/project board thay vì tạo thư mục cá nhân:

| Task ID | Owner | Reviewer | Trạng thái | Blocker | Link PR/đầu ra |
|---|---|---|---|---|---|
| Ví dụ: W5-Do1 | Đô | Dũng | In progress | Không | Link notebook/PR |

Trạng thái hợp lệ: `Todo`, `In progress`, `In review`, `Done`, `Blocked`. Task `Blocked` phải ghi rõ nguyên nhân và người có thể gỡ blocker.
