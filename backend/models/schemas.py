from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional

class RecommendRequest(BaseModel):
    destination: str = Field(..., description="Tên tỉnh hoặc thành phố cần tìm điểm đến", json_schema_extra={"example": "Khánh Hòa"})
    interests: List[str] = Field(..., description="Danh sách sở thích hoặc trải nghiệm mong muốn", json_schema_extra={"example": ["biển đảo", "hải sản tươi sống"]})
    top_k: Optional[int] = Field(default=10, ge=1, le=50, description="Số lượng địa điểm gợi ý tối đa")

class PlaceSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    destination: str
    description: Optional[str] = None
    category: Optional[str] = "sightseeing"
    rating: float = 0.0
    image_url: Optional[str] = Field(default=None, alias="image")
    tags: List[str] = Field(default_factory=list)

    @field_validator("rating", mode="before")
    @classmethod
    def parse_rating(cls, v):
        if v is None or v == "" or str(v).lower() == "Not a Number ":
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        # Tách chuỗi dạng "4.8/5" hoặc "4,8"
        clean_str = str(v).split("/")[0].replace(",", ".").strip()
        try:
            return float(clean_str)
        except ValueError:
            return 0.0

class FoodSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Mã định danh món ăn (ví dụ: F001)")
    name: str = Field(..., description="Tên món ăn")
    destination: str = Field(..., description="Tỉnh/thành phố tương ứng với Place")
    description: str = Field(default="", description="Mô tả món ăn đặc sản")
    food_type: str = Field(default="đặc sản địa phương", description="Phân loại: đặc sản địa phương | hải sản tươi sống | ẩm thực đường phố | cà phê & trà")
    image_url: Optional[str] = Field(default=None, alias="image")
    tags: List[str] = Field(default_factory=list)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)

    @field_validator("rating", mode="before")
    @classmethod
    def parse_rating(cls, v):
        if v is None or v == "" or str(v).lower() == "not a number":
            return 0.0
        if isinstance(v, (int, float)):
            return min(float(v), 5.0)
        clean_str = str(v).split("/")[0].replace(",", ".").strip()
        try:
            return min(float(clean_str), 5.0)
        except ValueError:
            return 0.0
