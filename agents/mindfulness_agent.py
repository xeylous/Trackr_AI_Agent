# agents/mindfulness_agent.py

from datetime import datetime
import json
from agents.base_agent import BaseAgent

class MindfulnessAgent(BaseAgent):
    """
    Mindfulness Agent:
    - Provides emotionally safe support and reflection.
    - Uses user's profile to personalize tone (age, name, goals).
    - Logs mood, then generates a gentle, non-clinical response.
    """

    def __init__(self, memory, llm):
        super().__init__(memory, llm, "mindfulness_agent")

    def handle(self, user_id: str, message: str, context: dict) -> dict:
        user = self.memory.get_user(user_id)
        profile = user["profile"]

        mood = context.get("mood", "unknown")
        note = context.get("note", message)

        # Store entry in memory
        self.memory.append_log(user_id, "mood", {
            "timestamp": datetime.utcnow().isoformat(),
            "mood": mood,
            "note": note
        })

        # Personalization data
        name = profile.get("name") or "friend"
        age = profile.get("age")
        goal = profile.get("goals")

        # Age-based tone adaptation (non-clinical)
        if age and age < 20:
            tone_instruction = "Use a relatable, encouraging tone like a supportive older sibling."
        elif age and age > 45:
            tone_instruction = "Use a grounded, gentle tone with respect and reassurance."
        else:
            tone_instruction = "Use a balanced, calm, supportive tone."

        # Goal-based contextual encouragement
        goal_context = ""
        if goal:
            goal_context = f"Their personal goal is: '{goal}'. Offer subtle encouragement connected to this goal without pressure."

        # ---------- SYSTEM PROMPT WITH PERSONALIZATION ---------- #
        system_prompt = f"""
        You are the Mindfulness & Emotional Support Agent for LifeBalance AI.

        {tone_instruction}
        {goal_context}

        Rules:
        - Respond with empathy, validation, and warmth.
        - DO NOT mention therapy, diagnosis, trauma, disorders, or crisis language.
        - DO NOT provide medical advice or imply treatment.
        - Keep suggestions small, actionable (breathing, awareness, journaling).
        - Be supportive without judgment.

        Respond ONLY as valid JSON with keys:
        {{
            "mood_acknowledgement": "",
            "journal_prompt": "",
            "optional_breathing_or_grounding": "",
            "supportive_message": ""
        }}
        """

        # ---------- USER INPUT CONTEXT ---------- #
        user_prompt = f"""
        User name: {name}
        Mood label: {mood}
        User message: "{note}"
        """

        # Try Gemini response
        try:
            generated = self.llm.generate(system_prompt, user_prompt) if self.llm else ""
        except Exception:
            generated = ""

        # Try parse JSON response
        try:
            parsed = json.loads(generated)
        except Exception:
            parsed = {
                "mood_acknowledgement": f"Thank you for sharing how you're feeling, {name}. Feeling {mood} is completely valid.",
                "journal_prompt": "If you feel okay, write one sentence about what's weighing on your mind or what brought you peace today.",
                "optional_breathing_or_grounding": (
                    "Try a gentle grounding pause: inhale slowly for 4 seconds, "
                    "hold for 2, then exhale for 6."
                ),
                "supportive_message": (
                    "You're doing something meaningful: you're acknowledging your emotions instead of bottling them. "
                    "Healing and growth often begin with awareness — and you're already there."
                )
            }

        return parsed
