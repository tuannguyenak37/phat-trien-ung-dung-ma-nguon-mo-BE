from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.schemas.thread import  ThreadResponse
from typing import Optional
from app.schemas.thread import ThreadListResponse
from app.controller.thread_controller import ThreadController
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