# memory/memory_service.py

from database.mongo_service import MongoService


class MemoryService:
    """
    MemoryService acts as an abstraction layer between the agents
    and persistent storage (MongoDB).

    Responsibilities:
    - Retrieve and update user profiles
    - Append logs for workouts, meals, mood, etc.
    - Ensure user exists before writing to storage
    """

    def __init__(self):
        self.db = MongoService()

    # ---------------- Core User Access ---------------- #

    def get_user(self, user_id: str) -> dict:
        """Fetch user record. Auto-creates user if missing."""
        return self.db.get_user(user_id)

    def update_profile(self, user_id: str, new_profile: dict) -> None:
        """Update user profile data."""
        self.db.update_profile(user_id, new_profile)

    def append_log(self, user_id: str, category: str, entry: dict) -> None:
        """Store timestamped data such as meals, workouts or moods."""
        self.db.append_log(user_id, category, entry)

    # ---------------- Optional Helpers ---------------- #

    def clear_logs(self, user_id: str) -> None:
        """Erase stored logs (useful for testing/reset)."""
        self.db.clear_logs(user_id)

    def delete_user(self, user_id: str) -> None:
        """Remove the user completely — optional admin use."""
        self.db.delete_user(user_id)
