from groq import Groq
from app.config import get_settings

class GroqProvider:
    name = "groq"

    def __init__(self, api_key: str):

        settings = get_settings()
        self.client = Groq(
            api_key=api_key
        )

        self.model = settings.groq_model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Groq returned an empty response."
            )
        return content