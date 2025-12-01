from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.connection import get_db
from app.middleware.JWT.auth import get_current_user_or_guest

# Import Controllers & Services
from app.controller.thread_controller import ThreadController
from app.controller.user_controller import UserController
from app.services.category_service import CategoryService

# Import Schemas
from app.schemas.thread import ThreadResponse, ThreadListResponse
from app.schemas.user import UserpublicResponse
from app.schemas.category import CategoryThead

router_public = APIRouter(
    prefix="/public",
    tags=["Public"],
)

# --- 1. XEM CHI TIẾT BÀI VIẾT ---
@router_public.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread_detail(
    thread_id: str,
    db: Session = Depends(get_db),
    # 👇 Thêm cái này để biết user xem là ai (để hiện tim đỏ)
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None
    
    return await controller.get_thread(db=db, thread_id=thread_id, current_user_id=viewer_id)


# --- 2. XEM FEED (TRANG CHỦ - CÓ LỌC) ---
@router_public.get("/", response_model=ThreadListResponse) 
async def get_list_threads(
    page: int = 1,
    limit: int = 10,
    category_id: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None
    
    # 👇 SỬA LẠI: Gọi hàm get_list_threads (Lấy danh sách chung)
    # Chứ không phải get_threads_by_user
    return await controller.get_list_threads(
        db=db, 
        page=page, 
        limit=limit, 
        category_id=category_id, 
        tag=tag, 
        current_user_id=viewer_id
    )


# --- 3. XEM THÔNG TIN PUBLIC CỦA USER ---
@router_public.get("/users/{user_id}", response_model=UserpublicResponse)
def get_user_public_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    # Giả sử UserController vẫn dùng sync (nếu async thì thêm await)
    return UserController.get_profile_public(db=db, user_id=user_id)


# --- 4. XEM DANH SÁCH BÀI VIẾT CỦA 1 USER (PROFILE) ---
@router_public.get("/users/profile/{user_id}", response_model=ThreadListResponse)
async def get_user_threads_public(
    user_id: str, # ID của chủ profile
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    # 👇 Thêm cái này để người xem (viewer) thấy mình đã like bài của người này chưa
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None

    # 👇 Gọi hàm get_threads_by_user và truyền viewer_id vào
    return await controller.get_threads_by_user(
        db=db, 
        user_id=user_id, # Lấy bài của ông này
        page=page, 
        limit=limit,
        current_user_id=viewer_id # Check like dựa trên ông đang xem
    )


# --- 5. LẤY CATEGORY ---
@router_public.get("/categories/get", response_model=CategoryThead)
def get_categories_with_threads(
    db: Session = Depends(get_db)
):
    categories_list = CategoryService.get_category_thead(db=db)
    return {"list_thread": categories_list}