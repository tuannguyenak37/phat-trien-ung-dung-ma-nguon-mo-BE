from sqlalchemy.orm import Session
from ..models.users import Users, UserStatus
from ..schemas.user import UserCreate,Login,UpdateAvatarRequest, UpdateBackgroundRequest,UpdateInfoRequest, ChangePasswordRequest, ChangeEmailRequest
from fastapi import  HTTPException,status
import bcrypt
from app.middleware.JWT.token import access_Token, refresh_token

# --- Hash mật khẩu ---
def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')          # chuyển string -> bytes
    salt = bcrypt.gensalt(10)                          # tạo salt
    hashed = bcrypt.hashpw(password_bytes, salt)      # hash
    return hashed.decode('utf-8')                      # trả về string để lưu db

class UserService:
    @staticmethod
    def get_user_by_email(db:Session,email:str):
        return db.query(Users).filter(Users.email== email).first()
  
    @staticmethod
    def create_new_user(db:Session, user_data:UserCreate):
        passwordHased = hash_password(user_data.password)
        db_user = Users(
              # từ request
        email = user_data.email,
        firstName= user_data.firstName,
        lastName = user_data.lastName,
        password = passwordHased             # từ hash_password()
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    
    @staticmethod
    def login(db:Session,user:Login):
        data = db.query(Users).filter(Users.email== user.email).first()
        if  not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=" email hoặc  mật khẩu sai")
        if not bcrypt.checkpw( user.password.encode('utf-8'),data.password.encode('utf-8')):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
        if data.status == UserStatus.BANNED:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=" tài khoản bạn đã vi phạm quy chế hoạt động  vui lòng liên hệ qua email quản trị :23050150@student.bdu.edu.vn")
        
        payload = {
    "user_id": data.user_id,
    "firstName": data.firstName,
    "lastName": data.lastName,
    "role": data.role,
    "reputation_score" : data.reputation_score,
    "url_avatar": data.url_avatar,
    "description":data.description
        }

        access_TokenNew = access_Token(payload)
        refresh_tokenNew = refresh_token(payload)
        return{"access_token":access_TokenNew,"refresh_token":refresh_tokenNew, "user_id": data.user_id,
    "firstName": data.firstName,
    "lastName": data.lastName,
    "role": data.role,
    "reputation_score" : data.reputation_score,
    "url_avatar": data.url_avatar,
    "description":data.description
    
    }
    @staticmethod
    def update_avatar(db: Session, user_id: str, data: UpdateAvatarRequest):
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.url_avatar = data.url_avatar
        db.commit()
        return {"message": "Cập nhật ảnh đại diện thành công", "url_avatar": user.url_avatar}

    @staticmethod
    def update_background(db: Session, user_id: str, data: UpdateBackgroundRequest):
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.url_background = data.url_background
        db.commit()
        return {"message": "Cập nhật ảnh bìa thành công", "url_background": user.url_background}

    # Trong UserService
    @staticmethod
    def update_info(db: Session, user_id: str, data: UpdateInfoRequest):
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.firstName = data.firstName
        user.lastName = data.lastName
        user.description = data.description
        
        db.commit()
        db.refresh(user)
        # Trả về data mới để frontend cập nhật Store
        return {
            "message": "Cập nhật thông tin thành công", 
            "firstName": user.firstName,
            "lastName": user.lastName,
            "description": user.description
        }

    @staticmethod
    def change_password(db: Session, user_id: str, data: ChangePasswordRequest):
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Kiểm tra mật khẩu cũ
        if not bcrypt.checkpw(data.old_password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác")
        
        # Lưu mật khẩu mới
        user.password = hash_password(data.new_password)
        db.commit()
        return {"message": "Đổi mật khẩu thành công"}

    @staticmethod
    def change_email(db: Session, user_id: str, data: ChangeEmailRequest):
        user = db.query(Users).filter(Users.user_id == user_id).first()
        
        # 1. Check mật khẩu để bảo mật
        if not bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Mật khẩu xác nhận không chính xác")
        
        # 2. Check xem email mới đã tồn tại chưa
        email_exist = db.query(Users).filter(Users.email == data.new_email).first()
        if email_exist:
             raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi tài khoản khác")

        user.email = data.new_email
        db.commit()
        return {"message": "Đổi email thành công", "new_email": user.email}

        
        
       


        