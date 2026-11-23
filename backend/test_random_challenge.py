
from services.place_data import get_places_by_destination
from services.random_challenge import run_random_challenge


print("===== TEST RANDOM CHALLENGE WITH MONGODB =====")


# 1. Lấy dữ liệu thật từ MongoDB
places = get_places_by_destination("Khánh Hòa")

print("\n1. SO LUONG DIA DIEM:", len(places))

if not places:
    print("Khong tim thay dia diem!")
    exit()


# 2. Kiểm tra dữ liệu địa điểm
print("\n2. KIEM TRA PLACE DATA")

for place in places:
    print("\nName:", place["name"])
    print("Rating:", place["rating"])
    print("Rating type:", type(place["rating"]).__name__)
    print("Tags:", place["tags"])


# 3. Chạy Random Challenge
print("\n3. RUN RANDOM CHALLENGE")

try:
    result = run_random_challenge(places)

    print("\n4. TAGS DUOC CHON:")
    print(result["tags"])

    print("\n5. FITNESS:")
    print(result["fitness"])

    print("\n6. CAC DIA DIEM PHU HOP:")

    for place in result["places"]:
        print(
            place["name"],
            "| Matched tags:", place.get("matched_tags"),
            "| Match count:", place.get("match_count")
        )

except ValueError as error:
    print("Random Challenge error:", error)

except Exception as error:
    print("Unexpected error:", error)
