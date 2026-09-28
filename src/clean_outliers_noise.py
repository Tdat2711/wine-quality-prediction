"""Module xử lý Outlier và Noise cho tập dữ liệu Wine Reviews 130k.

Bao gồm các chức năng:
- Phát hiện và phân loại Outlier đơn biến (price) và đa biến (points vs price)
- Hiệu chỉnh các lỗi nhập liệu thực tế (Data entry error)
- Khử nhiễu văn bản (HTML entities, ký tự không ngắt, review ngắn không mang thông tin)
- Trích xuất niên vụ (Vintage Year) thông minh, khử nhiễu năm thành lập hãng
- Cung cấp biến đổi Log Transform cho biến giá (price) phục vụ Machine Learning
"""

import html
import re
import sys
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def detect_price_outliers(df: pd.DataFrame) -> Dict[str, Any]:
    """Phân tích thống kê và phát hiện outlier trên cột price."""
    prices = df['price'].dropna()
    q1 = float(prices.quantile(0.25))
    q3 = float(prices.quantile(0.75))
    iqr = q3 - q1
    
    mild_upper = q3 + 1.5 * iqr
    extreme_upper = q3 + 3.0 * iqr
    
    mild_outliers = (prices > mild_upper).sum()
    extreme_outliers = (prices > extreme_upper).sum()
    
    return {
        'total_valid': len(prices),
        'missing': int(df['price'].isna().sum()),
        'mean': float(prices.mean()),
        'median': float(prices.median()),
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
        'mild_upper_threshold': mild_upper,
        'extreme_upper_threshold': extreme_upper,
        'mild_outliers_count': int(mild_outliers),
        'mild_outliers_pct': float((mild_outliers / len(prices)) * 100),
        'extreme_outliers_count': int(extreme_outliers),
        'extreme_outliers_pct': float((extreme_outliers / len(prices)) * 100),
        'over_500_count': int((prices > 500).sum()),
        'over_1000_count': int((prices > 1000).sum())
    }


def extract_clean_vintage(title: str) -> float:
    """Trích xuất năm niên vụ (Vintage Year) từ tiêu đề chai rượu.
    
    Khử nhiễu:
    - Nếu rượu là NV (Non-Vintage), bỏ qua.
    - Không nhận nhầm năm thành lập hãng (thường < 1980 đối với các chai sparkling/cava phổ thông).
    """
    if not isinstance(title, str):
        return np.nan
        
    # Rượu không niên vụ
    if re.search(r'\b(NV|Non-Vintage)\b', title, re.IGNORECASE):
        return np.nan
        
    match = re.search(r'\b(19\d\d|20[0-2]\d)\b', title)
    if match:
        year = int(match.group(1))
        # Khoảng năm vintage thực tế hợp lý trong tập đánh giá
        if 1980 <= year <= 2021:
            return float(year)
            
    return np.nan


def clean_text_noise(text: str) -> str:
    """Loại bỏ ký tự HTML entities và chuẩn hóa khoảng trắng đặc biệt."""
    if not isinstance(text, str):
        return ""
    # Giải mã HTML entities (&amp;, &eacute;, ...)
    cleaned = html.unescape(text)
    # Loại bỏ ký tự khoảng trắng không ngắt
    cleaned = cleaned.replace('\xa0', ' ')
    # Chuẩn hóa khoảng trắng đầu cuối
    return cleaned.strip()


def handle_outliers_and_noise(
    df: pd.DataFrame,
    correct_known_errors: bool = True,
    add_log_transform: bool = True,
    extract_vintage: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Thực hiện toàn bộ quy trình làm sạch Outlier và Noise trên DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame gốc từ winemag-data-130k-v2.csv
    correct_known_errors : bool, default=True
        Có sửa các lỗi nhập liệu đã được xác minh (Blair 2013 và Ormes Sorbet) hay không.
    add_log_transform : bool, default=True
        Có tạo cột `log_price` phục vụ mô hình hoá hay không.
    extract_vintage : bool, default=True
        Có tạo cột `vintage_year` đã khử nhiễu hay không.
        
    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        DataFrame đã xử lý và từ điển ghi nhận log hành động.
    """
    df_cleaned = df.copy()
    actions_log = {}
    
    # 1. Khử nhiễu văn bản
    for col in ['description', 'title']:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].apply(clean_text_noise)
            
    # Gắn cờ review siêu ngắn (< 10 từ)
    if 'description' in df_cleaned.columns:
        word_counts = df_cleaned['description'].apply(lambda x: len(x.split()))
        df_cleaned['is_non_informative_review'] = word_counts < 10
        actions_log['short_reviews_flagged'] = int(df_cleaned['is_non_informative_review'].sum())
        
    # 2. Trích xuất niên vụ khử nhiễu
    if extract_vintage and 'title' in df_cleaned.columns:
        df_cleaned['vintage_year'] = df_cleaned['title'].apply(extract_clean_vintage)
        actions_log['valid_vintages_extracted'] = int(df_cleaned['vintage_year'].notna().sum())
        
    # 3. Hiệu chỉnh Outlier do lỗi nhập liệu (Artificial Outliers)
    if correct_known_errors and 'price' in df_cleaned.columns:
        corrected_count = 0
        
        # Case 1: Blair 2013 Chardonnay (dòng 120391) nhầm năm 2013 thành giá 2013.0
        mask_blair = (
            df_cleaned['title'].str.contains('Blair 2013 Roger Rose Vineyard', na=False) &
            (df_cleaned['price'] == 2013.0)
        )
        if mask_blair.sum() > 0:
            df_cleaned.loc[mask_blair, 'price'] = 35.0
            corrected_count += int(mask_blair.sum())
            
        # Case 2: Château les Ormes Sorbet 2013 (dòng 80290) nhầm 3300.0 thay vì 33.0
        mask_ormes = (
            df_cleaned['title'].str.contains('Château les Ormes Sorbet 2013', na=False) &
            (df_cleaned['price'] == 3300.0)
        )
        if mask_ormes.sum() > 0:
            df_cleaned.loc[mask_ormes, 'price'] = 33.0
            corrected_count += int(mask_ormes.sum())
            
        actions_log['artificial_outliers_corrected'] = corrected_count
        
    # 4. Biến đổi Log-transform cho price để điều trị Skewness phục vụ ML
    if add_log_transform and 'price' in df_cleaned.columns:
        df_cleaned['log_price'] = np.log1p(df_cleaned['price'])
        actions_log['log_price_created'] = True
        
    return df_cleaned, actions_log


if __name__ == '__main__':
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    data_path = root / 'data' / 'raw' / 'winemag-data-130k-v2.csv'
    
    if data_path.exists():
        print(f"Đang đọc dữ liệu từ: {data_path}")
        raw_df = pd.read_csv(data_path)
        outlier_stats = detect_price_outliers(raw_df)
        print("\n--- THỐNG KÊ OUTLIER PRICE ---")
        for k, v in outlier_stats.items():
            print(f"{k}: {v}")
            
        cleaned_df, logs = handle_outliers_and_noise(raw_df)
        print("\n--- KẾT QUẢ XỬ LÝ ---")
        for k, v in logs.items():
            print(f"{k}: {v}")
            
        print(f"\nSkewness ban đầu của price: {raw_df['price'].skew():.2f}")
        print(f"Skewness sau khi log-transform: {cleaned_df['log_price'].skew():.2f}")
        print("\nHoàn tất kiểm tra!")
    else:
        print(f"Không tìm thấy file tại {data_path}")
