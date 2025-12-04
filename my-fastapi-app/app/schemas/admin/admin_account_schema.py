from pydantic import BaseModel,EmailStr
from typing import Optional,List,Dict, Any
from enum import Enum
from app.models.users import UserStatus,UserRole
from datetime import datetime
from datetime import date
class UpdateStatusRequest(BaseModel):
    email:  EmailStr
    status: UserStatus  
    reason: Optional[str] = None  


# 1. Dữ liệu của 1 dòng User trong bảng
class UserAdminItem(BaseModel):
    user_id: str
    email: EmailStr
    firstName: str
    lastName: str
    status: UserStatus
    role: UserRole
    reputation_score: int
    url_avatar: Optional[str] = None
    created_at: datetime
    # Đã loại bỏ: password, description, bg_url

    class Config:
        from_attributes = True

# 2. Dữ liệu bọc bên ngoài (Trả về danh sách + tổng số)
class UserListResponse(BaseModel):
    total: int          # Tổng số user tìm thấy (để tính số trang)
    page: int           # Trang hiện tại
    limit: int          # Số lượng hiển thị mỗi trang
    data: List[UserAdminItem] # Danh sách user

# 1. Model con: Dùng cho từng điểm trên biểu đồ đường (Line Chart)
class UserGrowthStats(BaseModel):
    date: date  # Ngày (YYYY-MM-DD)
    count: int  # Số lượng đăng ký

# 2. Model chính: Trả về toàn bộ Dashboard
class DashboardStatsResponse(BaseModel):
    # Tổng quan
    total_users: int
    
    # Thống kê theo vai trò (Admin/User...) -> Vẽ Pie Chart
    # Dạng: {"admin": 5, "user": 100}
    users_by_role: Dict[str, int]       
    
    # Thống kê theo trạng thái (Active/Banned) -> Vẽ Pie Chart cảnh báo
    # Dạng: {"active": 90, "banned": 10}
    # (Đây là trường bạn vừa nhắc bổ sung)
    users_by_status: Dict[str, int]     
    
    # Thống kê tăng trưởng theo thời gian -> Vẽ Line Chart
    users_by_date: List[UserGrowthStats] 

    class Config:
        from_attributes = True