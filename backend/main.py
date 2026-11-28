
import sys
from pathlib import Path

from fastapi import FastAPI


# ==========================================
# 1. CONFIGURE PROJECT PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==========================================
# 2. IMPORT ROUTERS
# ==========================================

# TV4: Random Challenge, Scheduler, Search History
from routes.random_challenge import router as random_challenge_router
from routes.search_history import router as search_history_router
from routes.scheduler import router as scheduler_router

# Module chung: Places, Input
from routes.places import router as places_router
from routes.input import router as input_router

# TV Food: Foods, Restaurants
from routes.restaurants import router as restaurants_router
from routes.foods import router as foods_router


# ==========================================
# 3. CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="TravelMate API - Recommendation & Safety Pruning Engine",
    description=(
        "Backend API ho tro goi y dia diem, mon an, nha hang, "
        "Random Challenge, Scheduler va Search History."
    ),
    version="1.0.0"
)


# ==========================================
# 4. REGISTER ROUTERS
# ==========================================

# Input
app.include_router(input_router)

# Places recommendation
app.include_router(places_router)

# Food
app.include_router(foods_router)

# Restaurants
app.include_router(restaurants_router)

# TV4: Random Challenge
app.include_router(random_challenge_router)

# TV4: Scheduler
app.include_router(scheduler_router)

# TV4: Search History
app.include_router(search_history_router)


# ==========================================
# 5. HOME API
# ==========================================

@app.get("/")
def home():
    return {
        "message": "TravelMate API is running!",
        "documentation": "/docs",
        "version": "1.0.0"
    }
