import traceback # <--- 1. Import thư viện này để in lỗi chi tiết
import sys
from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.connection import get_db 
from app.models.users import Users, UserStatus
from app.services.admin.email_service import EmailService 
from app.schemas.admin.admin_account_schema import UpdateStatusRequest,UpdateStatusRequestTheadTheads

class email_controler:
    
    def __init__(self):
        self.service = EmailService

    async def ban_account(self, db: AsyncSession, data: UpdateStatusRequest):
        print(f"🚀 [START] Banning account: {data.email}") # Log bắt đầu
        try:
            # 1. Truy vấn user
            result = await db.execute(
                select(Users).filter(Users.email == data.email)
            )
            data_user = result.scalar_one_or_none()
            
            if not data_user:
                print(f"⚠️ User not found: {data.email}")
                raise HTTPException(status_code=404, detail="User not found")
            
            # 2. Cập nhật trạng thái
            data_user.status = UserStatus.BANNED
            
            # 3. Gửi Email
            print(f"📧 Sending email to: {data.email}...")
            fullName = f"{data_user.firstName} {data_user.lastName}"
            
            await EmailService.send_banned_email(
                email_to=data_user.email, full_name=fullName, reason=data.reason
            )
            
            # 4. Commit
            await db.commit()
            print(f"✅ [SUCCESS] Account {data.email} banned.")
            
            return {"message": f"User {data.email} banned successfully."}

        except HTTPException as e: # <--- Sửa: Thêm 'as e'
            # Lỗi HTTP (404, etc) là lỗi logic đã dự tính, không cần traceback dài dòng
            print(f"❌ [HTTP ERROR] {e.detail}")
            raise e
            
        except Exception as e:
            # 5. Rollback ngay lập tức
            await db.rollback()
            
            # --- PHẦN IN LỖI CHO DỄ NHÌN ---
            print("\n" + "="*60)
            print(f"🔥 [CRITICAL ERROR] in ban_account processing email: {data.email}")
            print(f"🔴 Error Message: {str(e)}")
            print("-" * 20 + " TRACEBACK " + "-" * 20)
            # In ra toàn bộ ngăn xếp cuộc gọi (Stack Trace) để biết lỗi dòng nào
            traceback.print_exc(file=sys.stderr) 
            print("="*60 + "\n")
            # -------------------------------
            
            # Ném lại lỗi để FastAPI trả về 500
            raise e
   
