from pydantic import BaseModel, Field
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