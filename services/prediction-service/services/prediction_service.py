# services/prediction-service/services/prediction_service.py
import joblib
import numpy as np
import os

# Tải mô hình vào bộ nhớ khi service khởi động
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'wine_model.pkl')
model = joblib.load(MODEL_PATH)

def make_prediction(features_dict: dict) -> dict:
    # Chuyển đổi dictionary thành mảng 2D cho model
    features_array = np.array([list(features_dict.values())])
    
    # Dự đoán
    prediction = model.predict(features_array)[0]
    
    # Lấy xác suất (Confidence)
    probabilities = model.predict_proba(features_array)[0]
    confidence = max(probabilities) * 100

    # Phân loại nhãn giao diện
    quality_class = "Average"
    if prediction >= 7: quality_class = "Good"
    elif prediction >= 8: quality_class = "Excellent"
    elif prediction <= 4: quality_class = "Poor"

    return {
        "quality_score": int(prediction),
        "quality_class": quality_class,
        "confidence": round(confidence, 2)
    }