import requests

url = "http://127.0.0.1:8000/api/places/recommend"

payload = {
    "destination": "Khánh Hòa",
    "interests": ["biển", "thiên nhiên", "nghỉ dưỡng"],
    "top_k": 5
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print("Response:")
print(response.json())