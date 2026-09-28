"""Remove system IDs and logical duplicates."""

import pandas as pd

def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy(deep=True)
    initial_rows = len(cleaned)
    report: dict[str, int] = {}

    # QUAN TRỌNG: Phải xóa cột ID hệ thống thì mới phát hiện được trùng lặp
    if 'Unnamed: 0' in cleaned.columns:
        cleaned = cleaned.drop(columns=['Unnamed: 0'])

    # Trùng lặp logic: Cùng nội dung đánh giá và cùng người đánh giá
    if 'description' in cleaned.columns and 'taster_name' in cleaned.columns:
        cleaned = cleaned.drop_duplicates(subset=['description', 'taster_name'], keep='first')
    else:
        cleaned = cleaned.drop_duplicates(keep='first')

    cleaned = cleaned.reset_index(drop=True)
    report["duplicates_removed"] = initial_rows - len(cleaned)

    return cleaned, report