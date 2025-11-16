# agents/fitness_agent.py

from datetime import datetime
import json
from agents.base_agent import BaseAgent

class FitnessAgent(BaseAgent):
    """
    Fitness Coach Agent:
    - Uses Gemini to generate safe beginner-friendly workouts.
    - Falls back to a default plan if Gemini output isn't valid JSON.
    """

    def __init__(self, memory, llm):
        super().__init__(memory, llm, "fitness_agent")

    def handle(self, user_id: str, message: str, context: dict) -> dict:
        user = self.memory.get_user(user_id)
        profile = user["profile"]
        minutes = context.get("minutes", 20)

        system_prompt = """
        You are the Fitness Coach Agent for LifeBalance AI.

        Rules:
        - Create a beginner-friendly workout.
        - Use only bodyweight unless user mentions equipment.
        - Stay within requested time.
        - Keep responses safe and non-medical.
        - Tone: short, positive, and encouraging.

        Respond ONLY as JSON:

        {
          "workout_name": "",
          "duration": "",
          "intensity": "",
          "steps": [],
          "tips": ""
        }
        """

        user_prompt = f"""
        User Profile:
        - Name: {profile['name']}
        - Age: {profile['age']}
        - Gender: {profile['gender']}
        - Fitness level: {profile.get('fitness_level', 'beginner')}
        Available time: {minutes} minutes
        User request: "{message}"
        """


        # Call Gemini if available, otherwise fallback
        try:
            result = self.llm.generate(system_prompt, user_prompt) if self.llm else ""
        except Exception:
            result = ""

        # Attempt to parse JSON; fallback if invalid
        try:
            workout = json.loads(result)
        except Exception:
            workout = {
                "workout_name": "Quick full-body routine",
                "duration": f"{minutes} minutes",
                "intensity": profile.get("fitness_level", "beginner"),
                "steps": [
                    "5 min warm-up: walk in place",
                    "3 x 10 bodyweight squats",
                    "3 x 10 push-ups (knees if needed)",
                    "3 x 20 jumping jacks",
                    "5 min stretching: legs, arms, back"
                ],
                "tips": "Move at a comfortable pace and stop if you feel discomfort."
            }

        # Save workout log
        self.memory.append_log(user_id, "workouts", {
            "timestamp": datetime.utcnow().isoformat(),
            "plan": workout
        })

        return workout
