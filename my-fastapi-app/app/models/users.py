from sqlalchemy import Column, String, Integer, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from typing import TYPE_CHECKING, List # Import này để fix lỗi "Not defined"

from ..db.connection import Base
from ..utils.createID import createID

# Chỉ import các file khác KHI đang kiểm tra type (không chạy lúc runtime)
# Đây là cách fix lỗi "Thread is not defined" chuẩn nhất
if TYPE_CHECKING:
    from .thread import Thread
    from .comment import Comment
    from .vote import Vote

class UserStatus(str, enum.Enum):
    ACTIVE = "active"     # Đang hoạt động bình thường
    BANNED = "banned"     # Đã bị khóa bởi Admin/Mod
class UserRole(str, enum.Enum):
    USER = "user"       
    ADMIN = "admin"
    MODERATOR = "moderator"

class Users(Base):
    __tablename__ ="users"

    user_id = Column(
        String(50),
        primary_key=True,
        index=True,
        # Truyền "user" vào createID như bạn yêu cầu
        default=lambda: createID("user") 
    )

    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(100), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    reputation_score = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    url_avatar = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)


    # --- RELATIONSHIPS ---
    # Dùng chuỗi string "Thread", "Comment" thay vì biến class trực tiếp
    threads = relationship("Thread", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    votes = relationship("Vote", back_populates="user")