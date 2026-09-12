import logging
import uuid

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest
from app.models.response import ChatResponse
from app.database.sqlite import create_conversation, save_message, get_recent_messages
from app.llm.manager import LLMManager
from app.rag.conversation import ConversationRewriter
from app.rag.hybrid_search import HybridSearch
from app.rag.reranker import Reranker
from app.rag.context_builder import ContextBuilder
from app.rag.prompts import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT,
    GENERAL_SYSTEM_PROMPT,
    GENERAL_USER_PROMPT,
)
from app.utils.citations import build_citations
from app.config import get_settings


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


# INITIALIZE SERVICES

llm_manager = LLMManager()
conversation_rewriter = ConversationRewriter(llm_manager)
reranker = Reranker()
context_builder = ContextBuilder()
settings = get_settings()

# Lazy-load HybridSearch.
# This prevents Hugging Face embeddings + Chroma
# from loading during FastAPI startup.
_hybrid_search = None


def get_hybrid_search():
    global _hybrid_search

    if _hybrid_search is None:
        logger.info("Initializing HybridSearch...")
        _hybrid_search = HybridSearch()
        logger.info("HybridSearch initialized successfully.")

    return _hybrid_search


# CHAT ENDPOINT

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        # Conversation ID

        conversation_id = request.conversation_id or str(uuid.uuid4())
        question = request.message.strip()

        if not question:
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        logger.info("==============================================")
        logger.info("New chat request: conversation=%s", conversation_id)
        logger.info("User question: %s", question)

        # Create conversation if necessary

        create_conversation(conversation_id=conversation_id)

        # Load conversation history

        history = get_recent_messages(
            conversation_id=conversation_id,
            limit=20
        )

        logger.info("Loaded %d previous messages.", len(history))

        # STEP 1
        # CONTEXTUALIZE FOLLOW-UP QUESTION

        retrieval_question = conversation_rewriter.rewrite_for_retrieval(
            question=question,
            history=history
        )

        logger.info("Retrieval question: %s", retrieval_question)

        # STEP 2
        # SEARCH COMPANY KNOWLEDGE BASE

        hybrid_search = get_hybrid_search()

        search_results = hybrid_search.search(
            query=retrieval_question,
            k=settings.top_k
        )

        logger.info("Hybrid search returned %d results.", len(search_results))

        # STEP 3
        # RERANK RESULTS

        final_results = reranker.rerank(
            query=retrieval_question,
            results=search_results,
            final_k=settings.final_k
        )

        logger.info("Reranking produced %d final results.", len(final_results))

        # STEP 4
        # DETERMINE BEST RELEVANCE
        #
        # THIS IS NOW OUR ROUTER.
        #
        # No LLM classifier.
        # No keyword classifier.
        # No greeting detector.

        best_score = 0.0

        if final_results:
            best_score = max(
                float(
                    result.get(
                        "rerank_score",
                        result.get("hybrid_score", 0.0)
                    )
                )
                for result in final_results
            )

        logger.info("Best company knowledge relevance: %.3f", best_score)

        # STEP 5
        # ROUTE BASED ON RETRIEVAL RELEVANCE

        is_company_question = best_score >= settings.min_relevance_score

        if is_company_question:

            query_type = "COMPANY"

            logger.info("ROUTE: COMPANY RAG")

        else:

            query_type = "GENERAL"

            logger.info("ROUTE: GENERAL LLM")

        # Save user message after determining route

        save_message(
            conversation_id=conversation_id,
            role="user",
            content=question,
            query_type=query_type
        )

        # GENERAL LLM

        if query_type == "GENERAL":

            history_text = _format_history(history)

            user_prompt = GENERAL_USER_PROMPT.format(
                history=history_text,
                question=question,
                contextualized_question=retrieval_question
            )

            result = llm_manager.generate(
                system_prompt=GENERAL_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )

            if not result.get("success"):
                raise HTTPException(
                    status_code=503,
                    detail="AI service is currently unavailable."
                )

            answer = result.get("answer", "")
            provider = result.get("provider")

            save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
                query_type=query_type,
                provider=provider
            )

            return ChatResponse(
                conversation_id=conversation_id,
                answer=answer,
                query_type=query_type,
                provider=provider,
                sources=[],
                retrieval_relevance=best_score
            )

        # COMPANY RAG

        context = context_builder.build(final_results)
        history_text = _format_history(history)

        user_prompt = RAG_USER_PROMPT.format(
            context=context,
            history=history_text,
            question=question,
            contextualized_question=retrieval_question
        )

        result = llm_manager.generate(
            system_prompt=RAG_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503,
                detail="AI service is currently unavailable."
            )

        answer = result.get("answer", "")
        provider = result.get("provider")

        # Build citations

        sources = build_citations(final_results)

        # Save assistant response

        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            query_type=query_type,
            provider=provider
        )

        # Return response

        return ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            query_type=query_type,
            provider=provider,
            sources=sources,
            retrieval_relevance=best_score
        )

    # HTTP ERRORS

    except HTTPException:
        raise

    # UNEXPECTED ERRORS

    except Exception as exc:

        logger.exception("Chat request failed: %s", exc)

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the request."
        )


# FORMAT CONVERSATION HISTORY

def _format_history(history: list[dict]) -> str:

    if not history:
        return "No previous conversation."

    lines = []

    for message in history:

        role = message.get("role", "unknown").upper()
        content = message.get("content", "")

        lines.append(f"{role}: {content}")

    return "\n".join(lines)