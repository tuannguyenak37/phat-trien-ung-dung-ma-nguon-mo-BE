from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

from app.models.comment import Comment
from app.models.thread import Thread
from app.schemas.comment import CommentCreateForm, CommentUpdateForm
from app.utils.reputation_score import update_reputation

class CommentService:
    
    # --- 1. TẠO COMMENT & TĂNG COUNTER ---
    @staticmethod
    async def create_comment(db: AsyncSession, user_id: str, form_data: CommentCreateForm):
        # 1. Kiểm tra bài viết
        # Dùng await db.get() là cách nhanh nhất để lấy theo ID
        thread = await db.get(Thread, form_data.thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # 2. Kiểm tra cha (nếu là reply)
        parent_comment = None
        if form_data.parent_comment_id:
            parent_comment = await db.get(Comment, form_data.parent_comment_id)
            if not parent_comment:
                raise HTTPException(status_code=404, detail="Parent comment not found")

        # 3. Tạo comment
        new_comment = Comment(
            user_id=user_id,
            thread_id=form_data.thread_id,
            parent_comment_id=form_data.parent_comment_id,
            content=form_data.content
        )
        
        # Tăng điểm uy tín
        await update_reputation(db=db, user_id=user_id, amount=3)
        
        db.add(new_comment)
        
        # --- CẬP NHẬT COUNTER ---
        # 4. Tăng tổng comment của Thread
        thread.comment_count += 1
        
        # 5. Nếu là Reply, tăng reply_count của Comment Cha
        if parent_comment:
            parent_comment.reply_count += 1

        await db.commit()
        await db.refresh(new_comment)
        
        # Load thêm User để trả về API (tránh lỗi MissingGreenlet)
        # Query lại comment vừa tạo kèm theo User info
        query = select(Comment).options(joinedload(Comment.user)).filter(Comment.comment_id == new_comment.comment_id)
        result = await db.execute(query)
        
        return result.scalar_one()

    # --- 2. LẤY DANH SÁCH ---
    @staticmethod
    async def get_comments(
        db: AsyncSession, 
        thread_id: str = None, 
        parent_comment_id: str = None, 
        skip: int = 0, 
        limit: int = 10
    ):
        # Tạo câu query cơ bản
        query = select(Comment).options(joinedload(Comment.user)) # Load User info

        # TRƯỜNG HỢP A: Lấy Reply
        if parent_comment_id:
            query = query.filter(Comment.parent_comment_id == parent_comment_id)
            
            # Để đếm tổng số (cho phân trang), ta cần query riêng
            count_stmt = select(func.count()).select_from(Comment).filter(Comment.parent_comment_id == parent_comment_id)

        # TRƯỜNG HỢP B: Lấy Comment gốc
        elif thread_id:
            query = query.filter(
                Comment.thread_id == thread_id,
                Comment.parent_comment_id.is_(None) 
            )
            count_stmt = select(func.count()).select_from(Comment).filter(
                Comment.thread_id == thread_id,
                Comment.parent_comment_id.is_(None) 
            )
        else:
            return {"total": 0, "data": []}

        # 1. Thực thi đếm tổng số trước
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        # 2. Thực thi lấy dữ liệu (Sắp xếp & Phân trang)
        query = query.order_by(desc(Comment.upvote_count), desc(Comment.created_at))
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        comments = result.scalars().all()

        return {
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "data": comments
        }

    # --- 3. SỬA COMMENT ---
    @staticmethod
    async def update_comment(db: AsyncSession, comment_id: str, user_id: str, form_data: CommentUpdateForm):
        # Tìm comment
        query = select(Comment).filter(Comment.comment_id == comment_id)
        result = await db.execute(query)
        comment = result.scalar_one_or_none()
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit")

        # Cập nhật
        comment.content = form_data.content
        
        await db.commit()
        await db.refresh(comment)
        
        # Load lại user để trả về
        query_full = select(Comment).options(joinedload(Comment.user)).filter(Comment.comment_id == comment_id)
        return (await db.execute(query_full)).scalar_one()

    # --- 4. XÓA COMMENT & GIẢM COUNTER ---
    @staticmethod
    async def delete_comment(db: AsyncSession, comment_id: str, user_id: str, role: str):
        # Tìm comment
        comment = await db.get(Comment, comment_id)
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if comment.user_id != user_id and role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete")

        # --- GIẢM COUNTER ---
        # 1. Giảm tổng comment của Thread
        thread = await db.get(Thread, comment.thread_id)
        if thread and thread.comment_count > 0:
            thread.comment_count -= 1
            
        # 2. Nếu là Reply, giảm reply_count của Cha
        if comment.parent_comment_id:
            parent = await db.get(Comment, comment.parent_comment_id)
            if parent and parent.reply_count > 0:
                parent.reply_count -= 1

        await db.delete(comment)
        await db.commit()
        return {"message": "Deleted successfully"}