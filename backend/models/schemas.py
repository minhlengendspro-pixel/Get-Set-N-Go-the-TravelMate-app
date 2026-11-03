from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendRequest(BaseModel):
    destination: str = Field(
        ..., 
        example="Khánh Hòa", 
        description="Tên tỉnh hoặc thành phố cần tìm điểm đến"
    )
    interests: List[str] = Field(
        ..., 
        example=["biển đảo", "hải sản tươi sống"], 
        description="Danh sách sở thích hoặc trải nghiệm mong muốn"
    )
    top_k: Optional[int] = Field(
        default=10, 
        ge=1, 
        le=50, 
        description="Số lượng địa điểm gợi ý tối đa trả về"
    )