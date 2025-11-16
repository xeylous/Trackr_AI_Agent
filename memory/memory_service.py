# import json
# import os

# class MemoryService:
#     def __init__(self, path="memory.json"):
#         self.path = path
#         self._data = {"users": {}}
#         self._load()

#     def _load(self):
#         if os.path.exists(self.path):
#             with open(self.path, "r") as f:
#                 self._data = json.load(f)

#     def _save(self):
#         with open(self.path, "w") as f:
#             json.dump(self._data, f, indent=2)

#     def get_user(self, user_id: str):
#         if user_id not in self._data["users"]:
#             self._data["users"][user_id] = {
#                 "profile": {
#                     "fitness_level": "beginner",
#                     "diet_type": "general",
#                     "equipment": []
#                 },
#                 "logs": {
#                     "workouts": [],
#                     "meals": [],
#                     "mood": []
#                 }
#             }
#             self._save()
#         return self._data["users"][user_id]

#     def append_log(self, user_id: str, type_: str, entry: dict):
#         user = self.get_user(user_id)
#         user["logs"][type_].append(entry)
#         self._save()

# memory/memory_service.py

import json
import os

class MemoryService:
    def __init__(self, path: str = "memory.json"):
        self.path = path
        self._data = {"users": {}}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {"users": {}}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get_user(self, user_id: str):
        if user_id not in self._data["users"]:
            self._data["users"][user_id] = {
                "profile": {
                    "name": None,
                    "age": None,
                    "gender": None,   # 'male' | 'female' | 'non-binary' | 'prefer not to say'
                    "fitness_level": "beginner",
                    "diet_type": "general",
                    "equipment": [],
                    "goals": []
                },
                "logs": {
                    "workouts": [],
                    "meals": [],
                    "mood": [],
                    "journal": []
                }
            }
            self._save()
        return self._data["users"][user_id]

    def append_log(self, user_id: str, log_type: str, entry: dict):
        user = self.get_user(user_id)
        user["logs"].setdefault(log_type, []).append(entry)
        self._save()
