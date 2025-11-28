"""Temporary script to drop orphaned enum."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def drop_enum():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.exec_driver_sql('DROP TYPE IF EXISTS event_type_enum CASCADE')
    await engine.dispose()
    print("Dropped event_type_enum")


if __name__ == "__main__":
    asyncio.run(drop_enum())
