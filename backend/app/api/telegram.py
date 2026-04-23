from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..clerk_auth import get_current_active_user
from ..services.telegram_bot import TelegramBotService

router = APIRouter()
telegram_service = TelegramBotService()


@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for Telegram updates.
    This is called by Telegram when messages are sent to the bot.
    """
    try:
        update_data = await request.json()
        result = await telegram_service.handle_webhook(update_data, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/set-webhook")
async def set_webhook(
    webhook_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Set webhook URL for the user's Telegram bot."""
    if not current_user.telegram_bot_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Telegram bot token configured"
        )
    
    success = await TelegramBotService.set_webhook(
        current_user.telegram_bot_token,
        webhook_url
    )
    
    if success:
        return {"message": "Webhook set successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set webhook"
        )


@router.post("/update-bot-token")
def update_bot_token(
    bot_token: str,
    bot_username: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update Telegram bot token for the current user."""
    current_user.telegram_bot_token = bot_token
    if bot_username:
        current_user.telegram_bot_username = bot_username
    
    db.commit()
    
    return {"message": "Bot token updated successfully"}
