from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from sqlalchemy import select # <--- 2. Dùng select
from fastapi import HTTPException, status
import bcrypt

from app.models.users import Users, UserStatus
from app.schemas.user import (
    UserCreate, Login, UpdateAvatarRequest, UpdateBackgroundRequest,
    UpdateInfoRequest, ChangePasswordRequest, ChangeEmailRequest
)
from app.middleware.JWT.token import access_Token, refresh_token

# --- Hash mật khẩu (Giữ nguyên) ---
def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(10)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

class UserService:
    
    # --- 1. GET USER BY EMAIL ---
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str): # <--- async def
        # Query kiểu Async
        query = select(Users).filter(Users.email == email)
        result = await db.execute(query) # <--- await execute
        return result.scalar_one_or_none()
  
    # --- 2. CREATE USER ---
    @staticmethod
    async def create_new_user(db: AsyncSession, user_data: UserCreate):
        passwordHased = hash_password(user_data.password)
        db_user = Users(
            email=user_data.email,
            firstName=user_data.firstName,
            lastName=user_data.lastName,
            password=passwordHased
        )

        db.add(db_user)
        await db.commit() # <--- await commit
        await db.refresh(db_user) # <--- await refresh

        return db_user
    
    # --- 3. LOGIN ---
    @staticmethod
    async def login(db: AsyncSession, user: Login):
        # 1. Tìm user
        query = select(Users).filter(Users.email == user.email)
        result = await db.execute(query)
        data = result.scalar_one_or_none()

        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email hoặc mật khẩu sai")
        
        # 2. Check Pass (Sync func is fine here)
        if not bcrypt.checkpw(user.password.encode('utf-8'), data.password.encode('utf-8')):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
        
        # 3. Check Status
        if data.status == UserStatus.BANNED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tài khoản bạn đã bị khóa. Vui lòng liên hệ quản trị viên."
            )
        
        # 4. Tạo Token
        payload = {
            "user_id": data.user_id,
            "firstName": data.firstName,
            "lastName": data.lastName,
            "role": data.role,
            "reputation_score" : data.reputation_score,
            "url_avatar": data.url_avatar,
            "description": data.description
        }

        access_TokenNew = access_Token(payload)
        refresh_tokenNew = refresh_token(payload)
        
        return {
            "access_token": access_TokenNew,
            "refresh_token": refresh_tokenNew,
            "user_id": data.user_id,
            "firstName": data.firstName,
            "lastName": data.lastName,
            "role": data.role,
            "reputation_score": data.reputation_score,
            "url_avatar": data.url_avatar,
            "description": data.description
        }

    # --- 4. UPDATE AVATAR ---
    @staticmethod
    async def update_avatar(db: AsyncSession, user_id: str, data: UpdateAvatarRequest):
        # Tìm user bằng ID (Dùng hàm get() nhanh gọn)
        user = await db.get(Users, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.url_avatar = data.url_avatar
        await db.commit() # <--- await
        return {"message": "Cập nhật ảnh đại diện thành công", "url_avatar": user.url_avatar}

    # --- 5. UPDATE BACKGROUND ---
    @staticmethod
    async def update_background(db: AsyncSession, user_id: str, data: UpdateBackgroundRequest):
        user = await db.get(Users, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.url_background = data.url_background
        await db.commit() # <--- await
        return {"message": "Cập nhật ảnh bìa thành công", "url_background": user.url_background}

    # --- 6. UPDATE INFO ---
    @staticmethod
    async def update_info(db: AsyncSession, user_id: str, data: UpdateInfoRequest):
        user = await db.get(Users, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.firstName = data.firstName
        user.lastName = data.lastName
        user.description = data.description
        
        await db.commit() # <--- await
        await db.refresh(user) # <--- await
        
        return {
            "message": "Cập nhật thông tin thành công", 
            "firstName": user.firstName,
            "lastName": user.lastName,
            "description": user.description
        }

    # --- 7. CHANGE PASSWORD ---
    @staticmethod
    async def change_password(db: AsyncSession, user_id: str, data: ChangePasswordRequest):
        user = await db.get(Users, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Kiểm tra mật khẩu cũ
        if not bcrypt.checkpw(data.old_password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác")
        
        # Lưu mật khẩu mới
        user.password = hash_password(data.new_password)
        await db.commit() # <--- await
        return {"message": "Đổi mật khẩu thành công"}

    # --- 8. CHANGE EMAIL ---
    @staticmethod
    async def change_email(db: AsyncSession, user_id: str, data: ChangeEmailRequest):
        user = await db.get(Users, user_id)
        
        # 1. Check mật khẩu để bảo mật
        if not bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Mật khẩu xác nhận không chính xác")
        
        # 2. Check xem email mới đã tồn tại chưa (Async Query)
        query = select(Users).filter(Users.email == data.new_email)
        result = await db.execute(query)
        email_exist = result.scalar_one_or_none()
        
        if email_exist:
             raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi tài khoản khác")

        user.email = data.new_email
        await db.commit() # <--- await
        return