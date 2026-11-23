from services.place_data import get_places_by_destination
from services.random_challenge import get_available_tags

places = get_places_by_destination("Khánh Hòa")

available_tags = get_available_tags(places)

print("===== TAG FREQUENCY =====")

for tag in sorted(available_tags):
    count = sum(
        1 for place in places
        if tag in place["tags"]
    )

    print(f"{tag}: {count}/{len(places)}")