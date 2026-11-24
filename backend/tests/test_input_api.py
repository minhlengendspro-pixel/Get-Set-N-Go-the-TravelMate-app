import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestInputAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_valid_input(self):
        request_data = {
            "destination": "Đà Nẵng",
            "mode": "solo",
            "interests": ["biển đảo"],
            "budget": 3000000,
            "duration": 3,
            "allergies": [],
            "user_text": "Mình thích nghỉ ngơi"
        }
        response = self.client.post(
            "/api/input/validate",
            json=request_data
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("biển đảo", data["tags"])
        self.assertIn("nghỉ dưỡng", data["tags"])
        self.assertEqual(data["tag_weights"]["biển đảo"], 1.0)

    def test_invalid_mode(self):
        request_data = {
            "destination": "Đà Nẵng",
            "mode": "friends",
            "duration": 3
        }
        response = self.client.post(
            "/api/input/validate",
            json=request_data
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_budget(self):
        request_data = {
            "destination": "Đà Nẵng",
            "mode": "solo",
            "budget": -100,
            "duration": 3
        }
        response = self.client.post(
            "/api/input/validate",
            json=request_data
        )
        self.assertEqual(response.status_code, 422)

    def test_unsupported_tag(self):
        request_data = {
            "destination": "Đà Nẵng",
            "mode": "solo",
            "interests": ["tag không tồn tại"],
            "duration": 3
        }
        response = self.client.post(
            "/api/input/validate",
            json=request_data
        )
        self.assertEqual(response.status_code, 422)
