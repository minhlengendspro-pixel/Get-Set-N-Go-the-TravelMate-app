from services.scheduler import generate_schedule


def extract_list(result, key):
    """
    Lấy danh sách từ kết quả module khác.

    Hỗ trợ:
    - Danh sách trực tiếp
    - {"safe_dishes": [...]}
    - {"data": {"safe_dishes": [...]}}
    """

    if isinstance(result, list):
        return result

    if not isinstance(result, dict):
        return []

    if isinstance(result.get(key), list):
        return result[key]

    data = result.get("data")

    if isinstance(data, dict):
        if isinstance(data.get(key), list):
            return data[key]

    return []


def run_scheduler(
    input_context: dict,
    places: list,
    tv2_result,
    tv3_result
) -> dict:
    """
    Điều phối dữ liệu từ TV1, TV2, TV3
    và tạo lịch trình bằng Scheduler của TV4.

    Scheduler chỉ có nhiệm vụ phân chia hoạt động
    thành các ngày. Không chạy Simulated Annealing.
    """

    # 1. Lấy thông tin từ TV1
    destination = input_context.get("destination")
    duration = input_context.get("duration", 1)

    # 2. Kiểm tra dữ liệu đầu vào
    if not isinstance(input_context, dict):
        raise TypeError("Input context phải là dictionary.")

    if not isinstance(places, list):
        raise TypeError("Places phải là danh sách.")

    if not isinstance(duration, int) or duration < 1:
        raise ValueError(
            "Duration phải là số nguyên lớn hơn 0."
        )

    # 3. Lấy dữ liệu từ TV2
    safe_dishes = extract_list(
        tv2_result,
        "safe_dishes"
    )

    # 4. Lấy dữ liệu từ TV3
    restaurants = extract_list(
        tv3_result,
        "restaurants"
    )

    # 5. Tạo lịch trình
    schedule_result = generate_schedule(
        places=places,
        restaurants=restaurants,
        duration=duration,
        safe_dishes=safe_dishes
    )

    # 6. Lấy lịch trình đã được phân chia theo ngày
    final_schedule = schedule_result["schedule"]

    total_activities = sum(
        len(day.get("activities", []))
        for day in final_schedule
    )

    # 7. Trả kết quả
    return {
        "success": True,
        "destination": destination,
        "total_days": duration,
        "total_activities": total_activities,
        "schedule": final_schedule,
        "remaining_places": schedule_result.get(
            "remaining_places",
            []
        )
    }