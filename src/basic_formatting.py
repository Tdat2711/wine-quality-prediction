"""Format data types and handle statistical outliers."""

import pandas as pd

def format_and_handle_outliers(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy(deep=True)
    initial_rows = len(cleaned)
    report: dict[str, int] = {}

    # 1. Ép kiểu (Type Casting)
    if 'price' in cleaned.columns:
        cleaned['price'] = pd.to_numeric(cleaned['price'], errors='coerce')
    if 'points' in cleaned.columns:
        cleaned['points'] = pd.to_numeric(cleaned['points'], errors='coerce')

    # 2. Xử lý ngoại lai (Outliers) bằng phương pháp IQR cho giá rượu
    if 'price' in cleaned.columns:
        Q1 = cleaned['price'].quantile(0.25)
        Q3 = cleaned['price'].quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR

        # Lọc giữ lại giá hợp lý (hoặc các dòng chưa có giá trị)
        valid_price_mask = (cleaned['price'] <= upper_bound) | cleaned['price'].isna()
        cleaned = cleaned[valid_price_mask]

    cleaned = cleaned.reset_index(drop=True)
    report["outliers_removed"] = initial_rows - len(cleaned)

    return cleaned, report
