from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.users import Users
from typing import Optional
from datetime import date, timedelta
from sqlalchemy import select, func, cast, Date, and_
class AdminUserService:
    
    async def get_all_users(self, db: AsyncSession, page: int, limit: int, search: str = None):
        # 1. Tạo query cơ bản
        query = select(Users)

        # 2. Nếu có từ khóa tìm kiếm -> Thêm điều kiện lọc
        if search:
            search_format = f"%{search}%" # Tìm chuỗi chứa từ khóa
            query = query.filter(
                or_(
                    Users.email.ilike(search_format),
                    Users.firstName.ilike(search_format),
                    Users.lastName.ilike(search_format)
                )
            )

        # 3. Đếm tổng số user (thỏa mãn điều kiện tìm kiếm) trước khi cắt trang
        # (Để frontend biết có bao nhiêu trang tất cả)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # 4. Áp dụng phân trang (Skip & Limit) và Sắp xếp (Mới nhất lên đầu)
        offset = (page - 1) * limit
        query = query.order_by(Users.created_at.desc()).offset(offset).limit(limit)

        # 5. Thực thi query lấy dữ liệu
        result = await db.execute(query)
        users = result.scalars().all()

        return users, total
    
    async def get_user_stats(self, db: AsyncSession, start_date: Optional[date], end_date: Optional[date]):
        
        # --- BƯỚC 1: Xây dựng bộ lọc chung ---
        conditions = []
        
        if start_date:
            # Lấy record có ngày tạo >= start_date
            conditions.append(cast(Users.created_at, Date) >= start_date)
            
        if end_date:
            # Lấy record có ngày tạo <= end_date
            conditions.append(cast(Users.created_at, Date) <= end_date)
            
        # Hàm filter(*conditions) sẽ tự động giải nén list thành các điều kiện AND
        
        # --- BƯỚC 2: Áp dụng bộ lọc vào từng Query ---

        # 1. Tổng user (Trong khoảng thời gian chọn)
        total_query = select(func.count(Users.user_id)).filter(*conditions)
        total_res = await db.execute(total_query)
        total_users = total_res.scalar_one()

        # 2. Theo Role
        role_query = (
            select(Users.role, func.count(Users.user_id))
            .filter(*conditions) # <--- Thêm lọc
            .group_by(Users.role)
        )
        role_res = await db.execute(role_query)
        by_role = {row[0].value: row[1] for row in role_res.all()}

        # 3. Theo Status
        status_query = (
            select(Users.status, func.count(Users.user_id))
            .filter(*conditions) # <--- Thêm lọc
            .group_by(Users.status)
        )
        status_res = await db.execute(status_query)
        by_status = {row[0].value: row[1] for row in status_res.all()}

        # 4. Biểu đồ tăng trưởng (Line Chart)
        date_query = (
            select(
                cast(Users.created_at, Date).label("date"), 
                func.count(Users.user_id).label("count")
            )
            .filter(*conditions) # <--- Thêm lọc
            .group_by(cast(Users.created_at, Date))
            .order_by(cast(Users.created_at, Date))
        )
        date_res = await db.execute(date_query)
        by_date = [{"date": row[0], "count": row[1]} for row in date_res.all()]

        return total_users, by_role, by_status, by_date