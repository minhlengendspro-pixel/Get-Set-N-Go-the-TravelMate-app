
import re
from database import db


def clean_rating(value):
    """
    Chuyển rating từ '4.5/5' thành 4.5.
    Rating không hợp lệ sẽ trả về 0.0.
    """

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
    collection = db["Places"]

    # Nếu có tỉnh/thành thì lọc theo tỉnh/thành.
    # Nếu không có thì lấy toàn bộ địa điểm.
    if destination and destination.strip():
        query = {
            "destination": {
                "$regex": f"^{re.escape(destination.strip())}$",
                "$options": "i"
            }
        }
    else:
        query = {}

    cursor = collection.find(query)

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

        normalized_place = {
            "id": str(place.get("id", "")),
            "name": place.get("name", ""),
            "destination": place.get("destination", ""),
            "category": place.get("category"),
            "description": place.get("description", ""),
            "tags": tags,
            "rating": clean_rating(place.get("rating", 0)),
            "image_url": place.get("image", "")
        }

        places.append(normalized_place)

    return places
def get_all_destinations():
    collection = db["Places"]

    destinations = collection.distinct("destination")

    return sorted(
        {
            str(destination).strip()
            for destination in destinations
            if destination and str(destination).strip()
        },
        key=str.casefold
    )