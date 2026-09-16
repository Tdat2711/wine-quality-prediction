# services/prediction-service/routes/prediction_routes.py
from fastapi import APIRouter
from controllers.prediction_controller import handle_prediction, WineFeatures

router = APIRouter()

@router.post("/predict")
async def predict_quality_route(features: WineFeatures):
    return handle_prediction(features)