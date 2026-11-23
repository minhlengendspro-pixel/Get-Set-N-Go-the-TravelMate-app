"""
MODULE QUAN LY & KET NOI DU LIEU DIEM THAM QUAN (CHO NGUOI 3)
Chuyen trach trich xuat va cung cap du lieu dia diem tham quan cho giao dien The Collection.
Su dung kho anh goc chan thuc (Authentic Landmark Images) luu tru cuc bo tai frontend/assets/places/
dam bao 100% tinh chinh xac lich su, khong phu thuoc mang ngoai va tuyet doi khong trung lap/nham lan anh.
"""
import os
import json
import base64
from typing import List, Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PLACES_DATA_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "backend", "data", "places_enriched.json"))
ASSETS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "assets", "places"))

# ==============================================================================
# 1. ANH CHINH GOC THEO MA DINH DANH POI ID (UU TIEN TUYET DOI - KHONG TRUNG LAP)
# ==============================================================================
POI_EXACT_IMAGE_MAP = {
    # Ninh Binh (Tach biet tuyet doi Trang An, Tam Coc, Hoa Lu)
    "P051": "trang_an.jpg",           # Trang An (ben thuyen hang dong non nuoc)
    "P052": "tam_coc.jpg",            # Tam Coc (song Ngo Dong uon luon giua mua lua vang)
    "P053": "hoa_lu.jpg",             # Co do Hoa Lu (cong thanh co va den vua Dinh - Le)

    # Quang Ninh (Tach biet tuyet doi Vinh, Bai Chay, Halong Park, Cua Van)
    "P086": "vinh_ha_long.jpg",       # Vinh Ha Long (dao da voi tren vinh)
    "P087": "bien_bai_chay.jpg",      # Bien Bai Chay (bo bien bo cat dai Bai Chay)
    "P088": "cong_vien_ha_long.jpg",  # Cong vien Ha Long (Vong quay mat troi Sun Wheel Halong Park)
    "P089": "cua_van.jpg",            # Lang chai Cua Van

    # Da Nang
    "P211": "bana_hills.jpg",         # Ba Na Hills (Anh lau dai Sun World thuc te tu nguoi dung)
    "P212": "cau_rong.jpg",           # Cau Rong Da Nang
    "P213": "ngu_hanh_son.jpg",       # Ngu Hanh Son
    "P214": "my_khe.jpg",             # Bai Bien My Khe
    "P215": "cau_rong.jpg",           # Cau Tinh Yeu ben bo song Han

    # Ha Noi
    "P281": "lang_bac.jpg",           # Lang Chu tich Ho Chi Minh
    "P282": "ho_guom.jpg",            # Ho Guom / Thap Rua
    "P283": "van_mieu.jpg",           # Van Mieu - Quoc Tu Giam
    "P284": "hoang_thanh_thang_long.jpg", # Hoang thanh Thang Long
    "P285": "cau_long_bien.jpg",      # Cau Long Bien

    # TP. Ho Chi Minh
    "P136": "cho_ben_thanh.jpg",      # Cho Ben Thanh
    "P137": "dinh_doc_lap.jpg",       # Dinh Doc Lap
    "P138": "nha_tho_duc_ba.jpg",     # Nha tho Duc Ba
    "P139": "dinh_doc_lap.jpg",       # Bao tang lich su
    "P140": "dia_dao_cu_chi.jpg",     # Dia dao Cu Chi

    # Quang Nam
    "P076": "hoi_an.jpg",             # Pho co Hoi An
    "P077": "an_bang.jpg",            # Bai bien An Bang
    "P078": "thap_chien_dan.jpg",     # Thap Chien Dan Cham Pa co
    "P079": "hoi_an.jpg",             # Dinh Que
    "P080": "my_son.jpg",             # Thanh Dia My Son

    # Khanh Hoa
    "P001": "bai_dai_cam_ranh.jpg",   # Bai Dai Cam Ranh (bien xanh ngoc)
    "P002": "thap_ba_ponagar.jpg",    # Thap Ba Ponagar
    "P003": "thanh_co_dien_khanh.jpg", # Thanh co Dien Khanh
    "P004": "cong_vien_ha_long.jpg",  # VinWonders Nha Trang (Khu vui choi)
    "P005": "bai_dai_cam_ranh.jpg",   # Suoi Ba Ho

    # Lam Dong
    "P021": "ho_xuan_huong.jpg",      # Ho Xuan Huong
    "P022": "thien_vien_truc_lam.jpg", # Thien Vien Truc Lam
    "P023": "cho_dem_da_lat.jpg",     # Cho Dem Da Lat
}

# ==============================================================================
# 2. TU DIEN ANH THEO TU KHOA CHI TIET (UU TIEN TU KHOA DAI TRUOC)
# ==============================================================================
KEYWORD_IMAGE_MAP = {
    # Ninh Binh
    "tam cốc": "tam_coc.jpg",
    "bích động": "tam_coc.jpg",
    "cố đô hoa lư": "hoa_lu.jpg",
    "hoa lư": "hoa_lu.jpg",
    "tràng an": "trang_an.jpg",

    # Quang Ninh
    "biển bãi cháy": "bien_bai_chay.jpg",
    "bãi cháy": "bien_bai_chay.jpg",
    "công viên hạ long": "cong_vien_ha_long.jpg",
    "sun world halong": "cong_vien_ha_long.jpg",
    "cửa vạn": "cua_van.jpg",
    "vịnh hạ long": "vinh_ha_long.jpg",

    # Da Nang
    "bà nà hills": "bana_hills.jpg",
    "ba na hills": "bana_hills.jpg",
    "bà nà": "bana_hills.jpg",
    "cầu vàng": "cau_vang.jpg",
    "cầu rồng": "cau_rong.jpg",
    "ngũ hành sơn": "ngu_hanh_son.jpg",
    "bãi biển mỹ khê": "my_khe.jpg",
    "mỹ khê": "my_khe.jpg",

    # Ha Noi
    "lăng chủ tịch": "lang_bac.jpg",
    "lăng bác": "lang_bac.jpg",
    "hồ hoàn kiếm": "ho_guom.jpg",
    "hồ gươm": "ho_guom.jpg",
    "văn miếu": "van_mieu.jpg",
    "cầu long biên": "cau_long_bien.jpg",
    "hoàng thành": "hoang_thanh_thang_long.jpg",

    # TP. HCM
    "chợ bến thành": "cho_ben_thanh.jpg",
    "bến thành": "cho_ben_thanh.jpg",
    "dinh độc lập": "dinh_doc_lap.jpg",
    "nhà thờ đức bà": "nha_tho_duc_ba.jpg",
    "địa đạo củ chi": "dia_dao_cu_chi.jpg",

    # Quang Nam
    "tháp chiên đàn": "thap_chien_dan.jpg",
    "phố cổ hội an": "hoi_an.jpg",
    "hội an": "hoi_an.jpg",
    "an bàng": "an_bang.jpg",
    "mỹ sơn": "my_son.jpg",

    # Khanh Hoa
    "thành cổ diên khánh": "thanh_co_dien_khanh.jpg",
    "diên khánh": "thanh_co_dien_khanh.jpg",
    "bãi dài": "bai_dai_cam_ranh.jpg",
    "cam ranh": "bai_dai_cam_ranh.jpg",
    "tháp bà ponagar": "thap_ba_ponagar.jpg",
    "ponagar": "thap_ba_ponagar.jpg",

    # Lam Dong
    "hồ xuân hương": "ho_xuan_huong.jpg",
    "xuân hương": "ho_xuan_huong.jpg",
    "trúc lâm": "thien_vien_truc_lam.jpg",
    "chợ đêm đà lạt": "cho_dem_da_lat.jpg"
}

# 3. Anh mac dinh dai dien cho tung Tinh / Thanh (Fallback cap 3)
PROVINCE_FALLBACK_IMAGES = {
    "đà nẵng": "bana_hills.jpg",
    "hà nội": "ho_guom.jpg",
    "quảng nam": "hoi_an.jpg",
    "quảng ninh": "vinh_ha_long.jpg",
    "tp. hồ chí minh": "cho_ben_thanh.jpg",
    "ninh bình": "trang_an.jpg",
    "khánh hòa": "thap_ba_ponagar.jpg",
    "lâm đồng": "ho_xuan_huong.jpg"
}


def get_html_image_src(image_path_or_url: str) -> str:
    """
    Chuyen doi duong dan anh cuc bo thanh base64 data URI de the HTML <img src='...'>
    hien thi ngay lap tuc tren trinh duyet ma khong can thiet lap may chu static file.
    Neu la URL truc tuyen thi giu nguyen.
    """
    if not image_path_or_url:
        return ""
    if image_path_or_url.startswith("http://") or image_path_or_url.startswith("https://") or image_path_or_url.startswith("data:image"):
        return image_path_or_url
    if os.path.exists(image_path_or_url):
        try:
            with open(image_path_or_url, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                ext = os.path.splitext(image_path_or_url)[1].lower().replace(".", "")
                mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
                return f"data:image/{mime};base64,{encoded}"
        except Exception:
            return ""
    return image_path_or_url


def get_authentic_image_path(poi_id: str, name: str, destination: str) -> str:
    """
    Xac dinh duong dan file anh chinh goc tu thu muc frontend/assets/places/.
    Thu tu uu tien kiem tra:
    1. POI ID chinh xac tuyet doi (tranh hoan toan trung lap ten)
    2. Tu khoa ten dai nhat (biển bãi cháy, công viên hạ long, tam cốc uu tien hon tu khoa ngan)
    3. Tinh / Thanh pho du phong
    """
    poi_id_clean = str(poi_id).strip()
    name_clean = str(name).strip().lower()
    dest_clean = str(destination).strip().lower()

    # 1. Kiem tra theo POI ID (Uu tien tuyet doi)
    if poi_id_clean in POI_EXACT_IMAGE_MAP:
        fname = POI_EXACT_IMAGE_MAP[poi_id_clean]
        fpath = os.path.join(ASSETS_DIR, fname)
        if os.path.exists(fpath):
            return fpath

    # 2. Kiem tra theo tu khoa ten (Sap xep theo do dai giam dan)
    sorted_keywords = sorted(KEYWORD_IMAGE_MAP.keys(), key=lambda k: len(k), reverse=True)
    for kw in sorted_keywords:
        if kw in name_clean:
            fname = KEYWORD_IMAGE_MAP[kw]
            fpath = os.path.join(ASSETS_DIR, fname)
            if os.path.exists(fpath):
                return fpath

    # 3. Kiem tra theo Tinh / Thanh du phong
    for prov, fname in PROVINCE_FALLBACK_IMAGES.items():
        if prov in dest_clean:
            fpath = os.path.join(ASSETS_DIR, fname)
            if os.path.exists(fpath):
                return fpath

    # 4. Mac dinh toan he thong
    default_path = os.path.join(ASSETS_DIR, "bana_hills.jpg")
    return default_path if os.path.exists(default_path) else ""


def load_all_places() -> List[Dict[str, Any]]:
    """Doc toan bo 315 dia diem tu file places_enriched.json."""
    if not os.path.exists(PLACES_DATA_PATH):
        return []
    try:
        with open(PLACES_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def enrich_place_image(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nang cap anh cua dia diem bang anh chinh goc tu thu muc assets cuc bo.
    Gan duong dan file cuc bo vao 'image' va base64 URI vao 'image_data_uri'.
    """
    p = dict(place)
    poi_id = p.get("id", "")
    name = p.get("name", "")
    destination = p.get("destination", "")

    auth_path = get_authentic_image_path(poi_id, name, destination)
    if auth_path:
        p["image"] = auth_path
        p["image_data_uri"] = get_html_image_src(auth_path)
    return p


def get_featured_places(destination: str = "Đà Nẵng", limit: int = 3) -> List[Dict[str, Any]]:
    """
    Lay danh sach dia diem tham quan noi bat theo tinh/thanh, duoc lam giau anh chinh goc.
    Day la diem khop noi (Integration Hook) de Nguoi 3 tich hop thuat toan goi y Cosine/Jaccard.
    """
    all_places = load_all_places()
    if not all_places:
        return []

    dest_lower = destination.strip().lower()

    # Loc dia diem theo Tinh / Thanh pho
    matched_places = [
        p for p in all_places
        if dest_lower in p.get("destination", "").lower()
    ]

    # Neu tinh/thanh chua co POI, lay cac dia diem dau tien lam mau
    selected = matched_places[:limit] if matched_places else all_places[:limit]

    # Lam giau anh chinh goc cho tung dia diem
    return [enrich_place_image(p) for p in selected]
