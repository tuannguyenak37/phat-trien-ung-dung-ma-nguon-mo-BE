from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.votes import VoteCreate
from app.services.vote_service import VoteService

class VoteController:
    def __init__(self, db: Session):
        self.service = VoteService(db)

    # ... hàm handle_vote cũ giữ nguyên ...
    def handle_vote(self, user_id: str, payload: VoteCreate):
        # (Giữ nguyên logic cũ, chỉ cần gọi self.service.create_vote là nó tự update counter rồi)
        # ... logic check exist ...
        existing_vote = self.service.get_vote(user_id, payload.thread_id, payload.comment_id)
        
        if existing_vote:
            if existing_vote.value == payload.value:
                self.service.delete_vote(existing_vote)
                return {"status": "unvoted", "message": "Vote removed"}
            else:
                updated = self.service.update_vote_value(existing_vote, payload.value)
                return {"status": "updated", "value": updated.value}
        else:
            new_vote = self.service.create_vote(
                user_id, payload.thread_id, payload.comment_id, payload.value
            )
            return {"status": "created", "value": new_vote.value}

    # 👇 HÀM MỚI: API KIỂM TRA TRẠNG THÁI
    def check_status(self, user_id: str, target_id: str, target_type: str):
        if target_type == "thread":
            return self.service.check_user_vote_status(user_id, thread_id=target_id)
        elif target_type == "comment":
            return self.service.check_user_vote_status(user_id, comment_id=target_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid target type")