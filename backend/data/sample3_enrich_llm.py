import json
import os
import time
from dotenv import load_dotenv

# 1. Tải API Key từ file backend/.env một cách chính xác
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(os.path.dirname(CURRENT_DIR), ".env")
load_dotenv(ENV_PATH)
load_dotenv() # Dự phòng nếu file .env nằm ở thư mục gốc

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY or API_KEY.strip() == "":
    print("❌ LỖI: Chưa tìm thấy GEMINI_API_KEY trong file backend/.env")
    print(f"Đường dẫn file .env đang đọc: {ENV_PATH}")
    exit(1)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ LỖI: Chưa cài đặt thư viện 'google-genai'.")
    print("👉 Hãy mở terminal và chạy lệnh: pip install google-genai")
    exit(1)

# Khởi tạo client Gemini
client = genai.Client(api_key=API_KEY)

# Đường dẫn file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(CURRENT_DIR, "mapped_places.json")
OUTPUT_PATH = os.path.join(CURRENT_DIR, "places_enriched.json")
TEST_OUTPUT_PATH = os.path.join(CURRENT_DIR, "test_places_preview.json")

# ==============================================================================
# CẤU HÌNH CHẾ ĐỘ CHẠY:
# - TEST_MODE = True:  Chỉ chạy thử 3 địa điểm để bạn kiểm tra kết quả ngay.
# - TEST_MODE = False: Chạy toàn bộ 315 địa điểm để hoàn thành đồ án.
# ==============================================================================
TEST_MODE = True
LIMIT_TEST = 3


def build_prompt(place):
    return f"""
Bạn là chuyên gia dữ liệu du lịch và ẩm thực Việt Nam cho ứng dụng TravelMate.
Hãy phân tích thông tin địa điểm dưới đây:
- Tên địa điểm: {place['name']}
- Tỉnh/Thành phố: {place['destination']}
- Mô tả ban đầu: {place['original_description']}
- Tags ban đầu: {', '.join(place['original_tags'])}
- Ngữ cảnh thực tế từ cẩm nang du lịch: {place['reference_context']}

Nhiệm vụ của bạn:
1. "enriched_tags": Trích xuất từ 5 đến 8 tags phân tầng chặt chẽ:
   - [BẮT BUỘC 1]: Chọn đúng 1 tag loại hình chính: ['thiên nhiên', 'văn hóa - lịch sử', 'nghỉ dưỡng', 'ẩm thực', 'vui chơi giải trí']
   - [BẮT BUỘC 2]: Chọn đúng 1 tag địa hình: ['biển đảo', 'núi rừng', 'đô thị', 'sông nước']
   - [TAGS ĐẶC SẮC (3-5 tags)]: Tên món ăn đặc sản, ẩm thực địa phương (nếu có liên quan), hoạt động trải nghiệm nổi bật (tắm biển, ngắm hoàng hôn, lặn san hô, chụp ảnh, leo núi...), không khí (chill, sôi động, yên bình...).
   - Quy tắc: Viết thường toàn bộ, tiếng Việt có dấu, không chứa ký tự lạ.

2. "enriched_description": Viết lại 1 đoạn mô tả súc tích (1 - 2 câu, khoảng 25 - 40 từ) thật hấp dẫn, làm nổi bật điểm nhấn cảnh quan và trải nghiệm/ẩm thực đặc sắc nhất.

Trả về DUY NHẤT một khối JSON hợp lệ theo định dạng:
{{
  "enriched_tags": ["thiên nhiên", "biển đảo", "hải sản tươi sống", "tắm biển", "ngắm hoàng hôn"],
  "enriched_description": "..."
}}
"""


CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.8-flash-lite"
]


def call_gemini_with_fallback(client, prompt):
    """Tự động chuyển đổi giữa các model và thử lại nếu gặp lỗi 503 (Server bận)"""
    last_error = None
    for model_name in CANDIDATE_MODELS:
        for attempt in range(2):  # Thử lại tối đa 2 lần
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2,
                    ),
                )
                return json.loads(response.text), model_name
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(2)  # Đợi 2 giây nếu server đang quá tải
                    continue
                else:
                    break  # Lỗi khác thì đổi sang model tiếp theo
    raise last_error


def enrich_data():
    print("========================================================")
    print("   QUY TRÌNH DÁN NHÃN ĐẶC TRƯNG & BASE TAGS BẰNG GEMINI")
    print("========================================================")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        places = json.load(f)

    target_places = places[:LIMIT_TEST] if TEST_MODE else places
    total = len(target_places)

    print(f"-> Chế độ: {'[TEST THỬ NGHIỆM - 3 ĐỊA ĐIỂM]' if TEST_MODE else '[CHẠY TOÀN BỘ 315 ĐỊA ĐIỂM]'}")
    print(f"-> Số lượng cần xử lý: {total} địa điểm\n")

    enriched_results = []

    for index, place in enumerate(target_places, start=1):
        print(f"[{index}/{total}] Đang xử lý: {place['name']} ({place['destination']})...")
        prompt = build_prompt(place)

        try:
            # Gọi Gemini với cơ chế tự động chuyển model dự phòng
            result_json, used_model = call_gemini_with_fallback(client, prompt)
            ai_tags = [t.strip().lower() for t in result_json.get("enriched_tags", []) if t.strip()]

            # --- TẦNG BẢO VỆ CODE: Ghim thêm Base Tag Tỉnh/Thành ---
            location_tag = place["destination"].strip().lower()
            combined_tags = [location_tag] + ai_tags
            # Loại bỏ trùng lặp giữ nguyên thứ tự
            final_tags = list(dict.fromkeys(combined_tags))

            enriched_place = dict(place)
            enriched_place["tags"] = final_tags
            enriched_place["description"] = result_json.get("enriched_description", place["original_description"])

            enriched_results.append(enriched_place)

            print(f"   -> [Model: {used_model}]")
            print(f"   -> Tags hoàn chỉnh (Base + AI): {enriched_place['tags']}")
            print(f"   -> Mô tả mới: {enriched_place['description']}\n")

            # Nghỉ ngắn giữa các request
            time.sleep(0.5)

        except Exception as e:
            print(f"   ⚠️ Lưu ý: {place['name']} dùng dữ liệu gốc do: {e}")
            enriched_place = dict(place)
            enriched_place["tags"] = [place["destination"].lower()] + place["original_tags"]
            enriched_place["description"] = place["original_description"]
            enriched_results.append(enriched_place)

    # Lưu kết quả
    output_file = TEST_OUTPUT_PATH if TEST_MODE else OUTPUT_PATH
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enriched_results, f, ensure_ascii=False, indent=2)

    print("========================================================")
    print(f"✅ HOÀN TẤT! Đã lưu kết quả ra: {os.path.basename(output_file)}")
    print("========================================================")
    if TEST_MODE:
        print("\n👉 Bạn hãy xem 3 địa điểm mẫu vừa chạy trên terminal.")
        print("   Nếu thấy tags và mô tả chuẩn xịn:")
        print("   1. Mở file `backend/data/sample3_enrich_llm.py`.")
        print("   2. Sửa dòng: `TEST_MODE = False`.")
        print("   3. Chạy lại để hoàn thành cả 315 địa điểm!")


if __name__ == "__main__":
    enrich_data()
