from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING, List

from ..db.connection import Base
from ..utils.createID import createID

if TYPE_CHECKING:
    from .thread import Thread

# Bảng trung gian
thread_tags = Table(
    "thread_tags",
    Base.metadata,
    Column("thread_id", String(50), ForeignKey("threads.thread_id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(50), ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True),
)

class Tags(Base):
    __tablename__ = "tags"

    tag_id = Column(
        String(50), 
        primary_key=True, 
        default=lambda: createID("tag") # Truyền "tag"
    )
    name = Column(String(50), unique=True, nullable=False)

    threads = relationship("Thread", secondary=thread_tags, back_populates="tags")