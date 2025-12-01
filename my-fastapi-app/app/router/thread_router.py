from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.connection import get_db
from ..controller.thread_controller import ThreadController
from ..schemas.thread import ThreadCreateForm, ThreadResponse, ThreadUpdateForm, ThreadListResponse

# Import Dependency Auth
from app.middleware.JWT.auth import get_current_user, get_current_user_or_guest

router_thead = APIRouter(
    prefix="/threads",
    tags=["Threads"]
)

# --- GET LIST (FEED) ---
@router_thead.get("/", response_model=ThreadListResponse) # <-- Dùng Schema mới
async def get_list_threads(
    page: int = 1,
    limit: int = 10,
    category_id: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    # 👇 Lấy user hiện tại hoặc Guest (để check like)
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    
    # Lấy ID user (nếu có)
    viewer_id = current_user.get("user_id") if current_user else None
    
    return await controller.get_list_threads(
        db=db, 
        page=page, 
        limit=limit, 
        category_id=category_id, 
        tag=tag,
        current_user_id=viewer_id # <-- Truyền vào Controller
    )

# --- CREATE ---
@router_thead.post("/", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    # Dùng Depends để parse Form Data
    form_data: ThreadCreateForm = Depends(ThreadCreateForm.as_form),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # Bắt buộc login
):
    controller = ThreadController()
    return await controller.create_thread(db, form_data, current_user)

# --- GET DETAIL ---
@router_thead.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread_detail(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_or_guest)
):
    controller = ThreadController()
    viewer_id = current_user.get("user_id") if current_user else None
    
    return await controller.get_thread(db, thread_id, viewer_id)

# --- UPDATE ---
@router_thead.put("/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: str,
    form_data: ThreadUpdateForm = Depends(ThreadUpdateForm.as_form),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    controller = ThreadController()
    return await controller.update_thread(db, thread_id, form_data, current_user)

# --- DELETE ---
@router_thead.delete("/{thread_id}")
async def delete_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    controller = ThreadController()
    return await controller.delete_thread(db, thread_id, current_user)