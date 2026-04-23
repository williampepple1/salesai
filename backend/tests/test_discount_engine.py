import pytest
from app.services.discount_engine import DiscountEngine
from app.models import Product, DiscountRule


def test_no_discount(db):
    """Test product with no discount rules"""
    product = Product(
        user_id=1,
        name="Test Product",
        price=100.00,
        stock_quantity=10
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    result = DiscountEngine.calculate_discount(product, 2, db)
    
    assert result["original_price"] == 200.00
    assert result["discount_applied"] == 0.0
    assert result["final_price"] == 200.00
    assert result["rule_name"] is None


def test_percentage_discount(db):
    """Test percentage-based discount"""
    product = Product(
        user_id=1,
        name="Test Product",
        price=100.00,
        stock_quantity=10
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Add discount rule: 10% off when buying 3 or more
    discount = DiscountRule(
        product_id=product.id,
        rule_name="10% off",
        discount_type="percentage",
        quantity_threshold=3,
        discount_value=10.0,
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    # Test with quantity below threshold
    result = DiscountEngine.calculate_discount(product, 2, db)
    assert result["discount_applied"] == 0.0
    
    # Test with quantity at threshold
    result = DiscountEngine.calculate_discount(product, 3, db)
    assert result["original_price"] == 300.00
    assert result["discount_applied"] == 30.00  # 10% of 300
    assert result["final_price"] == 270.00
    assert result["rule_name"] == "10% off"


def test_fixed_discount(db):
    """Test fixed amount discount"""
    product = Product(
        user_id=1,
        name="Test Product",
        price=50.00,
        stock_quantity=10
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Add discount rule: $20 off when buying 5 or more
    discount = DiscountRule(
        product_id=product.id,
        rule_name="$20 off",
        discount_type="fixed",
        quantity_threshold=5,
        discount_value=20.0,
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    result = DiscountEngine.calculate_discount(product, 5, db)
    assert result["original_price"] == 250.00
    assert result["discount_applied"] == 20.00
    assert result["final_price"] == 230.00


def test_buy_x_get_y_discount(db):
    """Test buy X get Y free discount"""
    product = Product(
        user_id=1,
        name="Test Product",
        price=10.00,
        stock_quantity=20
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Add discount rule: Buy 2 get 1 free
    discount = DiscountRule(
        product_id=product.id,
        rule_name="Buy 2 Get 1 Free",
        discount_type="buy_x_get_y",
        quantity_threshold=2,
        discount_value=0,
        free_quantity=1,
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    # Buy 2 items
    result = DiscountEngine.calculate_discount(product, 2, db)
    assert result["discount_applied"] == 10.00  # 1 free item worth $10
    assert result["effective_quantity"] == 3
    
    # Buy 4 items
    result = DiscountEngine.calculate_discount(product, 4, db)
    assert result["discount_applied"] == 20.00  # 2 free items
    assert result["effective_quantity"] == 6


def test_multiple_discount_rules(db):
    """Test selecting best discount from multiple rules"""
    product = Product(
        user_id=1,
        name="Test Product",
        price=100.00,
        stock_quantity=20
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Add multiple discount rules
    discount1 = DiscountRule(
        product_id=product.id,
        rule_name="5% off",
        discount_type="percentage",
        quantity_threshold=2,
        discount_value=5.0,
        is_active=True
    )
    discount2 = DiscountRule(
        product_id=product.id,
        rule_name="15% off",
        discount_type="percentage",
        quantity_threshold=5,
        discount_value=15.0,
        is_active=True
    )
    db.add(discount1)
    db.add(discount2)
    db.commit()
    
    # Buy 5 items - should apply the better 15% discount
    result = DiscountEngine.calculate_discount(product, 5, db)
    assert result["discount_applied"] == 75.00  # 15% of 500
    assert result["rule_name"] == "15% off"


def test_inactive_discount(db):
    """Test that inactive discounts are not applied"""
    product = Product(
        user_id=1,
        name="Test Product",
        price=100.00,
        stock_quantity=10
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Add inactive discount rule
    discount = DiscountRule(
        product_id=product.id,
        rule_name="Inactive",
        discount_type="percentage",
        quantity_threshold=2,
        discount_value=20.0,
        is_active=False
    )
    db.add(discount)
    db.commit()
    
    result = DiscountEngine.calculate_discount(product, 5, db)
    assert result["discount_applied"] == 0.0
