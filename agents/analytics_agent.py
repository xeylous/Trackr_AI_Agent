# agents/analytics_agent.py

from agents.base_agent import BaseAgent
from datetime import datetime, timedelta

class AnalyticsAgent(BaseAgent):
    """
    Analytics Agent:
    - Summarizes history, habits, streaks, and overall engagement.
    - Creates positive motivation using badge system.
    - Uses profile data to tailor tone (never gives clinical/medical advice).
    """

    def __init__(self, memory, llm=None):
        super().__init__(memory, llm, "analytics_agent")

    # ---------- Internal Streak Logic ---------- #

    def calculate_streak(self, logs: list) -> int:
        """Return consecutive daily streak length."""
        if not logs:
            return 0

        sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
        streak = 1
        previous_date = datetime.fromisoformat(sorted_logs[0]["timestamp"]).date()

        for entry in sorted_logs[1:]:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date == previous_date - timedelta(days=1):
                streak += 1
                previous_date = entry_date
            else:
                break

        return streak

    def reward_badge(self, best_streak: int) -> str:
        """Return achievement badge based on consistency level."""
        if best_streak >= 30:
            return "🏆 Iron Discipline (30+ days streak!)"
        if best_streak >= 14:
            return "🔥 Momentum Builder (2 weeks!)"
        if best_streak >= 7:
            return "💪 Consistency Achiever (1 week!)"
        if best_streak >= 3:
            return "✨ Healthy Habit Starter (3+ days streak)"
        return "🌱 Getting Started — proud of your first steps!"

    # ---------- Main Execute Method ---------- #

    def handle(self, user_id: str, message: str, context: dict) -> dict:
        user = self.memory.get_user(user_id)
        profile = user["profile"]
        logs = user["logs"]

        workouts = logs.get("workouts", [])
        meals = logs.get("meals", [])
        moods = logs.get("mood", [])

        # Streak calculations
        workout_streak = self.calculate_streak(workouts)
        meal_streak = self.calculate_streak(meals)
        mood_streak = self.calculate_streak(moods)

        best_streak = max(workout_streak, meal_streak, mood_streak)
        badge = self.reward_badge(best_streak)

        # Tone personalization
        name = profile.get("name") or "friend"
        age = profile.get("age")
        gender = profile.get("gender")
        goal = profile.get("goals")

        personal_note = f"You're making steady progress, {name}."
        if age and age > 45:
            personal_note += " Your consistency at this stage of life is especially inspiring."
        elif age and age < 18:
            personal_note += " You're building strong habits early — amazing foundation!"

        if goal:
            personal_note += f" Every step moves you closer to your goal: **{goal}**."

        summary = {
            "summary_range": "entire logged history",
            "profile": {
                "name": name,
                "age": age,
                "gender": gender,
                "goal": goal
            },
            "stats": {
                "total_workouts": len(workouts),
                "total_meals_logged": len(meals),
                "total_mood_checkins": len(moods),
                "streaks": {
                    "workout_streak_days": workout_streak,
                    "meal_streak_days": meal_streak,
                    "mood_streak_days": mood_streak
                }
            },
            "achievement_badge": badge,
            "encouragement": personal_note,
            "next_micro_goal": (
                "Tomorrow, repeat ANY habit you've logged and add one tiny improvement "
                "— even 3 minutes counts."
            )
        }

        return summary
