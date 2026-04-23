from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    clerk_user_id: str
    email: str
    username: str
    full_name: Optional[str]
    business_name: Optional[str]
    telegram_bot_username: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    business_name: Optional[str] = None


class TokenData(BaseModel):
    clerk_user_id: Optional[str] = None
