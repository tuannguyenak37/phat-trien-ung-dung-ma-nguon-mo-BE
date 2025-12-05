from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from sqlalchemy import select # <--- 2. Import select để query
from fastapi import HTTPException, status, Response

from ..schemas.user import UserCreate, Login
from ..services.user_service import UserService
from app.models.users import Users

class UserController:
    
    # --- 1. ĐĂNG KÝ ---
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate): # <--- async def
        # Gọi Service kiểm tra email (Thêm await)
        if await UserService.get_user_by_email(db, email=user_data.email):
            raise HTTPException(
                status_code=400, 
                detail="Email này đã được đăng ký."
            )

        # Gọi Service tạo user (Thêm await)
        return await UserService.create_new_user(db=db, user_data=user_data)

    # --- 2. ĐĂNG NHẬP ---
    @staticmethod
    async def login_controller(db: AsyncSession, user_data: Login, response: Response): # <--- async def
        # Gọi service để login (Thêm await)
        res = await UserService.login(db, user=user_data)

        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản hoặc mật khẩu không chính xác"
            )
        
        refresh_token = res["refresh_token"]

        # Set Cookie (Giữ nguyên logic)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            max_age=60*60*24*7
        )

        return res

    # --- 3. LẤY PROFILE PUBLIC ---
    @staticmethod
    async def get_profile_public(db: AsyncSession, user_id: str): # <--- async def
        # ⚠️ QUAN TRỌNG: Không dùng db.query() được nữa
        # Phải dùng select() và await db.execute()
        
        query = select(Users).filter(Users.user_id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none() # Lấy 1 dòng hoặc None

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Ẩn mật khẩu thủ công (Hoặc để Pydantic lo việc này thì tốt hơn)
        # user.password_hash = None 
        return user