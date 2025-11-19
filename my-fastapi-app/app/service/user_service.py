from sqlalchemy.orm import Session
from ..models.users import Users
from ..schemas.user import UserCreate
import bcrypt
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
    def get_user_by_username(db: Session, username: str):
        return db.query(Users).filter(Users.username == username).first()
    @staticmethod
    def create_new_user(db:Session, user_data:UserCreate):
        passwordHased = hash_password(user_data.password)
        db_user = Users(
        username = user_data.username,       # từ request
        email = user_data.email,
        password = passwordHased             # từ hash_password()
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    

        