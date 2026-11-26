from fastapi import APIRouter, HTTPException, Query

from models.search_history import SearchHistorySchema

from services.search_history_service import (
    create_search_history,
    get_search_history,
    get_search_history_detail
)


router = APIRouter(
    prefix="/api/search-history",
    tags=["Search History"]
)


@router.post("/")
def save_search_history(history: SearchHistorySchema):
    """
    Lưu lịch sử tìm kiếm hoặc tạo lịch trình.
    """

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
    limit: int = Query(default=50, ge=1, le=100),
    search_type: str | None = Query(
        default=None,
        description="random_challenge, scheduler hoặc place_recommendation"
    )
):
    """
    Lấy danh sách lịch sử.
    Có thể lọc theo loại lịch sử.
    """

    allowed_types = [
        "random_challenge",
        "scheduler",
        "place_recommendation"
    ]

    if search_type and search_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Loại lịch sử không hợp lệ"
        )

    try:
        histories = get_search_history(
            limit=limit,
            search_type=search_type
        )

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


@router.get("/{history_id}")
def read_search_history_detail(history_id: str):
    """
    Lấy toàn bộ kết quả của một lần tìm kiếm cụ thể.
    """

    try:
        history = get_search_history_detail(history_id)

        if history is None:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy lịch sử tìm kiếm"
            )

        return {
            "success": True,
            "data": history
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Get Search History Detail error:", error)

        raise HTTPException(
            status_code=500,
            detail="Lỗi khi lấy chi tiết lịch sử"
        )