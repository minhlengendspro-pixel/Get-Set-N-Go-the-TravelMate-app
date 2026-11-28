import os
from dotenv import load_dotenv

# Đọc file .env
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(CURRENT_DIR), ".env"))

api_key = os.getenv("GEMINI_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

print("--- ĐANG QUÉT CÁC MODEL GEMINI MÀ TÀI KHOẢN CỦA BẠN ĐƯỢC PHÉP DÙNG ---")
try:
    models = list(client.models.list())
    for m in models:
        # Lấy tên ngắn gọn
        name = getattr(m, "name", str(m))
        print(f" -> {name}")
except Exception as e:
    print("Lỗi khi lấy danh sách model:", e)
