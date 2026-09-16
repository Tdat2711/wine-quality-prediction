# src/train_model.py
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

def train_and_save_model():
    print("1. Đang tải dữ liệu...")
    # Giả định bạn đã chạy pipeline.py để tạo ra file này
    data_path = '../data/processed/wine_ready_for_ML.csv'
    
    # Nếu chưa có file dữ liệu SMOTE, ta dùng tạm file cleaned
    if not os.path.exists(data_path):
        data_path = '../data/processed/wine_cleaned.csv'
        
    df = pd.read_csv(data_path)
    X = df.drop('quality', axis=1)
    y = df['quality']

    print("2. Đang chia tập Train/Test...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("3. Đang huấn luyện Random Forest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Đánh giá nhanh
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"-> Độ chính xác (Accuracy): {acc * 100:.2f}%")

    print("4. Đang lưu file mô hình (.pkl)...")
    save_dir = '../services/prediction-service/models/'
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(model, os.path.join(save_dir, 'wine_model.pkl'))
    
    print("✅ Hoàn tất! File wine_model.pkl đã được lưu vào prediction-service.")

if __name__ == "__main__":
    train_and_save_model()