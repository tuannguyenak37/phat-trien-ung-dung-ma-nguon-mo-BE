from fastapi import APIRouter, Depends, Query, status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession 
from app.db.connection import get_async_db
from app.schemas.admin.admin_account_schema import UpdateStatusRequest,DashboardStatsResponse
from app.controller.admin.email_controller import email_controler 
from app.middleware.JWT.authAdmin import require_admin
import traceback # Import cái này để soi lỗi
import sys
from typing import Optional
from datetime import date
from app.controller.thread_controller import ThreadController 
from app.controller.admin.user_management_controller import UserManagementController
from app.schemas.admin.admin_account_schema import UserListResponse
# 1. Khởi tạo APIRouter
# Prefix sẽ thêm vào phía trước tất cả các đường dẫn trong router này (ví dụ: /api/v1/admin/ban)
router = APIRouter(
    prefix="/admin", 
    tags=["Admin Management account"] ,
    dependencies=[Depends(require_admin)]
)



@router.post("/ban-account", 
             status_code=status.HTTP_200_OK,
             summary="Cấm (Ban) tài khoản người dùng và gửi email thông báo")
async def ban_user_account_endpoint(
    data: UpdateStatusRequest,
    db: AsyncSession = Depends(get_async_db) 
):  
    try:
        # --- SỬA LỖI Ở ĐÂY ---
        # 1. Khởi tạo controller (thêm dấu ngoặc đơn)
        controller = email_controler() 
        
        # 2. Gọi hàm từ biến controller đã khởi tạo
        await controller.ban_account(db=db, data=data)
        
        return {"message": f"Account with email {data.email} has been banned successfully."}
        
    except HTTPException as http_ex:
        # Lỗi do Controller chủ động ném ra (404, etc) -> Trả về y nguyên
        raise http_ex
        
    except Exception as e:
        # --- LOG LỖI CHI TIẾT ĐỂ DEBUG ---
        print("\n" + "!"*20 + " LỖI 500 TẠI ROUTER " + "!"*20)
        print(f"🔴 Lỗi: {e}")
        traceback.print_exc(file=sys.stderr) # In ra dòng code bị lỗi cụ thể
        print("!"*60 + "\n")
        # ---------------------------------

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing the request."
        )

@router.post("/unlock-account", 
             status_code=status.HTTP_200_OK,
             summary="mở  tài khoản người dùng và gửi email thông báo")
async def unlock_user_account_endpoint(
    data: UpdateStatusRequest,
    db: AsyncSession = Depends(get_async_db) 
):  
    try:
        # --- SỬA LỖI Ở ĐÂY ---
        # 1. Khởi tạo controller (thêm dấu ngoặc đơn)
        controller = email_controler() 
        
        # 2. Gọi hàm từ biến controller đã khởi tạo
        await controller.unlock_account(db=db, data=data)
        
        return {"message": f"Account with email {data.email} has been banned successfully."}
        
    except HTTPException as http_ex:
        # Lỗi do Controller chủ động ném ra (404, etc) -> Trả về y nguyên
        raise http_ex
        
    except Exception as e:
        # --- LOG LỖI CHI TIẾT ĐỂ DEBUG ---
        print("\n" + "!"*20 + " LỖI 500 TẠI ROUTER " + "!"*20)
        print(f"🔴 Lỗi: {e}")
        traceback.print_exc(file=sys.stderr) # In ra dòng code bị lỗi cụ thể
        print("!"*60 + "\n")
        # ---------------------------------

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing the request."
        )
    
@router.get("/users", 
            response_model=UserListResponse, 
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_admin)], # BẮT BUỘC: Chỉ Admin được xem
            summary="Lấy danh sách user (Phân trang & Tìm kiếm)")
async def get_list_users_endpoint(
    # Query params trên URL: /admin/users?page=1&limit=10&search=abc
    page: int = Query(1, ge=1, description="Số trang hiện tại"),
    limit: int = Query(10, ge=1, le=100, description="Số lượng user mỗi trang"),
    search: str = Query(None, description="Tìm theo tên hoặc email"),
    db: AsyncSession = Depends(get_async_db)
):
    controller = UserManagementController()
    return await controller.get_list_users(db=db, page=page, limit=limit, search=search)

@router.get("/dashboard/stats",
            response_model=DashboardStatsResponse,
            dependencies=[Depends(require_admin)],
            summary="Thống kê Dashboard (Có lọc theo ngày)")
async def get_dashboard_stats(
    # Nếu không gửi start_date/end_date thì mặc định là None (Lấy toàn bộ)
    start_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_db)
):
    controller = UserManagementController()
    return await controller.get_stats(db=db, start_date=start_date, end_date=end_date)

# ============================================================

@router.post("/threads/{thread_id}/lock", 
             status_code=status.HTTP_200_OK,
             summary="Cảnh báo & Khóa bài viết (Gửi email vi phạm)")
async def warn_and_lock_thread_endpoint(
    thread_id: str,
    data: UpdateStatusRequest, 
    db: AsyncSession = Depends(get_async_db),
    # Lấy thông tin Admin đang thực hiện hành động này
    current_user: dict = Depends(require_admin) 
):
    try:
        controller = ThreadController()
        # Gọi hàm warn_thread trong controller
        return await controller.warn_thread(db=db, thread_id=thread_id, form_data=data, current_user=current_user)
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"🔴 Lỗi khi khóa bài viết: {e}")
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error while locking thread"
        )