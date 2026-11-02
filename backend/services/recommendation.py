
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend_places(
    destination: str,
    interests: list,
    places: list,
    top_k: int = 10
):
    # 1. Kiểm tra đầu vào
    if not destination:
        raise ValueError("Destination cannot be empty")

    if not isinstance(interests, list):
        raise ValueError("Interests must be a list")

    if top_k < 1:
        raise ValueError("top_k must be greater than 0")

    # 2. Lọc địa điểm theo thành phố
    candidates = [
        place for place in places
        if place.get("destination", "").strip().casefold()
        == destination.strip().casefold()
    ]

    if not candidates:
        return []

    # 3. Chuẩn hóa tags và interests
    user_tags = [
        str(tag).strip().lower()
        for tag in interests
    ]

    place_tags = [
        [
            str(tag).strip().lower()
            for tag in place.get("tags", [])
        ]
        for place in candidates
    ]

    # 4. Tạo bộ từ vựng chung
    all_tags = [user_tags] + place_tags

    mlb = MultiLabelBinarizer()
    vectors = mlb.fit_transform(all_tags)

    # 5. Tách vector người dùng và vector địa điểm
    user_vector = vectors[0:1]
    place_vectors = vectors[1:]

    # 6. Tính Cosine Similarity
    scores = cosine_similarity(
        user_vector,
        place_vectors
    )[0]

    # 7. Tạo kết quả
    results = []

    for place, score in zip(candidates, scores):

        matched_tags = sorted(
            set(user_tags) & set(
                tag.lower() for tag in place.get("tags", [])
            )
        )

        results.append({
            "id": place["id"],
            "name": place["name"],
            "destination": place["destination"],
            "category": place["category"],
            "description": place["description"],
            "tags": place["tags"],
            "score": round(float(score), 4),
            "matched_tags": matched_tags
        })

    # 8. Sắp xếp theo điểm giảm dần
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]
