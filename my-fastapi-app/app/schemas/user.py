from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
import bcrypt


# --- Kiểm tra mật khẩu ---
def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# --- Enum role ---
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

# --- Pydantic model input ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr           # dùng EmailStr validate email
    password: str
    role: UserRole = UserRole.USER   # mặc định là user

class UserResponse(BaseModel):
    user_id: str       # <--- Đã đổi từ 'id' sang 'user_id'
    username: str
    email: EmailStr
    role: UserRole
    reputation_score: int
    created_at: datetime # Pydantic tự convert thời gian về dạng chuỗi ISO 8601

class Config:
        from_attributes = True