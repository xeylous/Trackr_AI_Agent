# main.py

import re
from memory.memory_service import MemoryService
from tools.gemini_client import GeminiClient

from agents.fitness_agent import FitnessAgent
from agents.nutrition_agent import NutritionAgent
from agents.mindfulness_agent import MindfulnessAgent
from agents.analytics_agent import AnalyticsAgent


class Orchestrator:
    def __init__(self):
        self.memory = MemoryService()
        self.llm = GeminiClient()

        # Initialize agents
        self.fitness_agent = FitnessAgent(self.memory, self.llm)
        self.nutrition_agent = NutritionAgent(self.memory, self.llm)
        self.mindfulness_agent = MindfulnessAgent(self.memory, self.llm)
        self.analytics_agent = AnalyticsAgent(self.memory, None)  # No LLM needed

    # ----------------- Onboarding Before Agent Logic ----------------- #
    def onboarding(self, user_id: str, message: str):
        user = self.memory.get_user(user_id)
        profile = self.memory.get_user(user_id)["profile"]

        defaults = {
            "name": None,
            "age": None,
            "gender": None,
            "fitness_level": profile.get("fitness_level", "beginner"),
            "diet_type": profile.get("diet_type", "general"),
            "goals": profile.get("goals", None),
            "equipment": profile.get("equipment", [])
        }

        for key, val in defaults.items():
            if key not in profile:
                profile[key] = val

        user["profile"] = profile
        self.memory._save()

        # Step 1: Ask name
        if profile["name"] is None:
            profile["name"] = message.strip().title()
            self.memory._save()
            return {"agent": "system", "message": f"Nice to meet you, {profile['name']}! How old are you?"}

        # Step 2: Ask age
        if profile["age"] is None:
            num = re.findall(r"\d+", message)
            if num:
                profile["age"] = int(num[0])
                self.memory._save()
                return {
                    "agent": "system",
                    "message": "Thanks! What gender do you identify with? (male / female / non-binary / prefer not to say)"
                }
            return {"agent": "system", "message": "Please enter a valid age number."}

        # Step 3: Ask gender
        if profile["gender"] is None:
            gender = message.lower().strip()
            valid = ["male", "female", "non-binary", "prefer not to say"]
            if gender in valid:
                profile["gender"] = gender
                self.memory._save()
                return {
                    "agent": "system",
                    "message": (
                        f"Great! You're all set, {profile['name']}.\n"
                        "You can now log meals 🍽️, request workouts 🏋️, or check in with emotions 🧘."
                    )
                }
            return {"agent": "system", "message": "Choose one: male / female / non-binary / prefer not to say"}

        return None  # Onboarding complete

    # ----------------- Intent Routing ----------------- #
    def detect_intent(self, message: str) -> str:
        text = message.lower()

        if any(w in text for w in ["workout", "exercise", "gym", "pushups", "squats"]):
            return "fitness"
        if any(w in text for w in ["i ate", "meal", "breakfast", "lunch", "dinner", "food"]):
            return "nutrition"
        if any(w in text for w in ["feel", "mood", "stress", "sad", "happy", "anxious"]):
            return "mindfulness"
        if any(w in text for w in ["progress", "summary", "stats", "report"]):
            return "analytics"

        return "unknown"

    # ----------------- Main Handler ----------------- #
    def handle(self, user_id: str, message: str) -> dict:

        # Run onboarding first
        onboarding_check = self.onboarding(user_id, message)
        if onboarding_check:
            return onboarding_check

        intent = self.detect_intent(message)
        context = {}

        if intent == "fitness":
            match = re.search(r"(\d+)", message)
            if match:
                context["minutes"] = int(match.group(1))
            return {"agent": "fitness", "data": self.fitness_agent.handle(user_id, message, context)}

        if intent == "nutrition":
            cleaned = message.lower().replace("i ate", "").strip()
            context["meal_description"] = cleaned
            return {"agent": "nutrition", "data": self.nutrition_agent.handle(user_id, cleaned, context)}

        if intent == "mindfulness":
            mood = "neutral"
            if any(w in message.lower() for w in ["sad", "low", "stressed", "bad"]): mood = "low"
            if any(w in message.lower() for w in ["happy", "good", "great"]): mood = "high"
            context["mood"] = mood
            return {"agent": "mindfulness", "data": self.mindfulness_agent.handle(user_id, message, context)}

        if intent == "analytics":
            return {"agent": "analytics", "data": self.analytics_agent.handle(user_id, message, context)}

        return {
            "agent": "system",
            "message": (
                "I'm not sure what you meant 🤔\nTry:\n"
                "• 🏋️ 'Give me a 20 min workout'\n"
                "• 🍽️ 'I ate pasta and veggies'\n"
                "• 🧘 'I feel stressed'\n"
                "• 📊 'Show my progress summary'"
            )
        }

    # ----------------- UI Output Formatting ----------------- #
    def pretty_print(self, response: dict):
        agent = response.get("agent")

        print("\n" + "="*55)

        # SYSTEM / ONBOARDING
        if agent == "system":
            print(f"\n💬 {response['message']}")
            print("="*55 + "\n")
            return

        data = response.get("data", {})

        if agent == "nutrition":
            print("🥗 Nutrition Log Recorded")
            print(f"🍽 Meal: {data.get('meal_log_entry')}")
            print(f"💡 Suggestion: {data.get('suggested_improvement')}")

        elif agent == "fitness":
            print("🏋️ Workout Plan Ready")
            print(f"📌 {data.get('workout_name')} ({data.get('duration')})")
            for step in data.get("steps", []):
                print(f" • {step}")
            print(f"✨ Tip: {data.get('tips')}")

        elif agent == "mindfulness":
            print("🧘 Mindfulness Check-In")
            print(f"💬 {data.get('mood_acknowledgement')}")
            print(f"📓 Journal: {data.get('journal_prompt')}")
            print(f"🌿 Breathing: {data.get('optional_breathing_or_grounding')}")
            print(f"💛 {data.get('supportive_message')}")

        elif agent == "analytics":
            print("📊 Progress Overview")
            stats = data.get("stats", {})
            streaks = stats.get("streaks", {})
            print(f"🏋️ Workouts: {stats.get('total_workouts', 0)}")
            print(f"🥗 Meals: {stats.get('total_meals_logged', 0)}")
            print(f"🧠 Mood logs: {stats.get('total_mood_checkins', 0)}")
            print(f"🔥 Best Streak: {max(streaks.values())} days")
            print(f"🏅 Badge: {data.get('achievement_badge')}")
            print(f"💛 {data.get('encouragement')}")
            print(f"🎯 Next step: {data.get('next_micro_goal')}")

        print("="*55 + "\n")


# ----------------- Run App ----------------- #
def main():
    orch = Orchestrator()
    user_id = "local_user"

    print("\n✨ Welcome to Trackr AI — your wellbeing companion ✨\n")
    print("Whats your name buddy?")

    while True:
        msg = input("You: ")
        if msg.lower() in ("exit", "quit"):
            print("\n👋 Bye! Small steps build big change.\n")
            break

        response = orch.handle(user_id, msg)
        orch.pretty_print(response)


if __name__ == "__main__":
    main()
