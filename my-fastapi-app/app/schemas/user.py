from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

# --- Enum role ---
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
class UserStatus(str, Enum):
    ACTIVE = "active"
    BANNED = "banned"

# --- Pydantic model input ---
class UserCreate(BaseModel):
  
    email: EmailStr           # dùng EmailStr validate email
    password: str
    firstName :str
    lastName:str
    role: UserRole = UserRole.USER   # mặc định là user

class UserResponse(BaseModel):
    user_id: str       # <--- Đã đổi từ 'id' sang 'user_id'
   
    email: EmailStr
    role: UserRole
    firstName :str
    lastName:str
    reputation_score: int
    created_at: datetime # Pydantic tự convert thời gian về dạng chuỗi ISO 8601


class Login(BaseModel):
    email: EmailStr
    password:str

class resposLogin(BaseModel):
     user_id:str
     role:str
     firstName:str
     lastName:str
     access_token:str
     refresh_token:str
     url_avatar: str | None = None
     description: str | None = None
     url_background: str | None = None
     reputation_score: int
class Config:
        from_attributes = True

class UserpublicResponse(BaseModel):
    user_id: str       
    email: EmailStr
    role: UserRole
    firstName :str
    lastName:str
    url_avatar: str | None = None
    description: str | None = None
    url_background: str | None = None
    reputation_score: int
    

    class Config:
        from_attributes = True
class  Userpublic(BaseModel):
    user_id: str       

    class Config:
        from_attributes = True
# 1. Schema sửa Avatar
class UpdateAvatarRequest(BaseModel):
    url_avatar: str

# 2. Schema sửa Background
class UpdateBackgroundRequest(BaseModel):
    url_background: str

# 3. Schema sửa Mô tả
class UpdateInfoRequest(BaseModel):
    firstName: str
    lastName: str
    description: str

# 4. Schema đổi Mật khẩu
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6) # Validate độ dài tối thiểu

# 5. Schema đổi Email
class ChangeEmailRequest(BaseModel):
    password: str # Cần xác nhận mật khẩu trước khi đổi email
    new_email: EmailStr