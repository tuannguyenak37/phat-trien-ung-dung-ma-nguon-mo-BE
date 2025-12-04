from sqlalchemy import update
from sqlalchemy.orm import Session
from app.models.users import Users
async def update_reputation(db: Session, user_id: str, amount: int) -> bool:
    """
    Cập nhật điểm uy tín (reputation_score) cho user một cách an toàn (Atomic Update).
    
    Args:
        db (Session): Database session
        user_id (str): ID của user cần cập nhật
        amount (int): Số điểm cần tăng (dương) hoặc giảm (âm)
        
    Returns:
        bool: True nếu cập nhật thành công, False nếu user không tồn tại hoặc lỗi
    """
    try:
        # Sử dụng update trực tiếp ở cấp độ Database để tránh Race Condition
        # synchronize_session=False: Tối ưu hiệu năng vì không cần cập nhật lại các object trong session hiện tại
        rows_affected = db.query(Users).filter(Users.user_id == user_id).update(
            {Users.reputation_score: Users.reputation_score + amount},
            synchronize_session=False
        )
        
        # Lưu thay đổi
        db.commit()
        
        # Nếu rows_affected > 0 nghĩa là tìm thấy user và đã update
        return rows_affected > 0

    except Exception as e:
        db.rollback()
        # Có thể log lỗi ra file log hoặc console
        print(f"Error updating reputation for user {user_id}: {e}")
        return False