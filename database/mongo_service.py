from pymongo import MongoClient, ASCENDING
from datetime import datetime
from dotenv import load_dotenv
import os


class MongoService:
    def __init__(self):
        load_dotenv()

        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME")

        print("🔗 Connecting to MongoDB...")

        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self.users = self.db["users"]

            # Test database connection
            self.client.admin.command("ping")
            print("✅ MongoDB connection successful!")

            # Index ensures no duplicate emails
            self.users.create_index([("email", ASCENDING)], unique=True)

        except Exception as e:
            print("❌ Connection failed:")
            print(e)
            raise

    def get_user(self, email):
        user = self.users.find_one({"email": email})

        if not user:
            user = {
                "email": email,
                "profile": {
                    "name": None,
                    "age": None,
                    "gender": None,
                    "fitness_level": "beginner",
                    "diet_type": "general",
                    "goal": None,
                    "equipment": [],
                },
                "logs": {"meals": [], "workouts": [], "mood": []},
                "created_at": datetime.utcnow(),
            }
            self.users.insert_one(user)

        return user

    def update_profile(self, email, profile):
        self.users.update_one({"email": email}, {"$set": {"profile": profile}})

    def append_log(self, email, log_type, entry):
        self.users.update_one({"email": email}, {"$push": {f"logs.{log_type}": entry}})
