from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.connection import get_db
from app.schemas.votes import VoteCreate
from app.controller.vote_controller import VoteController
from app.middleware.JWT.auth import get_current_user, get_current_user_or_guest

router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)

# 1. ACTION: VOTE / UNVOTE
@router.post("/", status_code=status.HTTP_200_OK)
def vote_action(
    payload: VoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    controller = VoteController(db)
    return controller.handle_vote(user_id, payload)

# 2. 👇 API MỚI: KIỂM TRA TRẠNG THÁI VOTE CỦA MÌNH
# URL: GET /votes/check?target_id=...&target_type=thread
@router.get("/check")
def check_vote_status(
    target_id: str,
    target_type: str = Query(..., regex="^(thread|comment)$"), # Chỉ chấp nhận 'thread' hoặc 'comment'
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    """
    API để Frontend kiểm tra xem user hiện tại đã like bài này chưa
    Trả về: { "is_voted": 1 } hoặc 0 hoặc -1
    """
    controller = VoteController(db)
    user_id = current_user.get("user_id") if current_user else None
    
    return controller.check_status(user_id, target_id, target_type)