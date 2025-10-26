from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from calendar import monthrange

from app.db.database import get_db
from app.auth.auth_dependencies import get_current_active_user
from app.models.user import User
from app.models.sadqa import SadqaEntry, SadqaType
from app.schemas.sadqa import (
    SadqaEntry as SadqaEntrySchema,
    SadqaEntryCreate,
    SadqaEntryUpdate,
    SadqaStats,
    DateRangeFilter
)

router = APIRouter()

@router.post("/", response_model=SadqaEntrySchema)
async def create_sadqa_entry(
    sadqa_data: SadqaEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new sadqa entry"""
    sadqa_entry = SadqaEntry(
        user_id=current_user.id,
        type=sadqa_data.type,
        amount=sadqa_data.amount,
        reason=sadqa_data.reason,
        received_by=sadqa_data.received_by,
        date=sadqa_data.date,
        notes=sadqa_data.notes
    )
    
    db.add(sadqa_entry)
    await db.commit()
    await db.refresh(sadqa_entry)
    
    return sadqa_entry

@router.get("/", response_model=List[SadqaEntrySchema])
async def get_sadqa_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    type_filter: Optional[SadqaType] = None,
    min_amount: Optional[float] = Query(None, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sadqa entries with filtering"""
    query = select(SadqaEntry).where(SadqaEntry.user_id == current_user.id)
    
    # Apply filters
    if start_date:
        query = query.where(SadqaEntry.date >= start_date)
    if end_date:
        query = query.where(SadqaEntry.date <= end_date)
    if type_filter:
        query = query.where(SadqaEntry.type == type_filter)
    if min_amount is not None:
        query = query.where(SadqaEntry.amount >= min_amount)
    
    # Order by date (most recent first)
    query = query.order_by(desc(SadqaEntry.date))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/recent", response_model=List[SadqaEntrySchema])
async def get_recent_sadqa_entries(
    limit: int = Query(3, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent sadqa entries"""
    query = select(SadqaEntry).where(
        SadqaEntry.user_id == current_user.id
    ).order_by(desc(SadqaEntry.date)).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/stats", response_model=SadqaStats)
async def get_sadqa_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sadqa statistics for the user"""
    # Total amount and entries
    total_result = await db.execute(
        select(
            func.coalesce(func.sum(SadqaEntry.amount), 0),
            func.count(SadqaEntry.id)
        ).where(SadqaEntry.user_id == current_user.id)
    )
    total_amount, total_entries = total_result.one()
    
    # Current month statistics
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    month_end = datetime(now.year, now.month, monthrange(now.year, now.month)[1], 23, 59, 59)
    
    monthly_result = await db.execute(
        select(
            func.coalesce(func.sum(SadqaEntry.amount), 0),
            func.count(SadqaEntry.id)
        ).where(
            and_(
                SadqaEntry.user_id == current_user.id,
                SadqaEntry.date >= month_start,
                SadqaEntry.date <= month_end
            )
        )
    )
    monthly_amount, monthly_entries = monthly_result.one()
    
    # Most frequent type
    type_counts_result = await db.execute(
        select(
            SadqaEntry.type,
            func.count(SadqaEntry.id).label('count')
        ).where(
            SadqaEntry.user_id == current_user.id
        ).group_by(SadqaEntry.type).order_by(desc('count'))
    )
    
    type_counts = {row.type.value: row.count for row in type_counts_result}
    most_frequent_type = list(type_counts.keys())[0] if type_counts else None
    
    return SadqaStats(
        total_amount=float(total_amount),
        total_entries=total_entries,
        monthly_amount=float(monthly_amount),
        monthly_entries=monthly_entries,
        most_frequent_type=most_frequent_type,
        types_count=type_counts
    )

@router.get("/{sadqa_id}", response_model=SadqaEntrySchema)
async def get_sadqa_entry(
    sadqa_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific sadqa entry"""
    result = await db.execute(
        select(SadqaEntry).where(
            and_(
                SadqaEntry.id == sadqa_id,
                SadqaEntry.user_id == current_user.id
            )
        )
    )
    sadqa_entry = result.scalar_one_or_none()
    
    if not sadqa_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sadqa entry not found"
        )
    
    return sadqa_entry

@router.put("/{sadqa_id}", response_model=SadqaEntrySchema)
async def update_sadqa_entry(
    sadqa_id: int,
    sadqa_update: SadqaEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a sadqa entry"""
    result = await db.execute(
        select(SadqaEntry).where(
            and_(
                SadqaEntry.id == sadqa_id,
                SadqaEntry.user_id == current_user.id
            )
        )
    )
    sadqa_entry = result.scalar_one_or_none()
    
    if not sadqa_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sadqa entry not found"
        )
    
    # Update fields
    update_data = sadqa_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sadqa_entry, field, value)
    
    await db.commit()
    await db.refresh(sadqa_entry)
    
    return sadqa_entry

@router.delete("/{sadqa_id}")
async def delete_sadqa_entry(
    sadqa_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a sadqa entry"""
    result = await db.execute(
        select(SadqaEntry).where(
            and_(
                SadqaEntry.id == sadqa_id,
                SadqaEntry.user_id == current_user.id
            )
        )
    )
    sadqa_entry = result.scalar_one_or_none()
    
    if not sadqa_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sadqa entry not found"
        )
    
    await db.delete(sadqa_entry)
    await db.commit()
    
    return {"message": "Sadqa entry deleted successfully"}
