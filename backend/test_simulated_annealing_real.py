
from collections import Counter

from database import db
from services.place_data import get_places_by_destination
from services.scheduler import generate_schedule
from services.simulated_annealing_scheduler import simulated_annealing


# 1. Lấy dữ liệu thật từ MongoDB
destination = "Khánh Hòa"
duration = 3

places = get_places_by_destination(destination)

restaurants = list(
    db["Restaurants"].find(
        {"destination": destination},
        {"_id": 0}
    )
)

safe_dishes = []

print("===== REAL DATA =====")
print("Places:", len(places))
print("Restaurants:", len(restaurants))
print("Safe dishes:", len(safe_dishes))


# 2. Tạo lịch trình ban đầu
initial_result = generate_schedule(
    places=places,
    restaurants=restaurants,
    duration=duration,
    safe_dishes=safe_dishes
)

initial_schedule = initial_result["schedule"]


# 3. Hàm kiểm tra hoạt động có được bảo toàn không
def get_activity_counter(schedule):
    activities = []

    for day in schedule:
        for activity in day["activities"]:
            activities.append(
                (
                    activity.get("type"),
                    activity.get("name")
                )
            )

    return Counter(activities)


initial_activities = get_activity_counter(initial_schedule)


# 4. Chạy Simulated Annealing 10 lần
print("\n===== SIMULATED ANNEALING TEST =====")

results = []

for run in range(1, 11):

    result = simulated_annealing(
        initial_schedule=initial_schedule,
        user_tags=["biển đảo", "thiên nhiên"],
        tag_weights={
            "biển đảo": 2.0,
            "thiên nhiên": 1.5
        }
    )

    best_schedule = result["schedule"]

    best_activities = get_activity_counter(best_schedule)

    preserved = initial_activities == best_activities

    initial_fitness = result["initial_fitness"]["fitness"]
    best_fitness = result["best_fitness"]["fitness"]

    improved = best_fitness > initial_fitness

    results.append({
        "run": run,
        "initial": initial_fitness,
        "best": best_fitness,
        "preserved": preserved,
        "improved": improved
    })

    print(f"\nRun {run}")
    print("Initial fitness:", initial_fitness)
    print("Best fitness:", best_fitness)
    print("Activities preserved:", preserved)
    print("Fitness improved:", improved)


# 5. Tổng kết
print("\n===== FINAL SUMMARY =====")

print("Total runs:", len(results))

print(
    "Runs preserving activities:",
    sum(item["preserved"] for item in results),
    "/",
    len(results)
)

print(
    "Runs improving fitness:",
    sum(item["improved"] for item in results),
    "/",
    len(results)
)

print(
    "Best fitness across runs:",
    max(item["best"] for item in results)
)


# 6. In lịch trình của lần chạy cuối
print("\n===== LAST OPTIMIZED SCHEDULE =====")

last_result = simulated_annealing(
    initial_schedule=initial_schedule,
    user_tags=["biển đảo", "thiên nhiên"],
    tag_weights={
        "biển đảo": 2.0,
        "thiên nhiên": 1.5
    }
)

for day in last_result["schedule"]:
    print(f"\n--- DAY {day['day']} ---")

    for activity in day["activities"]:
        print(
            activity["type"],
            ":",
            activity["name"]
        )

print("\n===== TEST COMPLETED =====")
