from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import Product, DiscountRule


class DiscountEngine:
    """
    Handles discount calculation logic for products based on quantity thresholds
    and configured discount rules.
    """
    
    @staticmethod
    def calculate_discount(
        product: Product,
        quantity: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Calculate applicable discount for a product based on quantity.
        
        Args:
            product: Product model instance
            quantity: Quantity being purchased
            db: Database session
            
        Returns:
            Dictionary with discount details:
            {
                "original_price": float,
                "discount_applied": float,
                "discount_percentage": float,
                "final_price": float,
                "savings": float,
                "rule_name": str or None
            }
        """
        original_price = product.price * quantity
        
        # Get active discount rules for this product
        discount_rules = db.query(DiscountRule).filter(
            DiscountRule.product_id == product.id,
            DiscountRule.is_active == True
        ).order_by(DiscountRule.quantity_threshold.desc()).all()
        
        # Find the best applicable discount
        best_discount = None
        best_savings = 0.0
        
        for rule in discount_rules:
            if quantity >= rule.quantity_threshold:
                savings = DiscountEngine._calculate_rule_savings(
                    rule, product.price, quantity
                )
                if savings > best_savings:
                    best_savings = savings
                    best_discount = rule
        
        if best_discount:
            discount_info = DiscountEngine._apply_discount_rule(
                best_discount, product.price, quantity
            )
            return {
                "original_price": original_price,
                "discount_applied": discount_info["discount_amount"],
                "discount_percentage": discount_info["discount_percentage"],
                "final_price": original_price - discount_info["discount_amount"],
                "savings": discount_info["discount_amount"],
                "rule_name": best_discount.rule_name,
                "effective_quantity": discount_info.get("effective_quantity", quantity)
            }
        
        return {
            "original_price": original_price,
            "discount_applied": 0.0,
            "discount_percentage": 0.0,
            "final_price": original_price,
            "savings": 0.0,
            "rule_name": None,
            "effective_quantity": quantity
        }
    
    @staticmethod
    def _calculate_rule_savings(
        rule: DiscountRule,
        unit_price: float,
        quantity: int
    ) -> float:
        """Calculate savings for a specific discount rule."""
        if rule.discount_type == "percentage":
            return (unit_price * quantity) * (rule.discount_value / 100)
        elif rule.discount_type == "fixed":
            return rule.discount_value
        elif rule.discount_type == "buy_x_get_y":
            # Calculate how many free items
            sets = quantity // rule.quantity_threshold
            free_items = sets * rule.free_quantity
            return free_items * unit_price
        return 0.0
    
    @staticmethod
    def _apply_discount_rule(
        rule: DiscountRule,
        unit_price: float,
        quantity: int
    ) -> Dict[str, Any]:
        """Apply a discount rule and return detailed information."""
        if rule.discount_type == "percentage":
            discount_percentage = rule.discount_value
            discount_amount = (unit_price * quantity) * (discount_percentage / 100)
            return {
                "discount_amount": discount_amount,
                "discount_percentage": discount_percentage
            }
        
        elif rule.discount_type == "fixed":
            discount_amount = rule.discount_value
            discount_percentage = (discount_amount / (unit_price * quantity)) * 100
            return {
                "discount_amount": discount_amount,
                "discount_percentage": discount_percentage
            }
        
        elif rule.discount_type == "buy_x_get_y":
            sets = quantity // rule.quantity_threshold
            free_items = sets * rule.free_quantity
            discount_amount = free_items * unit_price
            effective_quantity = quantity + free_items
            discount_percentage = (discount_amount / (unit_price * quantity)) * 100
            return {
                "discount_amount": discount_amount,
                "discount_percentage": discount_percentage,
                "effective_quantity": effective_quantity,
                "free_items": free_items
            }
        
        return {
            "discount_amount": 0.0,
            "discount_percentage": 0.0
        }
    
    @staticmethod
    def calculate_cart_total(
        items: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """
        Calculate total for a cart with multiple items.
        
        Args:
            items: List of dicts with {product_id, quantity}
            db: Database session
            
        Returns:
            Dictionary with cart totals and itemized discounts
        """
        cart_items = []
        subtotal = 0.0
        total_discount = 0.0
        final_total = 0.0
        
        for item in items:
            product = db.query(Product).filter(
                Product.id == item["product_id"]
            ).first()
            
            if not product:
                continue
            
            discount_info = DiscountEngine.calculate_discount(
                product, item["quantity"], db
            )
            
            cart_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item["quantity"],
                "unit_price": product.price,
                "original_price": discount_info["original_price"],
                "discount_applied": discount_info["discount_applied"],
                "final_price": discount_info["final_price"],
                "rule_name": discount_info["rule_name"]
            })
            
            subtotal += discount_info["original_price"]
            total_discount += discount_info["discount_applied"]
            final_total += discount_info["final_price"]
        
        return {
            "items": cart_items,
            "subtotal": subtotal,
            "total_discount": total_discount,
            "final_total": final_total,
            "savings_percentage": (total_discount / subtotal * 100) if subtotal > 0 else 0
        }
