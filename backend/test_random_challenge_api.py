
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routes.random_challenge_test import router


app = FastAPI()
app.include_router(router)

client = TestClient(app)


TEST_PLACES = [
    {
        "id": 1,
        "name": "Bãi Dài",
        "tags": ["biển", "thiên nhiên", "check-in"],
        "rating": 4.5
    },
    {
        "id": 2,
        "name": "Hòn Chồng",
        "tags": ["biển", "tham quan"],
        "rating": 4.3
    },
    {
        "id": 3,
        "name": "Tháp Bà Ponagar",
        "tags": ["văn hóa", "tham quan", "check-in"],
        "rating": 4.7
    },
    {
        "id": 4,
        "name": "VinWonders",
        "tags": ["giải trí", "check-in", "tham quan"],
        "rating": 4.6
    },
    {
        "id": 5,
        "name": "Viện Hải dương học",
        "tags": ["tham quan", "giáo dục"],
        "rating": 4.4
    }
]


response = client.post(
    "/api/random-challenge-test/",
    json={"places": TEST_PLACES}
)

print("========== RANDOM CHALLENGE API TEST ==========")
print("Status code:", response.status_code)
print("Response:")

print(response.json())

assert response.status_code == 200
assert response.json()["success"] is True
assert 2 <= len(response.json()["data"]["tags"]) <= 4

print("\nALL API CHECKS PASSED!")
