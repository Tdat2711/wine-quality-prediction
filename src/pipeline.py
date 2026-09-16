# src/pipeline.py
import pandas as pd
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

def run_data_pipeline():
    # 1. Đọc dữ liệu sạch từ Tuần 3
    df = pd.read_csv('../data/processed/wine_cleaned.csv')
    
    X = df.drop('quality', axis=1)
    y = df['quality']
    
    # 2. Chuẩn hóa thang đo (Feature Scaling)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
    
    # 3. Cân bằng nhãn (SMOTE)
    smote = SMOTE(random_state=42)
    X_smote, y_smote = smote.fit_resample(X_scaled_df, y)
    
    # 4. Gộp lại và xuất file
    df_final = pd.concat([X_smote, y_smote], axis=1)
    df_final.to_csv('../data/processed/wine_ready_for_ML.csv', index=False)
    print(f"Hoàn tất! Dữ liệu mới có kích thước: {df_final.shape}")

if __name__ == "__main__":
    run_data_pipeline()