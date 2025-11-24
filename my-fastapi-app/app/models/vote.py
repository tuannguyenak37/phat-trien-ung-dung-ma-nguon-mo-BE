from sqlalchemy import Column, String, ForeignKey, SmallInteger, CheckConstraint
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
        CheckConstraint('value = 1 OR value = -1', name='check_vote_value'),
        CheckConstraint(
            '(thread_id IS NOT NULL AND comment_id IS NULL) OR (thread_id IS NULL AND comment_id IS NOT NULL)',
            name='check_vote_target'
        ),
    )

    vote_id = Column(
        String(50), 
        primary_key=True, 
        default=lambda: createID("vote") # Truyền "vote"
    )
    
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"))
    thread_id = Column(String(50), ForeignKey("threads.thread_id", ondelete="CASCADE"), nullable=True)
    comment_id = Column(String(50), ForeignKey("comments.comment_id", ondelete="CASCADE"), nullable=True)
    
    value = Column(SmallInteger, nullable=False)

    user = relationship("Users", back_populates="votes")
    thread = relationship("Thread", back_populates="votes")
    comment = relationship("Comment", back_populates="votes")