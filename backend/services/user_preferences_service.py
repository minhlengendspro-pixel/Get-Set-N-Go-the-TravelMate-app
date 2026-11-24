from pymongo.collection import Collection
from backend.models.user_preferences import UserPreferences
from bson import ObjectId

def save_preferences(
    preferences: UserPreferences,
    collection: Collection
):
    document = preferences.model_dump()
    result = collection.insert_one(document)
    preference_id = str(result.inserted_id)
    return preference_id

def get_preferences(
    preference_id: str,
    collection: Collection
):
    if not ObjectId.is_valid(preference_id):
        raise ValueError("ID không hợp lệ")
    document_id = ObjectId(preference_id)
    document = collection.find_one({"_id": document_id})
    if document is None:
        return None
    document["_id"] = str(document["_id"])
    return document


def update_preferences(
    preference_id: str,
    preferences: UserPreferences,
    collection: Collection
    ):
    if not ObjectId.is_valid(preference_id):
        raise ValueError("ID không hợp lệ")
    document_id = ObjectId(preference_id)
    condition = {"_id": document_id}
    new_data = preferences.model_dump(exclude={"created_at"})
    result = collection.update_one(
        condition,
        {"$set": new_data}
    )
    was_found = result.matched_count > 0 # Kiểm tra có tìm thấy document cần sửa không
    return was_found
