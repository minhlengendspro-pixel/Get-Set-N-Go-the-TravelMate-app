"""
step5_import_foods.py — Nạp dữ liệu món ăn vào MongoDB Atlas
Đảm bảo kiểm tra toàn vẹn dữ liệu (destination matching & unique id)
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Import database connection
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CURRENT_DIR, ".."))
from database import db

FOODS_PATH = os.path.join(CURRENT_DIR, "foods_data.json")


def validate_destinations(foods, places_collection):
    """Kiểm tra tất cả destination trong foods khớp với Places collection."""
    valid_dests = set(
        doc["destination"]
        for doc in places_collection.find({}, {"destination": 1, "_id": 0})
    )

    errors = []
    for food in foods:
        if food["destination"] not in valid_dests:
            errors.append(
                f"  ❌ {food['id']} ({food['name']}): "
                f"destination '{food['destination']}' không tồn tại trong Places!"
            )
    return errors


def validate_no_duplicate_ids(foods):
    """Kiểm tra không có id trùng lặp."""
    seen = {}
    dupes = []
    for f in foods:
        if f["id"] in seen:
            dupes.append(f"  ❌ ID trùng: {f['id']} ({f['name']} vs {seen[f['id']]})")
        seen[f["id"]] = f["name"]
    return dupes


def run():
    print("=" * 66)
    print("   BƯỚC 5: NẠP DỮ LIỆU MÓN ĂN VÀO MONGODB ATLAS (COLLECTION: Foods)   ")
    print("=" * 66)

    # 1. Đọc file JSON
    if not os.path.exists(FOODS_PATH):
        print(f"❌ Không tìm thấy file: {FOODS_PATH}")
        return

    with open(FOODS_PATH, "r", encoding="utf-8") as f:
        foods = json.load(f)
    print(f"\n📖 Đọc được {len(foods)} món ăn từ foods_data.json")

    # 2. Validate destinations against MongoDB Places
    print("\n🔍 Kiểm tra tính nhất quán destination với collection Places...")
    dest_errors = validate_destinations(foods, db.Places)
    if dest_errors:
        print("⚠️ Phát hiện lỗi destination KHÔNG KHỚP với Places:")
        for e in dest_errors[:10]:
            print(e)
        if len(dest_errors) > 10:
            print(f"... và {len(dest_errors) - 10} lỗi khác.")
        print("\n❌ DỪNG IMPORT. Hãy sửa lỗi trước khi tiếp tục.")
        return

    # 3. Validate unique IDs
    dupe_errors = validate_no_duplicate_ids(foods)
    if dupe_errors:
        print("⚠️ Phát hiện ID trùng lặp:")
        for e in dupe_errors:
            print(e)
        print("\n❌ DỪNG IMPORT. Hãy sửa lỗi trước khi tiếp tục.")
        return

    print("✅ Tất cả destination đều khớp 100% với collection Places.")
    print("✅ Không có ID trùng lặp.")

    # 4. Xóa collection cũ (nếu có) và import mới
    foods_collection = db.Foods
    old_count = foods_collection.count_documents({})
    if old_count > 0:
        print(f"\n🗑️ Xóa {old_count} documents cũ trong collection Foods...")
        foods_collection.delete_many({})

    # 5. Bulk insert
    result = foods_collection.insert_many(foods)
    print(f"\n✅ ĐÃ NẠP THÀNH CÔNG {len(result.inserted_ids)} món ăn vào MongoDB!")

    # 6. Tạo index hỗ trợ tìm kiếm nhanh
    foods_collection.create_index("destination")
    foods_collection.create_index("food_type")
    foods_collection.create_index("tags")
    print("📇 Đã tạo index: 'destination', 'food_type', 'tags'")

    # 7. Thống kê
    pipeline = [
        {"$group": {"_id": "$destination", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    stats = list(foods_collection.aggregate(pipeline))
    print(f"\n📊 Tổng cộng: {len(stats)} tỉnh/thành đã nạp dữ liệu món ăn.")

    print("\n" + "=" * 66)
    print("🎉 HOÀN TẤT NẠP DỮ LIỆU FOODS VÀO MONGODB ATLAS!")
    print("=" * 66)


if __name__ == "__main__":
    run()
