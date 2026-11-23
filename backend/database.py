import os
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "get_set_n_go_db")

if not MONGO_URI:
    raise ValueError("Không tìm thấy MONGO_URI trong backend/.env")


client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client[DATABASE_NAME]


def check_connection():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")
        return True

    except Exception as error:
        print(f"MongoDB connection failed: {error}")
        return False