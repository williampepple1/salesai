from typing import Optional
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User

security = HTTPBearer()


class ClerkAuth:
    """
    Clerk authentication middleware for FastAPI.
    Validates JWT tokens from Clerk and manages user sessions.
    """
    
    def __init__(self):
        self.jwks_url = f"https://{settings.CLERK_DOMAIN}/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(self.jwks_url)
    
    def verify_token(self, token: str) -> dict:
        """
        Verify Clerk JWT token and return decoded payload.
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Decoded token payload with user information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Get signing key from Clerk's JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.CLERK_AUDIENCE,
                options={"verify_exp": True}
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )


clerk_auth = ClerkAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from Clerk token.
    Creates user in database if they don't exist (first login).
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    # Verify token with Clerk
    payload = clerk_auth.verify_token(token)
    
    # Extract user information from Clerk payload. Clerk session JWTs can vary
    # by template, so keep local/demo mode tolerant of missing email claims.
    clerk_user_id = payload.get("sub")
    email = (
        payload.get("email")
        or payload.get("email_address")
        or payload.get("primary_email_address")
        or payload.get("emailAddress")
        or (f"{clerk_user_id}@demo.local" if clerk_user_id else None)
    )
    username = payload.get("username") or (email.split("@")[0] if email else clerk_user_id)
    
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get or create user in database
    user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
    
    if not user:
        # Create new user on first login
        user = User(
            clerk_user_id=clerk_user_id,
            email=email,
            username=username,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active user instance
    """
    return current_user


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract Clerk user ID from token without full verification.
    Useful for webhook validation.
    
    Args:
        token: JWT token string
        
    Returns:
        Clerk user ID or None
    """
    try:
        payload = clerk_auth.verify_token(token)
        return payload.get("sub")
    except:
        return None
