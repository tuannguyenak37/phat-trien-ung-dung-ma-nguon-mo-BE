from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.tags import Tags
from app.models.thread import Thread

class TagService:
    @staticmethod
    async def get_popular(db: AsyncSession, limit: int = 10):
        # Query: Tags được sử dụng nhiều nhất
        query = (
            select(Tags)
            .join(Tags.threads)
            .group_by(Tags.tag_id)
            .order_by(desc(func.count(Thread.thread_id)))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()