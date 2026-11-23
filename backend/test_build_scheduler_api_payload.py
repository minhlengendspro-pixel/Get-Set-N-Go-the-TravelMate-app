
import json

from database import db
from services.place_data import get_places_by_destination


destination = "Khánh Hòa"

# Lấy Places thật
places = get_places_by_destination(destination)

# Lấy Restaurants thật
restaurants = list(
    db["Restaurants"].find(
        {"destination": destination},
        {"_id": 0}
    )
)

# Input Context kiểm thử
input_context = {
    "destination": destination,
    "mode": "random",
    "tags": ["biển đảo", "thiên nhiên"],
    "tag_weights": {
        "biển đảo": 2.0,
        "thiên nhiên": 1.5
    },
    "duration": 3
}

# Tạo Request Body
payload = {
    "input_context": input_context,
    "places": places,
    "tv2_result": {
        "success": True,
        "safe_dishes": []
    },
    "tv3_result": {
        "success": True,
        "restaurants": restaurants
    }
}

print("===== API TEST DATA =====")
print("Places:", len(places))
print("Restaurants:", len(restaurants))

print("\n===== COPY JSON BELOW =====")

print(
    json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        default=str
    )
)
