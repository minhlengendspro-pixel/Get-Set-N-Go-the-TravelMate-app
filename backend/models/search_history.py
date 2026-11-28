from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime, timezone


class SearchHistorySchema(BaseModel):
    keyword: str = Field(..., min_length=1)

    destination: Optional[str] = None

    search_type: Optional[
        Literal[
            "random_challenge",
            "scheduler",
            "place_recommendation",
            "restaurant",
            "food",
        ]
    ] = None

    # Lưu thông tin người dùng đã nhập trước khi chạy chức năng
    request_data: dict[str, Any] = Field(default_factory=dict)

    # Lưu toàn bộ kết quả API trả về tại thời điểm tìm kiếm
    result_data: Any = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )