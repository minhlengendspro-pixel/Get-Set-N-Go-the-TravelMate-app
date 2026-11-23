
from typing import Any


def get_item_name(item: Any) -> str:
    """Lấy tên địa điểm, nhà hàng hoặc món ăn."""

    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        return (
            item.get("name")
            or item.get("restaurant_name")
            or item.get("food_name")
            or "Chưa có tên"
        )

    return "Chưa có tên"


def generate_schedule(
    places: list,
    restaurants: list,
    duration: int,
    safe_dishes: list | None = None
) -> dict:
    """
    Tạo lịch trình linh hoạt theo số ngày.

    Địa điểm, nhà hàng và món ăn an toàn
    được xem là các hoạt động riêng biệt.
    """

    if duration < 1:
        raise ValueError("Số ngày phải lớn hơn hoặc bằng 1.")

    if safe_dishes is None:
        safe_dishes = []

    if not all(
        isinstance(data, list)
        for data in [places, restaurants, safe_dishes]
    ):
        raise TypeError("Dữ liệu đầu vào phải là danh sách.")

    # 1. Tạo hoạt động tham quan
    place_activities = []

    for place in places:
        place_activities.append({
            "type": "place",
            "name": get_item_name(place),
            "tags": (
                place.get("tags", [])
                if isinstance(place, dict)
                else []
            )
        })

    # 2. Tạo hoạt động nhà hàng
    restaurant_activities = []

    for restaurant in restaurants:
        restaurant_activities.append({
            "type": "restaurant",
            "name": get_item_name(restaurant),
            "rating": (
                restaurant.get("rating")
                if isinstance(restaurant, dict)
                else None
            )
        })

    # 3. Tạo hoạt động món ăn an toàn từ TV2
    food_activities = []

    for dish in safe_dishes:
        food_activities.append({
            "type": "food",
            "name": get_item_name(dish)
        })

    # 4. Kết hợp tất cả hoạt động
    all_activities = (
        place_activities
        + restaurant_activities
        + food_activities
    )

    # 5. Khởi tạo lịch trình
    schedule = []

    for day_index in range(duration):
        schedule.append({
            "day": day_index + 1,
            "activities": []
        })

    # 6. Phân bổ hoạt động vào các ngày
    for index, activity in enumerate(all_activities):
        day_index = index % duration

        schedule[day_index]["activities"].append(activity)

    return {
        "success": True,
        "total_days": duration,
        "total_activities": len(all_activities),
        "schedule": schedule
    }
