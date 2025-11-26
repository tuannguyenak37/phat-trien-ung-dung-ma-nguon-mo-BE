from sqlalchemy.orm import Session
from fastapi import HTTPException,status,Response
from ..schemas.user import UserCreate,Login
from ..services.user_service  import UserService
from app.models.users import Users
class UserController:
    @staticmethod
    def create_user(db: Session,user_data: UserCreate):
        # Check trùng Email
        if UserService.get_user_by_email(db, email=user_data.email):
            raise HTTPException(
                status_code=400, 
                detail="Email này đã được đăng ký."
            )

      
        return UserService.create_new_user(db=db,user_data=user_data)
    @staticmethod
    def login_controller(db: Session, user_data: Login,response =Response):
        # Gọi service để login
        res = UserService.login(db, user=user_data)

        # Nếu service trả về None hoặc False → ném exception
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Có lỗi xảy ra, vui lòng thử lại sau"
            )
        refresh_token = res["refresh_token"]

        # ⚡ Dùng response instance
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            max_age=60*60*24*7
        )

        return res
    @staticmethod
    def get_profile_public(db: Session,user_id:str):
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user.password_hash = None  # Ẩn thông tin mật khẩu
        return user

    