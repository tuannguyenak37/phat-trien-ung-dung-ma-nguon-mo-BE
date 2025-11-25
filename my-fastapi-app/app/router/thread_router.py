from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.schemas.thread import ThreadCreateForm, ThreadResponse,ThreadUpdateForm
from app.middweare.JWT.auth import get_current_user
from app.controller.thread_controller import ThreadController

router_thead = APIRouter(
    prefix="/threads",
    tags=["Threads"],
    dependencies=[Depends(get_current_user)]
)

@router_thead.post("/create", response_model=ThreadResponse)
# --- SỬA Ở ĐÂY: Thêm async ---
async def create_thread(
    data: ThreadCreateForm = Depends(ThreadCreateForm.as_form),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user) 
):
    # --- SỬA Ở ĐÂY: Thêm await ---
    return await ThreadController().create_thread(db=db, thread_data=data, payload=payload)

# 1. API: XEM CHI TIẾT (Ai cũng xem được, không cần login -> Không cần dependencies user)
@router_thead.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread_detail(
    thread_id: str,
    db: Session = Depends(get_db)
):
    return await ThreadController().get_thread(db=db, thread_id=thread_id)


# 2. API: CẬP NHẬT (Phải login -> Có Depends user)
@router_thead.put("/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: str,
    # Dùng ThreadUpdateForm.as_form
    data: ThreadUpdateForm = Depends(ThreadUpdateForm.as_form), 
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):
    return await ThreadController().update_thread(
        db=db, 
        thread_id=thread_id, 
        thread_data=data, 
        payload=payload
    )


# 3. API: XÓA (Phải login)
@router_thead.delete("/{thread_id}")
async def delete_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):
    return await ThreadController().delete_thread(
        db=db, 
        thread_id=thread_id, 
        payload=payload
    )
