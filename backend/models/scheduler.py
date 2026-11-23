
from pydantic import BaseModel, Field
from typing import Any


class SchedulerRequest(BaseModel):
    input_context: dict[str, Any]

    places: list[dict[str, Any]]

    # Kết quả giả định hoặc kết quả thực tế từ TV2
    tv2_result: dict[str, Any] | list[Any]

    # Kết quả giả định hoặc kết quả thực tế từ TV3
    tv3_result: dict[str, Any] | list[Any]
