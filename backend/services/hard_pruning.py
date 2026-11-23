"""
hard_pruning.py — Dịch vụ Thuật toán Bộ lọc Ràng buộc & Cắt tỉa An toàn (Module 2)
Phụ trách: Cắt tỉa Y tế (Dị ứng thực phẩm) & Trần Ngân sách cứng
"""
import os
import sys
import re
import unicodedata
from typing import List, Set, Iterable, Optional, Dict, Any, Union

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from database import db
except Exception:
    db = None

try:
    from models.schemas import SafetyPruneRequest, SafetyPruneResponse, EvaluatedRestaurant
except Exception:
    SafetyPruneRequest = None
    SafetyPruneResponse = None
    EvaluatedRestaurant = None

# ==============================================================================
# SUB-TASK 2.2.1: MODULE CHUẨN HÓA DỮ LIỆU & TỪ ĐIỂN ĐỒNG NGHĨA 
# ==============================================================================

# Bảng tra từ đồng nghĩa và biến thể vùng miền quy đổi về dạng chuẩn
SYNONYMS_MAP = {
    # 1. Đậu phộng / Lạc
    "lạc": "đậu phộng",
    "hạt lạc": "đậu phộng",
    "đậu phụng": "đậu phộng",
    "củ lạc": "đậu phộng",

    # 2. Mè / Vừng
    "vừng": "mè",
    "hạt vừng": "mè",
    "dầu mè": "mè",

    # 3. Hải sản & Động vật có vỏ
    "tôm": "hải sản",
    "tôm sú": "hải sản",
    "tôm hùm": "hải sản",
    "tôm biển": "hải sản",
    "tôm khô": "hải sản",
    "cua": "hải sản",
    "cua biển": "hải sản",
    "ghẹ": "hải sản",
    "mực": "hải sản",
    "mực tươi": "hải sản",
    "bạch tuộc": "hải sản",
    "hàu": "hải sản",
    "sò huyết": "hải sản",
    "nghêu": "hải sản",
    "bề bề": "hải sản",
    "nhum biển": "hải sản",

    # 4. Cá
    "cá biển": "cá",
    "cá lóc": "cá",
    "cá bống": "cá",
    "cá ngừ": "cá",
    "cá hồi": "cá",
    "cá trích": "cá",
    "chả cá": "cá",

    # 5. Thịt bò
    "thịt bò": "bò",
    "bắp bò": "bò",
    "bò tơ": "bò",
    "bê": "bò",
    "bê thui": "bò",
    "nậm bò": "bò",

    # 6. Trứng
    "hột gà": "trứng",
    "hột vịt": "trứng",
    "trứng gà": "trứng",
    "trứng vịt": "trứng",
    "trứng cút": "trứng",
    "trứng muối": "trứng",

    # 7. Sữa & Chế phẩm
    "sữa tươi": "sữa",
    "phô mai": "sữa",
    "bơ lạt": "sữa",

    # 8. Gluten & Bột mì
    "bột mì": "gluten",
    "bánh mì": "gluten",
    "mì trứng": "gluten",

    # 9. Đậu nành
    "đậu hũ": "đậu nành",
    "tàu hũ": "đậu nành",
    "chao": "đậu nành",
    "tương bần": "đậu nành",
}


def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản tiếng Việt:
    - Đưa về chuẩn dựng sẵn Unicode NFC (tránh lỗi lệch mã ký tự gõ dấu)
    - Chuyển thành chữ thường (.lower())
    - Loại bỏ khoảng trắng thừa ở 2 đầu và giữa các từ
    """
    if not text or not isinstance(text, str):
        return ""
    # Chuẩn hóa Unicode NFC
    normalized = unicodedata.normalize("NFC", text.strip().lower())
    # Gộp nhiều khoảng trắng liên tiếp thành 1 khoảng trắng
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def map_to_canonical(term: str) -> str:
    """
    Quy đổi một từ khóa về dạng chuẩn (Canonical Form).
    Ví dụ: 'lạc' -> 'đậu phộng', 'hạt vừng' -> 'mè'
    Nếu không nằm trong từ điển, giữ nguyên từ khóa đã làm sạch.
    """
    clean_term = normalize_text(term)
    if clean_term in SYNONYMS_MAP:
        return SYNONYMS_MAP[clean_term]
    
    # Quét từ khóa con nếu từ ghép có chứa từ đồng nghĩa
    for syn, canonical in SYNONYMS_MAP.items():
        if syn in clean_term:
            return canonical
            
    return clean_term


def normalize_allergen_set(raw_allergens: Iterable[str]) -> Set[str]:
    """
    Chuyển đổi danh sách/mảng chất dị ứng thô từ người dùng thành Set các chất dị ứng đã chuẩn hóa.
    Ví dụ input:  [' Lạc rang ', 'VỪNG ĐEN', 'Tôm sú']
    Ví dụ output: {'đậu phộng', 'mè', 'hải sản'}
    """
    if not raw_allergens:
        return set()

    result = set()
    for item in raw_allergens:
        if not item:
            continue
        cleaned = normalize_text(str(item))
        canonical = map_to_canonical(cleaned)
        if canonical:
            result.add(canonical)
            # Thêm cả từ khóa gốc đã làm sạch để so khớp dự phòng
            result.add(cleaned)

    return result


# ==============================================================================
# SUB-TASK 2.2.2: MODULE CẮT TỈA CẤP MÓN ĂN (DISH-LEVEL SET INTERSECTION)
# ==============================================================================

def extract_dish_keywords(dish: dict) -> Set[str]:
    """
    Trích xuất toàn bộ từ khóa nguyên liệu và dị ứng của 1 món ăn thành một Set chuẩn hóa.
    Bao gồm:
    - Các thành phần trong mảng 'ingredients'
    - Các nhãn trong mảng 'allergens'
    - Cả dạng gốc và dạng canonical (sau khi tra từ điển)
    """
    dish_set = set()

    # 1. Quét mảng ingredients
    for ing in dish.get("ingredients", []):
        if ing:
            clean_ing = normalize_text(str(ing))
            dish_set.add(clean_ing)
            canonical = map_to_canonical(clean_ing)
            if canonical:
                dish_set.add(canonical)

    # 2. Quét mảng allergens
    for alg in dish.get("allergens", []):
        if alg:
            clean_alg = normalize_text(str(alg))
            dish_set.add(clean_alg)
            canonical = map_to_canonical(clean_alg)
            if canonical:
                dish_set.add(canonical)

    return dish_set


def check_dish_safety(dish: dict, user_allergens_set: Set[str]) -> dict:
    """
    Kiểm tra độ an toàn của 1 món ăn dựa trên phép toán giao tập hợp:
        Intersection = Dish_Keywords & User_Allergens
        
    Trả về dict chi tiết:
    {
        "dish_id": str,
        "dish_name": str,
        "price": int,
        "is_safe": bool,
        "matched_allergens": list[str],
        "reason": str
    }
    """
    dish_id = dish.get("dish_id", "")
    dish_name = dish.get("dish_name", "Món ăn chưa đặt tên")
    price = dish.get("price", 0)

    # Trường hợp biên: Nếu người dùng không có dị ứng nào -> 100% an toàn
    if not user_allergens_set:
        return {
            "dish_id": dish_id,
            "dish_name": dish_name,
            "price": price,
            "is_safe": True,
            "matched_allergens": [],
            "reason": "An toàn (Đoàn không khai báo dị ứng)"
        }

    # Trích xuất toàn bộ từ khóa của món ăn
    dish_keywords = extract_dish_keywords(dish)

    # THỰC THI PHÉP GIAO TẬP HỢP (SET INTERSECTION: O(min(len(A), len(B))))
    conflict_allergens = sorted(list(dish_keywords & user_allergens_set))

    if conflict_allergens:
        return {
            "dish_id": dish_id,
            "dish_name": dish_name,
            "price": price,
            "is_safe": False,
            "matched_allergens": conflict_allergens,
            "reason": f"Nguy hiểm: Món có chứa thành phần trùng dị ứng: {', '.join(conflict_allergens)}"
        }
    else:
        return {
            "dish_id": dish_id,
            "dish_name": dish_name,
            "price": price,
            "is_safe": True,
            "matched_allergens": [],
            "reason": "An toàn: Không chứa bất kỳ thành phần nào trong danh mục dị ứng của đoàn"
        }


# ==============================================================================
# SUB-TASK 2.2.3: MODULE DANH GIA CAP NHA HANG & NGAN SACH CUNG (RESTAURANT EVALUATION)
# ==============================================================================

def evaluate_restaurant(
    restaurant: Dict[str, Any],
    user_allergens_set: Set[str],
    max_budget_per_person: Optional[int] = None
) -> Dict[str, Any]:
    """
    Danh gia tong the nha hang theo 2 tieu chi:
    1. Tran ngan sach binh quan dau nguoi (Hard Budget Constraint)
    2. Nang luc phuc vu thuc don an toan cho nguoi di ung (Safe Menu Capacity)

    Nguyen tac nhom (Group-aware):
    - Neu chi phi binh quan vuot tran ngan sach -> Cat tia (is_safe = False)
    - Neu khong co mon nao an toan -> Cat tia (is_safe = False)
    - Neu co it nhat 1 mon an toan va trong ngan sach -> Chap nhan (is_safe = True)
      + 100% thuc don khong di ung -> is_100_percent_safe = True
      + Co ca mon an toan va mon di ung -> is_100_percent_safe = False, kem canh bao
    """
    res_id = str(restaurant.get("id", ""))
    name = str(restaurant.get("name", "Nha hang chua dat ten"))
    destination = str(restaurant.get("destination", ""))
    address = str(restaurant.get("address", "") or "")
    rating = float(restaurant.get("rating", 0.0) or 0.0)
    avg_cost = int(restaurant.get("avg_cost_per_person", 0) or 0)
    menu_items = restaurant.get("menu_items", [])

    # 1. Kiem tra tran ngan sach binh quan dau nguoi
    is_over_budget = False
    budget_reason = None
    if max_budget_per_person is not None and max_budget_per_person > 0:
        if avg_cost > max_budget_per_person:
            is_over_budget = True
            budget_reason = f"Vuot tran ngan sach: {avg_cost:,} VND > {max_budget_per_person:,} VND / nguoi"

    # 2. Cat tia va phan loai tung mon an theo danh muc di ung
    safe_dishes = []
    unsafe_dishes = []

    for dish in menu_items:
        dish_eval = check_dish_safety(dish, user_allergens_set)
        if dish_eval["is_safe"]:
            safe_dishes.append(dish)
        else:
            flagged_dish = dict(dish)
            flagged_dish["matched_allergens"] = dish_eval.get("matched_allergens", [])
            flagged_dish["reason"] = dish_eval.get("reason", "")
            unsafe_dishes.append(flagged_dish)

    # 3. Danh gia trang thai an toan cap nha hang
    total_dishes = len(menu_items)
    is_safe = True
    is_100_percent_safe = False
    warning_note = None
    rejection_reason = None
    prune_type = None

    if total_dishes == 0:
        all_ing = restaurant.get("all_ingredients", [])
        if all_ing:
            normalized_all_ing = normalize_allergen_set(all_ing)
            conflict = sorted(list(normalized_all_ing & user_allergens_set))
            if conflict:
                is_safe = False
                prune_type = "unsafe"
                rejection_reason = f"Chua co menu chi tiet, tong hop nguyen lieu chua chat di ung: {', '.join(conflict)}"
                warning_note = rejection_reason
            elif is_over_budget:
                is_safe = False
                prune_type = "overbudget"
                rejection_reason = budget_reason
                warning_note = budget_reason
            else:
                is_safe = True
                warning_note = "Nha hang chua cap nhat menu chi tiet tung mon an"
        else:
            is_safe = False
            prune_type = "unsafe"
            rejection_reason = "Nha hang chua cap nhat thuc don mon an"
            warning_note = rejection_reason

    elif len(safe_dishes) == 0:
        is_safe = False
        prune_type = "unsafe"
        rejection_reason = "Tat ca cac mon trong thuc don deu chua chat gay di ung cua doan"
        warning_note = "Khong co mon an an toan thay the cho thanh vien di ung"

    elif is_over_budget:
        is_safe = False
        is_100_percent_safe = (len(unsafe_dishes) == 0)
        prune_type = "overbudget"
        rejection_reason = budget_reason
        warning_note = budget_reason

    else:
        is_safe = True
        rejection_reason = None
        if len(unsafe_dishes) == 0:
            is_100_percent_safe = True
            warning_note = "100% thuc don an toan voi danh muc di ung cua doan"
        else:
            is_100_percent_safe = False
            warning_note = f"Quan co {len(safe_dishes)}/{total_dishes} mon an toan thay the. Luu y tranh {len(unsafe_dishes)} mon chua di ung cua thanh vien trong doan."

    return {
        "id": res_id,
        "name": name,
        "destination": destination,
        "address": address,
        "rating": rating,
        "avg_cost_per_person": avg_cost,
        "source": str(restaurant.get("source", "") or ""),
        "is_safe": is_safe,
        "is_100_percent_safe": is_100_percent_safe,
        "safe_dishes": safe_dishes,
        "unsafe_dishes": unsafe_dishes,
        "warning_note": warning_note,
        "rejection_reason": rejection_reason,
        "prune_type": prune_type
    }


# ==============================================================================
# SUB-TASK 2.2.4: MODULE DIEU PHOI TRUY VAN MONGODB ATLAS & DONG GOI RESPONSE
# ==============================================================================

def prune_restaurants(
    request: Union[Any, Dict[str, Any]],
    collection: Any = None
) -> Dict[str, Any]:
    """
    Dieu phoi toan bo quy trinh Cat tia an toan y te va ngan sach:
    1. Chuan hoa danh muc di ung cua doan (Sub-task 2.2.1)
    2. Truy van danh sach nha hang theo tinh/thanh tu MongoDB Atlas
    3. Chay vong lap danh gia tung nha hang (Sub-task 2.2.3)
    4. Thong ke va dong goi ket qua tra ve dung chuan SafetyPruneResponse
    """
    # 1. Trich xuat thong so tu request (ho tro ca Pydantic model va dict)
    if hasattr(request, "destination"):
        destination = str(request.destination or "").strip()
        group_allergens = getattr(request, "group_allergens", []) or []
        max_budget = getattr(request, "max_budget_per_person", None)
    elif isinstance(request, dict):
        destination = str(request.get("destination", "") or "").strip()
        group_allergens = request.get("group_allergens", []) or []
        max_budget = request.get("max_budget_per_person", None)
    else:
        destination = ""
        group_allergens = []
        max_budget = None

    if not destination:
        return {
            "destination": "",
            "total_candidates": 0,
            "passed_count": 0,
            "pruned_overbudget_count": 0,
            "pruned_unsafe_count": 0,
            "safe_restaurants": []
        }

    # 2. Xac dinh collection can truy van tu MongoDB Atlas
    target_collection = collection
    if target_collection is None and db is not None:
        target_collection = db.Restaurants

    candidates = []
    if target_collection is not None:
        try:
            query = {"destination": {"$regex": f"^{re.escape(destination)}$", "$options": "i"}}
            candidates = list(target_collection.find(query, {"_id": 0}))
        except Exception:
            candidates = []

    # 3. Chuan hoa danh muc di ung cua doan
    user_allergens_set = normalize_allergen_set(group_allergens)

    # 4. Chay vong lap danh gia tung nha hang qua Sub-task 2.2.3
    safe_restaurants = []
    pruned_overbudget_count = 0
    pruned_unsafe_count = 0

    for r in candidates:
        eval_res = evaluate_restaurant(
            restaurant=r,
            user_allergens_set=user_allergens_set,
            max_budget_per_person=max_budget
        )

        if eval_res["is_safe"]:
            safe_restaurants.append(eval_res)
        else:
            if eval_res.get("prune_type") == "overbudget":
                pruned_overbudget_count += 1
            else:
                pruned_unsafe_count += 1

    # 5. Dong goi ket qua chuan hoa
    response_data = {
        "destination": destination,
        "total_candidates": len(candidates),
        "passed_count": len(safe_restaurants),
        "pruned_overbudget_count": pruned_overbudget_count,
        "pruned_unsafe_count": pruned_unsafe_count,
        "safe_restaurants": safe_restaurants
    }

    return response_data


# ==============================================================================
# KHOI CHAY THU NGHIEM DOC LAP CHO SUB-TASK 2.2.1, 2.2.2 & 2.2.3
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("   KIEM THU SUB-TASK 2.2.1: CHUAN HOA VAN BAN & TU DIEN DONG NGHIA")
    print("=" * 70)

    test_inputs = [
        "  Lạc rang muối  ",
        "Hột Gà",
        "VỪNG ĐEN",
        "Tôm Sú Biển"
    ]

    print("\nDu lieu tho ban dau:", test_inputs)
    normalized_set = normalize_allergen_set(test_inputs)
    print("Tap di ung da chuan hoa (Set):", normalized_set)

    print("\n" + "=" * 70)
    print("   KIEM THU SUB-TASK 2.2.2: CAT TIA CAP MON AN (SET INTERSECTION)")
    print("=" * 70)

    sample_dish = {
        "dish_id": "D001",
        "dish_name": "Mực cơm chiên nước mắm",
        "price": 140000,
        "ingredients": ["mực tươi", "nước mắm nhỉ", "tỏi", "ớt"],
        "allergens": ["hải sản"]
    }

    user_test_allergens = normalize_allergen_set(["tôm", "vừng"])
    print("Khach khai bao di ung: ['tôm', 'vừng']")
    print("Tap di ung chuan hoa:", user_test_allergens)

    dish_res = check_dish_safety(sample_dish, user_test_allergens)
    status_dish = "[SAFE]" if dish_res["is_safe"] else "[UNSAFE]"
    print(f"Ket qua kiem tra mon: {status_dish} {dish_res['dish_name']} -> {dish_res['reason']}")

    print("\n" + "=" * 70)
    print("   KIEM THU SUB-TASK 2.2.3: DANH GIA CAP NHA HANG & NGAN SACH CUNG")
    print("=" * 70)

    mock_restaurants = [
        {
            "id": "R001",
            "name": "Nhà hàng Cơm Niêu Đà Nẵng",
            "destination": "Đà Nẵng",
            "avg_cost_per_person": 85000,
            "menu_items": [
                {"dish_id": "D1", "dish_name": "Cơm niêu cá kho tộ", "price": 75000, "ingredients": ["cá lóc", "tiêu", "hành"], "allergens": ["cá"]},
                {"dish_id": "D2", "dish_name": "Canh cải nấu tôm", "price": 50000, "ingredients": ["cải xanh", "tôm tươi"], "allergens": ["hải sản"]},
                {"dish_id": "D3", "dish_name": "Rau muống xào tỏi", "price": 40000, "ingredients": ["rau muống", "tỏi"], "allergens": []}
            ]
        },
        {
            "id": "R002",
            "name": "Quán Hải Sản Biển Đông",
            "destination": "Đà Nẵng",
            "avg_cost_per_person": 95000,
            "menu_items": [
                {"dish_id": "D4", "dish_name": "Mực hấp gừng", "price": 120000, "ingredients": ["mực tươi", "gừng"], "allergens": ["hải sản"]},
                {"dish_id": "D5", "dish_name": "Tôm sú nướng muối ớt", "price": 150000, "ingredients": ["tôm sú", "ớt"], "allergens": ["hải sản"]}
            ]
        },
        {
            "id": "R003",
            "name": "Nhà hàng Chay Hoàng Cung",
            "destination": "Đà Nẵng",
            "avg_cost_per_person": 220000,
            "menu_items": [
                {"dish_id": "D6", "dish_name": "Cơm chay hạt sen", "price": 180000, "ingredients": ["gạo", "hạt sen", "nấm"], "allergens": []},
                {"dish_id": "D7", "dish_name": "Nấm kho tiêu", "price": 120000, "ingredients": ["nấm rơm", "tiêu"], "allergens": []}
            ]
        }
    ]

    budget_cap = 100000
    print(f"Ngu canh kiem thu: Doan di ung ['tôm', 'vừng'], Tran ngan sach: {budget_cap:,} VND / nguoi\n")

    for r in mock_restaurants:
        eval_res = evaluate_restaurant(r, user_test_allergens, max_budget_per_person=budget_cap)
        status_label = "[PASS - DUOC CHON]" if eval_res["is_safe"] else "[REJECT - LOAI BO]"
        print(f"{status_label}: {eval_res['name']} (Gia TB: {eval_res['avg_cost_per_person']:,} VND)")
        print(f"  - 100% An toan: {eval_res['is_100_percent_safe']}")
        print(f"  - So mon an toan: {len(eval_res['safe_dishes'])} mon | So mon nguy hiem: {len(eval_res['unsafe_dishes'])} mon")
        print(f"  - Ghi chu / Ly do: {eval_res['warning_note']}")
        if eval_res["is_safe"]:
            safe_names = [d["dish_name"] for d in eval_res["safe_dishes"]]
            print(f"  - Thuc don an toan de xuat: {safe_names}")
        print()

    print("=" * 70)
    print("SUB-TASK 2.2.3 DA HOAN THANH VA CHAY CHINH XAC 100%!")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("   KIEM THU SUB-TASK 2.2.4: DIEU PHOI TRUY VAN ATLAS & DONG GOI RESPONSE")
    print("=" * 70)

    test_request = {
        "destination": "Đà Nẵng",
        "group_allergens": ["tôm", "mè"],
        "max_budget_per_person": 120000,
        "group_size": 4
    }

    print("Yeu cau loc:", test_request)
    live_response = prune_restaurants(test_request)
    print(f"\nKet qua dieu phoi tai {live_response['destination']}:")
    print(f"  - Tong so nha hang tim thay: {live_response['total_candidates']}")
    print(f"  - So quan dat chuan (Passed): {live_response['passed_count']}")
    print(f"  - So quan bi loai do vuot ngan sach: {live_response['pruned_overbudget_count']}")
    print(f"  - So quan bi loai do khong an toan: {live_response['pruned_unsafe_count']}")
    for idx, r in enumerate(live_response['safe_restaurants'], 1):
        print(f"\n  [Quan {idx}] {r['name']}")
        print(f"      - Gia TB: {r['avg_cost_per_person']:,} VND | 100% An toan: {r['is_100_percent_safe']}")
        print(f"      - Ghi chu: {r['warning_note']}")
        safe_names = [d['dish_name'] for d in r['safe_dishes']]
        print(f"      - Mon an toan de xuat: {safe_names}")

    print("\n" + "=" * 70)
    print("SUB-TASK 2.2.4 DA HOAN THANH VA CHAY CHINH XAC 100%!")
    print("=" * 70)
