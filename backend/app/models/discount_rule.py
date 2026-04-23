from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class DiscountRule(Base):
    __tablename__ = "discount_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rule_name = Column(String, nullable=False)
    discount_type = Column(String, nullable=False)  # "percentage", "fixed", "buy_x_get_y"
    quantity_threshold = Column(Integer, nullable=False)  # Minimum quantity to trigger discount
    discount_value = Column(Float, nullable=False)  # Percentage (0-100) or fixed amount
    free_quantity = Column(Integer, default=0)  # For buy_x_get_y rules
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="discount_rules")
