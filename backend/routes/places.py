
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.place_recommendation import recommend_places

router = APIRouter(
    prefix="/api/places",
    tags=["Places"]
)

# Dữ liệu mẫu để kiểm thử API.
# Sau này sẽ thay bằng dữ liệu lấy từ MongoDB.
MOCK_PLACES = [
    {
        "id": "1",
        "name": "Bãi Dài",
        "destination": "Khánh Hòa",
        "description": "Bãi biển đẹp, thích hợp chụp ảnh và vui chơi",
        "tags": ["biển", "chụp ảnh", "vui chơi"],
        "rating": 4.8,
        "image_url": ""
    },
    {
        "id": "2",
        "name": "Tháp Bà Ponagar",
        "destination": "Khánh Hòa",
        "description": "Di tích văn hóa Chăm",
        "tags": ["tham quan", "văn hóa", "di tích"],
        "rating": 4.5,
        "image_url": ""
    },
    {
        "id": "3",
        "name": "VinWonders Nha Trang",
        "destination": "Khánh Hòa",
        "description": "Khu vui chơi giải trí",
        "tags": ["vui chơi", "chụp ảnh", "giải trí"],
        "rating": 4.7,
        "image_url": ""
    },
    {
        "id": "4",
        "name": "Bà Nà Hills",
        "destination": "Đà Nẵng",
        "description": "Khu du lịch nổi tiếng",
        "tags": ["núi", "chụp ảnh", "tham quan"],
        "rating": 4.8,
        "image_url": ""
    }
]


# Cấu trúc dữ liệu đầu vào của API
class RecommendRequest(BaseModel):
    destination: str = Field(min_length=1)
    interests: list[str] = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=50)


@router.get("/")
def get_places():
    return {
        "success": True,
        "total": len(MOCK_PLACES),
        "data": MOCK_PLACES
    }


@router.post("/recommend")
def recommend(request: RecommendRequest):

    try:
        results = recommend_places(
            destination=request.destination,
            interests=request.interests,
            places=MOCK_PLACES,
            top_k=request.top_k
        )

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
