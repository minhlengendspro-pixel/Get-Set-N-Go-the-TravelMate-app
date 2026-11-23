
from fastapi import FastAPI
from routes.random_challenge_test import router

app = FastAPI(
    title="Random Challenge API Test",
    version="1.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Random Challenge Test Server is running"
    }
