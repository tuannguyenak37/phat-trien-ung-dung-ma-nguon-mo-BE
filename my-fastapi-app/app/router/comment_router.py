from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from typing import Optional

# 2. Dùng get_async_db
from app.db.connection import get_async_db 
from app.schemas.comment import CommentCreateForm, CommentResponse, CommentUpdateForm, CommentListResponse
from app.controller.comment_controller import CommentController
from app.middleware.JWT.auth import get_current_user, get_current_user_or_guest

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

# 1. TẠO COMMENT
@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_comment(
    payload: CommentCreateForm,
    # 👇 Đổi sang AsyncSession
    db: AsyncSession = Depends(get_async_db), 
    current_user: dict = Depends(get_current_user)
):
    controller = CommentController()
    return await controller.create_comment(db, payload, current_user)

# 2. LẤY DANH SÁCH (Hỗ trợ lọc & phân trang)
@router.get("/", response_model=CommentListResponse)
async def get_comments(
    thread_id: Optional[str] = None,       
    parent_comment_id: Optional[str] = None, 
    page: int = 1,
    limit: int = 10,
    # 👇 Đổi sang AsyncSession
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = CommentController()
    viewer_id = current_user.get("user_id") if current_user else None
    
    return await controller.get_list_comments(
        db=db, 
        thread_id=thread_id, 
        parent_comment_id=parent_comment_id, 
        page=page, 
        limit=limit,
        current_user_id=viewer_id
    )

# 3. SỬA COMMENT
@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    form_data: CommentUpdateForm,
    # 👇 Đổi sang AsyncSession
    db: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user)
):
    controller = CommentController()
    return await controller.update_comment(db, comment_id, form_data, current_user)

# 4. XÓA COMMENT
@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    # 👇 Đổi sang AsyncSession
    db: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user)
):
    controller = CommentController()
    return await controller.delete_comment(db, comment_id, current_user)