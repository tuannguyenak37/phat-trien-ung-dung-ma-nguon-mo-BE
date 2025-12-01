from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR
from typing import TYPE_CHECKING, List, Optional

from ..db.connection import Base
from ..utils.createID import createID

if TYPE_CHECKING:
    from .users import Users
    from .thread import Thread
    from .vote import Vote

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(
        String(50), 
        primary_key=True, 
        default=lambda: createID("comment")
    )
    
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="SET NULL"))
    thread_id = Column(String(50), ForeignKey("threads.thread_id", ondelete="CASCADE"))
    parent_comment_id = Column(String(50), ForeignKey("comments.comment_id", ondelete="CASCADE"))
    
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 👇 Thêm updated_at
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 👇 3 CỘT MỚI THÊM VÀO ĐÂY
    reply_count = Column(Integer, default=0, nullable=False)
    upvote_count = Column(Integer, default=0, nullable=False)
    downvote_count = Column(Integer, default=0, nullable=False)

    search_vector = Column(TSVECTOR)

    # Relationships
    user = relationship("Users", back_populates="comments")
    thread = relationship("Thread", back_populates="comments")
    votes = relationship("Vote", back_populates="comment", cascade="all, delete-orphan")

    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("Comment", remote_side=[comment_id], back_populates="replies")