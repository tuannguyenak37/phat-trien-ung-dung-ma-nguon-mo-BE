# dependencies.py
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader 
from jose import jwt, JWTError
from ..config import SECRET_KEY, ALGORITHM 

# 1. Cấu hình Header Authorization
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

async def get_current_user(token_header: str = Security(api_key_header)):
    # Định nghĩa lỗi trả về chung
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 👇 2. QUAN TRỌNG: Cắt bỏ chữ "Bearer " thừa đi
        # Nếu header là "Bearer eyJ...", ta chỉ lấy "eyJ..."
        if token_header.startswith("Bearer "):
            token = token_header.replace("Bearer ", "")
        else:
            token = token_header
            
        # Xóa khoảng trắng thừa (nếu có)
        token = token.strip()

        # 3. Giải mã token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 4. Lấy user_id
        # ⚠️ Lưu ý: Token của bạn (lúc nãy bạn gửi) dùng key là "user_id", không phải "sub"
        user_id = payload.get("user_id") 
        
        if user_id is None:
            print("DEBUG: Token hợp lệ nhưng không có user_id")
            raise credentials_exception
            
        # 5. Trả về payload thành công
        return payload

    except JWTError as e:
        # In lỗi ra terminal để bạn biết tại sao (ví dụ: hết hạn, sai key)
        print(f"❌ JWT Error: {str(e)}")
        raise credentials_exception