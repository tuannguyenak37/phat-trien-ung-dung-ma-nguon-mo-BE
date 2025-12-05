from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import Users
import logging

# Cấu hình log để dễ debug thay vì print
logger = logging.getLogger(__name__)

async def update_reputation(db: AsyncSession, user_id: str, amount: int) -> bool:
    """
    Cập nhật điểm uy tín (reputation_score) cho user (Async).
    
    Args:
        db (AsyncSession): Database session (Async)
        user_id (str): ID của user
        amount (int): Số điểm cần cộng (dương) hoặc trừ (âm)
        
    Returns:
        bool: True nếu thành công, False nếu lỗi
    """
    try:
        # 1. Tạo câu lệnh UPDATE chuẩn SQLAlchemy 2.0
        # UPDATE users SET reputation_score = reputation_score + :amount WHERE user_id = :user_id
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(reputation_score=Users.reputation_score + amount)
            .execution_options(synchronize_session=False) # Tối ưu hiệu năng
        )
        
        # 2. Thực thi (Async)
        result = await db.execute(stmt)
        
        # 3. Kiểm tra xem có dòng nào được update không
        if result.rowcount > 0:
            # Lưu ý: Thường thì Service gọi hàm này sẽ lo việc commit cuối cùng.
            # Nhưng nếu bạn muốn hàm này tự commit luôn thì để dòng này:
            # await db.commit() 
            return True
        
        return False

    except Exception as e:
        # await db.rollback() # Chỉ rollback nếu hàm này quản lý transaction
        logger.error(f"Error updating reputation for user {user_id}: {e}")
        return False