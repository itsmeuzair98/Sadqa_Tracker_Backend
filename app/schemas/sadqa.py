from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class SadqaType(str, Enum):
    MONEY = "MONEY"
    FOOD = "FOOD"
    CLOTHES = "CLOTHES"
    OTHER = "OTHER"


class SadqaEntryBase(BaseModel):
    type: SadqaType
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    reason: Optional[str] = Field(None, max_length=500)
    received_by: str = Field(..., max_length=255, min_length=1)
    date: datetime
    notes: Optional[str] = None


class SadqaEntryCreate(SadqaEntryBase):
    """Schema for creating a new sadqa entry"""
    pass


class SadqaEntryUpdate(BaseModel):
    """Schema for updating an existing sadqa entry"""
    type: Optional[SadqaType] = None
    amount: Optional[float] = Field(None, gt=0)
    reason: Optional[str] = Field(None, max_length=500)
    received_by: Optional[str] = Field(None, max_length=255, min_length=1)
    date: Optional[datetime] = None
    notes: Optional[str] = None


class SadqaEntryInDBBase(SadqaEntryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SadqaEntry(SadqaEntryInDBBase):
    """Schema for returning sadqa entries"""
    pass


class SadqaEntryInDB(SadqaEntryInDBBase):
    """Schema for internal use"""
    pass


# Statistics schemas
class SadqaStats(BaseModel):
    total_amount: float
    total_entries: int
    monthly_amount: float
    monthly_entries: int
    most_frequent_type: Optional[str] = None
    types_count: dict[str, int] = {}


class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    type_filter: Optional[SadqaType] = None
    min_amount: Optional[float] = Field(None, ge=0)
