
import os
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv

# Đọc file .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Lấy cấu hình từ .env
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "get_set_n_go_db")

if not MONGO_URI:
    raise ValueError("Khong tim thay MONGO_URI trong file .env")

# Tạo kết nối MongoDB
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

# Chọn database
db = client[DATABASE_NAME]


def check_connection():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")
        return True

    except Exception as error:
        print("MongoDB connection failed:", error)
        return False
