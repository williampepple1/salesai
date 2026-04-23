from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "USD"
    image_urls: List[str] = []
    stock_quantity: int = 0
    is_available: bool = True
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    image_urls: Optional[List[str]] = None
    stock_quantity: Optional[int] = None
    is_available: Optional[bool] = None
    category: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    price: float
    currency: str
    image_urls: List[str]
    stock_quantity: int
    is_available: bool
    category: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
