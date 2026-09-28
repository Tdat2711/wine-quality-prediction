"""Enforce text consistency and standard formatting."""

import pandas as pd

def enforce_consistency(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy(deep=True)
    report: dict[str, int] = {}

    # Lấy các cột chứa văn bản
    string_cols = cleaned.select_dtypes(include=['object', 'string']).columns

    for col in string_cols:
        # Cắt khoảng trắng 2 đầu và chuẩn hóa các khoảng trắng liên tiếp bên trong
        cleaned[col] = cleaned[col].astype(str).str.strip().replace(r'\s+', ' ', regex=True)
        # Đưa các giá trị chuỗi 'nan' về lại pd.NA chuẩn
        cleaned.loc[cleaned[col] == 'nan', col] = pd.NA

    report["formatted_text_columns"] = len(string_cols)

    # Quy tắc riêng: Chuẩn hóa viết hoa chữ cái đầu cho quốc gia
    if 'country' in cleaned.columns:
        cleaned['country'] = cleaned['country'].str.title()

    # Quy tắc riêng: Đảm bảo twitter handle luôn có '@' ở đầu
    if 'taster_twitter_handle' in cleaned.columns:
        mask = cleaned['taster_twitter_handle'].notna() & \
               ~cleaned['taster_twitter_handle'].isin(['Not provided', 'Unknown']) & \
               ~cleaned['taster_twitter_handle'].str.startswith('@')
        
        cleaned.loc[mask, 'taster_twitter_handle'] = '@' + cleaned.loc[mask, 'taster_twitter_handle']
        report["twitter_handles_fixed"] = int(mask.sum())

    return cleaned, report