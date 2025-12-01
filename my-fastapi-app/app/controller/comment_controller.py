from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.services.comment_service import CommentService
from app.services.vote_service import VoteService # Cần import cái này
from app.schemas.comment import CommentCreateForm, CommentUpdateForm

class CommentController:
    def __init__(self):
        self.service = CommentService()

    # CREATE
    async def create_comment(self, db: Session, form_data: CommentCreateForm, current_user: dict):
        user_id = current_user.get("user_id")
        if not user_id:
             raise HTTPException(status_code=401, detail="Unauthorized")
             
        return await self.service.create_comment(db, user_id, form_data)

    # GET LIST (Có gắn Vote Stats)
    async def get_list_comments(
        self, db: Session, 
        thread_id: str = None, 
        parent_comment_id: str = None,
        page: int = 1, 
        limit: int = 10,
        current_user_id: Optional[str] = None
    ):
        skip = (page - 1) * limit
        
        # 1. Lấy danh sách từ Service
        result = await self.service.get_comments(
            db=db, thread_id=thread_id, parent_comment_id=parent_comment_id, skip=skip, limit=limit
        )
        
        comments_list = result.get("data", [])

        # 2. Gắn thông tin Vote (User đã like comment này chưa?)
        vote_service = VoteService(db)
        
        if current_user_id:
            for cmt in comments_list:
                # Check trạng thái vote của user với từng comment
                user_vote = vote_service.check_user_vote_status(
                    user_id=current_user_id, 
                    comment_id=cmt.comment_id
                )
                cmt.vote_stats = user_vote
        else:
            # Khách vãng lai
            for cmt in comments_list:
                cmt.vote_stats = {"is_voted": 0}

        return result

    # UPDATE
    async def update_comment(self, db: Session, comment_id: str, form_data: CommentUpdateForm, current_user: dict):
        user_id = current_user.get("user_id")
        return await self.service.update_comment(db, comment_id, user_id, form_data)

    # DELETE
    async def delete_comment(self, db: Session, comment_id: str, current_user: dict):
        user_id = current_user.get("user_id")
        role = current_user.get("role", "user")
        return await self.service.delete_comment(db, comment_id, user_id, role)