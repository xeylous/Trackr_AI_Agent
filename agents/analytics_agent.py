# agents/analytics_agent.py

from agents.base_agent import BaseAgent
from datetime import datetime, timedelta
from utils.personality import add_warmth


class AnalyticsAgent(BaseAgent):
    """
    Analytics Agent:
    - Reviews logged history and summarizes engagement.
    - Tracks streaks and assigns achievement badges.
    - Adapts encouragement to user profile traits.
    """

    def __init__(self, memory, llm=None):
        super().__init__(memory, llm, "analytics_agent")

    # ---------- Streak Calculation ---------- #

    def calculate_streak(self, logs: list) -> int:
        """Return number of consecutive days with logging activity."""
        if not logs:
            return 0

        sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
        streak = 1
        last_date = datetime.fromisoformat(sorted_logs[0]["timestamp"]).date()

        for entry in sorted_logs[1:]:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date == last_date - timedelta(days=1):
                streak += 1
                last_date = entry_date
            else:
                break

        return streak

    def reward_badge(self, best_streak: int) -> str:
        """Generate badge label matching streak difficulty."""
        if best_streak >= 30:
            return "🏆 Iron Discipline (30+ day streak)"
        if best_streak >= 14:
            return "🔥 Momentum Builder (2 weeks streak)"
        if best_streak >= 7:
            return "💪 Health Consistency Award (7 day streak)"
        if best_streak >= 3:
            return "✨ Habit Starter Badge (3+ days)"
        return "🌱 First Steps — proud of your progress!"

    # ---------- Main Execution ---------- #

    def handle(self, user_id: str, message: str, context: dict = None) -> dict:
        user = self.memory.get_user(user_id)
        profile = user["profile"]
        logs = user["logs"]

        workouts = logs.get("workouts", [])
        meals = logs.get("meals", [])
        moods = logs.get("mood", [])

        # Compute streaks
        workout_streak = self.calculate_streak(workouts)
        meal_streak = self.calculate_streak(meals)
        mood_streak = self.calculate_streak(moods)

        best_streak = max(workout_streak, meal_streak, mood_streak)
        badge = self.reward_badge(best_streak)

        # Personal tone
        name = profile.get("name") or "friend"
        age = profile.get("age")
        goal = profile.get("goals")

        encouragement = f"You're showing meaningful consistency, {name}."

        if age:
            if age > 45:
                encouragement += " Your dedication at this stage of life really stands out."
            elif age < 18:
                encouragement += " Building healthy habits this early is amazing!"

        if goal:
            encouragement += f" You're progressing toward your goal: **{goal}**."

        # Build structured summary
        summary = {
            "summary_range": "full history",
            "profile": {
                "name": name,
                "age": age,
                "gender": profile.get("gender"),
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
            "badge": badge,
            "encouragement": encouragement,
            "next_micro_goal": (
                "Repeat any logged habit tomorrow and add one tiny improvement — "
                "even 3 minutes or one mindful moment counts."
            )
        }

        # Create friendly user-facing message
        display_text = (
            f"📊 **Progress Summary for {name}**\n\n"
            f"🏋️ Workouts logged: **{len(workouts)}**\n"
            f"🥗 Meals logged: **{len(meals)}**\n"
            f"🧠 Mood check-ins: **{len(moods)}**\n\n"
            f"🔥 Best streak: **{best_streak} days**\n"
            f"🏅 Badge earned: **{badge}**\n\n"
            f"{encouragement}\n\n"
            f"🎯 Next micro-goal:\n➡ {summary['next_micro_goal']}"
        )

        summary["display"] = add_warmth(display_text)

        return summary
