from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR
from typing import TYPE_CHECKING, List

from ..db.connection import Base
from ..utils.createID import createID
from .tags import thread_tags 

if TYPE_CHECKING:
    from .users import Users
    from .categories import Categories
    from .tags import Tags
    from .comment import Comment
    from .vote import Vote

class Thread(Base):
    __tablename__ = "threads"

    thread_id = Column(
        String(50), 
        primary_key=True, 
        default=lambda: createID("thread")
    )
    
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="SET NULL"))
    category_id = Column(String(50), ForeignKey("categories.category_id", ondelete="RESTRICT"))
    
    title = Column(String(255), nullable=False)
    content = Column(Text)
    is_locked = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 👇 3 CỘT MỚI THÊM VÀO ĐÂY
    comment_count = Column(Integer, default=0, nullable=False)
    upvote_count = Column(Integer, default=0, nullable=False)
    downvote_count = Column(Integer, default=0, nullable=False)
    
    search_vector = Column(TSVECTOR)

    # Relationships
    user = relationship("Users", back_populates="threads")
    category = relationship("Categories", back_populates="threads")
    
    tags = relationship("Tags", secondary=thread_tags, back_populates="threads", lazy="selectin")
    
    media = relationship("ThreadMedia", back_populates="thread", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="thread", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="thread", cascade="all, delete-orphan")

class ThreadMedia(Base):
    __tablename__ = "thread_media"

    media_id = Column(String(50), primary_key=True, default=lambda: createID("media"))
    thread_id = Column(String(50), ForeignKey("threads.thread_id", ondelete="CASCADE"))
    
    media_type = Column(String(20), nullable=False)
    file_url = Column(String(512), nullable=False)
    sort_order = Column(SmallInteger, default=0)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("Thread", back_populates="media")