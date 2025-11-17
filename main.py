# main.py

import re
from memory.memory_service import MemoryService
from tools.gemini_client import GeminiClient

from agents.fitness_agent import FitnessAgent
from agents.nutrition_agent import NutritionAgent
from agents.mindfulness_agent import MindfulnessAgent
from agents.analytics_agent import AnalyticsAgent

from services.auth_service import AuthService



class Orchestrator:
    def __init__(self):
        self.memory = MemoryService()
        self.llm = GeminiClient()
        self.auth = AuthService(self.memory)

        # Agents
        self.fitness_agent = FitnessAgent(self.memory, self.llm)
        self.nutrition_agent = NutritionAgent(self.memory, self.llm)
        self.mindfulness_agent = MindfulnessAgent(self.memory, self.llm)
        self.analytics_agent = AnalyticsAgent(self.memory, None)

    # ---------------- Onboarding ---------------- #

    def onboarding(self, email: str, message: str):
        user = self.memory.get_user(email)
        profile = user["profile"]
        status = user.get("onboarding_status", {"step": 0, "completed": False})

        if status.get("completed"):
            return None

        step = status.get("step", 0)

        if step == 0:
            profile["name"] = message.strip().title()
            status["step"] = 1
            self.memory.update_profile(email, profile)
            self.memory.db.users.update_one({"email": email}, {"$set": {"onboarding_status": status}})
            return {"agent": "system", "message": f"Nice to meet you, {profile['name']} 😊\nHow old are you?"}

        if step == 1:
            num = re.findall(r"\d+", message)
            if num:
                profile["age"] = int(num[0])
                status["step"] = 2
                self.memory.update_profile(email, profile)
                self.memory.db.users.update_one({"email": email}, {"$set": {"onboarding_status": status}})
                return {
                    "agent": "system",
                    "message": "Got it! What gender do you identify with?\n(male / female / non-binary / prefer not to say)"
                }
            return {"agent": "system", "message": "Please enter a valid number for age 😊"}

        if step == 2:
            gender = message.lower().strip()
            valid = ["male", "female", "non-binary", "prefer not to say"]
            if gender in valid:
                profile["gender"] = gender
                status["completed"] = True
                self.memory.update_profile(email, profile)
                self.memory.db.users.update_one({"email": email}, {"$set": {"onboarding_status": status}})

                return {
                    "agent": "system",
                    "message": (
                        f"Awesome! You're all set, {profile['name']} 🎉\n\n"
                        "You can now:\n"
                        "• 🍽 Log meals\n"
                        "• 🧘 Check your emotions\n"
                        "• 🏋️ Request a workout\n"
                        "• 📊 Ask for a progress summary\n\n"
                        "How can I help today?"
                    )
                }

            return {"agent": "system", "message": "Please choose a valid option 🙏"}

        return None

    # ---------------- Intent Detection ---------------- #

    def detect_intent(self, msg: str) -> str:
        msg = msg.lower()

        rules = {
            "fitness": ["workout", "exercise", "gym", "pushups", "squats"],
            "nutrition": ["i ate", "meal", "breakfast", "lunch", "dinner", "food"],
            "mindfulness": ["feel", "mood", "stress", "sad", "happy", "anxious"],
            "analytics": ["progress", "summary", "stats", "report"]
        }

        for intent, words in rules.items():
            if any(word in msg for word in words):
                return intent

        return "unknown"

    # ---------------- Route Requests ---------------- #

    def handle(self, email: str, message: str) -> dict:

        onboarding_response = self.onboarding(email, message)
        if onboarding_response:
            return onboarding_response

        intent = self.detect_intent(message)
        ctx = {}

        if intent == "fitness":
            match = re.search(r'\d+', message)
            if match:
                ctx["minutes"] = int(match.group(0))
            return {"agent": "fitness", "data": self.fitness_agent.handle(email, message, ctx)}

        if intent == "nutrition":
            cleaned = message.lower().replace("i ate", "").strip()
            ctx["meal_description"] = cleaned
            return {"agent": "nutrition", "data": self.nutrition_agent.handle(email, cleaned, ctx)}

        if intent == "mindfulness":
            mood = "neutral"
            if any(w in message.lower() for w in ["sad", "stressed", "bad"]): mood = "low"
            if any(w in message.lower() for w in ["happy", "great"]): mood = "high"
            ctx["mood"] = mood
            return {"agent": "mindfulness", "data": self.mindfulness_agent.handle(email, message, ctx)}

        if intent == "analytics":
            return {"agent": "analytics", "data": self.analytics_agent.handle(email, message, ctx)}

        return {
            "agent": "system",
            "message": "Hmm... I didn’t catch that 🤔\nTry:\n• “I ate pasta”\n• “Give me a workout”\n• “I feel stressed”\n• “Show stats”"
        }

    # ---------------- Output for Terminal ---------------- #

    def pretty_print(self, res: dict):
        if res.get("agent") == "system":
            print("\n💬", res.get("message"), "\n")
            return

        print("\n🤖", res, "\n")


# ---------------- Main Program ---------------- #

def main():
    orch = Orchestrator()

    print("\n✨ Welcome to Trackr AI — your wellbeing companion ✨")

    email = input("\n📧 Enter your email: ").strip().lower()

    print("\n📨 Sending OTP...")
    if not orch.auth.start_login(email):
        print("❌ OTP could not be sent. Check email config.")
        return

    print(f"📧 OTP sent to {email} — check inbox!")

    while True:
        otp = input("🔐 Enter OTP: ").strip()
        if orch.auth.verify(email, otp):
            print("\n🎉 Login successful!")
            break
        print("❌ Incorrect OTP — try again.\n")

    print("\nLet's get started 😊 What's your name?\n")

    while True:
        msg = input("You: ")
        if msg.lower() in ["exit", "quit"]:
            print("\n👋 Take care — small steps build big change 💛")
            break

        reply = orch.handle(email, msg)
        orch.pretty_print(reply)


if __name__ == "__main__":
    main()
