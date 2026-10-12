# Quy tắc làm việc nhóm

## 1. Nguyên tắc tổ chức

- Không tạo thư mục riêng theo tên Khánh, Đạt, Đô, Dương hoặc Dũng.
- Tổ chức file theo loại sản phẩm: dữ liệu, source code, notebook, test, figures và tài liệu.
- Mỗi đầu ra có một owner và một reviewer; reviewer không được trùng owner.
- Khánh chịu trách nhiệm tích hợp và quyết định cuối khi có xung đột kỹ thuật, không mặc định phải làm hoặc review mọi nhiệm vụ.
- Mọi kết quả báo cáo phải truy ngược được tới dữ liệu, code và cấu hình đã dùng.

## 2. Quy trình một nhiệm vụ

1. Chọn task ID trong [Roadmap tuần 5–10](ROADMAP_W5_W10.md).
2. Ghi rõ owner, reviewer, đầu ra, deadline và dependency.
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
analysis/w5-do1-eda-points-price
model/w6-dg1-compare-regressors
docs/w8-du1-report-method
```

### Commit

- Một commit nên biểu diễn một thay đổi logic.
- Dùng động từ rõ ràng, ví dụ: `Add points distribution analysis` hoặc `Fix train-only imputation`.
- Không dùng message mơ hồ như `update`, `fix`, `final`, `code moi`.
- Không commit cache, virtual environment, checkpoint hoặc file tạm.
- Không trộn refactor không liên quan vào cùng pull request.

## 4. Pull request và review

Mỗi pull request phải ghi:

- Task ID và mục tiêu.
- File/đầu ra chính đã thay đổi.
- Cách chạy lại.
- Test/check đã chạy và kết quả.
- Ảnh hoặc bảng trước/sau nếu thay đổi visualization/model result.
- Hạn chế hoặc vấn đề còn lại.
- Xác nhận không đọc/chạm test set nếu chưa đến tuần 9.

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
- File dùng trực tiếp cho phân tích/model đặt trong `data/processed/`.
- Mọi bước thay đổi dữ liệu phải được thực hiện bằng code, không sửa CSV thủ công.
- Cần lưu row count, schema và quyết định loại/giữ dữ liệu sau bước xử lý quan trọng.
- Không tự động xóa logical duplicate nếu chưa đủ bằng chứng.
- Không xóa outlier chỉ vì giá trị lớn; phải có lý do nghiệp vụ hoặc bằng chứng lỗi nhập liệu.
- Không đưa dữ liệu nhạy cảm hoặc credential vào repository.

## 6. Quy tắc notebook và visualization

### Notebook

- Đặt tên theo thứ tự chạy: `02_eda.ipynb`, `03_statistical_inference.ipynb`, `04_error_analysis.ipynb`.
- Mỗi notebook có phần mục tiêu, dữ liệu đầu vào, phương pháp, kết quả và kết luận.
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
- Split chuẩn: 70/15/15, seed cố định, cân nhắc phân tầng theo bins của `points`.
- Imputer, scaler, encoder, rare-category mapping và feature selection chỉ fit trên train.
- Cross-validation và validation dùng để chọn feature/model/hyperparameter.
- Test set bị khóa đến tuần 9 và chỉ được đánh giá một lần sau khi Khánh xác nhận checklist.
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
- Chỉ mở task web khi gate tuần 8 đạt: pipeline end-to-end chạy được, test pass, báo cáo đạt khoảng 70% và model artifact đã được tạo.
- Nếu làm web, API phải dùng đúng pipeline Wine Reviews 130k và input schema phải được định nghĩa từ model cuối.

## 10. Khi có xung đột hoặc trễ hạn

- Thành viên báo `Blocked` ngay khi xác định không thể tự giải quyết trong buổi làm việc hiện tại.
- Ghi rõ blocker, ảnh hưởng, việc đã thử và người cần hỗ trợ.
- Khánh điều phối đổi reviewer hoặc thu hẹp task; không âm thầm chuyển toàn bộ việc sang một người.
- Nếu phải giảm phạm vi, ưu tiên theo thứ tự: dữ liệu đúng → evaluation đúng → báo cáo rõ → visualization → web.
