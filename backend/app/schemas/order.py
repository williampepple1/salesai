from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class OrderItem(BaseModel):
    product_id: int
    name: str
    quantity: int
    unit_price: float
    discount_applied: float = 0.0
    total_price: float


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    items: List[OrderItem]
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    customer_name: str
    customer_phone: Optional[str]
    customer_address: Optional[str]
    items: List[Dict[str, Any]]
    subtotal: float
    discount_amount: float
    total_amount: float
    currency: str
    status: str
    invoice_url: Optional[str] = None
    receipt_url: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
