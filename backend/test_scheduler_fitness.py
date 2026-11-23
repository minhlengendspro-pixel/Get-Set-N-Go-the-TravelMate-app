
from services.scheduler_fitness import calculate_fitness


# =====================================
# 1. DU LIEU LICH TRINH MAU
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
                "restaurant": "Quán A",
                "dish": "Nem nướng",
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
                "restaurant": "Quán B",
                "dish": "Bún cá",
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
                "restaurant": "Quán C",
                "dish": "Bánh căn",
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
# 3. TINH FITNESS
# =====================================

result = calculate_fitness(
    schedule=initial_schedule,
    user_tags=user_tags,
    tag_weights=tag_weights
)


# =====================================
# 4. HIEN THI KET QUA
# =====================================

print("===== TEST SCHEDULER FITNESS =====")

print("Total days:", len(initial_schedule))

total_activities = sum(
    len(day["activities"])
    for day in initial_schedule
)

print("Total activities:", total_activities)

print("\n===== FITNESS RESULT =====")

print("Overall fitness:", result["fitness"])

for name, score in result["details"].items():
    print(f"{name}: {score}")
