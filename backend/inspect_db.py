
from database import db

collection = db["Places"]

print("========== PLACE DATA SAMPLE ==========")

# Lấy 3 địa điểm đầu tiên
samples = collection.find().limit(3)

for index, place in enumerate(samples, start=1):
    print(f"\n--- PLACE {index} ---")

    fields = [
        "_id",
        "id",
        "name",
        "destination",
        "category",
        "description",
        "tags",
        "rating",
        "image"
    ]

    for field in fields:
        value = place.get(field)

        print(
            f"{field}: {value}"
            f" | Type: {type(value).__name__}"
        )
