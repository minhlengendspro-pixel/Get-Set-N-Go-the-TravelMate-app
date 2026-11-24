import unittest
from unittest.mock import Mock
from bson import ObjectId
from backend.models.user_preferences import UserPreferences
from backend.services.user_preferences_service import (
    save_preferences,
    get_preferences,
    update_preferences
)
from pymongo.errors import PyMongoError

class TestUserPreferencesService(unittest.TestCase):
    def test_save_preferences(self):
        collection = Mock()
        collection.insert_one.return_value.inserted_id = ObjectId()
        preferences = UserPreferences(
            destination="Đà Nẵng",
            mode="solo",
            interests=["biển đảo"],
            tags=["biển đảo"],
            duration=3
        )
        preference_id = save_preferences(preferences, collection)
        self.assertIsInstance(preference_id, str)
        collection.insert_one.assert_called_once()

    def test_get_preferences_found(self):
        collection = Mock()
        document_id = ObjectId()
        collection.find_one.return_value = {
            "_id": document_id,
            "mode": "solo"
        }
        document = get_preferences(str(document_id), collection)
        self.assertEqual(document["_id"], str(document_id))
        self.assertEqual(document["mode"], "solo")
        collection.find_one.assert_called_once_with(
            {"_id": document_id}
        )

    def test_get_preferences_not_found(self):
        collection = Mock()
        collection.find_one.return_value = None
        document = get_preferences(str(ObjectId()), collection)
        self.assertIsNone(document)

    def test_update_preferences_found(self):
        collection = Mock()
        collection.update_one.return_value.matched_count = 1
        preferences = UserPreferences(
            destination="Đà Nẵng",
            mode="solo",
            budget=5000000,
            duration=3
        )
        updated = update_preferences(
            str(ObjectId()),
            preferences,
            collection
        )
        self.assertTrue(updated)
        collection.update_one.assert_called_once()

    def test_update_preferences_not_found(self):
        collection = Mock()
        collection.update_one.return_value.matched_count = 0
        preferences = UserPreferences(
            destination="Đà Nẵng",
            mode="solo",
            duration=3
        )
        updated = update_preferences(
            str(ObjectId()),
            preferences,
            collection
        )
        self.assertFalse(updated)


    def test_save_preferences_database_error(self):
        collection = Mock()
        collection.insert_one.side_effect = PyMongoError(
            "Không thể kết nối Database"
        )
        preferences = UserPreferences(
            destination="Đà Nẵng",
            mode="solo",
            interests=["biển đảo"],
            tags=["biển đảo"],
            duration=3
        )
        with self.assertRaises(PyMongoError):
            save_preferences(preferences, collection)
        collection.insert_one.assert_called_once()

    
    def test_get_preferences_invalid_id(self):
        collection = Mock()
        with self.assertRaises(ValueError):
            get_preferences("abc", collection)
        collection.find_one.assert_not_called()

    def test_update_preferences_invalid_id(self):
        collection = Mock()
        preferences = UserPreferences(
            destination="Đà Nẵng",
            mode="solo",
            duration=3
        )
        with self.assertRaises(ValueError):
            update_preferences("abc", preferences, collection)
        collection.update_one.assert_not_called()

    def test_update_preferences_correct_data(self):
        collection = Mock()
        collection.update_one.return_value.matched_count = 1
        document_id = ObjectId()
        preferences = UserPreferences(
            destination="Đà Nẵng",
            mode="solo",
            interests=["biển đảo"],
            tags=["biển đảo"],
            budget=5000000,
            duration=3
        )
        updated = update_preferences(
            str(document_id),
            preferences,
            collection
        )
        expected_condition = {"_id": document_id}
        expected_data = preferences.model_dump(
            exclude={"created_at"}
        )
        collection.update_one.assert_called_once_with(
            expected_condition,
            {"$set": expected_data}
        )
        self.assertTrue(updated)

    def test_get_preferences_database_error(self):
        collection = Mock()
        collection.find_one.side_effect = PyMongoError(
            "Lỗi khi đọc Database"
        )
        with self.assertRaises(PyMongoError):
            get_preferences(str(ObjectId()), collection)
        collection.find_one.assert_called_once()

    def test_update_preferences_database_error(self):
        collection = Mock()
        collection.update_one.side_effect = PyMongoError(
            "Lỗi khi cập nhật Database"
        )
        preferences = UserPreferences(
            destination="Đà Nẵng",
            mode="solo",
            duration=3
        )
        with self.assertRaises(PyMongoError):
            update_preferences(
                str(ObjectId()),
                preferences,
                collection
            )
        collection.update_one.assert_called_once()

