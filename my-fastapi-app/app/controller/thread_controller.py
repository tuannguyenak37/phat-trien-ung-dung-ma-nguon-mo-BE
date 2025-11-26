from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.thread import ThreadCreateForm
from app.services.thread_service import ThreadService
from app.schemas.thread import ThreadCreateForm, ThreadUpdateForm 
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
    async def get_list_threads(
        self, db: Session, page: int, limit: int, category_id: str, tag: str
    ):
        skip = (page - 1) * limit
        return await self.service.get_threads(
            db=db, 
            skip=skip, 
            limit=limit, 
            category_id=category_id, 
            tag_name=tag
        )
    
    def get_thread_by_id(self, db: Session, user_id: str, page: int, limit: int):
        # 1. Tính toán skip
        skip = (page - 1) * limit
        
        # 2. Lấy danh sách bài viết (Đây là cái List mà lúc nãy bị lỗi)
        threads_data = self.service.get_user_threads_by_page(db=db, user_id=user_id, skip=skip, limit=limit)
        
        # 3. (Tùy chọn) Tính tổng số bài viết để Frontend biết có bao nhiêu trang
        # Nếu chưa làm hàm đếm thì tạm thời dùng len() hoặc số giả, 
        # nhưng đúng logic là phải query count trong DB.
        # total_records = self.service.count_threads_by_user(db, user_id) 
        total_records = 0 # Tạm thời để 0 hoặc len(threads_data) nếu lười query count

        # 4. Đóng gói trả về (Return Dictionary khớp với ThreadListResponse)
        return {
            "total": total_records,  # Khớp với field 'total'
            "page": page,            # Khớp với field 'page'
            "size": limit,           # Khớp với field 'size'
            "data": threads_data     # Khớp với field 'data' (List bài viết bỏ vào đây)
        }