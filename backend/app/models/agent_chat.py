"""
Agent Chat Models for persistent conversation memory.
Similar to ChatGPT/Gemini chat sessions.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from bson import ObjectId


class ChatMessage(BaseModel):
    """Individual message in a chat"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AgentChatCreate(BaseModel):
    """Request model for creating a new chat"""
    agent_type: Literal["roadmap", "resources", "qa", "quiz", "math", "jobs"]
    title: Optional[str] = None
    initial_message: Optional[str] = None


class AgentChatInDB(BaseModel):
    """Chat document stored in MongoDB"""
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    chat_id: str  # Unique identifier for the chat session
    user_id: str  # User who owns this chat
    agent_type: str  # Which agent this chat belongs to
    title: str  # Chat title (usually from first message)
    messages: List[ChatMessage] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, datetime: lambda v: v.isoformat()}
    }


class AgentChatResponse(BaseModel):
    """Response model for chat data"""
    id: str
    chat_id: str
    user_id: str
    agent_type: str
    title: str
    messages: List[ChatMessage]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class AgentChatListItem(BaseModel):
    """Lightweight chat item for list display"""
    id: str
    chat_id: str
    agent_type: str
    title: str
    message_count: int
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SendMessageRequest(BaseModel):
    """Request model for sending a message to an agent chat"""
    chat_id: Optional[str] = None  # If None, creates new chat
    agent_type: Literal["roadmap", "resources", "qa", "quiz", "math", "jobs"]
    message: str
    # Additional data for specific agents
    form_data: Optional[dict] = None  # For roadmap questionnaire, quiz settings, etc.


class UpdateChatTitleRequest(BaseModel):
    """Request model for updating chat title"""
    title: str
