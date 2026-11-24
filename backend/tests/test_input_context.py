import unittest
from pydantic import ValidationError
from backend.models.input_context import InputContextRequest

class TestInputContext(unittest.TestCase):
    def test_valid_input(self):
        request = InputContextRequest(
            destination="Đà Nẵng",
            mode="solo",
            budget=3000000,
            duration=3
        )
        self.assertEqual(request.destination, "Đà Nẵng")
        self.assertEqual(request.mode, "solo")
        self.assertEqual(request.duration, 3)
        self.assertEqual(request.interests, [])
        self.assertEqual(request.allergies, [])

    def test_invalid_mode(self):
        with self.assertRaises(ValidationError):
            InputContextRequest(
                destination="Đà Nẵng",
                mode="friends",
                duration=3
            )

    def test_negative_budget(self):
        with self.assertRaises(ValidationError):
            InputContextRequest(
                destination="Đà Nẵng",
                mode="solo",
                budget=-100,
                duration=3
            )

    def test_invalid_duration(self):
        with self.assertRaises(ValidationError):
            InputContextRequest(
                destination="Đà Nẵng",
                mode="solo",
                duration=0
            )
        with self.assertRaises(ValidationError):
            InputContextRequest(
                destination="Đà Nẵng",
                mode="solo",
                duration=31
            )

    def test_user_text_more_than_30_words(self):
        long_text = "du lịch " * 16
        with self.assertRaises(ValidationError):
            InputContextRequest(
                destination="Đà Nẵng",
                mode="solo",
                duration=3,
                user_text=long_text
            )

    def test_user_text_exactly_30_words(self):
        valid_text = "du lịch " * 15
        request = InputContextRequest(
            destination="Đà Nẵng",
            mode="solo",
            duration=3,
            user_text=valid_text
        )
        self.assertEqual(
            len(request.user_text.split()),
            30
        )
