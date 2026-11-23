from fastapi import APIRouter, HTTPException, status
from typing import Any, Dict
from models.schemas import SafetyPruneRequest, SafetyPruneResponse
from services.hard_pruning import prune_restaurants

router = APIRouter(prefix="/api/restaurants", tags=["Restaurants"])


@router.post(
    "/prune-safe",
    response_model=SafetyPruneResponse,
    status_code=status.HTTP_200_OK,
    summary="Loc va cat tia nha hang theo do an toan di ung va ngan sach",
    description=(
        "Tiep nhan yeu cau tu Nguoi 1 hoac Frontend, truy van danh sach quan an "
        "tai tinh/thanh, danh gia nguy co di ung cap nhom va loc tran ngan sach."
    )
)
async def filter_safe_restaurants(request: SafetyPruneRequest):
    """
    Endpoint dieu phoi cat tia an toan y te va ngan sach:
    - Input: SafetyPruneRequest (destination, group_allergens, max_budget_per_person)
    - Output: SafetyPruneResponse (danh sach quan an an toan kem thong ke)
    """
    try:
        result = prune_restaurants(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loi he thong trong qua trinh cat tia an toan: {str(e)}"
        )
