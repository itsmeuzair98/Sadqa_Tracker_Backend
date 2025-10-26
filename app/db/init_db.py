from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import engine, Base
from app.models.user import User
from app.models.sadqa import SadqaEntry


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")
