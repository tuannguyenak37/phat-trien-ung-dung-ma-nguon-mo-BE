import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 1. Khai báo biến (Bắt buộc phải có trong file .env)
    DB_URL: str 

    # 2. Cấu hình Pydantic V2 (Thay thế cho class Config cũ)
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Bỏ qua các biến lạ trong .env
    )

    # 3. Tính năng Tự động tạo URL cho Async (Rất tiện!)
    @property
    def DB_URL_ASYNC(self):
        """
        Tự động chuyển đổi URL từ driver thường sang driver async.
        Ví dụ: postgresql://... -> postgresql+asyncpg://...
        """
        # Nếu URL chưa có driver asyncpg thì thêm vào
        if "postgresql://" in self.DB_URL and "asyncpg" not in self.DB_URL:
            return self.DB_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DB_URL

# Khởi tạo settings
settings = Settings()