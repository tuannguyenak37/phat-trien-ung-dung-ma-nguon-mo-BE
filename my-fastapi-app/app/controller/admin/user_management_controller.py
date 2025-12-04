from sqlalchemy.ext.asyncio import AsyncSession
from app.services.admin.admin_user_service import AdminUserService
from app.schemas.admin.admin_account_schema import UserListResponse
from datetime import date
from typing import Optional
from app.schemas.admin.admin_account_schema import DashboardStatsResponse
class UserManagementController:
    
    def __init__(self):
        self.service = AdminUserService()

    async def get_list_users(self, db: AsyncSession, page: int, limit: int, search: str) -> UserListResponse:
        # Gọi service lấy data
        users, total = await self.service.get_all_users(db, page, limit, search)

        # Trả về đúng format Schema đã định nghĩa
        return UserListResponse(
            total=total,
            page=page,
            limit=limit,
            data=users
        )
    async def get_stats(self, db: AsyncSession, start_date: Optional[date], end_date: Optional[date]):
        
        # Truyền tiếp xuống Service
        total, by_role, by_status, by_date = await self.service.get_user_stats(
            db, start_date, end_date
        )
        
        return DashboardStatsResponse(
            total_users=total,
            users_by_role=by_role,
            users_by_status=by_status,
            users_by_date=by_date
        )