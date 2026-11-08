import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# Xác định thư mục chứa database.py
BASE_DIR = Path(__file__).resolve().parent

# Đọc file .env trong backend
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("Không tìm thấy MONGO_URI trong backend/.env")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client["get_set_n_go_db"]


def check_connection():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")
        return True
    except Exception as error:
        print(f"MongoDB connection failed: {error}")
        return False