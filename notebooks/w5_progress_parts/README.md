# Notebook phần việc cho buổi đánh giá tiến trình

Mỗi thành viên **tự tạo một notebook**, không tạo file rỗng thay người khác:

| Người | File sẽ nộp | Nội dung chính |
|---|---|---|
| Khánh | `01_khanh_price_tiers.ipynb` | Bốn khoảng giá và điểm trung vị |
| Đạt | `02_dat_data_split.ipynb` | Chọn mẫu, kiểm tra và split theo nhóm `title` |
| Đô | `03_do_eda_plots.ipynb` | Hai biểu đồ giá và giá–điểm |
| Dương | `04_duong_story_stats.ipynb` | Bối cảnh, giả thuyết và thống kê thử nếu đủ điều kiện |
| Dũng | `05_dung_baseline.ipynb` | Bốn cấu hình dự kiến và hồi quy thử nếu đủ điều kiện |

Mỗi file đọc cùng `data/processed/wine_cleaned_final.csv` bằng đường dẫn tương đối, chạy độc lập từ project root hoặc thư mục `notebooks`, và có mục tiêu, code, kết quả, 2–3 nhận xét cùng giới hạn. Không chạy lại cleaning, không chỉ dán ảnh, không in toàn bộ dataset. Ghi rõ số mẫu trong bảng/hình.

Để nạp dữ liệu khi mở notebook từ thư mục phần việc, dùng cùng một quy tắc đường dẫn:

```python
from pathlib import Path
import pandas as pd

root = Path.cwd()
if root.name == "w5_progress_parts":
    root = root.parent.parent
elif root.name == "notebooks":
    root = root.parent
df = pd.read_csv(root / "data" / "processed" / "wine_cleaned_final.csv")
```

Nếu split chưa được kiểm tra, chỉ làm phân tích mô tả trên mẫu có giá và ghi *khám phá sơ bộ*. Không công bố kiểm định, metric validation hoặc dùng test. Sau khi Đạt nộp split và Khánh duyệt, mọi phân tích có tính kiểm định/mô hình dùng cùng train/validation đã khóa.

Chỉ Khánh chỉnh `notebooks/02_eda.ipynb` để tích hợp các cell đã kiểm tra. Năm notebook ở đây được giữ trong repo làm bằng chứng đóng góp và để chạy lại; buổi thứ Tư chỉ mở notebook chung.
