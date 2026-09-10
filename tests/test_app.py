import unittest
from copy import deepcopy

from fastapi import HTTPException

from src import app as app_module


class SignupCapacityTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = deepcopy(app_module.activities)

    def tearDown(self):
        app_module.activities.clear()
        app_module.activities.update(self.original_activities)

    def test_signup_succeeds_when_capacity_is_available(self):
        result = app_module.signup_for_activity("Chess Club", "new@example.edu")

        self.assertEqual(result["message"], "Signed up new@example.edu for Chess Club")

    def test_signup_rejects_full_activity(self):
        activity = app_module.activities["Chess Club"]
        activity["participants"] = [
            f"student{i}@example.edu"
            for i in range(activity["max_participants"])
        ]

        with self.assertRaises(HTTPException) as context:
            app_module.signup_for_activity("Chess Club", "new@example.edu")

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "Activity is full")

    def test_duplicate_signup_remains_rejected(self):
        with self.assertRaises(HTTPException) as context:
            app_module.signup_for_activity(
                "Chess Club", "michael@mergington.edu"
            )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            "Student is already signed up",
        )

    def test_signup_succeeds_after_unregistering(self):
        email = "new@example.edu"
        activity = app_module.activities["Chess Club"]
        activity["participants"] = [
            f"student{i}@example.edu"
            for i in range(activity["max_participants"])
        ]
        activity["participants"][-1] = email

        app_module.unregister_from_activity("Chess Club", email)
        result = app_module.signup_for_activity("Chess Club", email)

        self.assertEqual(result["message"], f"Signed up {email} for Chess Club")


if __name__ == "__main__":
    unittest.main()
