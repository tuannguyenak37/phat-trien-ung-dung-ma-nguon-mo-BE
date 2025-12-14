from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import datetime, date, timedelta
import asyncio
from pydantic import BaseModel

# Import DB Connection (Sửa lại đường dẫn import nếu cần)
from app.db.connection import get_async_db

#
from app.models.users import Users, UserStatus
from app.models.thread import Thread
from app.models.comment import Comment
from app.models.categories import Categories
from app.models.tags import Tags
from app.models.vote import Vote

# ==========================================
# 1. SCHEMA (Response Model)
# ==========================================
class DashboardStatsResponse(BaseModel):
    total_users: int
    new_users_today: int
    banned_users: int
    
    total_threads: int
    new_threads_today: int
    locked_threads: int
    
    total_comments: int
    total_categories: int
    total_tags: int
    
    total_votes: int # Tổng lượt tương tác toàn hệ thống

# ==========================================
# 2. ROUTER SETUP
# ==========================================
router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"]
)

# Giả sử bạn có hàm check admin (dependency), nếu không thì bỏ dòng dependencies
# dependencies=[Depends(require_admin)] 

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: AsyncSession = Depends(get_async_db)):
    """
    API lấy số liệu thống kê tổng quan cho trang chủ Admin.
    """
    
    # 1. Lấy mốc thời gian đầu ngày hôm nay
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # 2. KHAI BÁO QUERY (Đây là phần bạn đang bị thiếu)
    # -------------------------------------------------
    
    # User
    query_total_users = select(func.count(Users.user_id))
    query_new_users = select(func.count(Users.user_id)).filter(Users.created_at >= today)
    query_banned_users = select(func.count(Users.user_id)).filter(Users.status == UserStatus.BANNED)

    # Thread
    query_total_threads = select(func.count(Thread.thread_id))
    query_new_threads = select(func.count(Thread.thread_id)).filter(Thread.created_at >= today)
    query_locked_threads = select(func.count(Thread.thread_id)).filter(Thread.is_locked == True)

    # Khác
    query_total_comments = select(func.count(Comment.comment_id))
    query_total_categories = select(func.count(Categories.category_id))
    query_total_tags = select(func.count(Tags.tag_id))
    query_total_votes = select(func.count(Vote.vote_id))

    # 3. THỰC THI TUẦN TỰ (Sequential Execution)
    # -------------------------------------------------
    # Phải có bước khai báo ở trên thì bước này mới có biến để chạy
    total_users = await db.scalar(query_total_users)
    new_users = await db.scalar(query_new_users)
    banned_users = await db.scalar(query_banned_users)
    
    total_threads = await db.scalar(query_total_threads)
    new_threads = await db.scalar(query_new_threads)
    locked_threads = await db.scalar(query_locked_threads)
    
    total_comments = await db.scalar(query_total_comments)
    total_cats = await db.scalar(query_total_categories)
    total_tags = await db.scalar(query_total_tags)
    total_votes = await db.scalar(query_total_votes)

    # 4. TRẢ VỀ KẾT QUẢ
    return {
        "total_users": total_users or 0,
        "new_users_today": new_users or 0,
        "banned_users": banned_users or 0,
        
        "total_threads": total_threads or 0,
        "new_threads_today": new_threads or 0,
        "locked_threads": locked_threads or 0,
        
        "total_comments": total_comments or 0,
        "total_categories": total_cats or 0,
        "total_tags": total_tags or 0,
        
        "total_votes": total_votes or 0
    }

@router.get("/chart-growth")
async def get_growth_chart(days: int = 7, db: AsyncSession = Depends(get_async_db)):
    """
    API lấy dữ liệu vẽ biểu đồ tăng trưởng.
    Fix lỗi GroupingError của PostgreSQL.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # --- 1. QUERY THREADS ---
    # Định nghĩa biểu thức cắt ngày ra biến riêng để PostgreSQL hiểu
    thread_date_expr = func.date_trunc('day', Thread.created_at)
    
    query_threads = (
        select(
            thread_date_expr.label('date'),
            func.count(Thread.thread_id).label('count')
        )
        .filter(Thread.created_at >= start_date)
        .group_by(thread_date_expr) # Dùng lại biến biểu thức
        .order_by(thread_date_expr) # Dùng lại biến biểu thức
    )
    
    # --- 2. QUERY USERS ---
    user_date_expr = func.date_trunc('day', Users.created_at)
    
    query_users = (
        select(
            user_date_expr.label('date'),
            func.count(Users.user_id).label('count')
        )
        .filter(Users.created_at >= start_date)
        .group_by(user_date_expr)
        .order_by(user_date_expr)
    )

    # --- 3. EXECUTE TUẦN TỰ ---
    result_threads = await db.execute(query_threads)
    result_users = await db.execute(query_users)
    
    # --- 4. FORMAT DATA ---
    data_threads = [{"date": row.date.strftime('%Y-%m-%d'), "count": row.count} for row in result_threads]
    data_users = [{"date": row.date.strftime('%Y-%m-%d'), "count": row.count} for row in result_users]

    return {
        "threads_growth": data_threads,
        "users_growth": data_users
    }