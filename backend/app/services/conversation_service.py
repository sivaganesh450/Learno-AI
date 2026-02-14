from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models.conversation import ConversationInDB, ConversationCreate, Message

class ConversationService:
    def __init__(self):
        self.collection_name = "conversations"
    
    async def get_collection(self):
        db = get_database()
        return db[self.collection_name]
    
    async def create_conversation(self, user_id: str, conversation: ConversationCreate) -> ConversationInDB:
        """Create a new conversation"""
        collection = await self.get_collection()
        
        conversation_dict = {
            "user_id": user_id,
            "title": conversation.title,
            "subject": conversation.subject,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(conversation_dict)
        conversation_dict["_id"] = result.inserted_id
        
        return ConversationInDB(**conversation_dict)
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[ConversationInDB]:
        """Get a conversation by ID"""
        collection = await self.get_collection()
        conversation_dict = await collection.find_one({
            "_id": ObjectId(conversation_id),
            "user_id": user_id
        })
        
        if conversation_dict:
            return ConversationInDB(**conversation_dict)
        return None
    
    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[ConversationInDB]:
        """Get all conversations for a user"""
        collection = await self.get_collection()
        cursor = collection.find({"user_id": user_id}).sort("updated_at", -1).limit(limit)
        
        conversations = []
        async for conversation_dict in cursor:
            conversations.append(ConversationInDB(**conversation_dict))
        
        return conversations
    
    async def add_message(self, conversation_id: str, user_id: str, message: Message) -> ConversationInDB:
        """Add a message to a conversation"""
        collection = await self.get_collection()
        
        result = await collection.find_one_and_update(
            {"_id": ObjectId(conversation_id), "user_id": user_id},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        if result:
            return ConversationInDB(**result)
        return None
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        collection = await self.get_collection()
        result = await collection.delete_one({
            "_id": ObjectId(conversation_id),
            "user_id": user_id
        })
        
        return result.deleted_count > 0

conversation_service = ConversationService()
