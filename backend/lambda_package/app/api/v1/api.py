from fastapi import APIRouter
from app.api.v1.endpoints import auth, chat, users, agents, agent_chats

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
api_router.include_router(agent_chats.router, prefix="/agent-chats", tags=["Agent Chats"])
