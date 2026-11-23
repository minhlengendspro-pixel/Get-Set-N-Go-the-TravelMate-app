from models.schemas import PlaceSchema, FoodSchema

print("===== TEST PLACE RATING =====")

place = PlaceSchema(
    name="Bãi Dài",
    destination="Khánh Hòa",
    category="Biển",
    rating="4.8/5"
)

print(place.rating, type(place.rating))

print("\n===== TEST FOOD RATING =====")

food = FoodSchema(
    name="Hải sản",
    category="Món ăn",
    price=150000,
    destination="Khánh Hòa",
    rating="4,5/5"
)

print(food.rating, type(food.rating))