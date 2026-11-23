
from services.place_data import get_places_by_destination
from services.random_challenge import run_random_challenge

destination = "Khánh Hòa"

# Lấy dữ liệu thật từ MongoDB
places = get_places_by_destination(destination)

print("===== RANDOM CHALLENGE REPEAT TEST =====")
print("Destination:", destination)
print("Total places:", len(places))

if not places:
    print("Khong tim thay dia diem!")
    raise SystemExit

# Chạy thử 10 lần
for i in range(10):
    result = run_random_challenge(places)

    print(f"\n===== LAN {i + 1} =====")
    print("Random tags:", result["tags"])
    print("So tags:", len(result["tags"]))
    print("Fitness:", result["fitness"])
    print("Places:")

    for place in result["places"]:
        print(
            "-", place.get("name"),
            "| Matched:", place.get("matched_tags"),
            "| Match count:", place.get("match_count")
        )
