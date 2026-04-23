from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DiscountRuleCreate(BaseModel):
    product_id: int
    rule_name: str
    discount_type: str  # "percentage", "fixed", "buy_x_get_y"
    quantity_threshold: int
    discount_value: float
    free_quantity: int = 0
    is_active: bool = True


class DiscountRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    discount_type: Optional[str] = None
    quantity_threshold: Optional[int] = None
    discount_value: Optional[float] = None
    free_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class DiscountRuleResponse(BaseModel):
    id: int
    product_id: int
    rule_name: str
    discount_type: str
    quantity_threshold: int
    discount_value: float
    free_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
