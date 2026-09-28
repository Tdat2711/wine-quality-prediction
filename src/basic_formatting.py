from pathlib import Path
import pandas as pd

# Xác định thư mục gốc của dự án
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Đường dẫn dữ liệu
input_path = PROJECT_ROOT / "data" / "raw" / "winemag-data-130k-v2.csv"
output_path = PROJECT_ROOT / "data" / "processed" / "wine_basic_formatted.csv"

# Đọc dữ liệu gốc, không chỉnh sửa trực tiếp file raw
df = pd.read_csv(input_path)

# Lưu thông tin trước khi xử lý để kiểm tra
rows_before, columns_before = df.shape
missing_before = df.isna().sum()

# Các cột chỉ cần bỏ khoảng trắng ở đầu/cuối
text_columns = [
    "description",
    "designation",
    "region_1",
    "taster_twitter_handle",
    "title",
    "variety",
    "winery",
]

# Giữ nguyên ô trống (NaN), chỉ làm sạch khoảng trắng ở ô có nội dung
for column in text_columns:
    df[column] = df[column].str.strip()

# Kiểm tra: không được tự ý xóa dòng/cột hoặc thay đổi missing values
assert df.shape == (rows_before, columns_before), "Số dòng hoặc cột đã bị thay đổi."
assert df.isna().sum().equals(missing_before), "Số giá trị thiếu đã bị thay đổi."

# Tạo thư mục processed nếu chưa có
output_path.parent.mkdir(parents=True, exist_ok=True)

# Xuất dữ liệu đã chuẩn hóa
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("Hoàn tất chuẩn hóa định dạng.")
print(f"Đã lưu file: {output_path}")
print(f"Kích thước dữ liệu: {df.shape}")
print("\nKiểu dữ liệu:")
print(df.dtypes)