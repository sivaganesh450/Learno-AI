"""
Agent Chat Service for persistent memory across sessions.
Handles CRUD operations for agent-specific chat histories.
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import uuid
from app.core.database import get_database
from app.models.agent_chat import (
    AgentChatInDB,
    AgentChatCreate,
    AgentChatResponse,
    AgentChatListItem,
    ChatMessage
)


class AgentChatService:
    """Service for managing agent chat sessions with MongoDB"""
    
    def __init__(self):
        self.collection_name = "agent_chats"
    
    async def get_collection(self):
        """Get the MongoDB collection"""
        db = get_database()
        return db[self.collection_name]
    
    def _generate_chat_id(self) -> str:
        """Generate a unique chat ID"""
        return str(uuid.uuid4())[:8]
    
    def _generate_title(self, message: str, agent_type: str) -> str:
        """Generate a title from the first message"""
        agent_names = {
            "roadmap": "Roadmap",
            "resources": "Resources",
            "qa": "Summarizer",
            "quiz": "Quiz",
            "math": "Math",
            "jobs": "Job Search"
        }
        agent_name = agent_names.get(agent_type, "Chat")
        
        # Truncate message for title
        if len(message) > 40:
            title = message[:40] + "..."
        else:
            title = message
        
        return f"{agent_name}: {title}"
    
    async def create_chat(
        self,
        user_id: str,
        agent_type: str,
        title: Optional[str] = None,
        initial_message: Optional[str] = None
    ) -> AgentChatInDB:
        """Create a new chat session"""
        collection = await self.get_collection()
        
        chat_id = self._generate_chat_id()
        
        # Generate title if not provided
        if not title and initial_message:
            title = self._generate_title(initial_message, agent_type)
        elif not title:
            title = f"New {agent_type.capitalize()} Chat"
        
        messages = []
        if initial_message:
            messages.append(ChatMessage(
                role="user",
                content=initial_message,
                timestamp=datetime.utcnow()
            ).model_dump())
        
        chat_dict = {
            "chat_id": chat_id,
            "user_id": user_id,
            "agent_type": agent_type,
            "title": title,
            "messages": messages,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(chat_dict)
        chat_dict["_id"] = result.inserted_id
        
        return AgentChatInDB(**chat_dict)
    
    async def get_chat(self, chat_id: str, user_id: str) -> Optional[AgentChatInDB]:
        """Get a specific chat by chat_id"""
        collection = await self.get_collection()
        
        chat_dict = await collection.find_one({
            "chat_id": chat_id,
            "user_id": user_id
        })
        
        if chat_dict:
            return AgentChatInDB(**chat_dict)
        return None
    
    async def get_chat_by_object_id(self, object_id: str, user_id: str) -> Optional[AgentChatInDB]:
        """Get a specific chat by MongoDB ObjectId"""
        collection = await self.get_collection()
        
        try:
            chat_dict = await collection.find_one({
                "_id": ObjectId(object_id),
                "user_id": user_id
            })
            
            if chat_dict:
                return AgentChatInDB(**chat_dict)
        except Exception:
            pass
        return None
    
    async def get_user_chats(
        self,
        user_id: str,
        agent_type: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[AgentChatListItem]:
        """Get all chats for a user, optionally filtered by agent type"""
        collection = await self.get_collection()
        
        query = {"user_id": user_id, "is_active": True}
        if agent_type:
            query["agent_type"] = agent_type
        
        cursor = collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        
        chats = []
        async for chat_dict in cursor:
            messages = chat_dict.get("messages", [])
            last_message = None
            if messages:
                last_msg = messages[-1]
                content = last_msg.get("content", "")
                last_message = content[:100] + "..." if len(content) > 100 else content
            
            chats.append(AgentChatListItem(
                id=str(chat_dict["_id"]),
                chat_id=chat_dict["chat_id"],
                agent_type=chat_dict["agent_type"],
                title=chat_dict["title"],
                message_count=len(messages),
                last_message=last_message,
                created_at=chat_dict["created_at"],
                updated_at=chat_dict["updated_at"]
            ))
        
        return chats
    
    async def add_message(
        self,
        chat_id: str,
        user_id: str,
        role: str,
        content: str
    ) -> Optional[AgentChatInDB]:
        """Add a message to an existing chat"""
        collection = await self.get_collection()
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        result = await collection.find_one_and_update(
            {"chat_id": chat_id, "user_id": user_id},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        if result:
            return AgentChatInDB(**result)
        return None
    
    async def get_chat_messages(
        self,
        chat_id: str,
        user_id: str,
        limit: int = 100
    ) -> List[ChatMessage]:
        """Get messages from a chat"""
        chat = await self.get_chat(chat_id, user_id)
        if chat:
            # Return last N messages
            messages = chat.messages[-limit:] if len(chat.messages) > limit else chat.messages
            return messages
        return []
    
    async def get_conversation_history(
        self,
        chat_id: str,
        user_id: str,
        limit: int = 20
    ) -> List[dict]:
        """Get conversation history in format suitable for LLM context"""
        messages = await self.get_chat_messages(chat_id, user_id, limit)
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    async def update_chat_title(
        self,
        chat_id: str,
        user_id: str,
        title: str
    ) -> Optional[AgentChatInDB]:
        """Update the title of a chat"""
        collection = await self.get_collection()
        
        result = await collection.find_one_and_update(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"title": title, "updated_at": datetime.utcnow()}},
            return_document=True
        )
        
        if result:
            return AgentChatInDB(**result)
        return None
    
    async def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """Soft delete a chat (mark as inactive)"""
        collection = await self.get_collection()
        
        result = await collection.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def hard_delete_chat(self, chat_id: str, user_id: str) -> bool:
        """Permanently delete a chat"""
        collection = await self.get_collection()
        
        result = await collection.delete_one({
            "chat_id": chat_id,
            "user_id": user_id
        })
        
        return result.deleted_count > 0
    
    async def clear_chat_messages(self, chat_id: str, user_id: str) -> bool:
        """Clear all messages from a chat but keep the chat"""
        collection = await self.get_collection()
        
        result = await collection.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {
                "$set": {
                    "messages": [],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    async def get_or_create_chat(
        self,
        user_id: str,
        agent_type: str,
        chat_id: Optional[str] = None,
        initial_message: Optional[str] = None
    ) -> AgentChatInDB:
        """Get existing chat or create new one"""
        if chat_id:
            chat = await self.get_chat(chat_id, user_id)
            if chat:
                return chat
        
        # Create new chat
        return await self.create_chat(
            user_id=user_id,
            agent_type=agent_type,
            initial_message=initial_message
        )


# Singleton instance
agent_chat_service = AgentChatService()
