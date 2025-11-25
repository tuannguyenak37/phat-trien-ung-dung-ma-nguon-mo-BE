from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.thread import ThreadCreateForm
from app.services.thread_service import ThreadService
from app.schemas.thread import ThreadCreateForm, ThreadUpdateForm # Import thêm
class ThreadController:
    def __init__(self):
        self.service = ThreadService()

    # --- SỬA Ở ĐÂY: Thêm async ---
    async def create_thread(self, db: Session, thread_data: ThreadCreateForm, payload: dict):
        user_id = payload.get("user_id")
        if not user_id:
             raise HTTPException(status_code=401, detail="User ID not found")
        
        # --- SỬA Ở ĐÂY: Thêm await ---
        return await self.service.create_thread(db=db, user_id=user_id, form_data=thread_data)
    # 1. GET DETAIL
    async def get_thread(self, db: Session, thread_id: str):
        return await self.service.get_thread_by_id(db=db, thread_id=thread_id)

    # 2. UPDATE
    async def update_thread(self, db: Session, thread_id: str, thread_data: ThreadUpdateForm, payload: dict):
        user_id = payload.get("user_id")
        return await self.service.update_thread(
            db=db, 
            thread_id=thread_id, 
            user_id=user_id, 
            form_data=thread_data
        )

    # 3. DELETE
    async def delete_thread(self, db: Session, thread_id: str, payload: dict):
        user_id = payload.get("user_id")
        role = payload.get("role", "user") # Lấy role từ token (mặc định user)
        return await self.service.delete_thread(
            db=db, 
            thread_id=thread_id, 
            user_id=user_id, 
            role=role
        )
    