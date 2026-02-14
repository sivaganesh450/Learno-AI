"""
Agent Chat API Endpoints.
Provides CRUD operations for persistent agent chat sessions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import json
import asyncio

from app.models.user import UserInDB
from app.models.agent_chat import (
    AgentChatCreate,
    AgentChatResponse,
    AgentChatListItem,
    SendMessageRequest,
    UpdateChatTitleRequest
)
from app.api.v1.deps import get_current_user
from app.services.agent_chat_service import agent_chat_service
from app.services.agents import (
    roadmap_agent,
    resources_agent,
    summarizer_agent,
    quiz_agent,
    math_solver_agent,
    job_search_agent
)

router = APIRouter()


def chat_to_response(chat) -> AgentChatResponse:
    """Convert AgentChatInDB to AgentChatResponse"""
    return AgentChatResponse(
        id=str(chat.id),
        chat_id=chat.chat_id,
        user_id=chat.user_id,
        agent_type=chat.agent_type,
        title=chat.title,
        messages=chat.messages,
        is_active=chat.is_active,
        created_at=chat.created_at,
        updated_at=chat.updated_at
    )


# ============= Chat CRUD Endpoints =============

@router.post("/create", response_model=AgentChatResponse)
async def create_chat(
    request: AgentChatCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new chat session for an agent"""
    user_id = str(current_user.id)
    
    chat = await agent_chat_service.create_chat(
        user_id=user_id,
        agent_type=request.agent_type,
        title=request.title,
        initial_message=request.initial_message
    )
    
    return chat_to_response(chat)


@router.get("/list", response_model=List[AgentChatListItem])
async def list_chats(
    agent_type: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get all chats for the current user, optionally filtered by agent type"""
    user_id = str(current_user.id)
    
    chats = await agent_chat_service.get_user_chats(
        user_id=user_id,
        agent_type=agent_type,
        limit=limit,
        skip=skip
    )
    
    return chats


@router.get("/{chat_id}", response_model=AgentChatResponse)
async def get_chat(
    chat_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific chat by chat_id"""
    user_id = str(current_user.id)
    
    chat = await agent_chat_service.get_chat(chat_id, user_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return chat_to_response(chat)


@router.put("/{chat_id}/title")
async def update_chat_title(
    chat_id: str,
    request: UpdateChatTitleRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update the title of a chat"""
    user_id = str(current_user.id)
    
    chat = await agent_chat_service.update_chat_title(
        chat_id=chat_id,
        user_id=user_id,
        title=request.title
    )
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return {"message": "Title updated", "title": request.title}


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    permanent: bool = False,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a chat (soft delete by default)"""
    user_id = str(current_user.id)
    
    if permanent:
        success = await agent_chat_service.hard_delete_chat(chat_id, user_id)
    else:
        success = await agent_chat_service.delete_chat(chat_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return {"message": "Chat deleted"}


@router.delete("/{chat_id}/messages")
async def clear_chat_messages(
    chat_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Clear all messages from a chat"""
    user_id = str(current_user.id)
    
    success = await agent_chat_service.clear_chat_messages(chat_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return {"message": "Messages cleared"}


# ============= Send Message with Streaming =============

@router.post("/send/stream")
async def send_message_stream(
    request: SendMessageRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Send a message to an agent with streaming response.
    Creates a new chat if chat_id is not provided.
    """
    user_id = str(current_user.id)
    
    # Get or create chat
    chat = await agent_chat_service.get_or_create_chat(
        user_id=user_id,
        agent_type=request.agent_type,
        chat_id=request.chat_id,
        initial_message=request.message if not request.chat_id else None
    )
    
    # Add user message if this is an existing chat
    if request.chat_id:
        await agent_chat_service.add_message(
            chat_id=chat.chat_id,
            user_id=user_id,
            role="user",
            content=request.message
        )
    
    # Get conversation history for context (future: pass to agents for context-aware responses)
    _ = await agent_chat_service.get_conversation_history(
        chat_id=chat.chat_id,
        user_id=user_id,
        limit=20
    )
    
    async def stream_generator():
        full_response = ""
        
        try:
            # Debug logging
            print(f"[Agent Chat] Routing to agent: {request.agent_type}")
            print(f"[Agent Chat] Chat ID: {chat.chat_id}, User: {user_id}")
            print(f"[Agent Chat] Message: {request.message[:100]}...")
            
            # Send chat_id first so frontend knows which chat this belongs to
            yield f"data: {json.dumps({'chat_id': chat.chat_id, 'type': 'meta'})}\n\n"
            
            # Route to appropriate agent
            if request.agent_type == "roadmap":
                form_data = request.form_data or {}
                async for chunk in roadmap_agent.generate_stream(
                    message=request.message,
                    topic=form_data.get("domain", request.message),
                    skill_level=form_data.get("level", "beginner"),
                    duration=form_data.get("duration", "3 months"),
                    skills_known=form_data.get("skillsKnown", "")
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            elif request.agent_type == "resources":
                # Use chat_id as session for conversation memory
                session_key = f"{user_id}_{chat.chat_id}"
                async for chunk in resources_agent.get_resources_stream(
                    message=request.message,
                    topic=request.message,
                    resource_type="all",
                    session_id=session_key
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            elif request.agent_type == "qa":
                # Use chat_id as session for conversation memory
                session_key = f"{user_id}_{chat.chat_id}"
                async for chunk in summarizer_agent.answer_stream(
                    question=request.message,
                    session_id=session_key
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            elif request.agent_type == "quiz":
                form_data = request.form_data or {}
                session_key = f"{user_id}_{chat.chat_id}"
                
                # Check if session needs to be started
                if form_data.get("domain"):
                    quiz_agent.start_session(
                        session_id=session_key,
                        domain=form_data.get("domain", ""),
                        purpose=form_data.get("purpose", "interview"),
                        difficulty=form_data.get("difficulty", "moderate")
                    )
                
                async for chunk in quiz_agent.process_message_stream(
                    message=request.message,
                    session_id=session_key
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            elif request.agent_type == "math":
                # Use chat_id as session for conversation memory
                session_key = f"{user_id}_{chat.chat_id}"
                async for chunk in math_solver_agent.solve_stream(
                    problem=request.message,
                    session_id=session_key
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            elif request.agent_type == "jobs":
                # Parse location from query
                query = request.message
                location = ""
                if " in " in request.message.lower():
                    parts = request.message.lower().split(" in ", 1)
                    query = parts[0].strip()
                    location = parts[1].strip() if len(parts) > 1 else ""
                
                # Use chat_id as session for conversation memory
                session_key = f"{user_id}_{chat.chat_id}"
                async for chunk in job_search_agent.search_stream(
                    query=query,
                    location=location,
                    session_id=session_key
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            else:
                full_response = "Unknown agent type"
                yield f"data: {json.dumps({'chunk': full_response})}\n\n"
            
            # Save assistant response to chat
            if full_response:
                await agent_chat_service.add_message(
                    chat_id=chat.chat_id,
                    user_id=user_id,
                    role="assistant",
                    content=full_response
                )
            
            yield f"data: {json.dumps({'done': True, 'chat_id': chat.chat_id})}\n\n"
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/send", response_model=AgentChatResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Send a message to an agent (non-streaming).
    Creates a new chat if chat_id is not provided.
    """
    user_id = str(current_user.id)
    
    # Get or create chat
    chat = await agent_chat_service.get_or_create_chat(
        user_id=user_id,
        agent_type=request.agent_type,
        chat_id=request.chat_id,
        initial_message=request.message if not request.chat_id else None
    )
    
    # Add user message if this is an existing chat
    if request.chat_id:
        await agent_chat_service.add_message(
            chat_id=chat.chat_id,
            user_id=user_id,
            role="user",
            content=request.message
        )
    
    # Generate response based on agent type
    response = ""
    
    try:
        if request.agent_type == "roadmap":
            form_data = request.form_data or {}
            response = await roadmap_agent.generate(
                message=request.message,
                topic=form_data.get("domain", request.message),
                skill_level=form_data.get("level", "beginner"),
                duration=form_data.get("duration", "3 months"),
                skills_known=form_data.get("skillsKnown", "")
            )
        
        elif request.agent_type == "resources":
            response = await resources_agent.get_resources(
                message=request.message,
                topic=request.message,
                resource_type="all"
            )
        
        elif request.agent_type == "qa":
            response = await summarizer_agent.answer(question=request.message)
        
        elif request.agent_type == "quiz":
            form_data = request.form_data or {}
            session_key = f"{user_id}_{chat.chat_id}"
            
            if form_data.get("domain"):
                quiz_agent.start_session(
                    session_id=session_key,
                    domain=form_data.get("domain", ""),
                    purpose=form_data.get("purpose", "interview"),
                    difficulty=form_data.get("difficulty", "moderate")
                )
            
            response = await quiz_agent.process_message(
                message=request.message,
                session_id=session_key
            )
        
        elif request.agent_type == "math":
            response = await math_solver_agent.solve(request.message)
        
        elif request.agent_type == "jobs":
            query = request.message
            location = ""
            if " in " in request.message.lower():
                parts = request.message.lower().split(" in ", 1)
                query = parts[0].strip()
                location = parts[1].strip() if len(parts) > 1 else ""
            
            response = await job_search_agent.search_and_format(
                query=query,
                location=location
            )
        
        else:
            response = "Unknown agent type"
        
        # Add assistant response
        chat = await agent_chat_service.add_message(
            chat_id=chat.chat_id,
            user_id=user_id,
            role="assistant",
            content=response
        )
        
    except Exception as e:
        response = f"Error: {str(e)}"
        chat = await agent_chat_service.add_message(
            chat_id=chat.chat_id,
            user_id=user_id,
            role="assistant",
            content=response
        )
    
    return chat_to_response(chat)
