from google import genai
from app.config import get_settings

class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str):

        settings = get_settings()

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = settings.gemini_model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:

        prompt = f"""
SYSTEM INSTRUCTIONS:

{system_prompt}


USER:

{user_prompt}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text