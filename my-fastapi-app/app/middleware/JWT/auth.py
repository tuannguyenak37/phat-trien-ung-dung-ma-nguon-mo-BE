# dependencies.py
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader 
from jose import jwt, JWTError
from typing import Optional
from ..config import SECRET_KEY, ALGORITHM 

# ==========================================
# CẤU HÌNH 1: BẮT BUỘC (Dùng cho POST/PUT/DELETE)
# ==========================================
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

async def get_current_user(token_header: str = Security(api_key_header)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if token_header.startswith("Bearer "):
            token = token_header.replace("Bearer ", "")
        else:
            token = token_header
        
        token = token.strip()
        
        # Giải mã
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
            
        return payload

    except JWTError:
        raise credentials_exception


# ==========================================
# CẤU HÌNH 2: TÙY CHỌN (Dùng cho GET danh sách bài viết)
# ==========================================

api_key_header_optional = APIKeyHeader(name="Authorization", auto_error=False)

async def get_current_user_or_guest(
    token_header: Optional[str] = Security(api_key_header_optional)
):
    # 👇 Khác biệt 2: Nếu không có header -> Trả về None (Khách) ngay
    if not token_header:
        return None

    try:
        # Sử dụng lại LOGIC Y HỆT HÀM TRÊN để xử lý chuỗi
        if token_header.startswith("Bearer "):
            token = token_header.replace("Bearer ", "")
        else:
            token = token_header
        
        token = token.strip()

        # Giải mã
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Nếu giải mã thành công -> Trả về user info
        return payload

    except JWTError:
        # 👇 Khác biệt 3: Nếu token sai/hết hạn -> Coi như là KHÁCH (None)
        # Không raise HTTPException ở đây để API vẫn chạy tiếp được
        return None