from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db
from models.schemas import FoodSchema

router = APIRouter(prefix="/api/foods", tags=["Foods"])


@router.get("/", response_model=List[FoodSchema])
async def get_all_foods(
    destination: Optional[str] = Query(None, description="Lọc theo tỉnh/thành phố"),
    food_type: Optional[str] = Query(None, description="Lọc theo phân loại món ăn"),
    tag: Optional[str] = Query(None, description="Lọc theo từ khóa tag"),
    limit: int = Query(50, ge=1, le=300, description="Số lượng món tối đa trả về"),
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua (phân trang)")
):
    """
    Lấy danh sách món ăn, hỗ trợ lọc đa tiêu chí theo tỉnh/thành, thể loại, hoặc tag.
    """
    query = {}
    if destination:
        query["destination"] = {"$regex": f"^{destination.strip()}$", "$options": "i"}
    if food_type:
        query["food_type"] = food_type.strip()
    if tag:
        query["tags"] = {"$in": [tag.strip().lower()]}

    foods = list(db.Foods.find(query, {"_id": 0}).skip(skip).limit(limit))
    return foods


@router.get("/by-destination/{destination}", response_model=List[FoodSchema])
async def get_foods_by_destination(destination: str):
    """
    Lấy toàn bộ danh sách món ăn đặc trưng của một tỉnh/thành phố cụ thể.
    """
    clean_dest = destination.strip()
    foods = list(db.Foods.find(
        {"destination": {"$regex": f"^{clean_dest}$", "$options": "i"}},
        {"_id": 0}
    ))
    if not foods:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy món ăn nào cho tỉnh/thành '{clean_dest}'"
        )
    return foods


@router.get("/destinations", response_model=List[dict])
async def get_food_destinations():
    """
    Liệt kê danh sách tất cả các tỉnh/thành đã có dữ liệu món ăn kèm số lượng món.
    """
    pipeline = [
        {"$group": {"_id": "$destination", "food_count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"destination": "$_id", "food_count": 1, "_id": 0}}
    ]
    return list(db.Foods.aggregate(pipeline))


@router.get("/{food_id}", response_model=FoodSchema)
async def get_food_by_id(food_id: str):
    """
    Lấy thông tin chi tiết một món ăn cụ thể theo mã ID (ví dụ: F001).
    """
    food = db.Foods.find_one({"id": food_id.strip().upper()}, {"_id": 0})
    if not food:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy món ăn với ID '{food_id}'"
        )
    return food
