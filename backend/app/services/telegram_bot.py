from typing import Dict, Any, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy.orm import Session
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ..models import User, Conversation, Product, Order
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
        
        except Exception:
            logger.exception("Error handling Telegram webhook")
            return {"status": "error", "message": "Unable to process webhook"}
    
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

        if message.photo or message.document:
            return await self._handle_receipt_upload(message, conversation, user, db)
        
        # Handle commands
        if text and text.startswith('/'):
            return await self._handle_command(text, message, conversation, user, db)

        # Fast local/demo handling for product questions and image requests.
        # This keeps the Telegram demo useful even without a valid OpenAI key.
        local_response = await self._handle_catalog_message(text or "", chat_id, user, db)
        if local_response:
            return local_response
        
        # Process message with AI agent
        try:
            response = await self.ai_agent.process_message(
                text,
                conversation.id,
                user.id,
                db
            )
        except Exception:
            logger.exception("AI agent failed, using catalog fallback")
            products = db.query(Product).filter(
                Product.user_id == user.id,
                Product.is_available == True
            ).all()
            fallback = self._catalog_summary(products)
            await self._send_message(chat_id, fallback, user.telegram_bot_token)
            return {"status": "ok", "fallback": "catalog_summary"}
        
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

    async def _handle_catalog_message(
        self,
        text: str,
        chat_id: str,
        user: User,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Answer common product/image questions directly from the catalog."""
        text_lower = text.lower()
        products = db.query(Product).filter(
            Product.user_id == user.id,
            Product.is_available == True
        ).all()

        if not products:
            await self._send_message(
                chat_id,
                "There are no products available right now. Please check back soon.",
                user.telegram_bot_token
            )
            return {"status": "ok", "handled": "no_products"}

        matched_product = self._find_product_in_text(text_lower, products)
        wants_image = any(word in text_lower for word in ["image", "photo", "picture", "pic", "show me"])
        asks_catalog = any(word in text_lower for word in ["catalog", "catalogue", "products", "items", "browse"])
        wants_checkout = any(word in text_lower for word in ["checkout", "done", "finish", "that's all", "that is all", "no more"])
        confirms_invoice = text_lower.strip() in ["yes", "yeah", "yep", "confirm", "send invoice", "invoice"]

        conversation = db.query(Conversation).filter(
            Conversation.telegram_chat_id == chat_id,
            Conversation.user_id == user.id
        ).first()

        if confirms_invoice and conversation and (conversation.context or {}).get("awaiting_final_confirmation"):
            await self._send_invoice(chat_id, conversation, user, db)
            return {"status": "ok", "handled": "invoice"}

        if wants_checkout and conversation:
            await self._ask_final_confirmation(chat_id, conversation, user, db)
            return {"status": "ok", "handled": "checkout"}

        if asks_catalog and not matched_product:
            await self._send_message(chat_id, self._catalog_summary(products), user.telegram_bot_token)
            return {"status": "ok", "handled": "catalog"}

        if matched_product:
            if wants_image:
                if matched_product.image_urls:
                    await self._send_message(
                        chat_id,
                        f"Here is the image for {matched_product.name}:",
                        user.telegram_bot_token
                    )
                    await self._send_product_images(chat_id, matched_product.id, user.telegram_bot_token, db)
                else:
                    await self._send_message(
                        chat_id,
                        f"{matched_product.name} does not have an image yet.",
                        user.telegram_bot_token
                    )
                return {"status": "ok", "handled": "image"}

            wants_to_add = (
                any(word in text_lower for word in ["buy", "add", "order", "want", "take", "need", "purchase"])
                or " of product" in text_lower
                or re.search(r"\b\d+\s+(of|x)\b", text_lower)
            )

            if wants_to_add:
                quantity = self._extract_quantity(text_lower)
                self._add_to_cart(conversation, matched_product, quantity, db)
                await self._send_message(
                    chat_id,
                    self._cart_summary(conversation, db)
                    + "\n\nIs that all you will buy? Reply **yes** to receive your invoice, or tell me another product and quantity.",
                    user.telegram_bot_token
                )
                return {"status": "ok", "handled": "cart_add"}

            await self._send_message(
                chat_id,
                self._product_details(matched_product),
                user.telegram_bot_token
            )
            return {"status": "ok", "handled": "details"}

        # If the user asks a product-like question but we cannot match a name,
        # guide them toward the available product names.
        if any(word in text_lower for word in ["price", "cost", "how much", "details", "tell me", "buy", "order", "add"]):
            await self._send_message(
                chat_id,
                "Which product do you mean? You can ask about: "
                + ", ".join(product.name for product in products[:8]),
                user.telegram_bot_token
            )
            return {"status": "ok", "handled": "clarify"}

        return None

    def _find_product_in_text(self, text_lower: str, products) -> Optional[Product]:
        """Find a product by name, partial name, or displayed catalog number."""
        for index, product in enumerate(products, 1):
            if f"product {index}" in text_lower or f"item {index}" in text_lower or text_lower.strip() == str(index):
                return product

        for product in products:
            name = product.name.lower()
            words = [word for word in name.split() if len(word) > 2]
            if name in text_lower or any(word in text_lower for word in words):
                return product

        return None

    def _product_details(self, product: Product) -> str:
        """Format product details for Telegram."""
        details = [
            f"**{product.name}**",
            f"Price: {product.price} {product.currency}",
            f"Stock: {product.stock_quantity}",
        ]
        if product.description:
            details.append(f"Description: {product.description}")
        if product.category:
            details.append(f"Category: {product.category}")
        if product.image_urls:
            details.append("You can ask: 'show me the image'.")
        return "\n".join(details)

    def _catalog_summary(self, products) -> str:
        """Format a concise product catalog for Telegram."""
        products_text = "🛍️ **Available Products:**\n\n"
        for i, product in enumerate(products, 1):
            products_text += f"{i}. **{product.name}** - {product.price} {product.currency}\n"
            if product.description:
                products_text += f"   {product.description}\n"
            products_text += "\n"
        products_text += "Ask me about any product, for example: 'Tell me about product 1' or 'Show me the image of product 1'."
        products_text += "\n\nWhat would you like to buy? Reply like: **2 of product 1** or **add laptop**."
        return products_text

    def _extract_quantity(self, text_lower: str) -> int:
        """Extract purchase quantity from free text."""
        quantity_match = re.search(r"\b(?:x|qty|quantity)?\s*(\d+)\b", text_lower)
        if quantity_match:
            return max(1, int(quantity_match.group(1)))
        word_numbers = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        }
        for word, number in word_numbers.items():
            if re.search(rf"\b{word}\b", text_lower):
                return number
        return 1

    def _add_to_cart(self, conversation: Conversation, product: Product, quantity: int, db: Session):
        """Add product to the conversation cart."""
        context = dict(conversation.context or {})
        cart = list(context.get("cart", []))
        existing_item = next((item for item in cart if item["product_id"] == product.id), None)

        if existing_item:
            existing_item["quantity"] += quantity
        else:
            cart.append({"product_id": product.id, "quantity": quantity})

        context["cart"] = cart
        context["awaiting_final_confirmation"] = True
        conversation.context = context
        db.commit()

    def _cart_summary(self, conversation: Conversation, db: Session) -> str:
        """Format cart summary."""
        cart = (conversation.context or {}).get("cart", [])
        if not cart:
            return "Your cart is empty."

        lines = ["🛒 **Current Cart:**"]
        total = 0.0
        for item in cart:
            product = db.query(Product).filter(Product.id == item["product_id"]).first()
            if not product:
                continue
            quantity = item["quantity"]
            line_total = float(product.price) * quantity
            total += line_total
            lines.append(f"- {product.name} x {quantity}: {line_total:.2f} {product.currency}")
        lines.append(f"\n**Total: {total:.2f}**")
        return "\n".join(lines)

    async def _ask_final_confirmation(
        self,
        chat_id: str,
        conversation: Conversation,
        user: User,
        db: Session
    ):
        """Ask if customer is done buying before invoice."""
        context = dict(conversation.context or {})
        context["awaiting_final_confirmation"] = True
        conversation.context = context
        db.commit()
        await self._send_message(
            chat_id,
            self._cart_summary(conversation, db)
            + "\n\nIs that all you will buy? Reply **yes** and I will send your invoice.",
            user.telegram_bot_token
        )

    async def _send_invoice(
        self,
        chat_id: str,
        conversation: Conversation,
        user: User,
        db: Session
    ):
        """Create and send invoice image."""
        invoice = self._build_invoice_data(conversation, user, db)
        if not invoice["items"]:
            await self._send_message(chat_id, "Your cart is empty. Tell me what you want to buy first.", user.telegram_bot_token)
            return

        order = Order(
            user_id=user.id,
            conversation_id=conversation.id,
            customer_name=f"Telegram customer {chat_id}",
            items=invoice["items"],
            subtotal=invoice["subtotal"],
            discount_amount=0.0,
            total_amount=invoice["total"],
            currency=invoice["currency"],
            status="pending",
            payment_status="awaiting_payment",
            notes="Created from Telegram bot demo flow"
        )
        db.add(order)
        db.flush()

        invoice_url = self._create_invoice_image(order.id, invoice, user)
        order.invoice_url = invoice_url
        context = dict(conversation.context or {})
        context["cart"] = []
        context["awaiting_final_confirmation"] = False
        context["awaiting_receipt"] = True
        context["latest_order_id"] = order.id
        conversation.context = context
        db.commit()
        db.refresh(order)

        bot = Bot(token=user.telegram_bot_token)
        await bot.send_photo(
            chat_id=chat_id,
            photo=invoice_url,
            caption="Here is your invoice. Please make payment using the bank details on the invoice, then send your payment receipt here."
        )

    async def _handle_receipt_upload(
        self,
        message,
        conversation: Conversation,
        user: User,
        db: Session
    ) -> Dict[str, Any]:
        """Store customer payment receipt and attach it to the latest order."""
        chat_id = str(message.chat_id)
        context = dict(conversation.context or {})
        order_id = context.get("latest_order_id")

        if not order_id:
            await self._send_message(
                chat_id,
                "I received the file, but I cannot find an active invoice for it. Please place an order first.",
                user.telegram_bot_token
            )
            return {"status": "ok", "handled": "receipt_without_order"}

        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user.id
        ).first()

        if not order:
            await self._send_message(
                chat_id,
                "I received the receipt, but the related order was not found.",
                user.telegram_bot_token
            )
            return {"status": "ok", "handled": "receipt_order_missing"}

        try:
            bot = Bot(token=user.telegram_bot_token)
            if message.photo:
                telegram_file = await bot.get_file(message.photo[-1].file_id)
                extension = ".jpg"
            elif message.document and (message.document.mime_type or "").startswith("image/"):
                telegram_file = await bot.get_file(message.document.file_id)
                extension = Path(message.document.file_name or "receipt.jpg").suffix or ".jpg"
            else:
                await self._send_message(
                    chat_id,
                    "Please send the receipt as an image/photo.",
                    user.telegram_bot_token
                )
                return {"status": "ok", "handled": "receipt_not_image"}

            receipt_dir = Path("static") / "receipts"
            receipt_dir.mkdir(parents=True, exist_ok=True)
            filename = f"receipt-order-{order.id}-{uuid.uuid4()}{extension}"
            receipt_path = receipt_dir / filename
            await telegram_file.download_to_drive(custom_path=str(receipt_path))

            public_base_url = settings.TELEGRAM_WEBHOOK_URL.split("/api/telegram/webhook")[0].rstrip("/")
            order.receipt_url = f"{public_base_url}/static/receipts/{filename}"
            order.payment_status = "receipt_submitted"
            order.status = "confirmed"
            context["awaiting_receipt"] = False
            conversation.context = context
            db.commit()

            await self._send_message(
                chat_id,
                f"Receipt received for Order #{order.id}. The seller can now view it in the dashboard.",
                user.telegram_bot_token
            )
            return {"status": "ok", "handled": "receipt_saved"}
        except Exception as e:
            logger.error(f"Error saving receipt: {e}")
            await self._send_message(
                chat_id,
                "I could not save the receipt. Please try sending the image again.",
                user.telegram_bot_token
            )
            return {"status": "error", "message": str(e)}

    def _build_invoice_data(self, conversation: Conversation, user: User, db: Session) -> Dict[str, Any]:
        """Build invoice data from cart."""
        items = []
        subtotal = 0.0
        currency = "USD"
        for item in (conversation.context or {}).get("cart", []):
            product = db.query(Product).filter(Product.id == item["product_id"]).first()
            if not product:
                continue
            quantity = item["quantity"]
            unit_price = float(product.price)
            line_total = unit_price * quantity
            currency = product.currency or currency
            subtotal += line_total
            items.append({
                "product_id": product.id,
                "name": product.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_applied": 0.0,
                "total_price": line_total,
            })
        return {"items": items, "subtotal": subtotal, "total": subtotal, "currency": currency}

    def _create_invoice_image(self, order_id: int, invoice: Dict[str, Any], user: User) -> str:
        """Generate a simple PNG invoice and return its public URL."""
        width = 900
        height = max(650, 360 + (len(invoice["items"]) * 45))
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        y = 40
        business_name = user.business_name or user.full_name or user.username
        draw.text((40, y), "INVOICE", fill=(2, 132, 199), font=font)
        y += 40
        draw.text((40, y), f"Invoice No: #{order_id}", fill="black", font=font)
        draw.text((600, y), datetime.now().strftime("%Y-%m-%d %H:%M"), fill="black", font=font)
        y += 35
        draw.text((40, y), f"Seller: {business_name}", fill="black", font=font)
        y += 50

        draw.rectangle((40, y, 860, y + 35), fill=(240, 249, 255))
        draw.text((55, y + 10), "Item", fill="black", font=font)
        draw.text((500, y + 10), "Qty", fill="black", font=font)
        draw.text((590, y + 10), "Unit", fill="black", font=font)
        draw.text((720, y + 10), "Total", fill="black", font=font)
        y += 45

        for item in invoice["items"]:
            draw.text((55, y), item["name"][:55], fill="black", font=font)
            draw.text((510, y), str(item["quantity"]), fill="black", font=font)
            draw.text((590, y), f"{item['unit_price']:.2f}", fill="black", font=font)
            draw.text((720, y), f"{item['total_price']:.2f}", fill="black", font=font)
            y += 40

        y += 20
        draw.line((40, y, 860, y), fill=(200, 200, 200), width=2)
        y += 25
        draw.text((590, y), "TOTAL", fill="black", font=font)
        draw.text((720, y), f"{invoice['total']:.2f} {invoice['currency']}", fill="black", font=font)
        y += 60

        draw.text((40, y), "Payment Details", fill=(2, 132, 199), font=font)
        y += 35
        draw.text((40, y), f"Bank: {user.bank_name or 'Not set'}", fill="black", font=font)
        y += 25
        draw.text((40, y), f"Account Name: {user.account_name or business_name}", fill="black", font=font)
        y += 25
        draw.text((40, y), f"Account Number: {user.account_number or 'Not set'}", fill="black", font=font)

        invoice_dir = Path("static") / "invoices"
        invoice_dir.mkdir(parents=True, exist_ok=True)
        filename = f"invoice-{order_id}-{uuid.uuid4()}.png"
        image_path = invoice_dir / filename
        image.save(image_path)

        public_base_url = settings.TELEGRAM_WEBHOOK_URL.split("/api/telegram/webhook")[0].rstrip("/")
        return f"{public_base_url}/static/invoices/{filename}"
    
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
                
                products_text += (
                    "What would you like to buy?\n"
                    "Reply like: **2 of product 1**, **add laptop**, or **show me image of product 1**."
                )
                
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
                    cart_text += "\nReply **yes** to receive your invoice, or tell me another product to add."
                    context = dict(conversation.context or {})
                    context["awaiting_final_confirmation"] = True
                    conversation.context = context
                    db.commit()
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
