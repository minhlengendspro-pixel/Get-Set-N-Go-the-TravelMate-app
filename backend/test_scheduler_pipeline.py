
from database import db
from services.place_data import get_places_by_destination
from services.scheduler_pipeline import run_scheduler

# 1. Input Context giả lập từ TV1
input_context = {
    "destination": "Khánh Hòa",
    "mode": "random",
    "tags": ["biển đảo", "thiên nhiên"],
    "tag_weights": {
        "biển đảo": 2.0,
        "thiên nhiên": 1.5
    },
    "duration": 3
}

destination = input_context["destination"]

# 2. Lấy Places thật từ MongoDB
places = get_places_by_destination(destination)

# 3. Lấy Restaurants thật từ MongoDB
restaurants = list(
    db["Restaurants"].find(
        {"destination": destination},
        {"_id": 0}
    )
)

# 4. TV2 tạm để rỗng, chờ tích hợp module thật
tv2_result = {
    "success": True,
    "safe_dishes": []
}

# 5. Dùng dữ liệu nhà hàng thật để mô phỏng kết quả TV3
tv3_result = {
    "success": True,
    "restaurants": restaurants
}

print("===== REAL DATABASE DATA =====")
print("Destination:", destination)
print("Places:", len(places))
print("Restaurants:", len(restaurants))

# 6. Chạy Scheduler
result = run_scheduler(
    input_context=input_context,
    places=places,
    tv2_result=tv2_result,
    tv3_result=tv3_result
)

print("\n===== SCHEDULER RESULT =====")
print("Success:", result["success"])
print("Total days:", result["total_days"])
print("Total activities:", result["total_activities"])
print("Optimized:", result["optimized"])

print("\n===== FITNESS =====")
print("Initial:", result["initial_fitness"])
print("Best:", result["best_fitness"])

print("\n===== FINAL SCHEDULE =====")

for day in result["schedule"]:
    print(f"\n--- DAY {day['day']} ---")

    for activity in day["activities"]:
        print(
            activity["type"],
            ":",
            activity["name"]
        )
