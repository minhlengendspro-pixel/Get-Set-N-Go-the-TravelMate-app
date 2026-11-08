
import pandas as pd

from services.place_recommendation import recommend_places

# Đọc dữ liệu Excel
df = pd.read_excel("backend/data/DataSet.xlsx")

# Chuẩn hóa tên cột
df.columns = df.columns.str.strip()

# Chuyển dữ liệu Excel thành list dictionary
places = []

for _, row in df.iterrows():
    raw_tags = row.get("Từ Khóa", [])

    if pd.isna(raw_tags):
        tags = []
    else:
        tags = [
    tag.strip().strip('"').strip("'").strip().casefold()
    for tag in str(raw_tags).split(",")
    if tag.strip().strip('"').strip("'").strip()
]

    places.append({
        "id": str(row["STT"]),
        "name": row["Tên địa điểm"],
        "destination": row["Vị trí"],
        "description": row.get("Mô tả", ""),
        "rating": row.get("Đánh giá", 0),
        "image_url": row.get("Ảnh", ""),
        "tags": tags
    })

print("\n========== DEBUG DATA ==========")

khanh_hoa = [
    p for p in places
    if p["destination"].strip().casefold() == "khánh hòa".casefold()
]

print("Số địa điểm ở Khánh Hòa:", len(khanh_hoa))

for p in khanh_hoa[:10]:
    print("Tên:", p["name"])
    print("Tags:", p["tags"])
    print("--------------------")
# Thử nghiệm đề xuất
results = recommend_places(
    destination="Khánh Hòa",
    interests=["biển", "chụp ảnh"],
    places=places,
    top_k=10
)

print(f"Tổng địa điểm trong dataset: {len(places)}")
print(f"Số địa điểm được đề xuất: {len(results)}")

for i, place in enumerate(results, 1):
    print(f"\n{i}. {place['name']}")
    print(f"   Tags: {place['tags']}")
    print(f"   Matched tags: {place['matched_tags']}")
    print(f"   Similarity: {place['score']}")
