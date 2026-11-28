
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
            or item.get("dish_name")
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
    - Chỉ đưa địa điểm và nhà hàng vào lịch trình.
    - Giữ nguyên toàn bộ dữ liệu gốc của địa điểm và nhà hàng.
    - Món ăn không được tạo thành hoạt động riêng.
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
    # Giữ toàn bộ thông tin gốc của địa điểm.
    place_activities = []

    for place in places:

        if isinstance(place, dict):
            activity = place.copy()

            activity["type"] = "place"
            activity["name"] = get_item_name(place)

        else:
            activity = {
                "type": "place",
                "name": get_item_name(place)
            }

        place_activities.append(activity)

    # 3. Tạo hoạt động nhà hàng
    # Giữ toàn bộ thông tin gốc, bao gồm safe_dishes/dishes
    # nếu dữ liệu nhà hàng đã có những trường này.
    restaurant_activities = []

    for restaurant in restaurants:

        if isinstance(restaurant, dict):
            activity = restaurant.copy()

            activity["type"] = "restaurant"
            activity["name"] = get_item_name(restaurant)

        else:
            activity = {
                "type": "restaurant",
                "name": get_item_name(restaurant)
            }

        restaurant_activities.append(activity)

    # 4. Không tạo hoạt động món ăn riêng.
    # safe_dishes được giữ lại trong dữ liệu đầu vào để tương thích
    # với luồng xử lý hiện tại, nhưng không được thêm vào lịch trình.

    # 5. Khởi tạo lịch trình
    schedule = []

    for day_index in range(duration):
        schedule.append({
            "day": day_index + 1,
            "activities": []
        })

    # 6. Phân bổ địa điểm tham quan đều giữa các ngày
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

    # 7. Phân bổ nhà hàng riêng
    for index, activity in enumerate(restaurant_activities):

        day_index = index % duration

        schedule[day_index]["activities"].append(
            activity
        )

    # 8. Lưu địa điểm chưa được xếp lịch
    remaining_places = place_activities[place_index:]

    # 9. Tính tổng hoạt động đã được xếp lịch
    total_scheduled = sum(
        len(day["activities"])
        for day in schedule
    )

    # 10. Trả kết quả
    return {
        "success": True,
        "total_days": duration,
        "total_activities": total_scheduled,
        "schedule": schedule,
        "remaining_places": remaining_places
    }
