import json
import os
import pandas as pd

# Đường dẫn đến 2 file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(CURRENT_DIR, "DataSet.xlsx")
KAGGLE_PATH = os.path.join(CURRENT_DIR, "vietnam_tourism", "train_vietnam_tourism.json")

print("--- ĐANG ĐỌC DỮ LIỆU ĐỂ KIỂM TRA ---")

# 1. Đọc file Excel (315 địa điểm)
df = pd.read_excel(EXCEL_PATH)
print(f"\n1. File Excel: Có tổng cộng {len(df)} địa điểm.")
sample_place = df.iloc[0]
print("   - Tên mẫu:     ", sample_place["Tên địa điểm"])
print("   - Vị trí:       ", sample_place["Vị trí"])
print("   - Từ khóa gốc:  ", sample_place["Từ Khóa"])

# 2. Đọc file JSON Kaggle
with open(KAGGLE_PATH, "r", encoding="utf-8") as f:
    kaggle_raw = json.load(f)

topics = kaggle_raw.get("data", [])
total_contexts = sum(len(topic.get("paragraphs", [])) for topic in topics)

print(f"\n2. File Kaggle: Có {len(topics)} chủ đề lớn và {total_contexts} đoạn văn ngữ cảnh.")

# In thử 1 đoạn ngữ cảnh mẫu
sample_topic = topics[20]  # Thử lấy 1 chủ đề (ví dụ về Hà Nội)
sample_title = sample_topic.get("title", "")
sample_paragraph = sample_topic.get("paragraphs", [])[0]
sample_context = sample_paragraph.get("context", "")

print(f"   - Chủ đề mẫu:   {sample_title}")
print(f"   - Trích ngữ cảnh: {sample_context[:180]}...")
print("\n--- HOÀN TẤT KIỂM TRA BƯỚC 1! SẴN SÀNG GHÉP DỮ LIỆU ---")