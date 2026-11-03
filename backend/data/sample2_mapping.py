import json
import os
import re
import pandas as pd

# Đường dẫn file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(CURRENT_DIR, "DataSet.xlsx")
KAGGLE_PATH = os.path.join(CURRENT_DIR, "vietnam_tourism", "train_vietnam_tourism.json")
OUTPUT_PATH = os.path.join(CURRENT_DIR, "mapped_places.json")

# Bản đồ vùng miền hỗ trợ mở rộng ngữ cảnh cho các tỉnh ngách
REGION_MAP = {
    "kon tum": "tây nguyên", "gia lai": "tây nguyên", "đắk lắk": "tây nguyên",
    "đắk nông": "tây nguyên", "lâm đồng": "tây nguyên",
    "lai châu": "tây bắc", "điện biên": "tây bắc", "sơn la": "tây bắc",
    "lào cai": "tây bắc", "yên bái": "tây bắc", "hòa bình": "tây bắc",
    "hà giang": "đông bắc", "cao bằng": "đông bắc", "lạng sơn": "đông bắc",
    "cần thơ": "đồng bằng sông cửu long", "an giang": "đồng bằng sông cửu long",
    "kiên giang": "đồng bằng sông cửu long", "cà mau": "đồng bằng sông cửu long"
}

def clean_tags(tag_str):
    """Làm sạch chuỗi '"biển" , "vui chơi"' thành list: ['biển', 'vui chơi']"""
    if not tag_str or pd.isna(tag_str):
        return []
    tags = str(tag_str).split(",")
    cleaned = [re.sub(r'[\'"]', '', t).strip().lower() for t in tags]
    return [t for t in cleaned if t]

def run_mapping():
    print("--- ĐANG THỰC HIỆN GHÉP NỐI NGỮ CẢNH (CONTEXT MAPPING) ---")
    
    # 1. Đọc dữ liệu
    df = pd.read_excel(EXCEL_PATH)
    with open(KAGGLE_PATH, "r", encoding="utf-8") as f:
        kaggle_raw = json.load(f)

    # Gom phẳng tất cả 1.386 đoạn văn ngữ cảnh
    all_paras = []
    for topic in kaggle_raw.get("data", []):
        t_title = topic.get("title", "")
        for p in topic.get("paragraphs", []):
            ctx = p.get("context", "").strip()
            if ctx:
                all_paras.append({"title": t_title, "context": ctx})

    print(f"-> Đã chuẩn bị {len(all_paras)} đoạn văn ngữ cảnh tham chiếu.")

    mapped_results = []
    direct_hits = 0
    loc_hits = 0

    # 2. Quét qua 315 địa điểm
    for i, row in df.iterrows():
        place_name = str(row["Tên địa điểm"]).strip()
        location = str(row["Vị trí"]).strip()
        old_desc = str(row["Mô tả"]).strip()
        cleaned_tags_list = clean_tags(row["Từ Khóa"])

        # Tìm kiếm ngữ cảnh phù hợp
        matched_contexts = []

        # Tầng 1: Khớp theo Tên địa điểm
        for p in all_paras:
            if place_name.lower() in p["context"].lower() or place_name.lower() in p["title"].lower():
                matched_contexts.append(p["context"])
                if len(matched_contexts) >= 2:
                    break

        if matched_contexts:
            direct_hits += 1
        else:
            # Tầng 2: Khớp theo Tỉnh/Thành
            for p in all_paras:
                if location.lower() in p["context"].lower() or location.lower() in p["title"].lower():
                    matched_contexts.append(p["context"])
                    if len(matched_contexts) >= 2:
                        break
            if matched_contexts:
                loc_hits += 1
            else:
                # Tầng 3: Khớp theo Vùng miền
                region = REGION_MAP.get(location.lower(), "")
                if region:
                    for p in all_paras:
                        if region in p["context"].lower() or region in p["title"].lower():
                            matched_contexts.append(p["context"])
                            if len(matched_contexts) >= 1:
                                break

        # Gộp ngữ cảnh và giới hạn độ dài ~800 ký tự để súc tích
        merged_context = " ".join(matched_contexts)[:800]
        if not merged_context:
            merged_context = old_desc  # Tầng 4 dự phòng: dùng luôn mô tả gốc nếu quá ngách

        mapped_results.append({
            "id": f"P{i+1:03d}",
            "name": place_name,
            "destination": location,
            "category": "sightseeing",
            "original_description": old_desc,
            "original_tags": cleaned_tags_list,
            "rating": str(row["Đánh giá "]).strip(),
            "image": str(row["Ảnh"]).strip(),
            "reference_context": merged_context
        })

    # 3. Xuất file kết quả trung gian
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(mapped_results, f, ensure_ascii=False, indent=2)

    print(f"\nKẾT QUẢ GHÉP NỐI:")
    print(f" - Khớp trực tiếp tên địa danh: {direct_hits}/315")
    print(f" - Khớp theo Tỉnh/Vùng miền:     {loc_hits}/315")
    print(f" - Tổng số điểm đã sẵn sàng:    {len(mapped_results)}/315")
    print(f"-> Đã lưu kết quả ra file: mapped_places.json")
    print("--- HOÀN TẤT BƯỚC 2! ---")

if __name__ == "__main__":
    run_mapping()