from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Literal

class RecommendRequest(BaseModel):
    destination: str = Field(..., description="Tên tỉnh hoặc thành phố cần tìm điểm đến", json_schema_extra={"example": "Khánh Hòa"})
    interests: List[str] = Field(..., description="Danh sách sở thích hoặc trải nghiệm mong muốn", json_schema_extra={"example": ["biển đảo", "hải sản tươi sống"]})
    top_k: Optional[int] = Field(default=10, ge=1, le=50, description="Số lượng địa điểm gợi ý tối đa")
    mode: Optional[Literal["solo", "couple", "family", "random"]] = Field(default="random", description="Chế độ du lịch theo nhóm của Người 1")

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
        if v is None or v == "" or str(v).lower() == "not a number":
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

    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    destination: str
    description: Optional[str] = ""
    category: Optional[str] = "đặc sản địa phương"
    food_type: Optional[str] = "đặc sản địa phương"
    price: Optional[int] = 0
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


# ==============================================================================
# MODULE 2: SCHEMAS DÀNH CHO BỘ LỌC RÀNG BUỘC & CẮT TỈA AN TOÀN (HARD PRUNING)
# ==============================================================================

class MenuItemSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dish_id: str = Field(..., description="Mã món ăn (ví dụ: D001)")
    dish_name: str = Field(..., description="Tên món ăn")
    price: int = Field(default=0, ge=0, description="Đơn giá món ăn (VNĐ)")
    ingredients: List[str] = Field(default_factory=list, description="Mảng thành phần nguyên liệu")
    allergens: List[str] = Field(default_factory=list, description="Mảng các tác nhân dị ứng chính")
    is_signature: bool = Field(default=False, description="Đánh dấu món đặc sản nổi bật")
    matched_allergens: List[str] = Field(default_factory=list, description="Danh sách các chất gây dị ứng phát hiện được cho món này")
    reason: Optional[str] = Field(default=None, description="Lý do chi tiết cảnh báo dị ứng hoặc an toàn")


class PriceRangeSchema(BaseModel):
    min: int = Field(default=0, ge=0)
    max: int = Field(default=0, ge=0)


class RestaurantSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Mã định danh nhà hàng (ví dụ: R001)")
    name: str = Field(..., description="Tên nhà hàng/quán ăn")
    destination: str = Field(..., description="Tỉnh/thành phố liên kết với Places")
    address: Optional[str] = Field(default="", description="Địa chỉ cụ thể")
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    avg_cost_per_person: int = Field(default=0, ge=0, description="Chi phí ăn uống bình quân 1 người (VNĐ)")
    price_range: Optional[PriceRangeSchema] = None
    specialties: List[str] = Field(default_factory=list, description="Danh sách món đặc sắc")
    cross_contamination_risk: str = Field(default="low", description="Mức nguy cơ lây nhiễm chéo: low | medium | high")
    source: Optional[str] = Field(default="", description="Nguồn dữ liệu thực tế xác thực")
    all_ingredients: List[str] = Field(default_factory=list, description="Tổng hợp nguyên liệu có trong quán")
    menu_items: List[MenuItemSchema] = Field(default_factory=list, description="Danh sách các món ăn trong thực đơn")


class SafetyPruneRequest(BaseModel):
    destination: str = Field(..., description="Tên tỉnh hoặc thành phố cần tìm", json_schema_extra={"example": "Hà Nội"})
    group_allergens: List[str] = Field(default_factory=list, description="Danh sách chất dị ứng của đoàn", json_schema_extra={"example": ["hải sản", "đậu phộng"]})
    max_budget_per_person: Optional[int] = Field(default=None, description="Trần ngân sách ăn uống tối đa cho 1 người / bữa (VNĐ)", json_schema_extra={"example": 120000})
    group_size: int = Field(default=1, ge=1, le=50, description="Số lượng thành viên trong đoàn")


class EvaluatedRestaurant(BaseModel):
    id: str
    name: str
    destination: str
    address: Optional[str] = ""
    rating: float = 0.0
    avg_cost_per_person: int
    source: Optional[str] = Field(default="", description="Nguồn dữ liệu xác thực thực tế")
    is_safe: bool = Field(default=True, description="Đạt chuẩn an toàn (có ít nhất 1 món an toàn và hợp ngân sách)")
    is_100_percent_safe: bool = Field(default=False, description="Toàn bộ thực đơn 100% không chứa chất dị ứng")
    safe_dishes: List[MenuItemSchema] = Field(default_factory=list, description="Danh sách món an toàn đề xuất cho người dị ứng")
    unsafe_dishes: List[MenuItemSchema] = Field(default_factory=list, description="Danh sách món chứa dị ứng cần tránh")
    warning_note: Optional[str] = None


class SafetyPruneResponse(BaseModel):
    destination: str
    total_candidates: int
    passed_count: int
    pruned_overbudget_count: int
    pruned_unsafe_count: int
    safe_restaurants: List[EvaluatedRestaurant]
