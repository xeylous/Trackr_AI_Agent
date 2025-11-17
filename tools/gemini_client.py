# tools/gemini_client.py

import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiClient:
    """
    Wrapper for Gemini text generation.
    Adds:
    - Structured prompt formatting
    - Retry on failure
    - Optional JSON enforcement
    """

    def __init__(self, model_name="gemini-2.0-flash", max_retries=2):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Missing GOOGLE_API_KEY in .env file")

        self.model = model_name
        self.max_retries = max_retries

        self.client = genai.Client(api_key=self.api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int = 512,
        require_json: bool = False
    ) -> str:
        """
        Fetches Gemini output with retries.
        If require_json=True, model is instructed to respond with valid JSON format only.
        """

        # Append JSON instructions if needed
        if require_json:
            system_prompt += (
                "\n\n⚠️ IMPORTANT: Your final response must be ONLY valid JSON. "
                "No explanations, no formatting, no markdown."
            )

        full_prompt = f"{system_prompt.strip()}\n\nUser:\n{user_prompt.strip()}"

        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config={"max_output_tokens": max_output_tokens}
                )

                # Extract output text safely
                result = self._extract_text(response)
                if result:
                    return result.strip()

            except Exception as e:
                print(f"⚠️ Gemini request failed (attempt {attempt+1}): {e}")
                time.sleep(1.2)  # minor cooldown

        return ""  # fallback if all attempts fail

    @staticmethod
    def _extract_text(response) -> str:
        """Extracts text output from Gemini result safely."""
        if not hasattr(response, "candidates") or not response.candidates:
            return ""

        parts = response.candidates[0].content.parts
        return " ".join(getattr(p, "text", "") for p in parts if hasattr(p, "text"))
