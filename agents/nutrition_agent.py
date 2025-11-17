# agents/nutrition_agent.py

from datetime import datetime
import json
from agents.base_agent import BaseAgent
from utils.personality import add_warmth


class NutritionAgent(BaseAgent):
    """
    Nutrition Agent:
    - Logs meals and encourages gentle improvements.
    - Uses profile data to tailor tone and suggestions.
    - Avoids calorie estimates, rules, or medical advice.
    """

    def __init__(self, memory, llm):
        super().__init__(memory, llm, "nutrition_agent")

    def handle(self, user_id: str, message: str, context: dict) -> dict:

        # Retrieve user info
        user = self.memory.get_user(user_id)
        profile = user["profile"]

        meal_desc = context.get("meal_description", message)

        # Store meal entry
        self.memory.append_log(user_id, "meals", {
            "timestamp": datetime.utcnow().isoformat(),
            "meal": meal_desc,
            "estimated_calories": None
        })

        # ---------------------- Personalization ---------------------- #
        name = profile.get("name") or "friend"
        age = profile.get("age")
        diet = profile.get("diet_type")
        goal = profile.get("goals")

        # Tone adjustments
        if age and age < 18:
            tone_instruction = "Tone should feel friendly and mentor-like."
        elif age and age > 50:
            tone_instruction = "Tone should be respectful, encouraging, and warm."
        else:
            tone_instruction = "Use a balanced, supportive tone."

        diet_context = ""
        if diet and diet != "general":
            diet_context = f"User prefers a **{diet}** style of eating — keep suggestions aligned without imposing rules."

        if goal:
            diet_context += f" Their personal goal is: **{goal}**."

        # ---------------------- System Prompt ---------------------- #
        system_prompt = f"""
        You are a supportive Nutrition Coach Agent for LifeBalance AI.

        Personalization:
        - Name: {name}
        - Age: {age}
        - Gender: {profile.get("gender")}
        - Diet preference: {diet}
        - Goal: {goal}

        {tone_instruction}
        {diet_context}

        Boundaries:
        - NO calorie guessing.
        - NO diet restrictions or rule-based language.
        - NO medical or diagnostic advice.
        - Encourage balance: water, vegetables, variety, fiber.

        Respond ONLY as valid JSON:
        {{
            "meal_log_entry": "",
            "estimated_calories": null,
            "nutrition_type": "",
            "suggested_improvement": ""
        }}
        """

        user_prompt = f'The user logged this meal: "{meal_desc}". Offer a gentle improvement idea.'

        # Attempt LLM response
        try:
            generated = self.llm.generate(system_prompt, user_prompt) if self.llm else ""
        except:
            generated = ""

        # Parse → or fallback
        try:
            structured = json.loads(generated)
        except:
            structured = {
                "meal_log_entry": meal_desc,
                "estimated_calories": None,
                "nutrition_type": diet or "general",
                "suggested_improvement": (
                    f"Nice job logging your meal, {name} 🌿. "
                    f"If you want a tiny improvement, consider adding a vegetable, fruit, "
                    f"or a glass of water to balance it."
                )
            }

        # ------- Create Friendly Display Text ------- #
        display_text = (
            f"🥗 Meal logged: **{structured['meal_log_entry']}**\n\n"
            f"💡 Suggested improvement:\n➡ {structured['suggested_improvement']}"
        )

        structured["display"] = add_warmth(display_text)

        return structured
