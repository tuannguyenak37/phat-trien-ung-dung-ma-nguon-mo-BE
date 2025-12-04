# routers/auth.py
from fastapi import APIRouter, Response, Cookie, HTTPException, status,Depends
from jose import jwt, JWTError
from ..config import SECRET_KEY, ALGORITHM
from .token import access_Token # Hàm tạo token của bạn
from .auth import get_current_user
from app.db.connection import get_db
from sqlalchemy.orm import Session
from app.models.users import Users
router_token = APIRouter()

# 👇 API này Frontend sẽ gọi khi bị lỗi 401
@router_token.post("/refresh")
def refresh_access_token(
    response: Response,
    refresh_token: str = Cookie(None) # 👈 Lấy Refresh Token từ Cookie
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        # 1. Verify Refresh Token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Lấy thông tin user từ payload cũ
        # (Lưu ý: Refresh Token thường lưu ít thông tin hơn)
        user_data = {
           "user_id": payload.get("user_id"),
            "role": payload.get("role"),
            "firstName": payload.get("firstName"),
            "lastName": payload.get("lastName"),
              "reputation_score" : payload.get("reputation_score"),
              "url_avatar": payload.get("url_avatar"),
                "description":payload.get("description")
            
        }

        # 3. Tạo Access Token mới
        new_access_token = access_Token(user_data)

        # 4. Trả về cho Frontend (để lưu vào Zustand)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        # Nếu Refresh Token cũng hết hạn hoặc sai -> Bắt đăng nhập lại
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token expired"
        )
@router_token.get("/api/users/me")
async def read_users_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)  # <--- SỬA 1: Chuyển Depends vào tham số
):
    """
    Endpoint này lấy thông tin user mới nhất từ DB dựa trên Token.
    """
    
    # <--- SỬA 2 & 3: Bỏ 'await', sửa 'Users.id' thành 'Users.user_id'
    user_in_db = db.query(Users).filter(Users.user_id == current_user.get("user_id")).first()

    if not user_in_db:
        raise HTTPException(status_code=404, detail="User not found")

    # Log kiểm tra (tuỳ chọn)
    print("Dữ liệu từ DB:", user_in_db.reputation_score)

    # Nên lấy dữ liệu từ 'user_in_db' (DB) thay vì 'current_user' (Token)
    # Vì Token có thể cũ (ví dụ user vừa đổi avatar xong, token chưa cập nhật)
    return {
        "success": True,
        "user": {
            "user_id": user_in_db.user_id,
            "role": user_in_db.role, # Lấy từ DB luôn cho chuẩn
            "firstName": user_in_db.firstName,
            "lastName": user_in_db.lastName,
            "reputation_score": user_in_db.reputation_score, # <--- Mục tiêu chính của bạn
            "url_avatar": user_in_db.url_avatar,
            "description": user_in_db.description
        }
    }