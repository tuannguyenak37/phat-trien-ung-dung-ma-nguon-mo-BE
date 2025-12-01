from ..config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE,REFRESH_TOKEN_EXPIRE_DAYS
from datetime import datetime, timedelta
from jose import jwt

def access_Token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)

    # 3. Thêm claim "exp" vào payload
    to_encode.update({"exp": expire})

    # 4. Encode JWT với secret key và thuật toán
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

def refresh_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

