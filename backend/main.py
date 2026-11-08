
from fastapi import FastAPI
from routes.places import router as places_router

app = FastAPI(title="TravelMate API")

# Đăng ký nhóm API địa điểm
app.include_router(places_router)


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!"
    }
