import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

# Load file .env
load_dotenv()

# Lấy dữ liệu từ .env
smtp_user = os.getenv("SMTP_USER")
smtp_pass = os.getenv("SMTP_PASS")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = int(os.getenv("SMTP_PORT", 465))

conf = ConnectionConfig(
    MAIL_USERNAME=smtp_user,
    MAIL_PASSWORD=smtp_pass,
    MAIL_FROM=smtp_user,  # Dùng chính email gửi để làm email hiển thị
    MAIL_PORT=smtp_port,
    MAIL_SERVER=smtp_host,
    MAIL_FROM_NAME="Community Forum Admin", # Tên hiển thị khi người dùng nhận mail
    
    # Cấu hình QUAN TRỌNG cho Port 465 (Gmail SSL)
    MAIL_STARTTLS=False, 
    MAIL_SSL_TLS=True,
    
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)