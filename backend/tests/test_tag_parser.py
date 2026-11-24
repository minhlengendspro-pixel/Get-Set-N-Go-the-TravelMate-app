import unittest
from backend.services.tag_parser import extract_tags

class TestTagParser(unittest.TestCase):
    def test_selected_interests(self):
        tags = extract_tags(
            ["biển đảo", "thiên nhiên"],
            ""
        )
        self.assertEqual(
            tags,
            ["biển đảo", "thiên nhiên"]
        )

    def test_duplicate_interests(self):
        tags = extract_tags(
            ["biển đảo", "biển đảo"],
            ""
        )
        self.assertEqual(tags, ["biển đảo"])

    def test_synonyms(self):
        tags = extract_tags(
            [],
            "Mình thích nghỉ ngơi và leo núi"
        )
        self.assertIn("nghỉ dưỡng", tags)
        self.assertIn("leo núi & trekking", tags)

    def test_basic_negation(self):
        tags = extract_tags(
            [],
            "Mình không thích leo núi"
        )
        self.assertNotIn("leo núi & trekking", tags)

    def test_unsupported_tag(self):
        with self.assertRaises(ValueError):
            extract_tags(["tag không tồn tại"], "")
