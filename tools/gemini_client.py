import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY in .env file")

        self.model = model_name
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, system_prompt: str, user_prompt: str, max_output_tokens=512):
        """Combines system and user prompt, calls Gemini, and returns text."""
        full_prompt = system_prompt + "\n\nUser:\n" + user_prompt
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config={"max_output_tokens": max_output_tokens}
        )

        # Extract text cleanly
        texts = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text"):
                    texts.append(part.text)

        return "\n".join(texts).strip()
