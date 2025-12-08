from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import List
from datetime import date
from typing import Optional
from fastapi import Query

from app.db.connection import get_async_db 
from app.schemas.category import CategoryStatsSummary, CategoryGrowthResponse,CategoryDistributionResponse

# Import Controller
from app.controller.category_controller import category_controller 
# Import Permission Middleware
from app.middleware.JWT.authAdmin import require_admin 

router = APIRouter( prefix="/admin", 
    tags=["Admin Management darkbord"] ,
    dependencies=[Depends(require_admin)])

@router.get("/category/{category_id}", response_model=CategoryStatsSummary)
async def get_category_statistics(
    category_id: str,
    db: AsyncSession = Depends(get_async_db)
    # Có thể thêm Depends(require_admin) nếu chỉ admin mới được xem
):
    return await category_controller.get_stats(db=db, category_id=category_id)


# 2. API Biểu đồ tăng trưởng (Growth Chart)
@router.get("/category/{category_id}/growth", response_model=CategoryGrowthResponse)
async def get_category_growth(
    category_id: str,
    start_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    period: str = Query("day", enum=["day", "month", "year"], description="Gom nhóm theo ngày/tháng/năm"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    API lấy dữ liệu vẽ biểu đồ.
    - Mặc định: Lấy toàn thời gian (nếu không truyền start/end).
    - Period: 'day' sẽ trả về số bài theo từng ngày.
    """
    return await category_controller.get_growth(
        db=db, 
        category_id=category_id, 
        start_date=start_date, 
        end_date=end_date, 
        period=period
    )

@router.get("/category/distribution/tuan", response_model=CategoryDistributionResponse)
async def get_categories_distribution(
    start_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_db)
):
   
    return await category_controller.get_distribution(
        db=db, 
        start_date=start_date, 
        end_date=end_date
    )