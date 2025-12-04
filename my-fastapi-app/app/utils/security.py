import bcrypt

def get_password_hash(password: str) -> str:
    """
    Mã hóa password từ String -> String (đã hash).
    Dùng để lưu vào Database.
    """
    # 1. Chuyển password sang bytes
    pwd_bytes = password.encode('utf-8')
    
    # 2. Tạo salt
    salt = bcrypt.gensalt()
    
    # 3. Hash password
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    
    # 4. Trả về dạng String để lưu vào cột VARCHAR trong DB
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu.
    - plain_password: Mật khẩu người dùng nhập (String)
    - hashed_password: Mật khẩu lấy từ DB ra (String)
    """
    # 1. Chuyển cả 2 về dạng bytes thì bcrypt mới so sánh được
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # 2. Check
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        # Trường hợp hash trong DB bị lỗi format hoặc rỗng
        return False