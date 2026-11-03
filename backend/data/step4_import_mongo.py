import json
import os
import sys
from pymongo import MongoClient

# Đảm bảo in tiếng Việt mượt mà trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 1. Cấu hình kết nối MongoDB Atlas (Kế thừa từ cấu hình chuẩn trong database.py của bạn)
MONGO_URI = "mongodb://minhlengendspro_db_user:minhduc123@ac-witmyyy-shard-00-00.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-01.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-02.e9bvp5a.mongodb.net:27017/?ssl=true&replicaSet=atlas-u5mki4-shard-0&authSource=admin&compressors=zlib"
DATABASE_NAME = "get_set_n_go_db"
COLLECTION_NAME = "Places"

# Đường dẫn file dữ liệu sạch
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENRICHED_JSON_PATH = os.path.join(CURRENT_DIR, "places_enriched.json")


def import_enriched_places():
    print("==================================================================")
    print("   CHẶNG 1: NẠP DỮ LIỆU ĐÃ DÁN NHÃN SẠCH VÀO MONGODB ATLAS       ")
    print("==================================================================")

    # 1. Kiểm tra sự tồn tại của file dữ liệu
    if not os.path.exists(ENRICHED_JSON_PATH):
        print(f"❌ LỖI: Không tìm thấy file {ENRICHED_JSON_PATH}")
        print("Hãy đảm bảo bạn đã chạy file sample3_enrich_rules.py trước đó.")
        return

    # 2. Đọc 315 bản ghi sạch
    print(f"1. Đang đọc dữ liệu từ: {os.path.basename(ENRICHED_JSON_PATH)}...")
    with open(ENRICHED_JSON_PATH, "r", encoding="utf-8") as f:
        places_data = json.load(f)

    total_records = len(places_data)
    print(f"-> Đã tải thành công {total_records} địa điểm sạch vào bộ nhớ.")

    # 3. Kết nối MongoDB
    print("\n2. Đang kết nối tới MongoDB Atlas...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Ping kiểm tra đường truyền
        client.admin.command("ping")
        print("-> Kết nối tới MongoDB Atlas thành công!")

        # 4. Làm sạch dữ liệu cũ trong collection Places
        print(f"\n3. Đang dọn dẹp collection '{COLLECTION_NAME}'...")
        delete_result = collection.delete_many({})
        print(f"-> Đã xóa {delete_result.deleted_count} bản ghi cũ.")

        # 5. Nạp toàn bộ 315 bản ghi mới
        print(f"\n4. Đang nạp {total_records} bản ghi mới kèm Tags chuẩn...")
        insert_result = collection.insert_many(places_data)
        print(f"-> Nạp thành công {len(insert_result.inserted_ids)} bản ghi vào Database!")

        # 6. Kiểm chứng dữ liệu thực tế trên Database
        current_count = collection.count_documents({})
        print(f"\n5. KIỂM CHỨNG DỮ LIỆU TRÊN DATABASE:")
        print(f"-> Tổng số Document hiện tại trong '{COLLECTION_NAME}': {current_count}")

        # Lấy thử mẫu Đình làng Nôm từ Database ra để kiểm tra
        sample_doc = collection.find_one({"name": "Đình làng Nôm"})
        if sample_doc:
            print("\n--- MẪU DỮ LIỆU TRÊN ATLAS (ĐÌNH LÀNG NÔM) ---")
            print(" - Tên:     ", sample_doc.get("name"))
            print(" - Vị trí:  ", sample_doc.get("destination"))
            print(" - Tags:    ", sample_doc.get("tags"))
            print(" - Mô tả:   ", sample_doc.get("description")[:80], "...")

        client.close()
        print("\n==================================================================")
        print("✅ HOÀN TẤT CHẶNG 1 XUẤT SẮC! CƠ SỞ DỮ LIỆU ĐÃ SẴN SÀNG.")
        print("==================================================================")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi kết nối MongoDB: {e}")


if __name__ == "__main__":
    import_enriched_places()
