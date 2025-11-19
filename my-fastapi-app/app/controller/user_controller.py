from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..schemas.user import UserCreate
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