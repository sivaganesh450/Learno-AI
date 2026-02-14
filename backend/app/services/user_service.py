from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.core.security import get_password_hash, verify_password
from app.models.user import UserCreate, UserInDB

class UserService:
    def __init__(self):
        self.collection_name = "users"
    
    async def get_collection(self):
        db = get_database()
        return db[self.collection_name]
    
    async def create_user(self, user: UserCreate) -> UserInDB:
        """Create a new user"""
        collection = await self.get_collection()
        
        print(f"[DEBUG] Creating user with email: {user.email}")
        
        # Validate password length
        if len(user.password) < 6:
            print(f"[DEBUG] Password too short: {len(user.password)} characters")
            raise ValueError("Password must be at least 6 characters long")
        
        # Check if user already exists
        existing_user = await collection.find_one({"email": user.email})
        if existing_user:
            print(f"[DEBUG] User already exists: {user.email}")
            raise ValueError("User with this email already exists")
        
        print(f"[DEBUG] Hashing password")
        hashed_pwd = get_password_hash(user.password)
        print(f"[DEBUG] Password hashed successfully")
        
        # Create user document
        user_dict = {
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_pwd,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        print(f"[DEBUG] User created successfully with ID: {result.inserted_id}")
        
        return UserInDB(**user_dict)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        collection = await self.get_collection()
        user_dict = await collection.find_one({"email": email})
        
        if user_dict:
            return UserInDB(**user_dict)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        collection = await self.get_collection()
        user_dict = await collection.find_one({"_id": ObjectId(user_id)})
        
        if user_dict:
            return UserInDB(**user_dict)
        return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user"""
        print(f"[DEBUG] Attempting to authenticate user: {email}")
        user = await self.get_user_by_email(email)
        if not user:
            print(f"[DEBUG] User not found: {email}")
            return None
        print(f"[DEBUG] User found, verifying password")
        password_valid = verify_password(password, user.hashed_password)
        print(f"[DEBUG] Password verification result: {password_valid}")
        if not password_valid:
            return None
        return user

user_service = UserService()
