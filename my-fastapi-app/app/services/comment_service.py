from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from app.models.comment import Comment
from app.models.thread import Thread
from app.schemas.comment import CommentCreateForm, CommentUpdateForm

class CommentService:
    
    # --- 1. TẠO COMMENT & TĂNG COUNTER ---
    @staticmethod
    async def create_comment(db: Session, user_id: str, form_data: CommentCreateForm):
        # Kiểm tra bài viết
        thread = db.query(Thread).filter(Thread.thread_id == form_data.thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Kiểm tra cha (nếu là reply)
        parent_comment = None
        if form_data.parent_comment_id:
            parent_comment = db.query(Comment).filter(Comment.comment_id == form_data.parent_comment_id).first()
            if not parent_comment:
                raise HTTPException(status_code=404, detail="Parent comment not found")

        # Tạo comment
        new_comment = Comment(
            user_id=user_id,
            thread_id=form_data.thread_id,
            parent_comment_id=form_data.parent_comment_id,
            content=form_data.content
        )
        db.add(new_comment)
        
        # --- CẬP NHẬT COUNTER ---
        # 1. Tăng tổng comment của Thread
        thread.comment_count += 1
        
        # 2. Nếu là Reply, tăng reply_count của Comment Cha
        if parent_comment:
            parent_comment.reply_count += 1

        db.commit()
        db.refresh(new_comment)
        return new_comment

    # --- 2. LẤY DANH SÁCH (SỬA LỖI FILTER NONE) ---
    @staticmethod
    async def get_comments(
        db: Session, 
        thread_id: str = None, 
        parent_comment_id: str = None, 
        skip: int = 0, 
        limit: int = 10
    ):
        query = db.query(Comment)

        # TRƯỜNG HỢP A: Lấy Reply của một comment
        if parent_comment_id:
            query = query.filter(Comment.parent_comment_id == parent_comment_id)
            
        # TRƯỜNG HỢP B: Lấy Comment gốc của bài viết
        elif thread_id:
            # 👇 QUAN TRỌNG: Dùng .is_(None) để lọc đúng chuẩn SQL
            query = query.filter(
                Comment.thread_id == thread_id,
                Comment.parent_comment_id.is_(None) 
            )
        else:
            return {"total": 0, "data": []}

        # Sắp xếp: Nhiều Tim nhất -> Mới nhất
        query = query.order_by(desc(Comment.upvote_count), desc(Comment.created_at))

        total = query.count()
        comments = query.offset(skip).limit(limit).all()

        return {
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "data": comments
        }

    # --- 3. SỬA COMMENT ---
    @staticmethod
    async def update_comment(db: Session, comment_id: str, user_id: str, form_data: CommentUpdateForm):
        comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit")

        comment.content = form_data.content
        # updated_at tự động nhảy nhờ onupdate trong Model
        
        db.commit()
        db.refresh(comment)
        return comment

    # --- 4. XÓA COMMENT & GIẢM COUNTER ---
    @staticmethod
    async def delete_comment(db: Session, comment_id: str, user_id: str, role: str):
        comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if comment.user_id != user_id and role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete")

        # --- GIẢM COUNTER ---
        # 1. Giảm tổng comment của Thread
        thread = db.query(Thread).get(comment.thread_id)
        if thread and thread.comment_count > 0:
            thread.comment_count -= 1
            
        # 2. Nếu là Reply, giảm reply_count của Cha
        if comment.parent_comment_id:
            parent = db.query(Comment).get(comment.parent_comment_id)
            if parent and parent.reply_count > 0:
                parent.reply_count -= 1

        db.delete(comment)
        db.commit()
        return {"message": "Deleted successfully"}