from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from app.schemas.votes import VoteCreate
from app.services.vote_service import VoteService

class VoteController:
    
    def __init__(self, db: AsyncSession): # <--- 2. Type hint AsyncSession
        self.service = VoteService(db)

    # --- HANDLE VOTE (Logic tạo/sửa/xóa) ---
    async def handle_vote(self, user_id: str, payload: VoteCreate): # <--- 3. async def
        
        # 4. Thêm await vào các hàm Service
        existing_vote = await self.service.get_vote(
            user_id, 
            thread_id=payload.thread_id, 
            comment_id=payload.comment_id
        )
        
        if existing_vote:
            if existing_vote.value == payload.value:
                # Vote giống nhau -> Hủy (Unvote)
                await self.service.delete_vote(existing_vote) # <--- await
                return {"status": "unvoted", "message": "Vote removed"}
            else:
                # Vote khác nhau -> Cập nhật (Update)
                updated = await self.service.update_vote_value(existing_vote, payload.value) # <--- await
                return {"status": "updated", "value": updated.value}
        else:
            # Chưa vote -> Tạo mới (Create)
            new_vote = await self.service.create_vote( # <--- await
                user_id=user_id, 
                thread_id=payload.thread_id, 
                comment_id=payload.comment_id, 
                value=payload.value
            )
            return {"status": "created", "value": new_vote.value}

    # --- CHECK STATUS (API Kiểm tra) ---
    async def check_status(self, user_id: str, target_id: str, target_type: str): # <--- async def
        if target_type == "thread":
            # <--- await
            return await self.service.check_user_vote_status(user_id, thread_id=target_id)
        elif target_type == "comment":
            # <--- await
            return await self.service.check_user_vote_status(user_id, comment_id=target_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid target type")