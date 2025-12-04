from sqlalchemy.orm import Session
from app.models.vote import Vote
from app.models.thread import Thread
from app.models.comment import Comment

class VoteService:
    def __init__(self, db: Session):
        self.db = db

    # --- HÀM 1: LẤY VOTE CŨ ---
    def get_vote(self, user_id: str, thread_id: str = None, comment_id: str = None):
        query = self.db.query(Vote).filter(Vote.user_id == user_id)
        if thread_id:
            query = query.filter(Vote.thread_id == thread_id)
        elif comment_id:
            query = query.filter(Vote.comment_id == comment_id)
        return query.first()

    # --- HÀM 2: KIỂM TRA TRẠNG THÁI (API Check) ---
    def check_user_vote_status(self, user_id: str, thread_id: str = None, comment_id: str = None):
        """Trả về 1 (Like), -1 (Dislike) hoặc 0 (Chưa vote)"""
        if not user_id:
            return {"is_voted": 0}
            
        vote = self.get_vote(user_id, thread_id, comment_id)
        return {"is_voted": vote.value if vote else 0}

    # --- HÀM 3: TẠO VOTE & TĂNG COUNTER ---
    def create_vote(self, user_id: str, thread_id: str, comment_id: str, value: int):
        # 1. Tạo bản ghi Vote
        new_vote = Vote(
            user_id=user_id, thread_id=thread_id, comment_id=comment_id, value=value
        )
        self.db.add(new_vote)
        


        # 2. Cập nhật Counter
        self._update_counter(thread_id, comment_id, value, is_increment=True)

        self.db.commit()
        self.db.refresh(new_vote)
        return new_vote

    # --- HÀM 4: XÓA VOTE & GIẢM COUNTER ---
    def delete_vote(self, vote: Vote):
        # 1. Cập nhật Counter (Giảm đi)
        self._update_counter(vote.thread_id, vote.comment_id, vote.value, is_increment=False)
        
        # 2. Xóa bản ghi
        self.db.delete(vote)
        self.db.commit()

    # --- HÀM 5: ĐẢO NGƯỢC VOTE (Like -> Dislike) ---
    def update_vote_value(self, vote: Vote, new_value: int):
        # Logic: 
        # - Giảm counter của loại cũ (vote.value)
        # - Tăng counter của loại mới (new_value)
        self._update_counter(vote.thread_id, vote.comment_id, vote.value, is_increment=False)
        self._update_counter(vote.thread_id, vote.comment_id, new_value, is_increment=True)

        vote.value = new_value
        self.db.commit()
        self.db.refresh(vote)
        return vote

    # --- HELPER: LOGIC CỘNG TRỪ SỐ LIỆU ---
    def _update_counter(self, thread_id, comment_id, value, is_increment: bool):
        """Hàm phụ trợ để cộng/trừ vào bảng Thread hoặc Comment"""
        factor = 1 if is_increment else -1
        
        if thread_id:
            target = self.db.query(Thread).filter(Thread.thread_id == thread_id).first()
            if target:
                if value == 1:
                    target.upvote_count += factor
                elif value == -1:
                    target.downvote_count += factor
        
        elif comment_id:
            target = self.db.query(Comment).filter(Comment.comment_id == comment_id).first()
            if target:
                if value == 1:
                    target.upvote_count += factor
                elif value == -1:
                    target.downvote_count += factor