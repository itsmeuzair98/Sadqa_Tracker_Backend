from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.auth.auth_dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate, UserWithToken

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

@router.delete("/me")
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete current user account"""
    current_user.is_active = False
    await db.commit()
    
    return {"message": "User account deactivated successfully"}

class UserSyncRequest:
    def __init__(self, email: str, name: str, sub: str, image: str = None):
        self.email = email
        self.name = name
        self.sub = sub
        self.image = image

@router.post("/sync", response_model=UserWithToken)
async def sync_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Sync user from NextAuth Google OAuth to database"""
    try:
        # Parse JSON body
        user_data = await request.json()
        
        # Extract user info from NextAuth session
        email = user_data.get("email")
        name = user_data.get("name") 
        google_id = user_data.get("sub") or user_data.get("id")
        picture_url = user_data.get("image") or user_data.get("picture")
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and Google ID are required"
            )
        
        # Check if user exists by Google ID
        result = await db.execute(
            select(User).where(User.google_id == google_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Check by email as well (in case of data inconsistency)
            result = await db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                picture_url=picture_url,
                is_verified=True  # Google users are pre-verified
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Update existing user info
            user.name = name
            user.picture_url = picture_url
            user.email = email  # Update in case it changed
            await db.commit()
            await db.refresh(user)
        
        # Create JWT token for this user
        from app.auth.jwt_handler import create_access_token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Return user data with token
        return UserWithToken(
            id=user.id,
            email=user.email,
            name=user.name,
            google_id=user.google_id,
            picture_url=user.picture_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            access_token=access_token,
            token_type="bearer"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync user: {str(e)}"
        )
