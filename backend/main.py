from fastapi import FastAPI

app = FastAPI(title="TravelMate API")


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!"
    }