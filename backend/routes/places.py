
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.place_recommendation import recommend_places
from services.place_data import (
    get_places_by_destination,
    get_all_destinations
)

router = APIRouter(
    prefix="/api/places",
    tags=["Places"]
)


class RecommendRequest(BaseModel):
    destination: str = Field(min_length=1)
    interests: list[str] = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=50)


# API lấy danh sách tỉnh/thành
@router.get("/destinations")
def get_destinations():
    try:
        destinations = get_all_destinations()

        return {
            "success": True,
            "total": len(destinations),
            "data": destinations
        }

    except Exception as error:
        print(f"Destination API error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Không thể lấy danh sách tỉnh/thành"
        )


# API lấy danh sách địa điểm theo tỉnh/thành
@router.get("/")
def get_places(destination: str):
    try:
        places = get_places_by_destination(destination)

        return {
            "success": True,
            "total": len(places),
            "data": places
        }

    except Exception as error:
        print(f"Get places error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Không thể lấy dữ liệu địa điểm từ MongoDB"
        )


# API gợi ý địa điểm
@router.post("/recommend")
def recommend(request: RecommendRequest):
    try:
        # 1. Lấy dữ liệu từ MongoDB
        places = get_places_by_destination(
            request.destination
        )

        # 2. Chạy thuật toán gợi ý
        results = recommend_places(
            destination=request.destination,
            interests=request.interests,
            places=places,
            top_k=request.top_k
        )

        # 3. Trả kết quả cho frontend
        return {
            "success": True,
            "total": len(results),
            "data": results
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(f"Recommendation API error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Lỗi khi xử lý yêu cầu gợi ý địa điểm"
        )
