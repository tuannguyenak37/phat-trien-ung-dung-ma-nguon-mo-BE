from fastapi_mail import FastMail, MessageSchema, MessageType
from typing import Optional
from app.middleware.mail_config import conf 

class EmailService:

    # Hàm nội bộ (private) để config và gửi
    @staticmethod
    async def _send(email_to: str, subject: str, html_content: str):
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[email_to],
                body=html_content,
                subtype=MessageType.html
            )
            fm = FastMail(conf)
            await fm.send_message(message)
        except Exception as e:
            print(f"❌ Error sending email to {email_to}: {e}")

    # --- HÀM 1: GỬI EMAIL KHÓA TÀI KHOẢN ---
    @staticmethod
    async def send_banned_email(email_to: str, full_name: str, reason: Optional[str] = None):
        """
        full_name: Chuỗi tên đã ghép (vd: "Nguyen Van A")
        """
        
        # Xử lý hiển thị lý do
        reason_html = f"<p><strong>Lý do:</strong> {reason}</p>" if reason else ""

        subject = "🚨 Thông báo: Tài khoản Community Forum đã bị KHÓA"
        
        # HTML Template
        html_content = f"""
<div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 24px; background: #fff3f3; border-radius: 10px; border: 1px solid #ffcccc;">
    
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="margin: 0; color: #d32f2f;">Messmer Community</h1>
        <p style="margin: 0; color: #555; font-size: 14px;">Nơi kết nối – Chia sẻ – Phát triển</p>
    </div>

    <h2 style="color: #b71c1c;">⚠ Tài khoản bị khóa</h2>

    <p>Xin chào <strong>{full_name}</strong>,</p>
    <p>Tài khoản của bạn liên kết với email <strong>{email_to}</strong> đã bị <strong style="color:#d32f2f;">tạm khóa</strong> vì vi phạm quy tắc cộng đồng Messmer Community.</p>

    {reason_html}

    <div style="margin-top: 20px; background: #ffe5e5; padding: 15px; border-radius: 8px; border-left: 4px solid #d32f2f;">
        <p style="margin: 0; color: #c62828; font-size: 14px;">
            Nếu bạn nghĩ đây là nhầm lẫn, vui lòng liên hệ đội ngũ quản trị để được hỗ trợ.
        </p>
    </div>

    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">

    <p style="font-size: 12px; color: #777; text-align: center;">
        © 2025 Messmer Community — Kết nối mọi người, lan tỏa giá trị.
    </p>

</div>
"""

        
        await EmailService._send(email_to, subject, html_content)
        print(f"📧 [BANNED] Sent to {email_to}")

    # --- HÀM 2: GỬI EMAIL MỞ KHÓA ---
    @staticmethod
    async def send_active_email(email_to: str, full_name: str, reason: Optional[str] = None):
        
        reason_html = f"<p><strong>Lời nhắn từ Admin:</strong> {reason}</p>" if reason else ""

        subject = "✅ Thông báo: Tài khoản đã hoạt động trở lại"
        
        html_content = f"""
<div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 24px; background: #f0fff4; border-radius: 10px; border: 1px solid #b2f5ea;">

    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="margin: 0; color: #2f855a;">Messmer Community</h1>
        <p style="margin: 0; color: #555; font-size: 14px;">Nơi kết nối – Chia sẻ – Phát triển</p>
    </div>

    <h2 style="color: #2f855a;">🎉 Tài khoản đã được mở khóa</h2>

    <p>Xin chào <strong>{full_name}</strong>,</p>
    <p>Tài khoản liên kết với email <strong>{email_to}</strong> đã được <strong style="color:#2f855a;">kích hoạt trở lại</strong>.</p>

    {reason_html}

    <div style="margin-top: 20px; background: #e6fffa; padding: 15px; border-radius: 8px; border-left: 4px solid #38b2ac;">
        <p style="margin:0; font-size:14px; color:#276749;">
            Chúc bạn có những trải nghiệm tuyệt vời cùng cộng đồng Messmer Community!
        </p>
    </div>

    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">

    <p style="font-size: 12px; color: #777; text-align: center;">
        © 2025 Messmer Community — Kiến tạo cộng đồng tri thức.
    </p>

</div>
"""


        await EmailService._send(email_to, subject, html_content)
        print(f"📧 [ACTIVE] Sent to {email_to}")