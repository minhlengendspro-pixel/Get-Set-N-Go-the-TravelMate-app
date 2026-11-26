
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

    - Mỗi ngày tối đa 2 địa điểm tham quan.
    - Ưu tiên phân bổ địa điểm đều giữa các ngày.
    - Nhà hàng và món ăn được phân bổ riêng.
    - Địa điểm chưa được xếp lịch sẽ được lưu lại.
    """

    # 1. Kiểm tra dữ liệu đầu vào
    if not isinstance(duration, int) or isinstance(duration, bool):
        raise TypeError("Số ngày phải là số nguyên.")

    if duration < 1:
        raise ValueError("Số ngày phải lớn hơn hoặc bằng 1.")

    if safe_dishes is None:
        safe_dishes = []

    if not all(
        isinstance(data, list)
        for data in [places, restaurants, safe_dishes]
    ):
        raise TypeError("Dữ liệu đầu vào phải là danh sách.")

    # 2. Tạo hoạt động tham quan
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

    # 3. Tạo hoạt động nhà hàng
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

    # 4. Tạo hoạt động món ăn an toàn từ TV2
    food_activities = []

    for dish in safe_dishes:
        food_activities.append({
            "type": "food",
            "name": get_item_name(dish)
        })

    # 5. Kết hợp nhà hàng và món ăn
    other_activities = (
        restaurant_activities + food_activities
    )

    # 6. Khởi tạo lịch trình
    schedule = []

    for day_index in range(duration):
        schedule.append({
            "day": day_index + 1,
            "activities": []
        })

    # 7. Phân bổ địa điểm tham quan đều giữa các ngày
    total_places = len(place_activities)

    # Tổng sức chứa địa điểm tham quan
    max_capacity = duration * 2

    # Số địa điểm có thể đưa vào lịch trình
    scheduled_count = min(
        total_places,
        max_capacity
    )

    # Chia đều địa điểm cho các ngày
    base_count = scheduled_count // duration
    remainder = scheduled_count % duration

    place_index = 0

    for day_index in range(duration):

        # Số địa điểm cơ bản mỗi ngày
        places_per_day = base_count

        # Những ngày đầu nhận thêm một địa điểm nếu còn dư
        if day_index < remainder:
            places_per_day += 1

        # Lấy địa điểm cho ngày hiện tại
        daily_places = place_activities[
            place_index:place_index + places_per_day
        ]

        # Cập nhật vị trí địa điểm tiếp theo
        place_index += len(daily_places)

        # Thêm địa điểm vào lịch trình
        schedule[day_index]["activities"].extend(
            daily_places
        )

    # 8. Phân bổ nhà hàng và món ăn riêng
    for index, activity in enumerate(other_activities):

        day_index = index % duration

        schedule[day_index]["activities"].append(
            activity
        )

    # 9. Lưu địa điểm chưa được xếp lịch
    remaining_places = place_activities[place_index:]

    # 10. Tính tổng hoạt động đã được xếp lịch
    total_scheduled = sum(
        len(day["activities"])
        for day in schedule
    )

    # 11. Trả kết quả
    return {
        "success": True,
        "total_days": duration,
        "total_activities": total_scheduled,
        "schedule": schedule,
        "remaining_places": remaining_places
    }
