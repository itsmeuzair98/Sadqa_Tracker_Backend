import httpx
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from app.core.config import settings

class GoogleOAuth:
    def __init__(self):
        self.client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        self.client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
        
    async def get_authorization_url(self):
        """Get Google OAuth authorization URL"""
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope=openid email profile&"
            f"response_type=code&"
            f"access_type=offline"
        )
        return auth_url
    
    async def get_access_token(self, code: str):
        """Exchange authorization code for access token"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
            
        return response.json()
    
    async def get_user_info(self, id_token_str: str):
        """Verify ID token and get user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                self.client_id
            )
            
            return {
                "google_id": idinfo["sub"],
                "email": idinfo["email"],
                "name": idinfo["name"],
                "picture_url": idinfo.get("picture", ""),
                "email_verified": idinfo.get("email_verified", False)
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")

google_oauth = GoogleOAuth()
