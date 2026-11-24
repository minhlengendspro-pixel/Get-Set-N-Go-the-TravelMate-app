import unittest
from backend.services.input_score import calculate_tag_weights

class TestInputScore(unittest.TestCase):
    def test_solo_weights(self):
        weights = calculate_tag_weights(
            "solo",
            ["leo núi & trekking", "thiên nhiên"]
        )
        self.assertEqual(
            weights,
            {
                "leo núi & trekking": 2.0,
                "thiên nhiên": 1.5
            }
        )

    def test_couple_weights(self):
        weights = calculate_tag_weights(
            "couple",
            ["ngắm hoàng hôn & bình minh"]
        )
        self.assertEqual(
            weights["ngắm hoàng hôn & bình minh"],
            2.0
        )

    def test_family_weights(self):
        weights = calculate_tag_weights(
            "family",
            ["vui chơi giải trí"]
        )
        self.assertEqual(
            weights["vui chơi giải trí"],
            2.0
        )

    def test_random_weights(self):
        weights = calculate_tag_weights(
            "random",
            ["thiên nhiên", "nghỉ dưỡng"]
        )
        self.assertEqual(
            weights,
            {
                "thiên nhiên": 1.0,
                "nghỉ dưỡng": 1.0
            }
        )

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            calculate_tag_weights("friends", [])

    def test_invalid_tag(self):
        with self.assertRaises(ValueError):
            calculate_tag_weights(
                "solo",
                ["tag không tồn tại"]
            )
