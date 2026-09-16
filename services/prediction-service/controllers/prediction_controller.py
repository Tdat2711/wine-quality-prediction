# services/prediction-service/controllers/prediction_controller.py
from pydantic import BaseModel
from services.prediction_service import make_prediction

# Định nghĩa cấu trúc dữ liệu bắt buộc từ Frontend gửi lên
class WineFeatures(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float

def handle_prediction(data: WineFeatures):
    # Gọi xuống tầng Service để xử lý
    result = make_prediction(data.dict())
    return {
        "status": "success",
        "message": "Dự đoán thành công",
        "data": result
    }