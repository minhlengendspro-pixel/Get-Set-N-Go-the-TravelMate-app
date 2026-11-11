import requests
API_URL = "http://127.0.0.1:8000/"
try:
    response = requests.get(API_URL, timeout=5) #Gửi HTTP Get đến FastAPI
    response.raise_for_status() #Kiểm tra phản hồi
    data = response.json()

    print("Kết nối FastAPI thành công!")
    print("Mã trạng thái:", response.status_code)
    print("Dữ liệu nhận được: ", data)

except requests.exceptions.RequestException as error:
    print("Lỗi gọi API: ", error)
except ValueError: 
    print("Backend không trả về JSON hợp lệ")