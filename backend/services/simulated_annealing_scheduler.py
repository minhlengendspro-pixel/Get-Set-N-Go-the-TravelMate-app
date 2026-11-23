
import copy
import math
import random

from services.scheduler_fitness import calculate_fitness


def generate_neighbor(schedule: list) -> list:
    """Chuyển một hoạt động từ ngày này sang ngày khác."""

    neighbor = copy.deepcopy(schedule)

    available_days = [
        index
        for index, day in enumerate(neighbor)
        if day["activities"]
    ]

    if len(neighbor) < 2 or not available_days:
        return neighbor

    source_index = random.choice(available_days)

    destination_options = [
        index
        for index in range(len(neighbor))
        if index != source_index
    ]

    destination_index = random.choice(destination_options)

    activity_index = random.randrange(
        len(neighbor[source_index]["activities"])
    )

    activity = neighbor[source_index]["activities"].pop(
        activity_index
    )

    neighbor[destination_index]["activities"].append(activity)

    return neighbor


def simulated_annealing(
    initial_schedule: list,
    user_tags: list,
    tag_weights: dict | None = None,
    initial_temperature: float = 1.0,
    cooling_rate: float = 0.995,
    iterations: int = 1000
) -> dict:
    """Tối ưu cách phân bổ hoạt động giữa các ngày."""

    current_schedule = copy.deepcopy(initial_schedule)
    best_schedule = copy.deepcopy(initial_schedule)

    current_result = calculate_fitness(
        current_schedule,
        user_tags,
        tag_weights
    )

    best_result = current_result

    # Lưu điểm ban đầu để so sánh
    initial_result = current_result

    temperature = initial_temperature

    for _ in range(iterations):

        if temperature < 0.0001:
            break

        neighbor = generate_neighbor(current_schedule)

        neighbor_result = calculate_fitness(
            neighbor,
            user_tags,
            tag_weights
        )

        difference = (
            neighbor_result["fitness"]
            - current_result["fitness"]
        )

        if difference > 0:
            accept = True
        else:
            probability = math.exp(
                difference / temperature
            )
            accept = random.random() < probability

        if accept:
            current_schedule = neighbor
            current_result = neighbor_result

        if current_result["fitness"] > best_result["fitness"]:
            best_schedule = copy.deepcopy(current_schedule)
            best_result = current_result

        temperature *= cooling_rate

    return {
        "success": True,
        "initial_fitness": initial_result,
        "best_fitness": best_result,
        "schedule": best_schedule
    }
