
import re

from database import db
from models.schemas import PlaceSchema


# Kết nối collection Places trong MongoDB
places_collection = db["Places"]


def clean_rating(value):
    """
    Chuẩn hóa rating về kiểu float trong khoảng 0-5.
    Ví dụ: '4.5/5' -> 4.5
    Rating không hợp lệ -> 0.0
    """

    if value is None:
        return 0.0

    if isinstance(value, bool):
        return 0.0

    if isinstance(value, (int, float)):
        rating = float(value)
    else:
        value = str(value).strip().replace(",", ".")

        match = re.fullmatch(
            r"(\d+(?:\.\d+)?)\s*(?:/\s*5)?",
            value
        )

        if not match:
            return 0.0

        rating = float(match.group(1))

    if not 0 <= rating <= 5:
        return 0.0

    return rating


def get_places_by_destination(destination: str | None = None):
    """
    Lấy địa điểm theo tỉnh/thành.
    Nếu destination không được truyền hoặc để trống,
    lấy toàn bộ địa điểm trong MongoDB.
    """

    if destination is not None and not isinstance(destination, str):
        raise ValueError("Destination phải là chuỗi")

    if destination and destination.strip():
        destination = destination.strip()

        query = {
            "destination": {
                "$regex": f"^{re.escape(destination)}$",
                "$options": "i"
            }
        }
    else:
        query = {}

    cursor = places_collection.find(query)

    places = []

    for place in cursor:
        raw_tags = place.get("tags", [])

        if not isinstance(raw_tags, list):
            raw_tags = []

        tags = [
            str(tag).strip().casefold()
            for tag in raw_tags
            if tag is not None and str(tag).strip()
        ]

        place_data = {
            "id": str(place.get("_id", "")),
            "name": place.get("name", ""),
            "destination": place.get("destination", ""),
            "description": place.get("description"),
            "category": place.get("category", ""),
            "rating": clean_rating(place.get("rating")),

            # Ưu tiên image_url, nếu rỗng hoặc None thì lấy image
            "image_url": place.get("image_url") or place.get("image"),

            "tags": tags,
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude")
        }

        validated_place = PlaceSchema(**place_data)

        places.append(validated_place.model_dump())

    return places


def get_all_destinations():
    """
    Lấy danh sách tỉnh/thành không trùng lặp.
    """

    destinations = places_collection.distinct("destination")

    return sorted(
        {
            str(destination).strip()
            for destination in destinations
            if isinstance(destination, str)
            and destination.strip()
        },
        key=str.casefold
    )


# Giữ tên hàm cũ để tương thích với frontend
def get_available_destinations():
    return get_all_destinations()
