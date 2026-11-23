
def normalize_tag(tag: str) -> str:
    """Chuẩn hóa tag để so sánh."""
    return str(tag).strip().lower()


def calculate_interest_score(
    schedule: list,
    user_tags: list,
    tag_weights: dict | None = None
) -> float:
    """Tính điểm phù hợp sở thích có xét trọng số từ TV1."""

    if not user_tags:
        return 1.0

    if tag_weights is None:
        tag_weights = {}

    normalized_weights = {
        normalize_tag(tag): float(weight)
        for tag, weight in tag_weights.items()
    }

    normalized_user_tags = [
        normalize_tag(tag) for tag in user_tags
    ]

    total_weight = sum(
        normalized_weights.get(tag, 1.0)
        for tag in normalized_user_tags
    )

    if total_weight <= 0:
        return 0.0

    place_scores = []

    for day in schedule:
        for activity in day.get("activities", []):

            if activity.get("type") != "place":
                continue

            place_tags = {
                normalize_tag(tag)
                for tag in activity.get("tags", [])
            }

            matched_weight = sum(
                normalized_weights.get(tag, 1.0)
                for tag in normalized_user_tags
                if tag in place_tags
            )

            place_score = matched_weight / total_weight
            place_scores.append(place_score)

    if not place_scores:
        return 0.0

    return sum(place_scores) / len(place_scores)


def calculate_restaurant_score(schedule: list) -> float:
    """Tính điểm chất lượng nhà hàng dựa trên rating TV3."""

    ratings = []

    for day in schedule:
        for activity in day.get("activities", []):

            if activity.get("type") != "restaurant":
                continue

            rating = activity.get("rating")

            if rating is None:
                continue

            try:
                rating = float(rating)
            except (TypeError, ValueError):
                continue

            if 0 <= rating <= 5:
                ratings.append(rating / 5)

    if not ratings:
        return 0.0

    return sum(ratings) / len(ratings)


def calculate_balance_score(counts: list) -> float:
    """Đánh giá mức độ cân bằng hoạt động giữa các ngày."""

    if not counts:
        return 0.0

    total = sum(counts)

    if total == 0:
        return 1.0

    average = total / len(counts)

    deviation = sum(
        abs(count - average)
        for count in counts
    )

    return 1 - deviation / (2 * total)


def calculate_distribution_score(schedule: list) -> float:
    """
    Đánh giá phân bổ hoạt động:
    - Tổng hoạt động mỗi ngày.
    - Địa điểm tham quan mỗi ngày.
    - Nhà hàng mỗi ngày.
    - Món ăn an toàn mỗi ngày.
    """

    if not schedule:
        return 0.0

    total_counts = []
    place_counts = []
    restaurant_counts = []
    food_counts = []

    for day in schedule:

        activities = day.get("activities", [])

        total_counts.append(len(activities))

        place_counts.append(
            sum(
                1 for activity in activities
                if activity.get("type") == "place"
            )
        )

        restaurant_counts.append(
            sum(
                1 for activity in activities
                if activity.get("type") == "restaurant"
            )
        )

        food_counts.append(
            sum(
                1 for activity in activities
                if activity.get("type") == "food"
            )
        )

    total_score = calculate_balance_score(total_counts)
    place_score = calculate_balance_score(place_counts)
    restaurant_score = calculate_balance_score(restaurant_counts)
    food_score = calculate_balance_score(food_counts)

    distribution_score = (
        total_score * 0.4
        + place_score * 0.2
        + restaurant_score * 0.2
        + food_score * 0.2
    )

    return distribution_score


def calculate_fitness(
    schedule: list,
    user_tags: list,
    tag_weights: dict | None = None
) -> dict:
    """Tính Fitness tổng hợp cho lịch trình."""

    interest_score = calculate_interest_score(
        schedule,
        user_tags,
        tag_weights
    )

    restaurant_score = calculate_restaurant_score(schedule)

    distribution_score = calculate_distribution_score(schedule)

    fitness = (
        interest_score * 0.5
        + restaurant_score * 0.3
        + distribution_score * 0.2
    )

    return {
        "fitness": round(fitness, 4),
        "details": {
            "interest_score": round(interest_score, 4),
            "restaurant_score": round(restaurant_score, 4),
            "distribution_score": round(distribution_score, 4)
        }
    }
