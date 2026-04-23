from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    telegram_chat_id = Column(String, nullable=False, index=True)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    messages = Column(JSON, default=[])  # List of message objects
    context = Column(JSON, default={})  # Conversation context (cart, preferences, etc.)
    status = Column(String, default="active")  # active, completed, abandoned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    seller = relationship("User", back_populates="conversations")
    orders = relationship("Order", back_populates="conversation")
