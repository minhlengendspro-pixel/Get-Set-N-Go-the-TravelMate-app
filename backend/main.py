from fastapi import FastAPI
from routes.foods import router as foods_router

app = FastAPI(title="TravelMate API - Food Service")

# Đăng ký router kiểm tra dữ liệu Món ăn
app.include_router(foods_router)


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!",
        "documentation": "/docs"
    }
