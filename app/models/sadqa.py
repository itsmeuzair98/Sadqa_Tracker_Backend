from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.db.database import Base


class SadqaType(PyEnum):
    MONEY = "MONEY"
    FOOD = "FOOD"
    CLOTHES = "CLOTHES"
    OTHER = "OTHER"


class SadqaEntry(Base):
    __tablename__ = "sadqa_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(SadqaType), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    reason = Column(String(500), nullable=True)
    received_by = Column(String(255), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    notes = Column(Text, nullable=True)  # Additional field for future use
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="sadqa_entries")
    
    def __repr__(self):
        return f"<SadqaEntry(id={self.id}, user_id={self.user_id}, type={self.type.value}, amount={self.amount})>"
