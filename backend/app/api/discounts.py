from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Product, DiscountRule
from ..schemas.discount_rule import DiscountRuleCreate, DiscountRuleUpdate, DiscountRuleResponse
from ..clerk_auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=DiscountRuleResponse, status_code=status.HTTP_201_CREATED)
def create_discount_rule(
    rule_data: DiscountRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new discount rule."""
    # Verify product belongs to user
    product = db.query(Product).filter(
        Product.id == rule_data.product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    rule = DiscountRule(**rule_data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.get("/product/{product_id}", response_model=List[DiscountRuleResponse])
def get_product_discounts(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all discount rules for a product."""
    # Verify product belongs to user
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    rules = db.query(DiscountRule).filter(
        DiscountRule.product_id == product_id
    ).all()
    
    return rules


@router.put("/{rule_id}", response_model=DiscountRuleResponse)
def update_discount_rule(
    rule_id: int,
    rule_data: DiscountRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a discount rule."""
    rule = db.query(DiscountRule).join(Product).filter(
        DiscountRule.id == rule_id,
        Product.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount rule not found"
        )
    
    for field, value in rule_data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discount_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a discount rule."""
    rule = db.query(DiscountRule).join(Product).filter(
        DiscountRule.id == rule_id,
        Product.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount rule not found"
        )
    
    db.delete(rule)
    db.commit()
    
    return None
