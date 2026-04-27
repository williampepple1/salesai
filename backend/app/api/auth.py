from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas.user import UserResponse, UserUpdateRequest
from ..clerk_auth import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    User is automatically created on first login via Clerk.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    """
    # Update allowed fields
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.business_name is not None:
        current_user.business_name = user_data.business_name
    if user_data.bank_name is not None:
        current_user.bank_name = user_data.bank_name
    if user_data.account_name is not None:
        current_user.account_name = user_data.account_name
    if user_data.account_number is not None:
        current_user.account_number = user_data.account_number
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/status")
def auth_status():
    """
    Check authentication service status.
    """
    return {
        "status": "ok",
        "auth_provider": "clerk",
        "message": "Authentication is handled by Clerk"
    }
