
from services.place_data import get_places_by_destination


print("===== TEST PLACE DATA TV4 =====")

places = get_places_by_destination("Khánh Hòa")

print("Total places:", len(places))

for place in places[:20]:
    rating = place.get("rating")

    print(
        "Name:", place.get("name"),
        "| Rating:", repr(rating),
        "| Type:", type(rating).__name__,
        "| Tags:", place.get("tags")
    )
