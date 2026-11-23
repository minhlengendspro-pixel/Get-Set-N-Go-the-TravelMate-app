
from services.scheduler import generate_schedule


# Danh sách địa điểm tham quan
TEST_PLACES = [
    {"name": "Bãi Dài"},
    {"name": "Hòn Chồng"},
    {"name": "Tháp Bà Ponagar"},
    {"name": "VinWonders"},
    {"name": "Viện Hải dương học"}
]


# Danh sách nhà hàng từ TV3
TEST_RESTAURANTS = [
    {"name": "Quán Hải sản A"},
    {"name": "Quán Nem nướng B"},
    {"name": "Quán đặc sản C"},
    {"name": "Quán ăn D"}
]


# Danh sách món ăn an toàn từ TV2
TEST_SAFE_DISHES = [
    {"name": "Nem nướng"},
    {"name": "Bún cá"},
    {"name": "Cơm hải sản"},
    {"name": "Bánh căn"}
]


# Tạo lịch trình 3 ngày
result = generate_schedule(
    places=TEST_PLACES,
    restaurants=TEST_RESTAURANTS,
    safe_dishes=TEST_SAFE_DISHES,
    duration=3
)


# In kết quả kiểm thử
print("===== TEST FLEXIBLE SCHEDULER =====")
print("Success:", result["success"])
print("Total days:", result["total_days"])
print("Total activities:", result["total_activities"])


# Hiển thị lịch trình từng ngày
for day in result["schedule"]:

    print(f"\n===== DAY {day['day']} =====")

    for activity in day["activities"]:

        if activity["type"] == "place":
            print("Tham quan:", activity["name"])

        elif activity["type"] == "restaurant":
            print("Nhà hàng:", activity["name"])

        elif activity["type"] == "food":
            print("Món ăn an toàn:", activity["name"])


print("\n===== TEST COMPLETED =====")
