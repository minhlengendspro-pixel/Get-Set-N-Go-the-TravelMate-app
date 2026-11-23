
from services.simulated_annealing_scheduler import simulated_annealing


# =====================================
# 1. DU LIEU LICH TRINH BAN DAU
# =====================================

initial_schedule = [
    {
        "day": 1,
        "activities": [
            {
                "type": "place",
                "name": "Bãi Dài",
                "tags": ["biển đảo", "thiên nhiên"]
            },
            {
                "type": "place",
                "name": "VinWonders",
                "tags": ["vui chơi giải trí"]
            },
            {
                "type": "food",
                "restaurant": "Quán B",
                "dish": "Bún cá",
                "rating": 4.5
            }
        ]
    },
    {
        "day": 2,
        "activities": [
            {
                "type": "place",
                "name": "Hòn Chồng",
                "tags": ["biển đảo", "thiên nhiên"]
            },
            {
                "type": "place",
                "name": "Viện Hải dương học",
                "tags": ["giáo dục", "thiên nhiên"]
            },
            {
                "type": "food",
                "restaurant": "Quán C",
                "dish": "Bánh căn",
                "rating": 4.8
            }
        ]
    },
    {
        "day": 3,
        "activities": [
            {
                "type": "place",
                "name": "Tháp Bà Ponagar",
                "tags": ["văn hóa - lịch sử"]
            },
            {
                "type": "food",
                "restaurant": "Quán A",
                "dish": "Nem nướng",
                "rating": 4.6
            }
        ]
    }
]


# =====================================
# 2. SO THICH VA TRONG SO TU TV1
# =====================================

user_tags = [
    "leo núi & trekking",
    "thiên nhiên",
    "núi rừng"
]

tag_weights = {
    "leo núi & trekking": 2.0,
    "thiên nhiên": 1.5,
    "núi rừng": 1.5
}


# =====================================
# 3. CHAY SIMULATED ANNEALING
# =====================================

result = simulated_annealing(
    initial_schedule=initial_schedule,
    user_tags=user_tags,
    tag_weights=tag_weights
)


# =====================================
# 4. SO SANH FITNESS
# =====================================

print("===== SIMULATED ANNEALING SCHEDULER =====")

print("Success:", result["success"])

print("\n===== FITNESS COMPARISON =====")

print("Initial fitness:")
print(result["initial_fitness"])

print("\nBest fitness:")
print(result["best_fitness"])


# =====================================
# 5. HIEN THI LICH TRINH TOI UU
# =====================================

print("\n===== OPTIMIZED SCHEDULE =====")

for day in result["schedule"]:

    print(f"\n--- DAY {day['day']} ---")

    for activity in day["activities"]:

        if activity["type"] == "place":
            print("Tham quan:", activity["name"])

        elif activity["type"] == "food":
            print("Nhà hàng:", activity["restaurant"])
            print("Món ăn:", activity.get("dish"))


# =====================================
# 6. KIEM TRA SO LUONG HOAT DONG
# =====================================

initial_total = sum(
    len(day["activities"])
    for day in initial_schedule
)

optimized_total = sum(
    len(day["activities"])
    for day in result["schedule"]
)

print("\n===== ACTIVITY COUNT CHECK =====")

print("Initial activities:", initial_total)
print("Optimized activities:", optimized_total)

print(
    "Activities preserved:",
    initial_total == optimized_total
)
