from database import db
from models.search_history import SearchHistorySchema

# Kết nối collection Search_History
collection = db["Search_History"]


def create_search_history(history: SearchHistorySchema):
    history_data = history.model_dump()

    result = collection.insert_one(history_data)

    response_data = history.model_dump()
    response_data["id"] = str(result.inserted_id)

    return response_data


def get_search_history(limit: int = 50):
    # Lấy lịch sử mới nhất trước
    histories = collection.find().sort("created_at", -1).limit(limit)

    result = []

    for history in histories:
        # Chuyển ObjectId thành chuỗi để API trả JSON được
        history["id"] = str(history["_id"])
        del history["_id"]

        result.append(history)

    return result