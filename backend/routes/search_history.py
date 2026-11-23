from fastapi import APIRouter, HTTPException, Query

from models.search_history import SearchHistorySchema
from services.search_history_service import (
    create_search_history,
    get_search_history
)

router = APIRouter(
    prefix="/api/search-history",
    tags=["Search History"]
)


@router.post("/")
def save_search_history(history: SearchHistorySchema):
    try:
        result = create_search_history(history)

        return {
            "success": True,
            "message": "Lưu lịch sử tìm kiếm thành công",
            "data": result
        }

    except Exception as error:
        print("Save Search History error:", error)
        raise HTTPException(
            status_code=500,
            detail="Lỗi khi lưu lịch sử tìm kiếm"
        )


@router.get("/")
def read_search_history(
    limit: int = Query(default=50, ge=1, le=100)
):
    try:
        histories = get_search_history(limit)

        return {
            "success": True,
            "total": len(histories),
            "data": histories
        }

    except Exception as error:
        print("Get Search History error:", error)
        raise HTTPException(
            status_code=500,
            detail="Lỗi khi lấy lịch sử tìm kiếm"
        )