"""
test_food_output.py — Công cụ kiểm tra dữ liệu Món ăn (Input -> Output)
Dành riêng cho Data Specialist để kiểm tra dữ liệu đã nạp trên MongoDB Atlas
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import db


def check_food_by_destination(destination: str):
    """
    INPUT: Tên tỉnh/thành phố
    OUTPUT: Danh sách món ăn đặc sản tương ứng trong Database
    """
    print(f"\n=======================================================")
    print(f"👉 INPUT (Điểm đến): '{destination}'")
    print(f"=======================================================")

    foods = list(db.Foods.find(
        {"destination": {"$regex": f"^{destination.strip()}$", "$options": "i"}},
        {"_id": 0}
    ))

    if not foods:
        print(f"❌ Không tìm thấy món ăn nào cho '{destination}'")
        return

    print(f"✅ OUTPUT: Tìm thấy {len(foods)} món ăn trong Database:")
    for idx, f in enumerate(foods, start=1):
        print(f"\n  [{idx}] {f['name']} (ID: {f['id']}) - Rating: {f['rating']}⭐")
        print(f"      - Phân loại: {f['food_type']}")
        print(f"      - Tags:      {f['tags']}")
        print(f"      - Mô tả:     {f['description']}")


if __name__ == "__main__":
    # Nhập thử nghiệm các tỉnh thành
    sample_provinces = ["Khánh Hòa", "Hà Nội", "Cần Thơ"]
    for prov in sample_provinces:
        check_food_by_destination(prov)
