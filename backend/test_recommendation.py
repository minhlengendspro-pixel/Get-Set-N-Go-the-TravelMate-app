
from services.test_data import places
from services.recommendation import recommend_places


# Giả lập yêu cầu của người dùng
destination = "Da Nang"
interests = ["beach", "nature"]

# Gọi thuật toán
results = recommend_places(
    destination=destination,
    interests=interests,
    places=places,
    top_k=10
)

# In kết quả
print("\n=== TRAVELMATE RECOMMENDATIONS ===")

for index, place in enumerate(results, start=1):
    print(f"\nRank: {index}")
    print(f"Name: {place['name']}")
    print(f"Score: {place['score']}")
    print(f"Matched tags: {place['matched_tags']}")
