from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    subject: Optional[str] = None

class ConversationInDB(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    user_id: str
    title: str
    subject: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    subject: Optional[str] = None
    messages: List[Message]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    subject: Optional[str] = None
