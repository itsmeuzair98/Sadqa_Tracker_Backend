from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    google_id: str
    picture_url: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    picture_url: Optional[str] = None


class UserInDBBase(UserBase):
    id: int
    google_id: str
    picture_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """User schema for responses"""
    pass


class UserInDB(UserInDBBase):
    """User schema for internal use (includes sensitive fields if any)"""
    pass


class UserWithToken(UserInDBBase):
    """User schema with JWT token for authentication responses"""
    access_token: str
    token_type: str
