from sqlalchemy.orm import Session
from fastapi import HTTPException,status,Response
from ..schemas.user import UserCreate,Login
from ..service.user_service  import UserService
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

    