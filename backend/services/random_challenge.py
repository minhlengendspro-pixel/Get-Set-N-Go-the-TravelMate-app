
import random
import math
import unicodedata


# 1. Chuan hoa tag
def normalize_tag(tag):
    if not isinstance(tag, str):
        return ""

    tag = unicodedata.normalize("NFC", tag)
    return tag.strip().casefold()



def get_available_tags(places):
    tag_counts = {}
    total_places = len(places)

    if total_places == 0:
        return []

    # Đếm số địa điểm có chứa từng tag
    for place in places:
        unique_tags = set(
            normalize_tag(tag)
            for tag in place.get("tags", [])
            if normalize_tag(tag)
        )

        for tag in unique_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Loại tag tên tỉnh/thành
    location_tags = {
        normalize_tag(place.get("destination", ""))
        for place in places
        if place.get("destination")
    }

    # Ngưỡng tần suất thích ứng
    min_frequency = 2

    if total_places <= 10:
        max_frequency = 0.80
    else:
        max_frequency = 0.30

    available_tags = [
        tag
        for tag, count in tag_counts.items()
        if count >= min_frequency
        and count / total_places <= max_frequency
        and tag not in location_tags
    ]

    return sorted(available_tags)



# 3. Chon ngau nhien tu 2 den 4 tags
def generate_random_tags(available_tags):
    available_tags = sorted({
        normalize_tag(tag)
        for tag in available_tags
        if normalize_tag(tag)
    })

    if len(available_tags) < 2:
        raise ValueError("Khong du tags de tao thu thach")

    tag_count = random.randint(2, min(4, len(available_tags)))

    return random.sample(available_tags, tag_count)


# 4. Tao to hop tags moi (Neighbor)
def generate_neighbor(current_tags, available_tags):
    available_tags = sorted({
        normalize_tag(tag)
        for tag in available_tags
        if normalize_tag(tag)
    })

    new_tags = list(dict.fromkeys(
        normalize_tag(tag)
        for tag in current_tags
        if normalize_tag(tag)
    ))

    if len(available_tags) < 2:
        return new_tags

    operations = ["replace"]

    if len(new_tags) < 4 and len(new_tags) < len(available_tags):
        operations.append("add")

    if len(new_tags) > 2:
        operations.append("remove")

    operation = random.choice(operations)

    if operation == "replace" and new_tags:
        candidates = [
            tag for tag in available_tags
            if tag not in new_tags
        ]

        if candidates:
            index = random.randrange(len(new_tags))
            new_tags[index] = random.choice(candidates)

    elif operation == "add":
        candidates = [
            tag for tag in available_tags
            if tag not in new_tags
        ]

        if candidates:
            new_tags.append(random.choice(candidates))

    elif operation == "remove" and len(new_tags) > 2:
        new_tags.pop(random.randrange(len(new_tags)))

    return new_tags


# 5. Danh gia to hop tags
def evaluate_tags(tags, places):
    if not tags or not places:
        return 0.0, []

    selected_tags = list(dict.fromkeys(
        normalize_tag(tag)
        for tag in tags
        if normalize_tag(tag)
    ))

    if not selected_tags:
        return 0.0, []

    matched_places = []
    valid_places_count = 0

    for place in places:
        if not isinstance(place, dict):
            continue

        valid_places_count += 1

        place_tags = place.get("tags", [])

        if not isinstance(place_tags, list):
            place_tags = []

        normalized_place_tags = {
            normalize_tag(tag)
            for tag in place_tags
            if normalize_tag(tag)
        }

        matched_tags = [
            tag for tag in selected_tags
            if tag in normalized_place_tags
        ]

        if matched_tags:
            result = place.copy()
            result["matched_tags"] = matched_tags
            result["match_count"] = len(matched_tags)
            result["match_ratio"] = (
                len(matched_tags) / len(selected_tags)
            )

            matched_places.append(result)

    if not matched_places or valid_places_count == 0:
        return 0.0, []

    coverage = len(matched_places) / valid_places_count

    average_match = sum(
        place["match_ratio"]
        for place in matched_places
    ) / len(matched_places)

    fitness = coverage * average_match

    return round(fitness, 4), matched_places


# 6. Thuat toan Simulated Annealing
def simulated_annealing(
    places,
    max_iterations=100,
    initial_temperature=1.0,
    cooling_rate=0.95
):
    available_tags = get_available_tags(places)

    if len(available_tags) < 2:
        raise ValueError(
            "Can it nhat 2 tags hop le de chay Random Challenge"
        )

    current_tags = generate_random_tags(available_tags)

    current_fitness, current_places = evaluate_tags(
        current_tags, places
    )

    best_tags = current_tags.copy()
    best_fitness = current_fitness
    best_places = current_places

    temperature = initial_temperature

    for _ in range(max_iterations):
        if temperature <= 0.0001:
            break

        neighbor_tags = generate_neighbor(
            current_tags,
            available_tags
        )

        neighbor_fitness, neighbor_places = evaluate_tags(
            neighbor_tags, places
        )

        difference = neighbor_fitness - current_fitness

        if difference > 0:
            accept = True
        else:
            probability = math.exp(difference / temperature)
            accept = random.random() < probability

        if accept:
            current_tags = neighbor_tags
            current_fitness = neighbor_fitness
            current_places = neighbor_places

        if current_fitness > best_fitness:
            best_tags = current_tags.copy()
            best_fitness = current_fitness
            best_places = current_places

        temperature *= cooling_rate

    best_places = sorted(
        best_places,
        key=lambda place: place["match_count"],
        reverse=True
    )

    return {
        "tags": best_tags,
        "fitness": best_fitness,
        "places": best_places[:5]
    }



# 7. Chay Random Challenge
def run_random_challenge(places):
    # Lay danh sach tag hop le tu MongoDB
    available_tags = get_available_tags(places)

    if len(available_tags) < 2:
        raise ValueError(
            "Can it nhat 2 tags hop le de chay Random Challenge"
        )

    # Moi lan goi API se chon ngau nhien 2-4 tags
    selected_tags = generate_random_tags(available_tags)

    # Danh gia fitness, khong thay doi bo tag
    fitness, matched_places = evaluate_tags(
        selected_tags,
        places
    )

    # Sap xep dia diem theo so tag khop
    matched_places = sorted(
        matched_places,
        key=lambda place: place["match_count"],
        reverse=True
    )

    return {
        "tags": selected_tags,
        "fitness": fitness,
        "places": matched_places[:5]
    }

