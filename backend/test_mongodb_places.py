import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

try:
    client.admin.command("ping")
    print("Ket noi MongoDB thanh cong!")

    db = client["get_set_n_go_db"]
    collection = db["Places"]

    print("Tong so dia diem:", collection.count_documents({}))

    places = list(collection.find().limit(5))

    for place in places:
        print("\nTen:", place.get("name"))
        print("Tags:", place.get("tags"))
        print("Latitude:", place.get("latitude"))
        print("Longitude:", place.get("longitude"))

except Exception as e:
    print("Loi:", e)

finally:
    client.close()