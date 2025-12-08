from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from ..schemas.category import CategoryCreate, categoryEdit
from ..services.category_service import CategoryService
from typing import Optional
from datetime import date
from fastapi import HTTPException 
class CategoryController:
    
    def __init__(self):
        self.service = CategoryService()

    # --- 1. CREATE ---
    async def create(self, db: AsyncSession, category_in: CategoryCreate): # <--- async def
        # Gọi xuống Service (thêm await)
        return await self.service.create_category(db, category_in)

    # --- 2. GET LIST ---
    async def get_list(self, db: AsyncSession):
        return await self.service.get_all(db)
    
    # --- 3. DELETE ---
    async def delete(self, db: AsyncSession, category_id: str):
        return await self.service.delete_category(db=db, category_id=category_id)

    # --- 4. EDIT ---
    # Lưu ý: Schema đầu vào là categoryEdit (khớp với Router)
    async def edit(self, db: AsyncSession, category_id: str, category_in: categoryEdit): 
        return await self.service.edit_category(db=db, category_id=category_id, category_in=category_in)
    
    # API 1: Lấy thống kê tổng quan
    async def get_stats(self, db: AsyncSession, category_id: str):
        stats = await self.service.get_stats_summary(db, category_id)
        
        # 2. Kiểm tra nếu không tìm thấy dữ liệu (Service trả về None)
        if not stats:
            # Phải báo lỗi 404 để FastAPI không cố validate dữ liệu None
            raise HTTPException(status_code=404, detail="Category not found")
            
        return stats

    # Các hàm khác giữ nguyên
    async def get_growth(self, db: AsyncSession, category_id: str, start_date: Optional[date], end_date: Optional[date], period: str):
        return await self.service.get_growth_stats(db, category_id, start_date, end_date, period)

    async def get_distribution(self, db: AsyncSession, start_date: Optional[date], end_date: Optional[date]):
        return await self.service.get_category_distribution(db, start_date, end_date)
    # API 2: Lấy biểu đồ tăng trưởng
    async def get_growth(
        self, 
        db: AsyncSession, 
        category_id: str, 
        start_date: Optional[date], 
        end_date: Optional[date],
        period: str
    ):
        return await self.service.get_growth_stats(
            db=db, 
            category_id=category_id, 
            start_date=start_date, 
            end_date=end_date, 
            period=period
        )
    
    async def get_distribution(
        self, 
        db: AsyncSession, 
        start_date: Optional[date], 
        end_date: Optional[date]
    ):
        """
        Controller xử lý thống kê tỷ lệ danh mục
        """
        return await self.service.get_category_distribution(
            db=db, 
            start_date=start_date, 
            end_date=end_date
        )
    

category_controller = CategoryController()