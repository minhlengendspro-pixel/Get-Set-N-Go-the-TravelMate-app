
import unittest

from services.place_recommendation import recommend_places


# Dataset giả lập để kiểm thử
TEST_PLACES = [
    {
        "id": "1",
        "name": "Bãi Dài",
        "destination": "Khánh Hòa",
        "description": "Bãi biển đẹp",
        "tags": ["biển", "chụp ảnh", "vui chơi"],
        "rating": 4.8,
        "image_url": ""
    },
    {
        "id": "2",
        "name": "Tháp Bà Ponagar",
        "destination": "Khánh Hòa",
        "description": "Di tích văn hóa Chăm",
        "tags": ["tham quan", "văn hóa", "di tích"],
        "rating": 4.5,
        "image_url": ""
    },
    {
        "id": "3",
        "name": "Địa điểm thiếu tags",
        "destination": "Khánh Hòa",
        "tags": [],
        "rating": 4.0
    },
    {
        "id": "4",
        "name": "Địa điểm tỉnh khác",
        "destination": "Đà Nẵng",
        "tags": ["biển", "chụp ảnh"],
        "rating": 4.7
    }
]


class TestPlaceRecommendation(unittest.TestCase):

    # Test 1: Địa điểm phù hợp phải được đề xuất
    def test_recommend_matching_places(self):
        results = recommend_places(
            destination="Khánh Hòa",
            interests=["biển", "chụp ảnh"],
            places=TEST_PLACES
        )

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["name"], "Bãi Dài")

    # Test 2: Không trả về địa điểm thiếu tags
    def test_exclude_empty_tags(self):
        results = recommend_places(
            destination="Khánh Hòa",
            interests=["biển"],
            places=TEST_PLACES
        )

        names = [place["name"] for place in results]

        self.assertNotIn("Địa điểm thiếu tags", names)

    # Test 3: Chỉ lấy địa điểm thuộc tỉnh được chọn
    def test_filter_destination(self):
        results = recommend_places(
            destination="Khánh Hòa",
            interests=["biển"],
            places=TEST_PLACES
        )

        for place in results:
            self.assertEqual(
                place["destination"],
                "Khánh Hòa"
            )

    # Test 4: Không có sở thích phải báo lỗi
    def test_empty_interests(self):
        with self.assertRaises(ValueError):
            recommend_places(
                destination="Khánh Hòa",
                interests=[],
                places=TEST_PLACES
            )

    # Test 5: Không có địa điểm phù hợp phải trả về []
    def test_no_matching_places(self):
        results = recommend_places(
            destination="Khánh Hòa",
            interests=["trượt tuyết"],
            places=TEST_PLACES
        )

        self.assertEqual(results, [])

    # Test 6: Kết quả không vượt quá top_k
    def test_top_k_limit(self):
        results = recommend_places(
            destination="Khánh Hòa",
            interests=["biển", "chụp ảnh", "tham quan"],
            places=TEST_PLACES,
            top_k=1
        )

        self.assertLessEqual(len(results), 1)

    # Test 7: Điểm similarity phải nằm trong khoảng 0 đến 1
    def test_similarity_score_range(self):
        results = recommend_places(
            destination="Khánh Hòa",
            interests=["biển"],
            places=TEST_PLACES
        )

        for place in results:
            self.assertGreater(place["score"], 0)
            self.assertLessEqual(place["score"], 1)

    def test_top_k_boolean(self):
      with self.assertRaises(ValueError):
        recommend_places(
            destination="Da Nang",
            interests=["beach"],
            places=TEST_PLACES,
            top_k=True
        )
    def test_ignore_none_interests(self):
        result = recommend_places(
            destination="Da Nang",
            interests=["beach", None],
            places=TEST_PLACES
    )

        self.assertTrue(all(
        "none" not in place["matched_tags"]
        for place in result
    ))

    def test_ignore_invalid_place_records(self):
         places = TEST_PLACES + [None, "invalid data", 123]

         result = recommend_places(
              destination="Khánh Hòa",
              interests=["biển"],
              places=places
    )

         self.assertTrue(len(result) > 0)

         self.assertTrue(all(
             isinstance(place, dict) for place in result
    ))

         self.assertTrue(all(
             place["destination"] == "Khánh Hòa"
             for place in result
    ))

if __name__ == "__main__":
    unittest.main(verbosity=2)
