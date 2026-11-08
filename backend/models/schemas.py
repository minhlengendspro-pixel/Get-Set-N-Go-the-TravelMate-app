from pydantic import BaseModel, Field
<<<<<<< HEAD
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
=======
from typing import Optional
class PlaceSchema(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")# có thể trống, mongo có thể tự tạo khi thêm dữ liệu mới
    name: str
    destination: str
    description: Optional[str] = None #có thể có or ko nếu kco dữ liệu
    category: str
    rating: float = 0.0
    image_url: Optional[str] = None
    tags: list[str] = []
    
    class Config:
        populate_by_name = True #linh hoạt khi truyền dữ liệu bằng id hoặc _id, tránh phải luôn sử dụng đúng tên alias khi tạo đối tượng.

class FoodSchema(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    category: str
    price: int #đơn vị vnd nên chỉ cần int
    destination: str # địa chỉ hoặc khu vực
    rating: float = 0.0
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)# tự tạo ra 1 danh sách trống mới khi tạo 1 đối tg mà kco truyền tags    
    class Config:
        populate_by_name= True
>>>>>>> a2e2a0882248231c2d92f1377b79cbe80c6f4996
