from sqlalchemy import Column, String, ForeignKey, SmallInteger, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

from ..db.connection import Base
from ..utils.createID import createID

if TYPE_CHECKING:
    from .users import Users
    from .thread import Thread
    from .comment import Comment

class Vote(Base):
    __tablename__ = "votes"
    
    __table_args__ = (
        # 1. Ràng buộc giá trị: Chỉ chấp nhận 1 (Upvote) hoặc -1 (Downvote)
        CheckConstraint('value = 1 OR value = -1', name='check_vote_value'),
        
        # 2. Ràng buộc mục tiêu: Chỉ vote cho Thread HOẶC Comment, không được cả hai, không được để trống cả hai
        CheckConstraint(
            '(thread_id IS NOT NULL AND comment_id IS NULL) OR (thread_id IS NULL AND comment_id IS NOT NULL)',
            name='check_vote_target'
        ),

        # 3. Ràng buộc duy nhất (QUAN TRỌNG): Chống spam vote
        # Một user chỉ được tồn tại 1 bản ghi vote cho 1 thread_id cụ thể
        UniqueConstraint('user_id', 'thread_id', name='uq_vote_user_thread'),
        
        # Một user chỉ được tồn tại 1 bản ghi vote cho 1 comment_id cụ thể
        UniqueConstraint('user_id', 'comment_id', name='uq_vote_user_comment'),
    )

    vote_id = Column(
        String(50), 
        primary_key=True, 
        default=lambda: createID("vote") # Truyền "vote" để tạo ID
    )
    
    # Cascade delete: Xóa User thì xóa vote của họ
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    # Cascade delete: Xóa Thread/Comment thì xóa các vote liên quan
    thread_id = Column(String(50), ForeignKey("threads.thread_id", ondelete="CASCADE"), nullable=True)
    comment_id = Column(String(50), ForeignKey("comments.comment_id", ondelete="CASCADE"), nullable=True)
    
    value = Column(SmallInteger, nullable=False)

    # Relationships
    user = relationship("Users", back_populates="votes")
    thread = relationship("Thread", back_populates="votes")
    comment = relationship("Comment", back_populates="votes")