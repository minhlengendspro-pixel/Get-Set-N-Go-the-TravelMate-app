from fastapi import FastAPI
from routes.foods import router as foods_router
from routes.restaurants import router as restaurants_router

app = FastAPI(
    title="TravelMate API - Recommendation & Safety Pruning Engine",
    description="Backend API ho tro goi y dia diem va loc an toan y te, ngan sach nha hang cho du lich nhom.",
    version="1.0.0"
)

# 1. Dang ky router quan ly du lieu Mon an
app.include_router(foods_router)

# 2. Dang ky router Module 2: Cat tia An toan & Ngan sach Nha hang
app.include_router(restaurants_router)


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!",
        "documentation": "/docs",
        "version": "1.0.0"
    }
