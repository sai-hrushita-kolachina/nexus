from fastapi import APIRouter, HTTPException

from app.database.sqlite import (
    get_conversations,
    get_messages,
    delete_conversation
)

router = APIRouter(
    prefix="/api/history",
    tags=["History"]
)

# LIST CONVERSATIONS

@router.get("")
def list_conversations():

    conversations = get_conversations()

    return {
        "conversations": conversations
    }

# GET ONE CONVERSATION

@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str
):

    messages = get_messages(
        conversation_id
    )

    if not messages:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "conversation_id": conversation_id,
        "messages": messages
    }

# DELETE CONVERSATION

@router.delete("/{conversation_id}")
def remove_conversation(
    conversation_id: str
):

    delete_conversation(
        conversation_id
    )

    return {
        "success": True,
        "conversation_id": conversation_id,
        "message": "Conversation deleted."
    }