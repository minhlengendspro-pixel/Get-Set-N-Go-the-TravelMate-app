import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_MONGO_URI = "mongodb://minhlengendspro_db_user:minhduc123@ac-witmyyy-shard-00-00.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-01.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-02.e9bvp5a.mongodb.net:27017/?ssl=true&replicaSet=atlas-u5mki4-shard-0&authSource=admin&compressors=zlib"
MONGO_URI = os.getenv("MONGO_URI") or DEFAULT_MONGO_URI

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
