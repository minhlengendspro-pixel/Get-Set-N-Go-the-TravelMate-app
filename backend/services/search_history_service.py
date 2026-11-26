
from bson import ObjectId
from database import db
from models.search_history import SearchHistorySchema


collection = db["Search_History"]


def create_search_history(history: SearchHistorySchema):
    history_data = history.model_dump()

    # Lưu dữ liệu vào MongoDB
    result = collection.insert_one(history_data)

    # Chuyển ObjectId thành chuỗi để FastAPI trả JSON được
    history_data["id"] = str(result.inserted_id)

    # Xóa _id kiểu ObjectId khỏi dữ liệu trả về
    history_data.pop("_id", None)

    return history_data


def get_search_history(limit: int = 50, search_type: str | None = None):
    query = {}

    if search_type:
        query["search_type"] = search_type

    histories = (
        collection.find(query, {"result_data": 0})
        .sort("created_at", -1)
        .limit(limit)
    )

    result = []

    for history in histories:
        history["id"] = str(history["_id"])
        del history["_id"]
        result.append(history)

    return result


def get_search_history_detail(history_id: str):
    if not ObjectId.is_valid(history_id):
        return None

    history = collection.find_one({"_id": ObjectId(history_id)})

    if history is None:
        return None

    history["id"] = str(history["_id"])
    del history["_id"]

    return history
