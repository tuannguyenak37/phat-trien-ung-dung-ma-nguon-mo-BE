from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING, List

from ..db.connection import Base
from ..utils.createID import createID

if TYPE_CHECKING:
    from .thread import Thread

class Categories(Base):
    __tablename__ = "categories"

    category_id = Column(
        String(50), 
        primary_key=True, 
        default=lambda: createID("category") # Truyền "category"
    )
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    threads = relationship("Thread", back_populates="category")