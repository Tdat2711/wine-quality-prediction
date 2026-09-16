import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Định vị đường dẫn chính xác tới thư mục frontend
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Từ services/prediction-service lùi về thư mục gốc wine-quality-prediction
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

app = FastAPI(title="VINÉRA Prediction Service", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount các thư mục static (css, js, assets nằm trong frontend)
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

# Trỏ trực tiếp thư mục chứa template HTML là thư mục frontend
templates = Jinja2Templates(directory=FRONTEND_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Trả về file index.html nằm trực tiếp trong thư mục frontend
    return templates.TemplateResponse(request=request, name="index.html")

try:
    from routes.prediction_routes import router as prediction_router
    app.include_router(prediction_router, prefix="/api")
except ImportError:
    @app.post("/predict")
    async def make_prediction(request: Request):
        return {"message": "Dữ liệu đã nhận!"}