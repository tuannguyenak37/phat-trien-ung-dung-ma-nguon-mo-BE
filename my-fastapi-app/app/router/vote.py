from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from typing import Optional

# 2. Dùng get_async_db
from app.db.connection import get_async_db 
from app.schemas.votes import VoteCreate
from app.controller.vote_controller import VoteController
from app.middleware.JWT.auth import get_current_user, get_current_user_or_guest

router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)

# 1. ACTION: VOTE / UNVOTE
@router.post("/", status_code=status.HTTP_200_OK)
async def vote_action( # <--- 3. Thêm async
    payload: VoteCreate,
    # <--- 4. Inject AsyncSession
    db: AsyncSession = Depends(get_async_db), 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    
    # Khởi tạo Controller với Async Session
    controller = VoteController(db)
    
    # <--- 5. Thêm await
    return await controller.handle_vote(user_id, payload)

# 2. API: KIỂM TRA TRẠNG THÁI VOTE CỦA MÌNH
@router.get("/check")
async def check_vote_status( # <--- 6. Thêm async
    target_id: str,
    target_type: str = Query(..., regex="^(thread|comment)$"), 
    # <--- 7. Inject AsyncSession
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    """
    API để Frontend kiểm tra xem user hiện tại đã like bài này chưa
    Trả về: { "is_voted": 1 } hoặc 0 hoặc -1
    """
    controller = VoteController(db)
    user_id = current_user.get("user_id") if current_user else None
    
    # <--- 8. Thêm await
    return await controller.check_status(user_id, target_id, target_type)