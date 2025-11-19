from sqlalchemy import Column, String, Integer, Enum, DateTime
import enum
from sqlalchemy.sql import func  
from ..db.connection import Base
from ..utils.createID import createID
# Enum trong Python phải khớp với enum trong PostgreSQL
class UserRole(str, enum.Enum):
    # Tên biến (bên trái) phải VIẾT HOA để khớp với UserRole.USER
    USER = "user"       
    ADMIN = "admin"
    MODERATOR = "moderator"
# ------------------------

class Users(Base):
    __tablename__ ="users"

    user_id  = Column(
        String(50),
        primary_key= True,
        index= True,
        default= lambda: createID("user")
    )

    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    fistName = Column(String(50),nullable=False)
    lastName = Column(String(100),nullable=False)

    
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # 5. reputation_score: INTEGER DEFAULT 0
    reputation_score = Column(Integer, default=0, nullable=False)

    # 6. created_at: TIMESTAMPTZ DEFAULT NOW()
    # server_default=func.now() nghĩa là để Database tự điền giờ server vào
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)