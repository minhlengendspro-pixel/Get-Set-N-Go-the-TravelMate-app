"""
KICH BAN KIEM THU TU DONG (UNIT TEST) - MODULE 2: HARD PRUNING CONSTRAINTS
Kich ban thuc te: Doan 4 nguoi, co 1 nguoi di ung tom, ngan sach 120.000d/nguoi.
"""
import sys
import os

# Dam bao import duoc cac module trong backend du chay tu thu muc nao
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from services.hard_pruning import evaluate_restaurant, prune_restaurants, normalize_allergen_set


# ==============================================================================
# 1. DU LIEU MOCK (DONG GOI THEO THIET KE SUB-TASK 3.2.1)
# ==============================================================================

MOCK_REQUEST = {
    "destination": "Hà Nội",
    "group_allergens": ["tôm"],
    "max_budget_per_person": 120000,
    "group_size": 4
}

MOCK_RESTAURANTS = [
    # QUAN 1: Com Nieu Dat Viet (Gia 95k <= 120k, 1 mon tom, 3 mon an toan)
    {
        "id": "R_MOCK_01",
        "name": "Cơm Niêu Đất Việt",
        "destination": "Hà Nội",
        "address": "12 Hàng Hòm, Hoàn Kiếm, Hà Nội",
        "rating": 4.5,
        "avg_cost_per_person": 95000,
        "all_ingredients": ["gạo tám", "thịt heo", "cá quả", "tôm sú", "rau muống"],
        "menu_items": [
            {
                "dish_id": "D_M01",
                "dish_name": "Tôm sú sốt me",
                "price": 85000,
                "ingredients": ["tôm sú", "me chua", "tỏi", "ớt"],
                "allergens": ["hải sản", "tôm"]
            },
            {
                "dish_id": "D_M02",
                "dish_name": "Sườn non kho tộ",
                "price": 75000,
                "ingredients": ["thịt heo", "hành", "nước màu"],
                "allergens": []
            },
            {
                "dish_id": "D_M03",
                "dish_name": "Canh rau ngót thịt băm",
                "price": 45000,
                "ingredients": ["thịt heo", "rau ngót", "hành hoa"],
                "allergens": []
            },
            {
                "dish_id": "D_M04",
                "dish_name": "Rau muống xào tỏi",
                "price": 35000,
                "ingredients": ["rau muống", "tỏi", "dầu ăn"],
                "allergens": []
            }
        ]
    },

    # QUAN 2: Hai San Bien Dong (Gia 110k <= 120k, 100% mon chua tom)
    {
        "id": "R_MOCK_02",
        "name": "Hải Sản Biển Đông",
        "destination": "Hà Nội",
        "address": "88 Trần Thái Tông, Cầu Giấy, Hà Nội",
        "rating": 4.2,
        "avg_cost_per_person": 110000,
        "all_ingredients": ["tôm hùm", "tôm sú", "phô mai", "bia"],
        "menu_items": [
            {
                "dish_id": "D_M05",
                "dish_name": "Tôm hùm nướng phô mai",
                "price": 120000,
                "ingredients": ["tôm hùm", "phô mai", "bơ"],
                "allergens": ["hải sản", "tôm", "sữa"]
            },
            {
                "dish_id": "D_M06",
                "dish_name": "Tôm sú hấp bia",
                "price": 95000,
                "ingredients": ["tôm sú", "bia", "sả"],
                "allergens": ["hải sản", "tôm"]
            },
            {
                "dish_id": "D_M07",
                "dish_name": "Gỏi tôm ngó sen",
                "price": 65000,
                "ingredients": ["tôm", "ngó sen", "đậu phộng"],
                "allergens": ["hải sản", "tôm", "đậu phộng"]
            }
        ]
    },

    # QUAN 3: Wagyu Steakhouse Premium (Gia 350k > 120k, khong co di ung)
    {
        "id": "R_MOCK_03",
        "name": "Wagyu Steakhouse Premium",
        "destination": "Hà Nội",
        "address": "5 Lý Thường Kiệt, Hoàn Kiếm, Hà Nội",
        "rating": 4.8,
        "avg_cost_per_person": 350000,
        "all_ingredients": ["thịt bò wagyu", "khoai tây", "bơ"],
        "menu_items": [
            {
                "dish_id": "D_M08",
                "dish_name": "Bò bít tết Wagyu",
                "price": 320000,
                "ingredients": ["thịt bò", "bơ", "tiêu đen"],
                "allergens": []
            },
            {
                "dish_id": "D_M09",
                "dish_name": "Khoai tây nghiền bơ",
                "price": 60000,
                "ingredients": ["khoai tây", "bơ", "sữa tươi"],
                "allergens": ["sữa"]
            }
        ]
    }
]


# Lop MockCollection gia lap MongoDB collection de test offline 100%
class MockCollection:
    def __init__(self, data):
        self._data = data

    def find(self, query=None, projection=None):
        return self._data


# ==============================================================================
# 2. CAC HAM KIEM THU CHI TIET
# ==============================================================================

def run_all_tests():
    print("======================================================================")
    print("KIEM THU MODULE 2: HARD PRUNING & GROUP ALLERGEN SAFETY")
    print("Kich ban: Doan 4 nguoi | Di ung: ['tom'] | Ngan sach tran: 120,000 VND")
    print("======================================================================")

    allergens_set = normalize_allergen_set(MOCK_REQUEST["group_allergens"])
    max_budget = MOCK_REQUEST["max_budget_per_person"]

    # --------------------------------------------------------------------------
    # TEST 1: Kiem tra Quan 1 (Com Nieu Dat Viet)
    # Ky vong: PASS (An toan co dieu kien), safe_dishes = 3, unsafe_dishes = 1
    # --------------------------------------------------------------------------
    print("\n[TEST 1] Kiem tra Quan 1: Com Nieu Dat Viet (Case Pass co dieu kien)...")
    res1 = evaluate_restaurant(MOCK_RESTAURANTS[0], allergens_set, max_budget)

    assert res1["is_safe"] is True, "Loi Test 1: Quan 1 phai duoc PASS"
    assert res1["is_100_percent_safe"] is False, "Loi Test 1: Quan 1 co mon tom nen khong the 100% an toan"
    assert len(res1["safe_dishes"]) == 3, f"Loi Test 1: Ky vong 3 mon an toan, nhan {len(res1['safe_dishes'])}"
    assert len(res1["unsafe_dishes"]) == 1, f"Loi Test 1: Ky vong 1 mon nguy hiem, nhan {len(res1['unsafe_dishes'])}"
    assert res1["unsafe_dishes"][0]["dish_name"] == "Tôm sú sốt me", "Loi Test 1: Mon bi loai phai la Tom su sot me"

    print("  -> Trang thai: PASS [An toan co dieu kien]")
    print(f"  -> So mon an toan de xuat: {len(res1['safe_dishes'])} mon")
    print(f"  -> So mon loai bo (chua tom): {len(res1['unsafe_dishes'])} mon ({res1['unsafe_dishes'][0]['dish_name']})")
    print("  -> Ket qua assert: [OK]")

    # --------------------------------------------------------------------------
    # TEST 2: Kiem tra Quan 2 (Hai San Bien Dong)
    # Ky vong: REJECT vi 100% mon chua tom, prune_type = 'unsafe'
    # --------------------------------------------------------------------------
    print("\n[TEST 2] Kiem tra Quan 2: Hai San Bien Dong (Case Reject 100% di ung)...")
    res2 = evaluate_restaurant(MOCK_RESTAURANTS[1], allergens_set, max_budget)

    assert res2["is_safe"] is False, "Loi Test 2: Quan 2 phai bi REJECT"
    assert res2["prune_type"] == "unsafe", f"Loi Test 2: prune_type phai la 'unsafe', nhan {res2.get('prune_type')}"
    assert len(res2["safe_dishes"]) == 0, "Loi Test 2: Khong duoc co mon an toan nao"
    assert len(res2["unsafe_dishes"]) == 3, "Loi Test 2: Ca 3 mon deu phai bi xep vao unsafe"

    print("  -> Trang thai: REJECT [Khong an toan y te]")
    print(f"  -> Ly do loai: {res2.get('rejection_reason')}")
    print("  -> Ket qua assert: [OK]")

    # --------------------------------------------------------------------------
    # TEST 3: Kiem tra Quan 3 (Wagyu Steakhouse Premium)
    # Ky vong: REJECT vi chi phi 350.000d > 120.000d, prune_type = 'overbudget'
    # --------------------------------------------------------------------------
    print("\n[TEST 3] Kiem tra Quan 3: Wagyu Steakhouse Premium (Case Reject ngan sach)...")
    res3 = evaluate_restaurant(MOCK_RESTAURANTS[2], allergens_set, max_budget)

    assert res3["is_safe"] is False, "Loi Test 3: Quan 3 phai bi REJECT"
    assert res3["prune_type"] == "overbudget", f"Loi Test 3: prune_type phai la 'overbudget', nhan {res3.get('prune_type')}"
    assert "vuot tran ngan sach" in res3.get("rejection_reason", "").lower(), "Loi Test 3: Ly do phai ghi ro vuot ngan sach"

    print("  -> Trang thai: REJECT [Vuot tran ngan sach]")
    print(f"  -> Ly do loai: {res3.get('rejection_reason')}")
    print("  -> Ket qua assert: [OK]")

    # --------------------------------------------------------------------------
    # TEST 4: Kiem tra Bo dieu phoi Pipeline toan cuc (prune_restaurants)
    # Ky vong: tong 3 quan -> pass 1 quan, loai 1 vi di ung, loai 1 vi gia
    # --------------------------------------------------------------------------
    print("\n[TEST 4] Kiem tra Bo dieu phoi toan cuc (prune_restaurants)...")
    pipeline_res = prune_restaurants(
        request=MOCK_REQUEST,
        collection=MockCollection(MOCK_RESTAURANTS)
    )

    assert pipeline_res["total_candidates"] == 3, "Loi Test 4: Tong so quan ung vien phai la 3"
    assert pipeline_res["passed_count"] == 1, "Loi Test 4: So quan pass phai la 1"
    assert pipeline_res["pruned_unsafe_count"] == 1, "Loi Test 4: So quan loai vi di ung phai la 1"
    assert pipeline_res["pruned_overbudget_count"] == 1, "Loi Test 4: So quan loai vi ngan sach phai la 1"
    assert len(pipeline_res["safe_restaurants"]) == 1, "Loi Test 4: Danh sach tra ve phai chua dung 1 quan an toan"
    assert pipeline_res["safe_restaurants"][0]["name"] == "Cơm Niêu Đất Việt", "Loi Test 4: Quan vuot qua phai la Com Nieu Dat Viet"

    print("  -> Tong so quan dua vao danh gia : 3 quan")
    print(f"  -> So quan vuot qua hop le       : {pipeline_res['passed_count']} quan ({pipeline_res['safe_restaurants'][0]['name']})")
    print(f"  -> So quan bi loai bo vi di ung  : {pipeline_res['pruned_unsafe_count']} quan")
    print(f"  -> So quan bi loai vi ngan sach  : {pipeline_res['pruned_overbudget_count']} quan")
    print("  -> Ket qua assert: [OK]")

    # --------------------------------------------------------------------------
    # TONG KET
    # --------------------------------------------------------------------------
    print("\n======================================================================")
    print("KET LUAN: TAT CA 4/4 BAI KIEM THU DA VUOT QUA XUAT SAC (100% PASS)")
    print("He thong cat tia an toan y te va tran ngan sach da san sang hoan toan!")
    print("======================================================================")


if __name__ == "__main__":
    run_all_tests()
