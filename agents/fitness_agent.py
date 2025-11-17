# agents/fitness_agent.py

from datetime import datetime
import json
from agents.base_agent import BaseAgent
from utils.personality import add_warmth


class FitnessAgent(BaseAgent):
    """
    Fitness Coach Agent:
    - Generates safe, beginner-friendly workouts using Gemini.
    - Adapts tone based on profile (age, gender, fitness level).
    - Includes fallback plan if LLM doesn't return valid JSON.
    """

    def __init__(self, memory, llm):
        super().__init__(memory, llm, "fitness_agent")

    def handle(self, user_id: str, message: str, context: dict) -> dict:

        user = self.memory.get_user(user_id)
        profile = user["profile"]

        name = profile.get("name") or "friend"
        age = profile.get("age")
        fitness_level = profile.get("fitness_level") or "beginner"
        equipment = profile.get("equipment", [])
        minutes = context.get("minutes", 20)

        # --------- Personalized Tone Context --------- #

        if age and age < 18:
            tone = "Make the tone positive and beginner-friendly, like an encouraging coach."
        elif age and age > 50:
            tone = "Tone should be respectful, calm, and gently motivating."
        else:
            tone = "Tone should be concise, encouraging, and supportive."

        equipment_note = (
            f"The user has equipment available: {', '.join(equipment)}. You may optionally incorporate it."
            if equipment else "Use only bodyweight unless needed."
        )

        # --------- System Prompt for Gemini --------- #

        system_prompt = f"""
        You are the Fitness Coach Agent for LifeBalance AI.

        Personalization:
        - User: {name}
        - Age: {age}
        - Fitness Level: {fitness_level}
        
        {tone}
        {equipment_note}

        Safety Rules:
        - Avoid medical instructions or injury guidance.
        - Keep workouts beginner-safe and time-friendly.

        Format the response ONLY as valid JSON:
        {{
            "workout_name": "",
            "duration": "",
            "intensity": "",
            "steps": [],
            "tips": ""
        }}
        """

        user_prompt = f'The user said: "{message}". They have {minutes} minutes available.'

        # --------- Attempt LLM --------- #

        try:
            generated = self.llm.generate(system_prompt, user_prompt) if self.llm else ""
        except:
            generated = ""

        try:
            workout = json.loads(generated)
        except:
            workout = {
                "workout_name": "Quick Full-Body Routine",
                "duration": f"{minutes} minutes",
                "intensity": fitness_level,
                "steps": [
                    "Warm-up: march in place — 2 minutes",
                    "10 bodyweight squats",
                    "10 push-ups (knees ok)",
                    "20 jumping jacks",
                    "Rest 1 minute, repeat sequence twice",
                    "Finish: light stretching — 5 minutes"
                ],
                "tips": "Move at a comfortable pace. Hydrate and take pauses if needed."
            }

        # --------- Save workout log --------- #
        self.memory.append_log(user_id, "workouts", {
            "timestamp": datetime.utcnow().isoformat(),
            "plan": workout
        })

        # --------- Prepare Friendly UI Output --------- #

        display_text = (
            f"🏋️ Workout Ready for **{name}!**\n\n"
            f"⏱ Duration: **{workout['duration']}**\n"
            f"🔥 Intensity: **{workout['intensity']}**\n\n"
            f"📋 Steps:\n" + "\n".join([f"• {step}" for step in workout["steps"]]) +
            f"\n\n✨ Tip:\n➡ {workout['tips']}"
        )

        workout["display"] = add_warmth(display_text)

        return workout
