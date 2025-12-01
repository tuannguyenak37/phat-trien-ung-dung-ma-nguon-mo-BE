from fastapi import Depends, HTTPException, status
# Import hàm xác thực token từ file dependencies
from .auth import get_current_user

# Hàm này chuyên để chặn cửa Admin
def require_admin(current_user: dict = Depends(get_current_user)):
    
    
    role = current_user.get("role")
    
    # Kiểm tra xem có đúng là admin không
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền Admin"
        )
    
    return current_user