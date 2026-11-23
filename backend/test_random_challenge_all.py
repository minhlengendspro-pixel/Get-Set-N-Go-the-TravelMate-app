
import time

from database import db
from services.random_challenge import run_random_challenge


# 1. Kết nối collection Places
collection = db["Places"]

# 2. Lấy toàn bộ địa điểm có tags dạng danh sách
places = list(collection.find({
    "tags": {"$type": "array"}
}))

print("===== TEST RANDOM CHALLENGE WITH ALL DATA =====")
print("Tong so dia diem:", len(places))

if not places:
    print("Khong tim thay dia diem!")
    exit()


# 3. Chạy thuật toán và đo thời gian
start_time = time.perf_counter()

try:
    result = run_random_challenge(places)

    end_time = time.perf_counter()

    print("\n===== KET QUA =====")
    print("Tags duoc chon:", result["tags"])
    print("Fitness:", result["fitness"])
    print("So dia diem tra ve:", len(result["places"]))

    print("\n===== DANH SACH DIA DIEM =====")

    for index, place in enumerate(result["places"], start=1):
        print(f"\n{index}. {place.get('name')}")
        print("Destination:", place.get("destination"))
        print("Matched tags:", place.get("matched_tags"))
        print("Match count:", place.get("match_count"))
        print("Match ratio:", place.get("match_ratio"))

    print("\n===== HIEU NANG =====")
    print("Thoi gian chay:", round(end_time - start_time, 4), "giay")

except ValueError as error:
    print("Loi du lieu:", error)

except Exception as error:
    print("Loi:", error)
