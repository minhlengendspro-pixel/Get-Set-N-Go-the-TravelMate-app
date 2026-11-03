from pymongo import MongoClient
uri = "mongodb://minhlengendspro_db_user:minhduc123@ac-witmyyy-shard-00-00.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-01.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-02.e9bvp5a.mongodb.net:27017/?ssl=true&replicaSet=atlas-u5mki4-shard-0&authSource=admin&compressors=zlib"
client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()

except Exception as e:
    raise Exception(
        "The following error occurred: ", e)
MONGO_URI = "mongodb+srv://minhlengendspro_db_user:minhduc123@ac-witmyyy-shard-00-00.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-01.e9bvp5a.mongodb.net:27017,ac-witmyyy-shard-00-02.e9bvp5a.mongodb.net:27017/?ssl=true&replicaSet=atlas-u5mki4-shard-0&authSource=admin&compressors=zlib"
# khởi động kết n
client = MongoClient(MONGO_URI)
db = client["get_set_n_go_db"]