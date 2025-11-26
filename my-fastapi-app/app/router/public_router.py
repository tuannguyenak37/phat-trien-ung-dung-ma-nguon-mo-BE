from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.schemas.thread import  ThreadResponse
from typing import Optional
from app.schemas.thread import ThreadListResponse
from app.controller.thread_controller import ThreadController
from app.schemas.user import UserpublicResponse
from app.controller.user_controller import UserController
from app.schemas.category import CategoryThead
from app.services.category_service import CategoryService
from typing import List
router_public = APIRouter(
    prefix="/public",
    tags=["Public"],
)
@router_public.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread_detail(
    thread_id: str,
    db: Session = Depends(get_db)
):
    return await ThreadController().get_thread(db=db, thread_id=thread_id)

@router_public.get("", response_model=ThreadListResponse) 
async def get_list_threads(
    page: int = 1,
    limit: int = 10,
    category_id: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Hàm controller trả về dict: {'total': 10, 'data': [ThreadObject, ...]}
    # Nhờ response_model=ThreadListResponse, FastAPI sẽ tự động chuyển ThreadObject thành JSON
    return await ThreadController().get_list_threads(
        db=db, page=page, limit=limit, category_id=category_id, tag=tag
    )
@router_public.get("/users/{user_id}", response_model=UserpublicResponse)
def get_user_public_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    return UserController.get_profile_public(db=db, user_id=user_id)

@router_public.get("/users/profile/{user_id}", response_model=ThreadListResponse) # <--- Dùng nó ở đây
def get_user_threads_public(
    user_id: str,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # Gọi Controller
    return ThreadController().get_thread_by_id(db=db, user_id=user_id, page=page, limit=limit)
@router_public.get("/categories/get", response_model=CategoryThead)
def get_categories_with_threads(
    db: Session = Depends(get_db)
):
    # Bước 1: Lấy list category từ Service (đây là list các SQLAlchemy Object)
    categories_list = CategoryService.get_category_thead(db=db)
    
    # Bước 2: Trả về đúng cấu trúc của response_model (CategoryThead)
    # CategoryThead yêu cầu một trường tên là 'list_thread'
    return {"list_thread": categories_list}