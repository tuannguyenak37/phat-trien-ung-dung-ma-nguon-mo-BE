# app/controller/tag_controller.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from fastapi import HTTPException, status

from app.models.tags import Tags
from app.models.thread import Thread

class TagController:
    
    # 1. Thống kê Tag phổ biến (cho Admin Dashboard)
    async def get_popular_stats(self, db: AsyncSession, limit: int = 10):
        # Query: Join Tag và Thread, đếm số lượng thread_id
        query = (
            select(Tags, func.count(Thread.thread_id).label("use_count"))
            .join(Tags.threads) 
            .group_by(Tags.tag_id)
            .order_by(desc("use_count"))
            .limit(limit)
        )
        
        result = await db.execute(query)
        data = result.all()
        
        # Map dữ liệu sang format của Schema TagStatsResponse
        response = []
        for tag_obj, count in data:
            response.append({
                "tag": tag_obj,
                "count": count
            })
        return response

    # 2. Xóa Tag
    async def delete_tag(self, db: AsyncSession, tag_id: str):
        # Kiểm tra tag tồn tại
        query = select(Tags).where(Tags.tag_id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tag not found"
            )
        
        # Xóa tag (sẽ tự động xóa liên kết trong bảng thread_tags nhờ ondelete='CASCADE')
        await db.delete(tag)
        await db.commit()
        return {"message": "Tag deleted successfully"}

# Khởi tạo instance để dùng trong Router
tag_controller = TagController()