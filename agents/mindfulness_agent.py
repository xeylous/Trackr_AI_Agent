# agents/mindfulness_agent.py

from datetime import datetime
import json
from agents.base_agent import BaseAgent
from utils.personality import add_warmth


class MindfulnessAgent(BaseAgent):
    """
    Mindfulness Agent:
    - Responds with supportive emotional reflection.
    - Avoids clinical language, advice, or diagnosis.
    - Logs user's emotional state and provides gentle guidance.
    """

    def __init__(self, memory, llm):
        super().__init__(memory, llm, "mindfulness_agent")

    def handle(self, user_id: str, message: str, context: dict) -> dict:

        user = self.memory.get_user(user_id)
        profile = user["profile"]

        mood = context.get("mood", "unknown")
        note = context.get("note", message)

        # Log entry
        self.memory.append_log(user_id, "mood", {
            "timestamp": datetime.utcnow().isoformat(),
            "mood": mood,
            "note": note
        })

        # Personal details
        name = profile.get("name") or "friend"
        age = profile.get("age")
        goal = profile.get("goals")

        # ----- Personal Tone Rules -----
        if age and age < 20:
            tone_instruction = "Use a relatable, hopeful, friendly tone as if talking to a young adult."
        elif age and age > 45:
            tone_instruction = "Use a slow, gentle, reassuring tone that feels grounding."
        else:
            tone_instruction = "Tone should be warm, validating, and balanced."

        goal_context = ""
        if goal:
            goal_context = f"The user cares about: '{goal}'. If natural, connect the support to this intention — but avoid pressure."

        # ----- System Prompt -----
        system_prompt = f"""
        You are the Mindfulness & Emotional Support Agent for LifeBalance AI.

        {tone_instruction}
        {goal_context}

        Boundaries:
        - No therapy terms, diagnosis, or labels.
        - No crisis language (examples: "help", "urgent", "emergency", "treatment").
        - No medical instructions.
        - Keep messages simple and emotionally safe.

        Response format ONLY as JSON:
        {{
            "mood_acknowledgement": "",
            "journal_prompt": "",
            "optional_breathing_or_grounding": "",
            "supportive_message": ""
        }}
        """

        user_prompt = f"""
        User: {name}
        Mood: {mood}
        Message: "{note}"
        """

        # ----- LLM Execution -----
        try:
            generated = self.llm.generate(system_prompt, user_prompt) if self.llm else ""
        except:
            generated = ""

        # ----- Parse Output -----
        try:
            parsed = json.loads(generated)
        except:
            parsed = {
                "mood_acknowledgement": f"I hear you, {name}. Feeling {mood} is completely valid.",
                "journal_prompt": "If it feels okay, write one short sentence describing what you need right now.",
                "optional_breathing_or_grounding": (
                    "You can pause for a single slow breath: inhale 4 seconds, exhale longer than the inhale."
                ),
                "supportive_message": (
                    "Checking in with how you feel is already a meaningful step. "
                    "You're doing your best — and that is enough for now."
                )
            }

        # ----- Create UI-Friendly Output -----
        display_text = (
            f"🧘 **Mindfulness Check-In**\n\n"
            f"💬 {parsed['mood_acknowledgement']}\n\n"
            f"🪷 Quick grounding suggestion:\n➡ {parsed['optional_breathing_or_grounding']}\n\n"
            f"📓 Journal prompt:\n➡ *{parsed['journal_prompt']}*\n\n"
            f"💛 {parsed['supportive_message']}"
        )

        parsed["display"] = add_warmth(display_text)

        return parsed
