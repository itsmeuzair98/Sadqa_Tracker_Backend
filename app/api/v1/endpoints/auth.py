from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.auth.google_oauth import google_oauth
from app.auth.jwt_handler import create_access_token
from app.models.user import User
from app.schemas.auth import GoogleAuthResponse, GoogleCallbackRequest, Token
from app.schemas.user import UserCreate, User as UserSchema

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get("/google", response_model=GoogleAuthResponse)
@limiter.limit("5/minute")
async def google_login(request):
    """Get Google OAuth authorization URL"""
    authorization_url = await google_oauth.get_authorization_url()
    return GoogleAuthResponse(authorization_url=authorization_url)

@router.post("/google/callback", response_model=Token)
@limiter.limit("10/minute")
async def google_callback(
    request,
    callback_data: GoogleCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        token_data = await google_oauth.get_access_token(callback_data.code)
        
        # Get user info from Google
        user_info = await google_oauth.get_user_info(token_data["id_token"])
        
        # Check if user exists
        result = await db.execute(
            select(User).where(User.google_id == user_info["google_id"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user_data = UserCreate(
                email=user_info["email"],
                name=user_info["name"],
                google_id=user_info["google_id"],
                picture_url=user_info.get("picture_url")
            )
            
            user = User(
                email=user_data.email,
                name=user_data.name,
                google_id=user_data.google_id,
                picture_url=user_data.picture_url,
                is_verified=user_info.get("email_verified", True)
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Update existing user info
            user.name = user_info["name"]
            user.picture_url = user_info.get("picture_url")
            await db.commit()
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture_url": user.picture_url
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/logout")
async def logout():
    """Logout endpoint (mainly for frontend state management)"""
    return {"message": "Successfully logged out"}
