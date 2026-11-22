
from fastapi import FastAPI

from routes.places import router as places_router
from backend.routes.input import router as input_router

app = FastAPI(title="TravelMate API")

# Đăng ký nhóm API địa điểm
app.include_router(places_router)

# Đăng ký API kiểm tra đầu vào
app.include_router(input_router)


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!"
    }
