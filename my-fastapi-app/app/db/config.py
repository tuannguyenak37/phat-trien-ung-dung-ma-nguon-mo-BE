import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Khai báo tên biến phải TRÙNG KHỚP với bên trong file .env
    # Ví dụ trong .env bạn để: DB_URL=postgresql://...
    DB_URL: str 

    class Config:
        # Pydantic sẽ tìm file .env ở thư mục gốc nơi bạn chạy lệnh uvicorn
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Bỏ qua các biến thừa trong .env để tránh lỗi validation
        extra = "ignore"

settings = Settings()