from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession # <--- Dùng AsyncSession
from typing import Optional, List

# Import Schemas
from app.schemas.thread import ThreadCreateForm, ThreadUpdateForm

# Import Services
from app.services.thread_service import ThreadService
from app.services.vote_service import VoteService 

class ThreadController:
    def __init__(self):
        self.service = ThreadService()

    # --- 1. CREATE ---
    async def create_thread(self, db: AsyncSession, thread_data: ThreadCreateForm, payload: dict):
        user_id = payload.get("user_id")
        if not user_id:
             raise HTTPException(status_code=401, detail="User ID not found")
        
        # Service đã cập nhật Async ở bước trước, gọi await là xong
        return await self.service.create_thread(db=db, user_id=user_id, form_data=thread_data)

    # --- 2. GET DETAIL ---
    async def get_thread(self, db: AsyncSession, thread_id: str, current_user_id: Optional[str] = None):
        thread = await self.service.get_thread_by_id(db=db, thread_id=thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Gắn trạng thái vote (Async)
        await self._append_vote_stats(db, [thread], current_user_id)
        
        return thread

    # --- 3. UPDATE ---
    async def update_thread(self, db: AsyncSession, thread_id: str, thread_data: ThreadUpdateForm, payload: dict):
        user_id = payload.get("user_id")
        return await self.service.update_thread(
            db=db, 
            thread_id=thread_id, 
            user_id=user_id, 
            form_data=thread_data
        )

    # --- 4. DELETE ---
    async def delete_thread(self, db: AsyncSession, thread_id: str, payload: dict):
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
        db: AsyncSession, 
        page: int, 
        limit: int, 
        category_id: str, 
        tag: str, 
        current_user_id: Optional[str] = None
    ):
        skip = (page - 1) * limit
        
        # 1. Gọi Service lấy danh sách
        result = await self.service.get_threads(
            db=db, 
            skip=skip, 
            limit=limit, 
            category_id=category_id, 
            tag_name=tag
        )

        threads_list = result.get("data", [])

        # 2. Gắn trạng thái Vote cho cả list
        await self._append_vote_stats(db, threads_list, current_user_id)

        return result
    
    # --- 6. GET USER THREADS (PROFILE) ---
    async def get_threads_by_user(self, db: AsyncSession, user_id: str, page: int, limit: int, current_user_id: Optional[str] = None):
        skip = (page - 1) * limit
        
        threads_data = await self.service.get_user_threads_by_page(db=db, user_id=user_id, skip=skip, limit=limit)
        
        # Gắn trạng thái Vote
        if threads_data:
            await self._append_vote_stats(db, threads_data, current_user_id)
        
        total_records = len(threads_data) if threads_data else 0 # (Lưu ý: Logic count chuẩn nên làm ở Service)

        return {
            "total": total_records,
            "page": page,
            "size": limit,
            "data": threads_data 
        }

    # --- HELPER: Gắn trạng thái Vote (DRY Code) ---
    async def _append_vote_stats(self, db: AsyncSession, threads: List, current_user_id: Optional[str]):
        """
        Hàm phụ trợ để gắn thông tin: User hiện tại đã like/dislike bài này chưa?
        """
        if not threads:
            return

        if current_user_id:
            vote_service = VoteService(db) # Khởi tạo service
            
            # Lặp qua từng thread để check status
            # (Lưu ý: Để tối ưu hiệu năng cao hơn, sau này nên viết hàm check_batch trong Service để query 1 lần)
            for thread in threads:
                # ⚠️ Quan trọng: check_user_vote_status trong VoteService CŨNG PHẢI LÀ ASYNC
                user_vote = await vote_service.check_user_vote_status(
                    user_id=current_user_id, 
                    thread_id=thread.thread_id
                )
                thread.vote_stats = user_vote
        else:
            # Khách vãng lai -> Mặc định chưa vote
            for thread in threads:
                thread.vote_stats = {"is_voted": 0}

    # --- 8. GET DETAIL BY FULL SLUG (Category + Thread) ---
    async def get_thread_by_full_slug(
        self, 
        db: AsyncSession, 
        category_slug: str, 
        thread_slug: str, 
        current_user_id: Optional[str] = None
    ):
        # Gọi Service
        thread = await self.service.get_thread_by_slug_and_category(
            db=db, 
            category_slug=category_slug, 
            thread_slug=thread_slug
        )
        
        if not thread:
            # Trả về 404 nếu không tìm thấy hoặc slug không khớp danh mục
            raise HTTPException(status_code=404, detail="Thread not found or URL mismatch")

        # Gắn trạng thái Vote (nếu user đang login)
        await self._append_vote_stats(db, [thread], current_user_id)
        
        return thread