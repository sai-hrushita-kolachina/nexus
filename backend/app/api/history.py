from fastapi import APIRouter,Depends,HTTPException
from app.database.sqlite import get_conversations,get_messages,delete_conversation
from app.utils.auth import get_current_user

router=APIRouter(prefix="/api/history",tags=["History"])

@router.get("")

def list_conversations(current_user: dict=Depends(get_current_user)):
    conversations=get_conversations(current_user["id"])
    return {"conversations":conversations}

@router.get("/{conversation_id}")
def get_conversation(conversation_id: str,current_user: dict=Depends(get_current_user)):
    messages=get_messages(conversation_id,current_user["id"])
    
    if not messages:
        raise HTTPException(status_code=404,detail="Conversation not found.")
    return {"conversation_id":conversation_id,"messages":messages}

@router.delete("/{conversation_id}")

def remove_conversation(conversation_id: str,current_user: dict=Depends(get_current_user)):
    deleted=delete_conversation(conversation_id,current_user["id"])
    
    if not deleted:
        raise HTTPException(status_code=404,detail="Conversation not found.")
    
    return {
        "success":True,
        "conversation_id":conversation_id,
        "message":"Conversation deleted."
    }