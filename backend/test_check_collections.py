from database import db

restaurants = list(
    db["Restaurants"].find(
        {"destination": "Khánh Hòa"}
    )
)

print("===== RESTAURANTS IN KHANH HOA =====")
print("Total:", len(restaurants))

for restaurant in restaurants:
    print(
        restaurant.get("name"),
        "| Rating:",
        restaurant.get("rating")
    )