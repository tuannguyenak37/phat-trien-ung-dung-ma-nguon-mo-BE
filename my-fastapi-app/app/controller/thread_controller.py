from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional

# Import Schemas
from app.schemas.thread import ThreadCreateForm, ThreadUpdateForm

# Import Services
from app.services.thread_service import ThreadService
from app.services.vote_service import VoteService 

class ThreadController:
    def __init__(self):
        self.service = ThreadService()

    # --- 1. CREATE ---
    async def create_thread(self, db: Session, thread_data: ThreadCreateForm, payload: dict):
        user_id = payload.get("user_id")
        if not user_id:
             raise HTTPException(status_code=401, detail="User ID not found")
        
        return await self.service.create_thread(db=db, user_id=user_id, form_data=thread_data)

    # --- 2. GET DETAIL ---
    async def get_thread(self, db: Session, thread_id: str, current_user_id: Optional[str] = None):
        thread = await self.service.get_thread_by_id(db=db, thread_id=thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Gắn trạng thái Vote của User (nếu đã đăng nhập)
        if current_user_id:
            vote_service = VoteService(db)
            # Hàm check_user_vote_status trả về {is_voted: 1/-1/0}
            user_vote = vote_service.check_user_vote_status(user_id=current_user_id, thread_id=thread.thread_id)
            thread.vote_stats = user_vote
        else:
            thread.vote_stats = {"is_voted": 0} # Mặc định nếu là khách
        
        return thread

    # --- 3. UPDATE ---
    async def update_thread(self, db: Session, thread_id: str, thread_data: ThreadUpdateForm, payload: dict):
        user_id = payload.get("user_id")
        return await self.service.update_thread(
            db=db, 
            thread_id=thread_id, 
            user_id=user_id, 
            form_data=thread_data
        )

    # --- 4. DELETE ---
    async def delete_thread(self, db: Session, thread_id: str, payload: dict):
        user_id = payload.get("user_id")
        role = payload.get("role", "user")
        return await self.service.delete_thread(
            db=db, 
            thread_id=thread_id, 
            user_id=user_id, 
            role=role
        )

    # --- 5. GET LIST (FEED) ---
    async def get_list_threads(
        self, 
        db: Session, 
        page: int, 
        limit: int, 
        category_id: str, 
        tag: str, 
        current_user_id: Optional[str] = None
    ):
        skip = (page - 1) * limit
        
        # 1. Gọi Service lấy danh sách bài
        result = await self.service.get_threads(
            db=db, 
            skip=skip, 
            limit=limit, 
            category_id=category_id, 
            tag_name=tag
        )

        threads_list = result.get("data", [])

        # 2. CHỈ CẦN CHECK IS_VOTED (Nếu có user)
        # Không cần tính tổng like/dislike nữa vì đã có cột counter
        if current_user_id:
            vote_service = VoteService(db)
            # Lấy danh sách thread_id để query 1 lần (Batch Query) hoặc loop
            # Ở đây loop đơn giản cho dễ hiểu
            for thread in threads_list:
                user_vote = vote_service.check_user_vote_status(
                    user_id=current_user_id, 
                    thread_id=thread.thread_id
                )
                thread.vote_stats = user_vote
        else:
            # Nếu là khách, gán mặc định cho tất cả
            for thread in threads_list:
                thread.vote_stats = {"is_voted": 0}

        return result
    
    # --- 6. GET USER THREADS (PROFILE) ---
    async def get_threads_by_user(self, db: Session, user_id: str, page: int, limit: int, current_user_id: Optional[str] = None):
        skip = (page - 1) * limit
        
        threads_data = await self.service.get_user_threads_by_page(db=db, user_id=user_id, skip=skip, limit=limit)
        
        if threads_data and current_user_id:
            vote_service = VoteService(db)
            for thread in threads_data:
                user_vote = vote_service.check_user_vote_status(
                    user_id=current_user_id,
                    thread_id=thread.thread_id
                )
                thread.vote_stats = user_vote
        elif threads_data:
             for thread in threads_data:
                thread.vote_stats = {"is_voted": 0}

        total_records = len(threads_data) if threads_data else 0

        return {
            "total": total_records,
            "page": page,
            "size": limit,
            "data": threads_data 
        }