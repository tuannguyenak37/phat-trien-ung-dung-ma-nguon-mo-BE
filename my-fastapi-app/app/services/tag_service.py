from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.tags import Tags
from app.models.thread import Thread

class TagService:
    @staticmethod
    async def get_popular(db: AsyncSession, limit: int = 10):
        # 1. Query lấy Tag và đếm số bài viết
        query = (
            select(Tags, func.count(Thread.thread_id).label("thread_count"))
            .join(Tags.threads)
            .group_by(Tags.tag_id)
            .order_by(desc("thread_count"))
            .limit(limit)
        )
        
        result = await db.execute(query)
        
        # 2. Xử lý làm phẳng (Flatten) dữ liệu tại đây
        # row[0] là object Tags, row[1] là số lượng (int)
        flat_data = []
        for row in result:
            tag_obj = row[0]     # Lấy object Tag
            count_val = row[1]   # Lấy số lượng
            
            flat_data.append({
                "tag_id": tag_obj.tag_id,  # Lấy id
                "name": tag_obj.name,      # Lấy name
                "count": count_val         # Thêm field count vào cùng cấp
            })
            
        return flat_data

    # 2. Xóa Tag
    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: str):
        # Tìm tag xem có tồn tại không
        query = select(Tags).where(Tags.tag_id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            return False 
        
    
        await db.delete(tag)
        await db.commit()
        return True