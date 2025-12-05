from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession # 1. Dùng AsyncSession
from typing import Optional, List

# 2. Dùng get_async_db
from app.db.connection import get_async_db 
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
    # 👇 Đổi sang AsyncSession
    db: AsyncSession = Depends(get_async_db), 
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None
    
    # 👇 Thêm await
    return await controller.get_thread(db=db, thread_id=thread_id, current_user_id=viewer_id)


# --- 2. XEM FEED (TRANG CHỦ - CÓ LỌC) ---
@router_public.get("/", response_model=ThreadListResponse) 
async def get_list_threads(
    page: int = 1,
    limit: int = 10,
    category_id: Optional[str] = None,
    tag: Optional[str] = None,
    # 👇 Đổi sang AsyncSession
    db: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None
    
    # 👇 Thêm await
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
async def get_user_public_profile( # Nhớ thêm async
    user_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    # ⚠️ LƯU Ý: Bạn cũng cần cập nhật UserController sang Async giống ThreadController
    # Nếu chưa update, dòng await này sẽ lỗi. Hãy đảm bảo UserController đã async.
    controller = UserController()
    return await controller.get_profile_public(db=db, user_id=user_id)


# --- 4. XEM DANH SÁCH BÀI VIẾT CỦA 1 USER (PROFILE) ---
@router_public.get("/users/profile/{user_id}", response_model=ThreadListResponse)
async def get_user_threads_public(
    user_id: str, 
    page: int = 1,
    limit: int = 10,
    # 👇 Đổi sang AsyncSession
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None

    # 👇 Thêm await
    return await controller.get_threads_by_user(
        db=db, 
        user_id=user_id, 
        page=page, 
        limit=limit,
        current_user_id=viewer_id 
    )


# --- 5. LẤY CATEGORY ---
@router_public.get("/categories/get", response_model=CategoryThead)
async def get_categories_with_threads(
    db: AsyncSession = Depends(get_async_db)
):
    service = CategoryService()
    
    # 1. Lấy danh sách category (List)
    categories_list = await service.get_category_thead(db=db)
    
    # 2. 👇 FIX LỖI Ở ĐÂY: Trả về Dictionary khớp với Schema CategoryThead
    # Thay vì return thẳng list, ta phải gán nó vào key "list_thread"
    return {"list_thread": categories_list}

@router_public.get("/posts/{category_slug}/{thread_slug}", response_model=ThreadResponse)
async def get_thread_by_category_and_slug(
    category_slug: str,
    thread_slug: str,
    db: AsyncSession = Depends(get_async_db), 
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None
    
    return await controller.get_thread_by_full_slug(
        db=db, 
        category_slug=category_slug, 
        thread_slug=thread_slug, 
        current_user_id=viewer_id
    )