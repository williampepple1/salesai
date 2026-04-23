from typing import Dict, Any, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy.orm import Session
import logging
from ..models import User, Conversation, Product
from ..config import settings
from .ai_agent import AIAgent

logger = logging.getLogger(__name__)


class TelegramBotService:
    """
    Telegram bot service for handling customer interactions.
    Uses webhook-based approach for AWS Lambda deployment.
    """
    
    def __init__(self):
        self.ai_agent = AIAgent()
    
    async def handle_webhook(
        self,
        update_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Handle incoming webhook from Telegram.
        
        Args:
            update_data: Telegram update data
            db: Database session
            
        Returns:
            Response dictionary
        """
        try:
            # Parse update
            update = Update.de_json(update_data, None)
            
            if update.message:
                return await self._handle_message(update, db)
            
            return {"status": "ok"}
        
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_message(
        self,
        update: Update,
        db: Session
    ) -> Dict[str, Any]:
        """Handle incoming message."""
        message = update.message
        chat_id = str(message.chat_id)
        text = message.text
        
        # Find seller by bot token (we'll need to match this)
        # For now, we'll use a simple approach - in production, 
        # you'd store bot_token -> user_id mapping
        user = self._get_user_for_bot(db)
        
        if not user:
            return {"status": "error", "message": "Bot not configured"}
        
        # Get or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.telegram_chat_id == chat_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                user_id=user.id,
                telegram_chat_id=chat_id,
                status="active"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Handle commands
        if text and text.startswith('/'):
            return await self._handle_command(text, message, conversation, user, db)
        
        # Process message with AI agent
        response = await self.ai_agent.process_message(
            text,
            conversation.id,
            user.id,
            db
        )
        
        # Send response via Telegram
        await self._send_message(
            chat_id,
            response["response"],
            user.telegram_bot_token
        )
        
        # Check if we need to send product images
        if conversation.context and "show_product" in conversation.context:
            product_id = conversation.context["show_product"]
            await self._send_product_images(
                chat_id,
                product_id,
                user.telegram_bot_token,
                db
            )
            # Clear the flag
            conversation.context.pop("show_product")
            db.commit()
        
        return {"status": "ok"}
    
    async def _handle_command(
        self,
        command: str,
        message,
        conversation: Conversation,
        user: User,
        db: Session
    ) -> Dict[str, Any]:
        """Handle Telegram commands."""
        chat_id = str(message.chat_id)
        
        if command == "/start":
            welcome_text = f"""👋 Welcome to {user.business_name or user.username}!

I'm your AI sales assistant. I can help you:
- Browse our products
- Get product details and prices
- Place orders
- Answer questions

Just ask me anything or type /browse to see our products!
"""
            await self._send_message(chat_id, welcome_text, user.telegram_bot_token)
        
        elif command == "/browse":
            products = db.query(Product).filter(
                Product.user_id == user.id,
                Product.is_available == True
            ).all()
            
            if not products:
                await self._send_message(
                    chat_id,
                    "Sorry, no products available right now.",
                    user.telegram_bot_token
                )
            else:
                products_text = "🛍️ **Available Products:**\n\n"
                for i, product in enumerate(products, 1):
                    products_text += f"{i}. **{product.name}** - ${product.price} {product.currency}\n"
                    if product.description:
                        products_text += f"   {product.description}\n"
                    products_text += "\n"
                
                products_text += "Ask me about any product to get more details!"
                
                await self._send_message(chat_id, products_text, user.telegram_bot_token)
        
        elif command == "/cart":
            if conversation.context and "cart" in conversation.context:
                cart = conversation.context["cart"]
                if cart:
                    cart_text = "🛒 **Your Cart:**\n\n"
                    for item in cart:
                        product = db.query(Product).filter(
                            Product.id == item["product_id"]
                        ).first()
                        if product:
                            cart_text += f"- {product.name} x {item['quantity']}\n"
                    await self._send_message(chat_id, cart_text, user.telegram_bot_token)
                else:
                    await self._send_message(
                        chat_id,
                        "Your cart is empty.",
                        user.telegram_bot_token
                    )
            else:
                await self._send_message(
                    chat_id,
                    "Your cart is empty.",
                    user.telegram_bot_token
                )
        
        return {"status": "ok"}
    
    async def _send_message(
        self,
        chat_id: str,
        text: str,
        bot_token: str
    ):
        """Send a text message via Telegram."""
        try:
            bot = Bot(token=bot_token)
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def _send_product_images(
        self,
        chat_id: str,
        product_id: int,
        bot_token: str,
        db: Session
    ):
        """Send product images to customer."""
        try:
            product = db.query(Product).filter(
                Product.id == product_id
            ).first()
            
            if product and product.image_urls:
                bot = Bot(token=bot_token)
                for image_url in product.image_urls[:5]:  # Max 5 images
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=image_url,
                        caption=f"{product.name} - ${product.price}"
                    )
        except Exception as e:
            logger.error(f"Error sending images: {e}")
    
    def _get_user_for_bot(self, db: Session) -> Optional[User]:
        """
        Get user for the current bot.
        In production, this would match based on the bot token from the webhook URL.
        For now, we'll return the first user with a bot token.
        """
        return db.query(User).filter(
            User.telegram_bot_token.isnot(None)
        ).first()
    
    @staticmethod
    async def set_webhook(bot_token: str, webhook_url: str) -> bool:
        """
        Set webhook URL for a Telegram bot.
        
        Args:
            bot_token: Telegram bot token
            webhook_url: Webhook URL (API Gateway endpoint)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bot = Bot(token=bot_token)
            await bot.set_webhook(url=webhook_url)
            return True
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
