from fastapi import FastAPI

# Import Router của TV4
from routes.random_challenge import router as random_challenge_router
from routes.search_history import router as search_history_router
from routes.scheduler import router as scheduler_router

# Import Router Places từ code thành viên khác
from routes.places import router as places_router

app = FastAPI(title="TravelMate API")


@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!"
    }


# Đăng ký API Random Challenge
app.include_router(random_challenge_router)

# Đăng ký API Search History
app.include_router(search_history_router)

# Đăng ký API Scheduler
app.include_router(scheduler_router)

# Đăng ký API Places
app.include_router(places_router)