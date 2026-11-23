
from collections import Counter
from database import db

collection = db["Places"]

places = list(collection.find(
    {"tags": {"$type": "array"}},
    {"name": 1, "tags": 1}
))

tag_frequency = Counter()

for place in places:
    tags = place.get("tags", [])

    # Mỗi địa điểm chỉ tính một lần cho mỗi tag
    unique_tags = {
        tag.strip().casefold()
        for tag in tags
        if isinstance(tag, str) and tag.strip()
    }

    tag_frequency.update(unique_tags)

print("===== TAG FREQUENCY =====")
print("Total places:", len(places))
print("Total unique tags:", len(tag_frequency))

print("\n===== TOP 30 MOST COMMON TAGS =====")

for tag, count in tag_frequency.most_common(30):
    percentage = count / len(places) * 100

    print(
        f"{tag}: {count}/{len(places)} "
        f"({percentage:.2f}%)"
    )
