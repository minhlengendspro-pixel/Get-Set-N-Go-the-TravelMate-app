import unittest
from bson import ObjectId
from pymongo import MongoClient
from backend.database import uri
from backend.models.user_preferences import UserPreferences
from backend.services.user_preferences_service import (
    save_preferences,
    get_preferences,
    update_preferences
)

class TestMongoIntegration(unittest.TestCase):
    def test_save_get_update_real_database(self):
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000
        )
        saved_id = None
        try:
            client.admin.command("ping")
            db = client["get_set_n_go_db"]
            collection = db["User_Preferences_Test"]
            preferences = UserPreferences(
                destination="Đà Nẵng",
                mode="solo",
                interests=["biển đảo"],
                tags=["biển đảo"],
                budget=3000000,
                duration=3
            )
            saved_id = save_preferences(
                preferences,
                collection
            )
            self.assertTrue(
                ObjectId.is_valid(saved_id)
            )
            saved_document = get_preferences(
                saved_id,
                collection
            )
            self.assertIsNotNone(saved_document)
            self.assertEqual(
                saved_document["budget"],
                3000000
            )
            new_preferences = UserPreferences(
                destination="Đà Nẵng",
                mode="solo",
                interests=["biển đảo"],
                tags=["biển đảo"],
                budget=5000000,
                duration=3
            )
            updated = update_preferences(
                saved_id,
                new_preferences,
                collection
            )
            self.assertTrue(updated)
            updated_document = get_preferences(
                saved_id,
                collection
            )
            self.assertIsNotNone(updated_document)
            self.assertEqual(
                updated_document["budget"],
                5000000
            )
        finally:
            if saved_id is not None:
                db = client["get_set_n_go_db"]
                collection = db["User_Preferences_Test"]
                collection.delete_one({
                    "_id": ObjectId(saved_id)
                })
            client.close()

if __name__ == "__main__":
    unittest.main()
