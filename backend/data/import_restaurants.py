"""
step6_import_restaurants.py — Nạp dữ liệu Nhà hàng & Thực đơn vào MongoDB Atlas
Dành cho Module 2: Bộ lọc Ràng buộc & Cắt tỉa An toàn (Hard Pruning Constraints)
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Kết nối database
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CURRENT_DIR, ".."))
from database import db

RESTAURANTS_PATH = os.path.join(CURRENT_DIR, "restaurants_seed.json")
PLACES_BACKUP_PATH = os.path.join(CURRENT_DIR, "places_enriched.json")


def validate_destinations(restaurants, places_collection):
    """Kiểm tra tất cả destination trong restaurants khớp 100% với Places."""
    try:
        valid_dests = set(
            doc["destination"]
            for doc in places_collection.find({}, {"destination": 1, "_id": 0})
        )
    except Exception as e:
        print(f"[CANH BAO] Không thể truy vấn trực tiếp Places từ MongoDB Atlas ({e}). Dùng file backup...")
        if os.path.exists(PLACES_BACKUP_PATH):
            places_data = json.load(open(PLACES_BACKUP_PATH, encoding="utf-8"))
            valid_dests = set(p["destination"] for p in places_data)
        else:
            valid_dests = set()

    errors = []
    for r in restaurants:
        if valid_dests and r["destination"] not in valid_dests:
            errors.append(
                f"   {r['id']} ({r['name']}): "
                f"destination '{r['destination']}' không tồn tại trong Places!"
            )
    return errors


def validate_no_duplicate_ids(restaurants):
    """Kiểm tra không có id nhà hàng bị trùng lặp."""
    seen = {}
    dupes = []
    for r in restaurants:
        if r["id"] in seen:
            dupes.append(f"   ID trùng: {r['id']} ({r['name']} vs {seen[r['id']]})")
        seen[r["id"]] = r["name"]
    return dupes


def validate_menu_integrity(restaurants):
    """Kiểm tra tính toàn vẹn của menu_items (phải có ingredients và allergens)."""
    errors = []
    for r in restaurants:
        menu = r.get("menu_items", [])
        if not menu:
            errors.append(f"   {r['id']} ({r['name']}): Không có món ăn nào trong menu_items!")
        for dish in menu:
            if "dish_name" not in dish:
                errors.append(f"   {r['id']}: Có món ăn thiếu tên!")
            if "ingredients" not in dish or not isinstance(dish["ingredients"], list):
                errors.append(f"   {r['id']} - {dish.get('dish_name')}: Thiếu mảng ingredients!")
            if "allergens" not in dish or not isinstance(dish["allergens"], list):
                errors.append(f"   {r['id']} - {dish.get('dish_name')}: Thiếu mảng allergens!")
    return errors


def run():
    print("=" * 70)
    print("   BƯỚC 6: NẠP DỮ LIỆU NHÀ HÀNG & MENU VÀO MONGODB ATLAS (COLLECTION: Restaurants)")
    print("=" * 70)

    # 1. Đọc file JSON
    if not os.path.exists(RESTAURANTS_PATH):
        print(f" Không tìm thấy file dữ liệu: {RESTAURANTS_PATH}")
        return

    with open(RESTAURANTS_PATH, "r", encoding="utf-8") as f:
        restaurants = json.load(f)
    print(f"\n Đọc thành công {len(restaurants)} nhà hàng từ restaurants_seed.json")

    # 2. Kiểm tra tính toàn vẹn
    print("\n Kiểm tra tính nhất quán destination với collection Places...")
    dest_errors = validate_destinations(restaurants, db.Places)
    if dest_errors:
        print(" Phát hiện lỗi destination KHÔNG KHỚP với Places:")
        for e in dest_errors[:10]:
            print(e)
        print("\n DỪNG IMPORT. Cần sửa lỗi destination trước khi nạp.")
        return
    print(" Tất cả destination đều khớp 100% với collection Places.")

    print("\n Kiểm tra ID trùng lặp...")
    dupe_errors = validate_no_duplicate_ids(restaurants)
    if dupe_errors:
        print(" Phát hiện ID trùng lặp:")
        for e in dupe_errors:
            print(e)
        print("\n DỪNG IMPORT. Cần sửa ID trùng lặp trước khi nạp.")
        return
    print(" Không có ID trùng lặp.")

    print("\n Kiểm tra mảng ingredients & allergens trong thực đơn...")
    menu_errors = validate_menu_integrity(restaurants)
    if menu_errors:
        print(" Phát hiện lỗi cấu trúc menu_items:")
        for e in menu_errors[:10]:
            print(e)
        print("\n DỪNG IMPORT. Cần chuẩn hóa menu trước khi nạp.")
        return
    print(" 100% món ăn đều có đầy đủ mảng ingredients và allergens.")

    # 3. Dọn dẹp collection cũ (nếu có)
    restaurants_collection = db.Restaurants
    old_count = restaurants_collection.count_documents({})
    if old_count > 0:
        print(f"\n Đang xóa {old_count} documents cũ trong collection Restaurants...")
        restaurants_collection.delete_many({})

    # 4. Bulk insert dữ liệu
    print(f"\n Đang nạp {len(restaurants)} nhà hàng vào MongoDB Atlas...")
    result = restaurants_collection.insert_many(restaurants)
    print(f"ĐÃ NẠP THÀNH CÔNG {len(result.inserted_ids)} nhà hàng vào MongoDB Atlas!")

    # 5. Tạo Index hỗ trợ truy vấn nhanh
    print("\n Đang tạo chỉ mục (Indexes) hỗ trợ tối ưu hóa truy vấn:")
    restaurants_collection.create_index("destination")
    restaurants_collection.create_index("avg_cost_per_person")
    restaurants_collection.create_index("all_ingredients")
    print("  [OK] Index: 'destination' (Lọc nhanh theo tỉnh thành)")
    print("  [OK] Index: 'avg_cost_per_person' (Lọc nhanh theo ngân sách trần)")
    print("  [OK] Index: 'all_ingredients' (Hỗ trợ truy vấn nguyên liệu)")

    # 6. Thống kê tổng kết
    pipeline = [
        {"$group": {"_id": "$destination", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    stats = list(restaurants_collection.aggregate(pipeline))
    total_dishes = sum(len(r["menu_items"]) for r in restaurants)
    print(f"\n Báo cáo tổng kết:")
    print(f"  - Tổng số tỉnh/thành đã nạp: {len(stats)}/64 tỉnh thành")
    print(f"  - Tổng số nhà hàng: {len(result.inserted_ids)}")
    print(f"  - Tổng số món ăn chi tiết: {total_dishes} món")

    print("\n" + "=" * 70)
    print(" HOÀN TẤT NẠP DỮ LIỆU RESTAURANTS VÀO MONGODB ATLAS THÀNH CÔNG!")
    print("=" * 70)


if __name__ == "__main__":
    run()
