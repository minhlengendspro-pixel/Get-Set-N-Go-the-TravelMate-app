from fastapi import FastAPI

from backend.routes.places import router as places_router
from backend.routes.input import router as input_router

app = FastAPI(title="TravelMate API")

app.include_router(places_router)
app.include_router(input_router)


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!"
    }