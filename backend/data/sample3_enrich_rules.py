import json
import os
import re
import sys

# Đảm bảo in tiếng Việt mượt mà trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(CURRENT_DIR, "mapped_places.json")
OUTPUT_PATH = os.path.join(CURRENT_DIR, "places_enriched.json")

# ==============================================================================
# BỘ TỪ ĐIỂN TRI THỨC DU LỊCH & ẨM THỰC CHUẨN XÁC (HIGH PRECISION TAXONOMY)
# ==============================================================================

# 1. NHÃN ĐỊA HÌNH (Dùng cụm từ chính xác, loại bỏ từ đơn gây hiểu nhầm như 'động')
TERRAIN_KEYWORDS = {
    "biển đảo": [
        "biển", "đảo", "vịnh", "bãi tắm", "hòn", "bán đảo", "bờ biển", "san hô", "hải đăng"
    ],
    "núi rừng": [
        "dãy núi", "ngọn núi", "đỉnh núi", "leo núi", "đèo", "thác nước", "hang động",
        "động đá", "cao nguyên", "rừng già", "rừng nguyên sinh", "thung lũng"
    ],
    "sông nước": [
        "sông", "hồ", "kênh", "rạch", "đầm", "miền tây", "chợ nổi", "miệt vườn", "cù lao"
    ],
    "làng quê & đồng bằng": [
        "làng", "đình", "làng cổ", "đồng bằng", "thôn", "cánh đồng", "miếu cổ"
    ],
    "đô thị": [
        "phố", "thành phố", "bảo tàng", "quảng trường", "nhà hát", "trung tâm", "cầu"
    ]
}

# 2. NHÃN THỂ LOẠI CHÍNH
CATEGORY_KEYWORDS = {
    "văn hóa - lịch sử": [
        "di tích", "lịch sử", "chùa", "đền", "đình", "tháp", "lăng", "bảo tàng",
        "cổ kính", "triều đại", "nhà thờ", "kiến trúc cổ", "lễ hội dân gian", "truyền thống"
    ],
    "thiên nhiên": [
        "sinh thái", "nguyên sinh", "hoang sơ", "hùng vĩ", "vườn quốc gia", "kỳ quan thiên nhiên"
    ],
    "nghỉ dưỡng": [
        "nghỉ dưỡng", "resort", "thư giãn", "yên bình", "tĩnh lặng", "trong lành", "khoáng nóng", "chữa lành"
    ],
    "ẩm thực": [
        "ẩm thực", "đặc sản", "món ăn", "chợ đêm", "ăn uống", "hải sản", "nướng", "quán ăn"
    ],
    "vui chơi giải trí": [
        "vui chơi", "khu giải trí", "công viên", "check-in", "sống ảo", "sôi động", "mua sắm"
    ]
}

# 3. NHÃN ĐẶC SẮC: ẨM THỰC ĐẶC SẢN & HOẠT ĐỘNG TRẢI NGHIỆM
FEATURE_KEYWORDS = {
    # Ẩm thực & Đặc sản
    "hải sản tươi sống": ["hải sản", "tôm hùm", "cua", "ghẹ", "mực", "ốc", "hàu", "cá ngừ", "chả cá"],
    "đặc sản địa phương": ["đặc sản", "bánh xèo", "bún bò", "mì quảng", "cao lầu", "nem nướng", "cơm gà", "gỏi lá", "nhãn lồng", "bánh đậu xanh"],
    "cà phê & trà": ["cà phê", "cafe", "trà", "uống trà", "quán nước"],
    "ẩm thực đường phố": ["ăn vặt", "chợ đêm", "xiên nướng", "bánh tráng", "chè", "ẩm thực đường phố"],

    # Hoạt động trải nghiệm
    "kiến trúc & di tích cổ": ["kiến trúc cổ", "cổ truyền", "ngàn năm", "di tích lịch sử", "lâu đời"],
    "lễ hội dân gian": ["lễ hội dân gian", "hội làng", "hội đền", "hội chùa"],
    "tắm biển & lặn ngắm san hô": ["tắm biển", "lặn biển", "ngắm san hô", "lướt sóng", "chèo thuyền", "kayak"],
    "leo núi & trekking": ["leo núi", "trekking", "chinh phục đỉnh", "đi bộ xuyên rừng"],
    "ngắm hoàng hôn & bình minh": ["hoàng hôn", "bình minh", "săn mây", "view đẹp", "chiều tà"],
    "check-in sống ảo": ["chụp ảnh", "sống ảo", "check-in", "khung cảnh đẹp", "góc chụp"],
    "du lịch tâm linh": ["tâm linh", "thắp hương", "cầu an", "dâng hương", "thanh tịnh", "hành hương"]
}

# Danh sách các tag rác do file Excel gốc nhập nhầm cần lọc bỏ
DIRTY_TAGS_BLACKLIST = {
    "động vật", "thực vật", "bảo tồn"  # Gốc Excel nhập nhầm cho đình, chùa, bảo tàng
}


def match_keywords(text, kw_list):
    """Khớp cụm từ chính xác trong văn bản"""
    text_lower = text.lower()
    for kw in kw_list:
        if kw.lower() in text_lower:
            return True
    return False


def extract_tags(place):
    """Trích xuất bộ tags phân tầng dựa trên Rule-based Knowledge Base"""
    name = place.get("name", "")
    location = place.get("destination", "")
    desc = place.get("original_description", "")
    context = place.get("reference_context", "")

    # Đặt trọng số cao nhất cho Tên và Mô tả của chính địa điểm đó
    primary_text = f"{name} {location} {desc}"
    full_text = f"{name} {location} {desc} {context}"

    tags = []

    # Tag cơ sở 1: Tỉnh/thành
    tags.append(location.strip().lower())

    # Tag cơ sở 2: Địa hình (Ưu tiên kiểm tra trên primary_text trước)
    found_terrain = False
    for terrain, kws in TERRAIN_KEYWORDS.items():
        if match_keywords(primary_text, kws):
            tags.append(terrain)
            found_terrain = True
            break
    if not found_terrain:
        for terrain, kws in TERRAIN_KEYWORDS.items():
            if match_keywords(full_text, kws):
                tags.append(terrain)
                found_terrain = True
                break
    if not found_terrain:
        tags.append("làng quê & đồng bằng" if any(w in primary_text.lower() for w in ["làng", "đình", "chùa"]) else "đô thị")

    # Tag cơ sở 3: Thể loại chính
    found_cat = False
    for cat, kws in CATEGORY_KEYWORDS.items():
        if match_keywords(primary_text, kws):
            tags.append(cat)
            found_cat = True
            if len([t for t in tags if t in CATEGORY_KEYWORDS]) >= 2:
                break
    if not found_cat:
        for cat, kws in CATEGORY_KEYWORDS.items():
            if match_keywords(full_text, kws):
                tags.append(cat)
                found_cat = True
                break

    # Tags đặc sắc: Quét ẩm thực và hoạt động
    for feature, kws in FEATURE_KEYWORDS.items():
        if match_keywords(full_text, kws):
            tags.append(feature)
        if len(tags) >= 7:
            break

    # Gộp thêm tags gốc từ Excel NHƯNG đã qua bộ lọc bỏ tag rác
    for orig_tag in place.get("original_tags", []):
        t_clean = orig_tag.strip().lower()
        if t_clean and t_clean not in DIRTY_TAGS_BLACKLIST and t_clean not in tags:
            # Chỉ nhận nếu từ khóa gốc xuất hiện trong mô tả
            if t_clean in full_text.lower():
                tags.append(t_clean)

    # Loại bỏ trùng lặp và giữ tối đa 7-8 tags tinh gọn nhất
    return list(dict.fromkeys(tags))[:8]


def enrich_description(place):
    """Tạo câu mô tả kết hợp từ mô tả gốc và ngữ cảnh Kaggle súc tích nhất"""
    orig_desc = place.get("original_description", "").strip()
    context = place.get("reference_context", "").strip()

    if len(orig_desc) >= 40:
        return orig_desc

    if context:
        sentences = re.split(r'(?<=[.!?]) +', context)
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) > 30 and place.get("name", "").lower() in s_clean.lower():
                return f"{orig_desc}. {s_clean}"[:180]
        if sentences:
            return f"{orig_desc}. {sentences[0]}"[:180]

    return orig_desc


def run():
    print("==================================================================")
    print("   QUY TRÌNH DÁN NHÃN 3B: TRI THỨC CHUYÊN NGÀNH (CHUẨN HÓA CAO)   ")
    print("==================================================================")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        places = json.load(f)

    total = len(places)
    print(f"\n-> Đang tiến hành làm giàu cho toàn bộ {total} địa điểm...\n")

    enriched_places = []
    for i, place in enumerate(places, start=1):
        tags = extract_tags(place)
        desc = enrich_description(place)

        enriched = dict(place)
        enriched["tags"] = tags
        enriched["description"] = desc
        enriched_places.append(enriched)

        # In mẫu địa điểm 1 và địa điểm 315 để kiểm chứng
        if i in [1, 2, 315]:
            print(f"[{i}/{total}] {enriched['name']} ({enriched['destination']})")
            print(f"   -> Tags: {enriched['tags']}")
            print(f"   -> Mô tả: {enriched['description'][:90]}...\n")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched_places, f, ensure_ascii=False, indent=2)

    print("==================================================================")
    print(f"✅ THÀNH CÔNG RỰC RỠ! Đã chuẩn hóa toàn bộ {total} địa điểm.")
    print(f"📁 Kết quả lưu tại: backend/data/places_enriched.json")
    print("==================================================================")


if __name__ == "__main__":
    run()
