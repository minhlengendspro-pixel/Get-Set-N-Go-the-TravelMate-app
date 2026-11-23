
from services.scheduler import generate_schedule
from services.simulated_annealing_scheduler import simulated_annealing


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
    """

    # 1. Lấy thông tin từ TV1
    destination = input_context.get("destination")
    mode = input_context.get("mode", "solo")
    duration = input_context.get("duration", 1)

    user_tags = input_context.get(
        "tags",
        input_context.get("interests", [])
    )

    tag_weights = input_context.get("tag_weights", {})

    # 2. Kiểm tra dữ liệu đầu vào
    if not isinstance(places, list):
        raise TypeError("Places phải là danh sách.")

    if not isinstance(user_tags, list):
        raise TypeError("Tags phải là danh sách.")

    if not isinstance(tag_weights, dict):
        raise TypeError("Tag weights phải là dictionary.")

    if not isinstance(duration, int) or duration < 1:
        raise ValueError("Duration phải là số nguyên lớn hơn 0.")

    if mode not in ["solo", "couple", "family", "random"]:
        raise ValueError("Mode không hợp lệ.")

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

    # 5. Tạo lịch trình ban đầu
    initial_result = generate_schedule(
        places=places,
        restaurants=restaurants,
        duration=duration,
        safe_dishes=safe_dishes
    )

    initial_schedule = initial_result["schedule"]

    # 6. Chỉ chạy Simulated Annealing khi mode là random
    if mode == "random":

        optimization_result = simulated_annealing(
            initial_schedule=initial_schedule,
            user_tags=user_tags,
            tag_weights=tag_weights
        )

        final_schedule = optimization_result["schedule"]

        fitness_result = optimization_result["best_fitness"]

        initial_fitness = optimization_result["initial_fitness"]

    else:
        final_schedule = initial_schedule
        fitness_result = None
        initial_fitness = None

    # 7. Trả kết quả
    total_activities = sum(
        len(day["activities"])
        for day in final_schedule
    )

    return {
        "success": True,
        "destination": destination,
        "mode": mode,
        "total_days": duration,
        "total_activities": total_activities,
        "optimized": mode == "random",
        "initial_fitness": initial_fitness,
        "best_fitness": fitness_result,
        "schedule": final_schedule
    }
