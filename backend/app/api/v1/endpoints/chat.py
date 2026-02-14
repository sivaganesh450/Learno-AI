from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserInDB
from app.models.conversation import (
    ChatRequest,
    ConversationResponse,
    ConversationCreate,
    Message
)
from app.api.v1.deps import get_current_user
from app.services.conversation_service import conversation_service
from app.services.ai_agent import learning_agent

router = APIRouter()

@router.post("/send", response_model=ConversationResponse)
async def send_message(
    request: ChatRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Send a message to the AI learning assistant
    """
    try:
        user_id = str(current_user.id)
        
        # Get or create conversation
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                request.conversation_id,
                user_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation = await conversation_service.create_conversation(
                user_id,
                ConversationCreate(title=title, subject=request.subject)
            )
        
        # Add user message
        user_message = Message(role="user", content=request.message)
        conversation = await conversation_service.add_message(
            str(conversation.id),
            user_id,
            user_message
        )
        
        # Generate AI response
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.messages[:-1]  # Exclude the just-added message
        ]
        
        ai_response = await learning_agent.generate_response(
            request.message,
            conversation_history,
            conversation.subject
        )
        
        # Add AI message
        ai_message = Message(role="assistant", content=ai_response)
        conversation = await conversation_service.add_message(
            str(conversation.id),
            user_id,
            ai_message
        )
        
        # Return conversation response
        return ConversationResponse(
            id=str(conversation.id),
            user_id=conversation.user_id,
            title=conversation.title,
            subject=conversation.subject,
            messages=conversation.messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: UserInDB = Depends(get_current_user),
    limit: int = 50
):
    """
    Get all conversations for the current user
    """
    user_id = str(current_user.id)
    conversations = await conversation_service.get_user_conversations(user_id, limit)
    
    return [
        ConversationResponse(
            id=str(conv.id),
            user_id=conv.user_id,
            title=conv.title,
            subject=conv.subject,
            messages=conv.messages,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        )
        for conv in conversations
    ]

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific conversation
    """
    user_id = str(current_user.id)
    conversation = await conversation_service.get_conversation(conversation_id, user_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse(
        id=str(conversation.id),
        user_id=conversation.user_id,
        title=conversation.title,
        subject=conversation.subject,
        messages=conversation.messages,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a conversation
    """
    user_id = str(current_user.id)
    deleted = await conversation_service.delete_conversation(conversation_id, user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"message": "Conversation deleted successfully"}
