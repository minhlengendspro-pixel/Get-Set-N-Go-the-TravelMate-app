
import re
from database import db
from models.schemas import PlaceSchema


# Kết nối collection Places trong MongoDB
places_collection = db["Places"]


def get_places_by_destination(destination):
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination không được để trống")

    destination = destination.strip()

    cursor = places_collection.find({
        "destination": {
            "$regex": f"^{re.escape(destination)}$",
            "$options": "i"
        }
    })

    places = []

    for place in cursor:
        place_data = {
            "id": str(place.get("_id", "")),
            "name": place.get("name", ""),
            "destination": place.get("destination", ""),
            "description": place.get("description"),
            "category": place.get("category", ""),
            "rating": place.get("rating", 0.0),
            "image_url": place.get("image_url", place.get("image")),
            "tags": (
                place.get("tags", [])
                if isinstance(place.get("tags"), list)
                else []
            ),
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude")
        }

        validated_place = PlaceSchema(**place_data)
        places.append(validated_place.model_dump())

    return places


def get_available_destinations():
    destinations = places_collection.distinct("destination")

    return sorted(
        {
            destination.strip()
            for destination in destinations
            if isinstance(destination, str)
            and destination.strip()
        },
        key=str.casefold
    )
