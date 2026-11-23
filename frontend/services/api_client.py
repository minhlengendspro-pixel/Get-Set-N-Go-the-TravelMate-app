"""
MODULE CLIENT GIAO TIEP REST API
Chuyen trach ket noi va gui yeu cau tu Streamlit sang FastAPI Backend.
"""
import requests
from typing import Dict, Any, Optional

BACKEND_BASE_URL = "http://127.0.0.1:8000"


def check_backend_connection(timeout: int = 2) -> bool:
    """
    Kiem tra nhanh xem Backend FastAPI co dang hoat dong hay khong.
    Tra ve True neu ket noi duoc, False neu server chua bat hoac loi mang.
    """
    try:
        res = requests.get(f"{BACKEND_BASE_URL}/", timeout=timeout)
        return res.status_code == 200
    except Exception:
        return False


def fetch_safe_restaurants(
    destination: str,
    group_allergens: list,
    max_budget_per_person: Optional[int] = None,
    group_size: int = 1,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Gui yeu cau loc nha hang an toan y te va ngan sach sang Backend:
    POST /api/restaurants/prune-safe

    Dinh dang ket qua tra ve:
    {
        "success": bool,
        "data": dict (SafetyPruneResponse neu thanh cong) hoac None,
        "error": str (thong bao loi neu that bai) hoac None
    }
    """
    endpoint = f"{BACKEND_BASE_URL}/api/restaurants/prune-safe"
    payload = {
        "destination": destination.strip(),
        "group_allergens": group_allergens or [],
        "max_budget_per_person": max_budget_per_person,
        "group_size": group_size
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        
        # Truong hop 1: Backend xu ly thanh cong (HTTP 200)
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json(),
                "error": None
            }
        
        # Truong hop 2: Backend tra ve ma loi (HTTP 422 sai du lieu, HTTP 500 loi he thong)
        else:
            return {
                "success": False,
                "data": None,
                "error": f"Loi tu Backend (HTTP {response.status_code}): {response.text}"
            }

    # Truong hop 3: Khong the ket noi toi Backend (Server chua khoi dong)
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "data": None,
            "error": "Khong the ket noi toi Backend (Port 8000). Vui long kiem tra xem uvicorn da duoc bat hay chua."
        }

    # Truong hop 4: Het thoi gian cho phan hoi (Timeout)
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "data": None,
            "error": f"Yeu cau qua thoi gian cho ({timeout} giay). Vui long thu lai."
        }

    # Truong hop 5: Cac loi ngoai y muon khac
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Loi ket noi ngoai le: {str(e)}"
        }


if __name__ == "__main__":
    print("--- DANG THU NGHIEM MODULE API_CLIENT DOC LAP ---")
    
    # 1. Kiem tra ket noi server
    is_alive = check_backend_connection()
    print(f"Trang thai Backend Server (Port 8000): {'DANG HOAT DONG' if is_alive else 'CHUA KHOI DONG'}")

    # 2. Thu goi API loc quan an Da Nang
    if is_alive:
        print("\nDang gui yeu cau thu nghiem toi /api/restaurants/prune-safe...")
        result = fetch_safe_restaurants(
            destination="Đà Nẵng",
            group_allergens=["tôm"],
            max_budget_per_person=150000,
            group_size=4
        )
        if result["success"]:
            data = result["data"]
            print(f"[OK] Ket qua tra ve: {data.get('passed_count')}/{data.get('total_candidates')} quan vuot qua an toan.")
        else:
            print(f"[LOI]: {result['error']}")
    else:
        print("\n[NHAC NHO]: Hay khoi dong Backend bang lenh 'uvicorn main:app --reload' de chay thu nghiem day du.")
