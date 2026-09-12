import logging
from app.llm.manager import LLMManager
logger = logging.getLogger(__name__)


class ConversationRewriter:

    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def rewrite_for_retrieval(self, question: str, history: list[dict]) -> str:

        # NO HISTORY

        if not history:
            return question

        # BUILD HISTORY

        history_text = ""

        for message in history:

            role = message.get("role", "unknown")
            content = message.get("content", "")

            history_text += f"{role.upper()}: {content}\n"

        # REWRITE PROMPT

        system_prompt = """
You are a query contextualization assistant.

Your job is to rewrite the user's latest question
into a standalone question that can be understood
without seeing the previous conversation.

Rules:

- Resolve pronouns such as:
  it, this, that, they, them, those, he, she
  using the conversation history.
- Resolve references such as:
  "the policy", "that process", "the document",
  "the above", etc.
- Preserve the user's original meaning.
- Do not answer the question.
- Do not add information that is not supported
  by the conversation.
- If the question is already standalone, return it
  essentially unchanged.
- Return ONLY the rewritten question.
"""

        user_prompt = f"""
CONVERSATION HISTORY:

{history_text}

LATEST USER QUESTION:

{question}

Rewrite the latest question as a standalone question.
"""

        # CALL LLM

        try:

            result = self.llm_manager.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

            if not result.get("success"):
                logger.warning(
                    "Question rewriting failed. Using original question."
                )
                return question

            rewritten = result.get("answer", "").strip()

            if not rewritten:
                return question

            logger.info(
                "Retrieval query rewritten: '%s' -> '%s'",
                question,
                rewritten
            )

            return rewritten

        except Exception as exc:

            logger.warning("Question rewriting error: %s", exc)

            return question