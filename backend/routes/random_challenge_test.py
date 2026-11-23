import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from services.random_challenge import run_random_challenge


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/random-challenge-test",
    tags=["Random Challenge Test"]
)


# =========================
# 1. REQUEST MODELS
# =========================

class PlaceInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = None
    name: str | None = None
    tags: list[str] = Field(default_factory=list)
    rating: float | None = None


class RandomChallengeTestRequest(BaseModel):
    places: list[PlaceInput] = Field(
        min_length=1,
        description="Danh sách địa điểm dùng để kiểm thử Random Challenge"
    )


# =========================
# 2. RESPONSE MODELS
# =========================

class RandomChallengeData(BaseModel):
    tags: list[str]
    fitness: float
    places: list[dict[str, Any]]


class RandomChallengeResponse(BaseModel):
    success: bool
    message: str
    total: int
    data: RandomChallengeData


# =========================
# 3. RANDOM CHALLENGE API
# =========================

@router.post(
    "/",
    response_model=RandomChallengeResponse,
    summary="Kiểm thử Random Challenge",
    description=(
        "Nhận danh sách địa điểm từ Request Body, "
        "chạy thuật toán Simulated Annealing và trả về "
        "các tags cùng địa điểm phù hợp."
    ),
    responses={
        400: {"description": "Dữ liệu không đủ điều kiện tạo thử thách"},
        422: {"description": "Request Body không đúng định dạng"},
        500: {"description": "Lỗi máy chủ khi xử lý Random Challenge"}
    }
)
def test_random_challenge(
    request: RandomChallengeTestRequest
):
    try:
        # Chuyển dữ liệu Pydantic thành dictionary
        places = [
            place.model_dump(exclude_none=True)
            for place in request.places
        ]

        # Chạy thuật toán Random Challenge
        result = run_random_challenge(places)

        return {
            "success": True,
            "message": "Random Challenge API test thành công",
            "total": len(result["places"]),
            "data": {
                "tags": result["tags"],
                "fitness": result["fitness"],
                "places": result["places"]
            }
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        logger.exception("Random Challenge Test API error")

        raise HTTPException(
            status_code=500,
            detail="Lỗi máy chủ khi thực hiện Random Challenge"
        )