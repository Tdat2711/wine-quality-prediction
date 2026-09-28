"""
Main Data Pipeline for Wine Quality Prediction
Tích hợp lưu trữ trung gian (Interim), làm sạch 4 bước và ML Preprocessing.
"""

import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# --- NHẬP CÁC MODULE LÀM SẠCH TỪ NHÓM ---
# Sử dụng try-except để quy trình không bị gãy nếu có thành viên đang sửa code
try:
    from handle_missing_values import handle_missing_values
except ImportError:
    handle_missing_values = None

try:
    from clean_consistency import enforce_consistency
except ImportError:
    enforce_consistency = None

try:
    from clean_duplicates import remove_duplicates
except ImportError:
    remove_duplicates = None

try:
    from basic_formatting import format_and_handle_outliers
except ImportError:
    format_and_handle_outliers = None

# --- ĐỊNH NGHĨA ĐƯỜNG DẪN DỮ LIỆU ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Thư mục hệ thống
RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# File dữ liệu
RAW_DATA_PATH = RAW_DIR / "winemag-data-130k-v2.csv"

# Các file trung gian (Interim) lưu lại sau từng bước để dễ Audit
INTERIM_MISSING_PATH = INTERIM_DIR / "01_missing_handled.csv"
INTERIM_CONSISTENCY_PATH = INTERIM_DIR / "02_consistency_handled.csv"
INTERIM_DUPLICATES_PATH = INTERIM_DIR / "03_duplicates_handled.csv"
INTERIM_FORMAT_OUTLIERS_PATH = INTERIM_DIR / "04_format_outliers_handled.csv"

# File đích (Processed)
CLEANED_DATA_PATH = PROCESSED_DIR / "wine_cleaned_final.csv"
FINAL_ML_PATH = PROCESSED_DIR / "wine_ready_for_ML.csv"


def run_cleaning_stage() -> pd.DataFrame:
    """Giai đoạn 1: Dây chuyền làm sạch dữ liệu 4 bước."""
    print("\n" + "="*50)
    print("🚀 BẮT ĐẦU GIAI ĐOẠN 1: LÀM SẠCH DỮ LIỆU TỔNG HỢP")
    print("="*50)
    
    # Tạo sẵn các thư mục nếu chưa tồn tại
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu gốc tại: {RAW_DATA_PATH}")
    
    # Đọc dữ liệu thô
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Kích thước file gốc: {df.shape}")
    overall_report = {}

    # ---------------------------------------------------------
    # Bước 1: Missing Values (Dương)
    # ---------------------------------------------------------
    if handle_missing_values:
        print("[1/4] Đang xử lý Missing Values (Dương)...")
        df, report_missing = handle_missing_values(df)
        overall_report.update(report_missing)
        df.to_csv(INTERIM_MISSING_PATH, index=False)
        print(f"      -> Đã lưu: {INTERIM_MISSING_PATH.name}")

    # ---------------------------------------------------------
    # Bước 2: Consistency (Đạt)
    # ---------------------------------------------------------
    if enforce_consistency:
        print("[2/4] Đang chuẩn hóa Consistency (Đạt)...")
        df, report_consistency = enforce_consistency(df)
        overall_report.update(report_consistency)
        df.to_csv(INTERIM_CONSISTENCY_PATH, index=False)
        print(f"      -> Đã lưu: {INTERIM_CONSISTENCY_PATH.name}")

    # ---------------------------------------------------------
    # Bước 3: Duplicates (Đạt)
    # ---------------------------------------------------------
    if remove_duplicates:
        print("[3/4] Đang loại bỏ Duplicates (Đạt)...")
        df, report_dupes = remove_duplicates(df)
        overall_report.update(report_dupes)
        df.to_csv(INTERIM_DUPLICATES_PATH, index=False)
        print(f"      -> Đã lưu: {INTERIM_DUPLICATES_PATH.name}")

    # ---------------------------------------------------------
    # Bước 4: Outliers & Formatting (Đô & Dũng)
    # ---------------------------------------------------------
    if format_and_handle_outliers:
        print("[4/4] Đang chuẩn hóa Format và loại bỏ Outliers (Đô & Dũng)...")
        df, report_outliers = format_and_handle_outliers(df)
        overall_report.update(report_outliers)
        df.to_csv(INTERIM_FORMAT_OUTLIERS_PATH, index=False)
        print(f"      -> Đã lưu: {INTERIM_FORMAT_OUTLIERS_PATH.name}")

    # =========================================================
    # LƯU KẾT QUẢ SẠCH CUỐI CÙNG VÀO PROCESSED
    # =========================================================
    df.to_csv(CLEANED_DATA_PATH, index=False)
    
    print(f"\n✅ HOÀN TẤT GIAI ĐOẠN 1! Kích thước file sạch: {df.shape}")
    print(f"File hoàn chỉnh để báo cáo: {CLEANED_DATA_PATH.name}")
    print("\n📊 TÓM TẮT BÁO CÁO LÀM SẠCH:")
    for k, v in overall_report.items():
        print(f"  - {k}: {v:,}")
        
    return df


def run_ml_preprocessing_stage(df: pd.DataFrame):
    """Giai đoạn 2: Chuẩn bị dữ liệu cho Machine Learning (Scaler & SMOTE)."""
    print("\n" + "="*50)
    print("⚙️ BẮT ĐẦU GIAI ĐOẠN 2: MACHINE LEARNING PREPROCESSING")
    print("="*50)
    
    # Ưu tiên dùng 'quality', nếu không có thì dùng 'points' làm nhãn dự đoán
    target_col = 'quality' if 'quality' in df.columns else 'points'
    
    if target_col not in df.columns:
        raise ValueError(f"Không tìm thấy cột nhãn '{target_col}' để chạy SMOTE.")

    X = df.drop(target_col, axis=1)
    y = df[target_col]
    
    # CHỐNG CRASH HỆ THỐNG: Chỉ Scale các cột dạng số (Numeric)
    X_numeric = X.select_dtypes(include=['int64', 'float64'])
    dropped_cols = len(X.columns) - len(X_numeric.columns)
    if dropped_cols > 0:
        print(f"⚠️ Đã tạm thời tách {dropped_cols} cột Text ra khỏi mô hình vì chưa được mã hóa (Encoding).")
    
    X = X_numeric

    # Chuẩn hóa (Scaler)
    print(f"-> Đang chuẩn hóa (StandardScaler) cho dữ liệu kích thước {X.shape}...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
    
    # Cân bằng nhãn (SMOTE)
    print("-> Đang cân bằng nhãn (SMOTE)...")
    smote = SMOTE(random_state=42)
    X_smote, y_smote = smote.fit_resample(X_scaled_df, y)
    
    # Gộp X và y lại và xuất file for ML
    print("-> Đang xuất file dữ liệu sẵn sàng cho Machine Learning...")
    df_final = pd.concat([X_smote, y_smote], axis=1)
    df_final.to_csv(FINAL_ML_PATH, index=False)
    
    print(f"\n🎉 HOÀN TẤT TOÀN BỘ QUY TRÌNH!")
    print(f"Dữ liệu ML cuối cùng có kích thước: {df_final.shape}")
    print(f"File sẵn sàng đưa vào thuật toán: {FINAL_ML_PATH.name}")


def run_data_pipeline():
    """Hàm trung tâm điều phối toàn bộ luồng chạy."""
    # 1. Chạy quá trình làm sạch từng bước
    run_cleaning_stage()
    
    # 2. Đọc lại file sạch hoàn hảo nhất từ thư mục processed để nạp vào mô hình
    df_cleaned = pd.read_csv(CLEANED_DATA_PATH)
    
    # 3. Chạy quá trình chuẩn bị ML
    run_ml_preprocessing_stage(df_cleaned)


if __name__ == "__main__":
    run_data_pipeline()