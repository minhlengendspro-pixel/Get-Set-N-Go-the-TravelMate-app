from fastapi import FastAPI
from backend.routes.input import router

app = FastAPI(title="TravelMate API")

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!"
    }