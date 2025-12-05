from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.vote import Vote
from app.models.thread import Thread
from app.models.comment import Comment

class VoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- HÀM 1: LẤY VOTE CŨ ---
    async def get_vote(self, user_id: str, thread_id: str = None, comment_id: str = None):
        query = select(Vote).filter(Vote.user_id == user_id)
        
        if thread_id:
            query = query.filter(Vote.thread_id == thread_id)
        elif comment_id:
            query = query.filter(Vote.comment_id == comment_id)
            
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    # --- HÀM 2: KIỂM TRA TRẠNG THÁI (API Check) ---
    async def check_user_vote_status(self, user_id: str, thread_id: str = None, comment_id: str = None):
        """Trả về 1 (Like), -1 (Dislike) hoặc 0 (Chưa vote)"""
        if not user_id:
            return {"is_voted": 0}
            
        vote = await self.get_vote(user_id, thread_id, comment_id)
        # Lưu ý: Đảm bảo Model Vote của bạn dùng cột 'value' hay 'vote_type' cho thống nhất
        return {"is_voted": vote.value if vote else 0}

    # --- HÀM 3: TẠO VOTE & TĂNG COUNTER ---
    async def create_vote(self, user_id: str, thread_id: str, comment_id: str, value: int):
        # 1. Tạo bản ghi Vote
        new_vote = Vote(
            user_id=user_id, 
            thread_id=thread_id, 
            comment_id=comment_id, 
            value=value
        )
        self.db.add(new_vote)

        # 2. Cập nhật Counter (Thêm await)
        await self._update_counter(thread_id, comment_id, value, is_increment=True)

        await self.db.commit()
        await self.db.refresh(new_vote)
        return new_vote

    # --- HÀM 4: XÓA VOTE & GIẢM COUNTER ---
    async def delete_vote(self, vote: Vote):
        # 1. Cập nhật Counter (Giảm đi)
        await self._update_counter(vote.thread_id, vote.comment_id, vote.value, is_increment=False)
        
        # 2. Xóa bản ghi
        await self.db.delete(vote)
        await self.db.commit()

    # --- HÀM 5: ĐẢO NGƯỢC VOTE (Like -> Dislike) ---
    async def update_vote_value(self, vote: Vote, new_value: int):
        # Logic: 
        # - Giảm counter của loại cũ (vote.value)
        # - Tăng counter của loại mới (new_value)
        await self._update_counter(vote.thread_id, vote.comment_id, vote.value, is_increment=False)
        await self._update_counter(vote.thread_id, vote.comment_id, new_value, is_increment=True)

        vote.value = new_value
        await self.db.commit()
        await self.db.refresh(vote)
        return vote

    # --- HELPER: LOGIC CỘNG TRỪ SỐ LIỆU ---
    async def _update_counter(self, thread_id, comment_id, value, is_increment: bool):
        """Hàm phụ trợ để cộng/trừ vào bảng Thread hoặc Comment"""
        factor = 1 if is_increment else -1
        
        if thread_id:
            # Dùng await db.get() lấy nhanh theo ID
            target = await self.db.get(Thread, thread_id)
            if target:
                if value == 1:
                    target.upvote_count += factor
                elif value == -1:
                    target.downvote_count += factor
        
        elif comment_id:
            target = await self.db.get(Comment, comment_id)
            if target:
                if value == 1:
                    target.upvote_count += factor
                elif value == -1:
                    target.downvote_count += factor