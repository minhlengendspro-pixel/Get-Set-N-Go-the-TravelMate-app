
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend_places(
    destination: str,
    interests: list,
    places: list,
    top_k: int = 10
):
    # 1. Validate input
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination cannot be empty")

    if not isinstance(interests, list):
        raise ValueError("Interests must be a list")

    if not interests or not any(str(tag).strip() for tag in interests):
        raise ValueError("Please select at least one interest")

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
       raise ValueError("top_k must be a positive integer")

    # 2. Normalize user interests
    user_tags = list(dict.fromkeys(
    str(tag).strip().casefold()
    for tag in interests
    if tag is not None and str(tag).strip()
))

    # 3. Filter by destination and non-empty tags
    candidates = []

    for place in places:
        if not isinstance(place, dict):
            continue
    
        place_destination = str(
            place.get("destination", "")
           ).strip().casefold()

        raw_tags = place.get("tags", [])

        if place_destination != destination.strip().casefold():
            continue

        if not isinstance(raw_tags, list) or not raw_tags:
            continue

        tags = list(dict.fromkeys(
            str(tag).strip().casefold()
            for tag in raw_tags
            if str(tag).strip()
        ))

        if not tags:
            continue

        candidates.append((place, tags))

    if not candidates:
        return []

    # 4. Build binary vectors
    place_tags = [tags for _, tags in candidates]

    mlb = MultiLabelBinarizer()
    vectors = mlb.fit_transform([user_tags] + place_tags)

    user_vector = vectors[0:1]
    place_vectors = vectors[1:]

    # 5. Calculate cosine similarity
    scores = cosine_similarity(
        user_vector,
        place_vectors
    )[0]

    # 6. Build results
    results = []

    for (place, tags), score in zip(candidates, scores):

        if score <= 0:
            continue

        results.append({
            "id": str(place.get("id", "")),
            "name": place.get("name", ""),
            "destination": place.get("destination", ""),
            "category": place.get("category"),
            "description": place.get("description"),
            "tags": tags,
            "rating": place.get("rating", 0),
            "image_url": place.get("image_url"),
            "score": round(float(score), 4),
            "matched_tags": sorted(set(user_tags) & set(tags))
        })

    # 7. Sort descending
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]
