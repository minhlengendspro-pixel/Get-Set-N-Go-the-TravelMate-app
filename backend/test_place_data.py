
from services.place_data import get_places_by_destination


places = get_places_by_destination("Khánh Hòa")

print("========== MONGODB QUERY TEST ==========")
print("Total places:", len(places))

for place in places[:3]:
    print("\nName:", place["name"])
    print("ID:", place["id"])
    print("Destination:", place["destination"])
    print("Tags:", place["tags"])
    print("Rating:", place["rating"])
    print("Image:", place["image_url"])

# Kiểm tra dữ liệu
assert len(places) > 0
assert all(isinstance(p["tags"], list) for p in places)
assert all(isinstance(p["rating"], float) for p in places)

print("\nALL CHECKS PASSED!")
