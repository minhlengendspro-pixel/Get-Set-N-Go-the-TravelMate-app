from database import db

collection = db["Places"]

print("===== KIEM TRA RATING RAW =====")

for place in collection.find({"destination": "Khánh Hòa"}).limit(20):
    rating = place.get("rating")

    print(
        "Name:", place.get("name"),
        "| Rating:", repr(rating),
        "| Type:", type(rating).__name__
    )