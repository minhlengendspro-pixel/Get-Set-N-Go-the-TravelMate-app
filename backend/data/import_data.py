import pandas as pd
from pymongo import MongoClient

# 1. Cấu hình kết nối MongoDB Atlas
# Thay thế <username>, <password>, và <cluster-url> bằng chuỗi kết nối thực tế trên Atlas của bạn
MONGO_URI = "mongodb+srv://minhduc:minhduc123@cluster0.e9bvp5a.mongodb.net/"

DATABASE_NAME = "get_set_n_go_db"
COLLECTION_NAME = "Places"
EXCEL_FILE_PATH = "DataSet.xlsx"

def import_excel_to_mongodb():
    try:
        # 2. Đọc file Excel bằng pandas
        print(f"Đang đọc dữ liệu từ file: {EXCEL_FILE_PATH}...")
        df = pd.read_excel(EXCEL_FILE_PATH)
        
        # Xử lý các ô trống (NaN) thành None để MongoDB nhận diện là kiểu Null thay vì lỗi NaN
        df = df.where(pd.notnull(df), None)
        
        # Chuyển DataFrame thành danh sách các từ điển (mỗi dict tương đương 1 document)
        records = df.to_dict(orient='records')
        
        # 3. Kết nối tới MongoDB Atlas
        print("Đang kết nối tới MongoDB Atlas...")
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # 4. Thêm dữ liệu vào Collection
        print(f"Chuẩn bị đẩy {len(records)} bản ghi vào collection '{COLLECTION_NAME}'...")
        
        # (Tùy chọn) Xóa sạch dữ liệu cũ trong collection trước khi import mới
        # collection.delete_many({}) 
        
        # Insert hàng loạt (bulk insert) để tối ưu hiệu năng
        result = collection.insert_many(records)
        
        print(f"Thành công! Đã thêm {len(result.inserted_ids)} bản ghi vào cơ sở dữ liệu.")
        
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    import_excel_to_mongodb()