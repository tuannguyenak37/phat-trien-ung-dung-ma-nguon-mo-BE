# routers/auth.py
from fastapi import APIRouter, Response, Cookie, HTTPException, status,Depends
from jose import jwt, JWTError
from ..config import SECRET_KEY, ALGORITHM
from .token import access_Token # Hàm tạo token của bạn
from .auth import get_current_user

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
            "lastName": payload.get("lastName")
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
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Endpoint này chỉ chạy khi token hợp lệ.
    Biến 'current_user' chính là dữ liệu trả về từ hàm verify ở trên.
    """
    return {
    
        "success": True,
        "user": {
            "user_id": current_user.get("user_id"),
            "role": current_user.get("role"),
            "firstName": current_user.get("firstName"),
            "lastName": current_user.get("lastName")
            # Trả về bất cứ thứ gì bạn đã lưu trong token
        }
    }