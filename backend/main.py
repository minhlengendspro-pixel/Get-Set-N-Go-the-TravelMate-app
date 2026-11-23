import sys
import os
from pathlib import Path
from fastapi import FastAPI

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from routes.places import router as places_router
    from routes.input import router as input_router
    from routes.restaurants import router as restaurants_router
    from routes.foods import router as foods_router
except ImportError:
    from backend.routes.places import router as places_router
    from backend.routes.input import router as input_router
    from backend.routes.restaurants import router as restaurants_router
    from backend.routes.foods import router as foods_router

app = FastAPI(
    title="TravelMate API - Recommendation & Safety Pruning Engine",
    description="Backend API ho tro goi y dia diem va loc an toan y te, ngan sach nha hang cho du lich nhom.",
    version="1.0.0"
)

# 1. Router Nguoi 1: Nhan dien che do du lich & sinh trong so
app.include_router(input_router)

# 2. Router Nguoi 2: Cat tia An toan Di ung & Tran Ngan sach Nha hang
app.include_router(restaurants_router)

# 3. Router Nguoi 3: Goi y & Cham diem Dia diem Tham quan (Cosine / TF-IDF / Jaccard)
app.include_router(places_router)

# 4. Router Mon an Dac san
app.include_router(foods_router)


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!",
        "documentation": "/docs",
        "version": "1.0.0"
    }
