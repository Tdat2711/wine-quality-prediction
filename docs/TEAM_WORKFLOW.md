# Quy tắc làm việc nhóm

## 1. Nguyên tắc tổ chức

- Không tạo thư mục riêng theo tên Khánh, Đạt, Đô, Dương hoặc Dũng.
- Tổ chức file theo loại sản phẩm: dữ liệu, source code, notebook, test, figures và tài liệu.
- Mỗi đầu ra có một owner và một reviewer; reviewer không được trùng owner.
- Khánh chịu trách nhiệm tích hợp và quyết định cuối khi có xung đột kỹ thuật, không mặc định phải làm hoặc review mọi nhiệm vụ.
- Mọi kết quả báo cáo phải truy ngược được tới dữ liệu, code và cấu hình đã dùng.

## 2. Quy trình một nhiệm vụ

1. Chọn nhiệm vụ và người phụ trách trong [Roadmap tuần 5–10](ROADMAP_W5_W10.md).
2. Nếu cần theo dõi bằng issue/branch, đặt task ID tại đó; ghi rõ reviewer, đầu ra, deadline và dependency. Roadmap không chứa task ID hay reviewer.
3. Tạo branch từ `dev` đã được cập nhật.
4. Chỉ thay đổi các file thuộc phạm vi task.
5. Tự chạy notebook/test liên quan và ghi bằng chứng trong pull request.
6. Mở pull request về `dev` và gắn reviewer.
7. Sửa các nhận xét review trước khi merge.
8. Chỉ chuyển task sang `Done` sau khi merge và kiểm tra đầu ra.

Không commit trực tiếp vào `dev` hoặc `main`. `dev` là nhánh tích hợp; `main` chỉ nhận phiên bản ổn định/release.

## 3. Quy tắc branch và commit

### Tên branch

```text
data/<task-id>-mo-ta-ngan
analysis/<task-id>-mo-ta-ngan
model/<task-id>-mo-ta-ngan
docs/<task-id>-mo-ta-ngan
fix/<task-id>-mo-ta-ngan
```

Ví dụ:

```text
analysis/w7-do1-eda-points-price
model/w9-dg1-compare-regressors
docs/w8-du1-inference
```

### Commit

- Một commit nên biểu diễn một thay đổi logic.
- Dùng động từ rõ ràng, ví dụ: `Add points distribution analysis` hoặc `Fix train-only imputation`.
- Không dùng message mơ hồ như `update`, `fix`, `final`, `code moi`.
- Không commit cache, virtual environment, checkpoint hoặc file tạm.
- Không trộn refactor không liên quan vào cùng pull request.

## 4. Pull request và review

Mỗi pull request phải ghi:

- Nhiệm vụ trong roadmap, mục tiêu và task ID nếu nhóm dùng issue/branch.
- File/đầu ra chính đã thay đổi.
- Cách chạy lại.
- Test/check đã chạy và kết quả.
- Ảnh hoặc bảng trước/sau nếu thay đổi visualization/model result.
- Hạn chế hoặc vấn đề còn lại.
- Xác nhận không dùng test set của thí nghiệm chính trước khi khóa mô hình và đến bước đánh giá cuối.

Reviewer kiểm tra:

- Kết quả có trả lời đúng nhiệm vụ không.
- Đường dẫn có chạy từ project root không.
- Có data leakage hoặc dùng test để tuning không.
- Biểu đồ có title, label, unit và kết luận không.
- Notebook có chạy lại từ đầu và không chứa code thử nghiệm thừa không.
- Claim trong báo cáo có bằng chứng và không diễn giải correlation thành causation không.

## 5. Quy tắc dữ liệu

- `data/raw/` là bất biến; không chỉnh sửa, ghi đè hoặc lưu file phát sinh vào đây.
- File trung gian có thể tái tạo đặt trong `data/interim/`.
- File dùng trực tiếp cho phân tích/model đặt trong `data/processed/`; giữ `price` thiếu trong cleaned data và chỉ lọc dòng có giá quan sát ở thí nghiệm chính.
- Mọi bước thay đổi dữ liệu phải được thực hiện bằng code, không sửa CSV thủ công.
- Cần lưu row count, schema và quyết định loại/giữ dữ liệu sau bước xử lý quan trọng.
- Không tự động xóa logical duplicate nếu chưa đủ bằng chứng.
- Không xóa outlier chỉ vì giá trị lớn; phải có lý do nghiệp vụ hoặc bằng chứng lỗi nhập liệu.
- Không đưa dữ liệu nhạy cảm hoặc credential vào repository.

## 6. Quy tắc notebook và visualization

### Notebook

- Đặt tên theo thứ tự chạy: `02_eda.ipynb`, `03_statistical_inference.ipynb`, `04_error_analysis.ipynb`.
- Mỗi notebook có phần mục tiêu, dữ liệu đầu vào, phương pháp, kết quả và kết luận.
- Riêng buổi đánh giá tiến trình thứ Tư tuần 6: mỗi người nộp một notebook phần việc trong `notebooks/w5_progress_parts/`, giữ lại trong repo. Khánh là người duy nhất tích hợp các cell cần thiết vào `notebooks/02_eda.ipynb`; notebook chung là nguồn minh chứng có thể chạy lại. Theo yêu cầu ngày 21/10/2026, nhóm dùng thêm PowerPoint hỗ trợ trình bày.
- Các notebook phần việc đều đọc cùng cleaned data, không chạy lại cleaning riêng hoặc chỉ dán ảnh kết quả. Chỉ chuyển code, bảng/hình và nhận xét đã kiểm tra vào notebook chung; không sao chép năm lần bước nạp dữ liệu.
- Đọc dữ liệu bằng đường dẫn tương đối tính từ project root.
- Dùng seed cố định khi có phép lấy mẫu hoặc thuật toán ngẫu nhiên.
- Trước khi review: restart kernel và run all.
- Logic được dùng bởi nhiều notebook phải chuyển sang `src/`.

### Visualization

- File cuối đặt trong `reports/figures/` với tên chữ thường, dùng dấu gạch dưới.
- Có title, axis label, unit, legend khi cần và caption trong báo cáo.
- Không dùng biểu đồ 3D hoặc quá nhiều màu nếu không giúp trả lời câu hỏi.
- Không cắt trục hoặc chọn phạm vi gây hiểu sai.
- Hình dùng trong báo cáo phải được tạo lại từ code.

## 7. Quy tắc modeling và chống data leakage

- Target chính là `points`; không dùng `quality`.
- Chia train/validation/test trước khi fit bước học từ dữ liệu.
- Split xấp xỉ 70/15/15, nhóm theo `title` chuẩn hóa; Khánh chốt giữ seed **42 ngày 21/10/2026** cho bộ chia hiện tại; ưu tiên không để cùng tên chai ở hai tập hơn là ép tỷ lệ dòng chính xác tuyệt đối.
- Bốn cấu hình Dummy / chỉ giá / chỉ metadata / kết hợp phải dùng cùng tập dòng và split. Metadata chính: `country`, `province`, `variety`, `vintage_year`; giá dùng `log1p(price)`.
- Imputer, scaler, encoder, rare-category mapping và feature selection chỉ fit trên train.
- Cross-validation và validation dùng để chọn feature/model/hyperparameter.
- Buổi đánh giá tiến trình thứ Tư tuần 6 trình bày câu hỏi hai tầng và EDA giá–điểm bằng một notebook; cleaning chỉ tóm tắt vì đã báo cáo trước. Nếu split chưa được xác nhận, biểu đồ trên mẫu có giá chỉ là khám phá sơ bộ, không công bố metric kiểm định/hồi quy. Nếu split đã được xác nhận, có thể trình bày Spearman trên train và `DummyRegressor`/`LinearRegression` chỉ giá trên train/validation như kết quả thử; không yêu cầu metric để được báo cáo và không dùng số giả.
- So sánh hồi quy **chính thức** bốn cấu hình ở tuần 9 của lịch học thực tế; kết quả thử trước đó không thay thế bước này. Test đánh giá ở tuần 10 sau khi giao thức và mô hình đã khóa, với sự xác nhận của Khánh. Quyết định 21/10/2026 giữ seed 42 thay cho yêu cầu đổi holdout trước đó. EDA đã xem toàn mẫu có giá và dự án có ghi nhận holdout seed 42 từng được thử. Giữ seed 42 không xác nhận test hoàn toàn chưa từng được quan sát. Giữ lịch sử này khi diễn giải kết quả; không đổi seed để chọn kết quả thuận lợi và không tuning theo test.
- Không tuning sau khi xem test. Nếu phát hiện lỗi kỹ thuật làm kết quả test vô hiệu, phải ghi biên bản, sửa lỗi và công bố rõ lần chạy lại.
- Mọi model phải được so với `DummyRegressor`.
- Metric chính là MAE; RMSE và \(R^2\) là metric phụ.
- Pipeline artifact phải chứa cả preprocessing và model để tránh sai lệch khi inference.

## 8. Definition of Done theo loại đầu ra

### Code

- Chạy được từ project root.
- Không chứa đường dẫn tuyệt đối máy cá nhân.
- Có docstring/comment cho logic không hiển nhiên.
- Test liên quan chạy thành công.

### Notebook

- Restart-and-run-all không lỗi.
- Không phụ thuộc biến được tạo ngoài thứ tự cell.
- Có kết luận bằng văn bản và không chứa output debug thừa.

### Báo cáo

- Nguồn dữ liệu, phương pháp và metric được ghi rõ.
- Mọi số liệu khớp artifact chính thức.
- Tách biệt kết quả, diễn giải và limitation.

### Task

- Đúng đầu ra, đúng deadline, có reviewer phê duyệt và đã merge vào `dev`.

## 9. Quản lý file legacy và phần web

- `src/train_model.py`, `frontend/` và `services/prediction-service/` hiện là legacy prototype.
- Không lấy kết quả từ các file legacy đưa vào báo cáo chính.
- Không sửa web/API trong giai đoạn data/model trừ khi có task được cả nhóm chấp thuận.
- Web không phải đầu ra bắt buộc của hướng hai tầng; chỉ mở task web riêng nếu phần data, thí nghiệm và báo cáo đã hoàn thành.
- Nếu làm web, API phải dùng đúng pipeline Wine Reviews 130k và input schema phải được định nghĩa từ model cuối.

## 10. Khi có xung đột hoặc trễ hạn

- Thành viên báo `Blocked` ngay khi xác định không thể tự giải quyết trong buổi làm việc hiện tại.
- Ghi rõ blocker, ảnh hưởng, việc đã thử và người cần hỗ trợ.
- Khánh điều phối đổi reviewer hoặc thu hẹp task; không âm thầm chuyển toàn bộ việc sang một người.
- Nếu phải giảm phạm vi, ưu tiên theo thứ tự: dữ liệu đúng → evaluation đúng → báo cáo rõ → visualization → web.
