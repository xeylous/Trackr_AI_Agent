# agents/nutrition_agent.py

from datetime import datetime
import json
from agents.base_agent import BaseAgent

class NutritionAgent(BaseAgent):
    """
    Nutrition Agent:
    - Logs meals and encourages gentle habit improvements.
    - Uses profile context (age, preferences, and goals) for tone personalization.
    - Avoids strict dietary advice, diagnoses, or calorie estimation.
    """

    def __init__(self, memory, llm):
        super().__init__(memory, llm, "nutrition_agent")

    def handle(self, user_id: str, message: str, context: dict) -> dict:
        user = self.memory.get_user(user_id)
        profile = user["profile"]

        meal_desc = context.get("meal_description", message)

        # Log the meal
        self.memory.append_log(user_id, "meals", {
            "timestamp": datetime.utcnow().isoformat(),
            "meal": meal_desc,
            "estimated_calories": None  # safely stored for future enhancements
        })

        # ---------- Personalization Context ---------- #
        name = profile.get("name") or "friend"
        age = profile.get("age")
        diet = profile.get("diet_type")
        goal = profile.get("goals")

        # Tone adjustments based on age (safe, non-medical)
        if age and age < 18:
            tone_instruction = "Use a warm supportive tone like a friendly mentor."
        elif age and age > 50:
            tone_instruction = "Use a respectful, encouraging tone."
        else:
            tone_instruction = "Use a balanced, encouraging tone."

        # Diet-specific encouragement (not restrictions)
        diet_context = ""
        if diet and diet != "general":
            diet_context = f"The user prefers a **{diet}** style of eating. Keep suggestions aligned with this preference without enforcing rules."

        # Health or lifestyle goals
        if goal:
            diet_context += f" Their personal goal is: **{goal}**. Offer small improvements aligned with this goal."

        # ---------- SYSTEM INSTRUCTION ---------- #
        system_prompt = f"""
        You are the Nutrition Coach Agent for LifeBalance AI.

        Personalization guidelines:
        - User name: {name}
        - Age: {age}
        - Gender: {profile.get("gender")}
        - Diet preference: {diet}
        - Goal: {goal}

        {tone_instruction}
        {diet_context}

        Strict boundaries:
        - NO calorie estimates.
        - NO medical, clinical, or diagnostic guidance.
        - NO strict diet rules ("you must", "avoid", "never").
        - Encourage balanced choices: hydration, fruits/vegetables, fiber.

        Respond ONLY in valid JSON format:
        {{
            "meal_log_entry": "",
            "estimated_calories": null,
            "nutrition_type": "",
            "suggested_improvement": ""
        }}
        """

        # ---------- USER PROMPT ---------- #
        user_prompt = f"""
        The user logged this meal: "{meal_desc}"
        Provide a supportive improvement idea.
        """

        # Try LLM generation
        try:
            generated = self.llm.generate(system_prompt, user_prompt) if self.llm else ""
        except Exception:
            generated = ""

        # Try parse response; fallback to safe template
        try:
            response = json.loads(generated)
        except Exception:
            response = {
                "meal_log_entry": meal_desc,
                "estimated_calories": None,
                "nutrition_type": diet or "general",
                "suggested_improvement": (
                    f"Thanks for logging that, {name}. If you'd like an optional improvement, "
                    f"you could add a fruit, vegetable, or glass of water to balance the meal."
                )
            }

        return response
