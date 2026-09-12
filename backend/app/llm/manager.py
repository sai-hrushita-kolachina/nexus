import logging
import time

from app.config import get_settings
from app.llm.gemini import GeminiProvider
from app.llm.groq import GroqProvider

logger = logging.getLogger(__name__)


class LLMManager:

    def __init__(self):
        settings = get_settings()

        self.providers = []

        # Gemini
        if settings.gemini_api_key:
            self.providers.append(
                (
                    "gemini",
                    lambda: GeminiProvider(
                        settings.gemini_api_key
                    )
                )
            )

        # Groq
        if settings.groq_api_key:
            self.providers.append(
                (
                    "groq",
                    lambda: GroqProvider(
                        settings.groq_api_key
                    )
                )
            )

    def _is_quota_error(self, error: Exception) -> bool:
        message = str(error).lower()

        quota_indicators = [
            "429",
            "quota exceeded",
            "rate limit",
            "resource_exhausted",
            "too many requests",
            "limit: 0",
            "insufficient_quota",
            "credit_balance_exhausted",
        ]

        return any(
            indicator in message
            for indicator in quota_indicators
        )

    def _is_temporary_error(self, error: Exception) -> bool:
        message = str(error).lower()

        temporary_indicators = [
            "503",
            "service unavailable",
            "temporarily unavailable",
            "internal server error",
            "502",
            "504",
            "timeout",
            "timed out",
        ]

        return any(
            indicator in message
            for indicator in temporary_indicators
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> dict:

        if not self.providers:
            raise RuntimeError(
                "No LLM API keys configured."
            )

        errors = []

        for provider_name, provider_factory in self.providers:

            max_attempts = 3
            attempt = 1

            while attempt <= max_attempts:

                try:

                    logger.info(
                        "Trying LLM provider: %s "
                        "(attempt %d/%d)",
                        provider_name,
                        attempt,
                        max_attempts
                    )

                    provider = provider_factory()

                    answer = provider.generate(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt
                    )

                    logger.info(
                        "LLM provider succeeded: %s",
                        provider_name
                    )

                    return {
                        "answer": answer,
                        "provider": provider_name,
                        "success": True
                    }

                except Exception as exc:

                    logger.warning(
                        "Provider %s failed on attempt %d: %s",
                        provider_name,
                        attempt,
                        str(exc)
                    )

                    # Quota/rate-limit errors:
                    # don't waste time retrying.
                    if self._is_quota_error(exc):

                        logger.warning(
                            "Quota/rate limit detected for %s. "
                            "Skipping remaining retries.",
                            provider_name
                        )

                        errors.append({
                            "provider": provider_name,
                            "error": str(exc),
                            "type": "quota"
                        })

                        break

                    # Temporary server/network errors:
                    # retry up to 3 times.
                    if self._is_temporary_error(exc):

                        if attempt < max_attempts:

                            wait_time = 2 ** (attempt - 1)

                            logger.info(
                                "Temporary error detected. "
                                "Retrying %s in %d seconds...",
                                provider_name,
                                wait_time
                            )

                            time.sleep(wait_time)

                            attempt += 1
                            continue

                    errors.append({
                        "provider": provider_name,
                        "error": str(exc),
                        "type": "error"
                    })

                    break

        logger.error(
            "All configured LLM providers failed."
        )

        return {
            "answer": (
                "I'm sorry, but the configured AI service "
                "is currently unavailable. Please try again later."
            ),
            "provider": None,
            "success": False,
            "errors": errors
        }