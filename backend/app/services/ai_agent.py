from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
import json
from ..models import User, Product, Conversation, Order
from ..config import settings
from .discount_engine import DiscountEngine


class AIAgent:
    """
    AI Sales Agent powered by OpenAI GPT-4 with function calling.
    Handles customer conversations, product queries, and order processing.
    
    IMPORTANT GUARDRAILS:
    This agent is designed to ONLY discuss products from the seller's catalog.
    It includes multiple layers of protection to prevent off-topic conversations:
    
    1. System Prompt: Explicitly instructs the AI to stay focused on catalog products
    2. Response Validation: Checks every response for off-topic content
    3. Fallback Responses: Replaces off-topic responses with product-focused redirects
    4. Keyword Detection: Monitors for common off-topic keywords
    5. Temperature Control: Uses lower temperature (0.7) for more focused responses
    6. Token Limits: Restricts response length to keep conversations concise
    
    The agent will politely decline and redirect any attempts to:
    - Discuss products not in the catalog
    - Engage in general conversation (politics, news, sports, etc.)
    - Provide advice on non-product topics
    - Compare to competitors
    
    This ensures sellers can trust the agent to maintain professional,
    on-brand conversations focused exclusively on their products.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Off-topic keywords that should trigger a warning
        self.off_topic_keywords = [
            "politics", "religion", "news", "weather", "sports", "movie", "music",
            "celebrity", "game", "recipe", "health advice", "legal advice", 
            "financial advice", "medical", "diagnosis", "prescription"
        ]
    
    def generate_system_prompt(self, user: User, products: List[Product]) -> str:
        """Generate a personalized system prompt for the sales agent."""
        business_name = user.business_name or user.username
        
        product_list = "\n".join([
            f"- ID {p.id}: {p.name} - ${p.price} {p.currency} - {p.description or 'No description'} "
            f"(Stock: {p.stock_quantity}, Available: {p.is_available})"
            for p in products
        ])
        
        if not products:
            product_list = "No products available at the moment."
        
        system_prompt = f"""You are an AI sales assistant EXCLUSIVELY for {business_name}.

**CRITICAL BOUNDARIES - YOU MUST FOLLOW THESE RULES:**
1. ONLY discuss products from the catalog below
2. NEVER discuss topics unrelated to these specific products
3. DECLINE politely if asked about anything outside the product catalog
4. DO NOT engage in general conversation, politics, news, or other topics
5. DO NOT provide information about products not in your catalog
6. If a customer asks about something not in the catalog, politely say you can only help with the products listed

**YOUR EXCLUSIVE PRODUCT CATALOG:**
{product_list}

**WHAT YOU CAN DO:**
- Show details ONLY for products in the catalog above
- Calculate prices and discounts for these products
- Add catalog products to cart
- Process orders for catalog products
- Answer questions ONLY about the products listed above

**WHAT YOU CANNOT DO:**
- Discuss products not in your catalog
- Provide general knowledge or information
- Engage in conversations about topics other than your products
- Compare your products to other brands or stores
- Give advice on topics unrelated to your specific products

**HANDLING OFF-TOPIC REQUESTS:**
If a customer asks about anything not related to the products in your catalog, respond with:
"I'm here specifically to help you with {business_name}'s products. I can only provide information about: {', '.join([p.name for p in products[:3]])}{'...' if len(products) > 3 else ''}. Is there anything about these products I can help you with?"

**SALES PROCESS:**
1. Help customers find products from YOUR CATALOG ONLY
2. Show product details and images
3. Calculate prices with applicable discounts
4. Add items to cart
5. Collect customer information (name, phone, address)
6. Create and confirm orders

**RESPONSE STYLE:**
- Be friendly, professional, and helpful
- Keep responses concise and focused on your products
- Always redirect off-topic conversations back to your products
- Be enthusiastic about YOUR products specifically
- Never pretend to have products you don't have

Remember: You are a specialized sales agent for {business_name} ONLY. Stay focused on your specific product catalog at all times.
"""
        return system_prompt
    
    def _is_response_on_topic(self, response: str, products: List[Product]) -> bool:
        """
        Check if the response is focused on the catalog products.
        Returns True if on-topic, False otherwise.
        """
        if not response:
            return True
        
        response_lower = response.lower()
        
        # Check for off-topic keywords
        for keyword in self.off_topic_keywords:
            if keyword in response_lower:
                return False
        
        # If response is very short (greeting/acknowledgment), it's okay
        if len(response.split()) < 15:
            return True
        
        # Check if response mentions at least one product name or "product" related terms
        product_related_terms = ["product", "price", "order", "cart", "buy", "purchase", "available", "stock"]
        product_names = [p.name.lower() for p in products]
        
        has_product_context = any(
            term in response_lower for term in product_related_terms
        ) or any(
            name in response_lower for name in product_names
        )
        
        return has_product_context
    
    def _get_fallback_response(self, business_name: str, products: List[Product]) -> str:
        """Generate a fallback response when AI goes off-topic."""
        if not products:
            return f"I'm here to help you with {business_name}'s products. Unfortunately, there are no products available right now. Please check back later!"
        
        product_names = ", ".join([p.name for p in products[:3]])
        more_text = "and more" if len(products) > 3 else ""
        
        return (
            f"I'm here specifically to help you with {business_name}'s products. "
            f"I can assist you with: {product_names} {more_text}. "
            f"What would you like to know about our products?"
        )
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Define available functions for the AI agent."""
        return [
            {
                "name": "get_product_details",
                "description": "Get detailed information about a specific product including price and availability",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "The ID of the product"
                        }
                    },
                    "required": ["product_id"]
                }
            },
            {
                "name": "calculate_price",
                "description": "Calculate the final price for a product with quantity and applicable discounts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "The ID of the product"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity to purchase"
                        }
                    },
                    "required": ["product_id", "quantity"]
                }
            },
            {
                "name": "add_to_cart",
                "description": "Add a product to the customer's cart",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "The ID of the product"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity to add"
                        }
                    },
                    "required": ["product_id", "quantity"]
                }
            },
            {
                "name": "create_order",
                "description": "Create an order with customer information and cart items",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Customer's full name"
                        },
                        "customer_phone": {
                            "type": "string",
                            "description": "Customer's phone number"
                        },
                        "customer_address": {
                            "type": "string",
                            "description": "Customer's shipping address"
                        }
                    },
                    "required": ["customer_name"]
                }
            }
        ]
    
    async def process_message(
        self,
        message: str,
        conversation_id: int,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Process a customer message and generate a response.
        
        Args:
            message: Customer's message
            conversation_id: Conversation ID
            user_id: Seller's user ID
            db: Database session
            
        Returns:
            Dictionary with response text and any actions taken
        """
        # Get conversation and user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        # Get products
        products = db.query(Product).filter(
            Product.user_id == user_id,
            Product.is_available == True
        ).all()
        
        # Build conversation history
        messages = [
            {"role": "system", "content": self.generate_system_prompt(user, products)}
        ]
        
        # Add previous messages from conversation
        if conversation and conversation.messages:
            for msg in conversation.messages[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI API with temperature to reduce randomness
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            functions=self.get_function_definitions(),
            function_call="auto",
            temperature=0.7,  # Lower temperature for more focused responses
            max_tokens=500  # Limit response length
        )
        
        response_message = response.choices[0].message
        
        # Handle function calls
        if response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            
            function_response = await self._execute_function(
                function_name,
                function_args,
                conversation,
                user_id,
                db
            )
            
            # Call OpenAI again with function response
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": response_message.function_call.arguments
                }
            })
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_response)
            })
            
            second_response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            final_response = second_response.choices[0].message.content
        else:
            final_response = response_message.content
        
        # Validate response is on-topic
        if not self._is_response_on_topic(final_response, products):
            final_response = self._get_fallback_response(user.business_name or user.username, products)
        
        # Update conversation
        if conversation:
            conversation.messages.append({
                "role": "user",
                "content": message
            })
            conversation.messages.append({
                "role": "assistant",
                "content": final_response
            })
            db.commit()
        
        return {
            "response": final_response,
            "conversation_id": conversation_id
        }
    
    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        conversation: Conversation,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Execute a function called by the AI agent."""
        
        if function_name == "get_product_details":
            product = db.query(Product).filter(
                Product.id == arguments["product_id"],
                Product.user_id == user_id
            ).first()
            
            if product:
                return {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "currency": product.currency,
                    "stock": product.stock_quantity,
                    "available": product.is_available,
                    "image_urls": product.image_urls
                }
            return {"error": "Product not found"}
        
        elif function_name == "calculate_price":
            product = db.query(Product).filter(
                Product.id == arguments["product_id"],
                Product.user_id == user_id
            ).first()
            
            if product:
                discount_info = DiscountEngine.calculate_discount(
                    product,
                    arguments["quantity"],
                    db
                )
                return discount_info
            return {"error": "Product not found"}
        
        elif function_name == "add_to_cart":
            # Update conversation context with cart
            if not conversation.context:
                conversation.context = {}
            
            if "cart" not in conversation.context:
                conversation.context["cart"] = []
            
            # Add or update cart item
            cart = conversation.context["cart"]
            product_id = arguments["product_id"]
            quantity = arguments["quantity"]
            
            # Check if item already in cart
            existing_item = next((item for item in cart if item["product_id"] == product_id), None)
            
            if existing_item:
                existing_item["quantity"] += quantity
            else:
                cart.append({
                    "product_id": product_id,
                    "quantity": quantity
                })
            
            db.commit()
            return {"success": True, "cart": cart}
        
        elif function_name == "create_order":
            # Create order from cart
            if not conversation.context or "cart" not in conversation.context:
                return {"error": "Cart is empty"}
            
            cart_items = conversation.context["cart"]
            cart_total = DiscountEngine.calculate_cart_total(cart_items, db)
            
            order = Order(
                user_id=user_id,
                conversation_id=conversation.id,
                customer_name=arguments["customer_name"],
                customer_phone=arguments.get("customer_phone"),
                customer_address=arguments.get("customer_address"),
                items=cart_total["items"],
                subtotal=cart_total["subtotal"],
                discount_amount=cart_total["total_discount"],
                total_amount=cart_total["final_total"],
                status="pending"
            )
            
            db.add(order)
            
            # Clear cart
            conversation.context["cart"] = []
            db.commit()
            
            return {
                "success": True,
                "order_id": order.id,
                "total": cart_total["final_total"],
                "discount": cart_total["total_discount"]
            }
        
        return {"error": "Unknown function"}
