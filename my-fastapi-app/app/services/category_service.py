from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from sqlalchemy import select ,and_,func
from slugify import slugify 
from fastapi import HTTPException, status
from sqlalchemy import func, desc
from typing import Optional
from ..models.categories import Categories
from ..schemas.category import CategoryCreate, categoryEdit
from app.schemas.category import CategoryStatsSummary, CategoryGrowthResponse, GrowthDataPoint,CategoryDistributionItem,CategoryDistributionResponse
from app.models.thread import Thread # Import Thread
from datetime import date, datetime
class CategoryService:

    # --- 1. CREATE ---
    @staticmethod
    async def create_category(db: AsyncSession, category_in: CategoryCreate): # <--- async def
        # 1. Tạo slug để check trùng
        slug = slugify(category_in.name)

        # 2. Kiểm tra trùng lặp (Async Query)
        query = select(Categories).filter(Categories.slug == slug)
        result = await db.execute(query) # <--- await execute
        existing_category = result.scalar_one_or_none()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Danh mục này đã tồn tại (trùng tên/slug)"
            )

        # 3. Tạo đối tượng DB
        new_category = Categories(
            name=category_in.name,
            slug=slug,
            description=category_in.description
        )
       
        # 4. Lưu và commit (Async)
        db.add(new_category)
        await db.commit() # <--- await commit
        await db.refresh(new_category) # <--- await refresh
        
        return new_category
    
    # --- 2. DELETE ---
    @staticmethod
    async def delete_category(db: AsyncSession, category_id: str):
        # Tìm category
        query = select(Categories).filter(Categories.category_id == category_id)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Xóa (Async)
        await db.delete(category) # <--- await delete
        await db.commit()
        return {"detail": "Category deleted successfully"}

    # --- 3. EDIT ---
    @staticmethod
    async def edit_category(db: AsyncSession, category_id: str, category_in: categoryEdit):
        # Tìm category
        query = select(Categories).filter(Categories.category_id == category_id)
        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Cập nhật thông tin
        if category_in.name:
            category.name = category_in.name
            # Tự động cập nhật slug nếu đổi tên
            category.slug = slugify(category_in.name)
            
        if category_in.description:
            category.description = category_in.description
            
        await db.commit() # <--- await commit
        await db.refresh(category)
        return category

    # --- 4. GET ALL ---
    @staticmethod
    async def get_all(db: AsyncSession):
        query = select(Categories)
        result = await db.execute(query)
        return result.scalars().all() 
    
    # --- 5. GET FOR THREAD (Logic giống get_all) ---
    @staticmethod
    async def get_category_thead(db: AsyncSession):
        query = select(Categories)
        result = await db.execute(query)
        categories = result.scalars().all()
        
        if not categories: 
             return [] 
             
        return categories
    
    @staticmethod
    async def get_popular(db: AsyncSession, limit: int = 5):
        # Query: Đếm số thread trong từng category
        query = (
            select(Categories)
            .join(Categories.threads)
            .group_by(Categories.category_id)
            .order_by(desc(func.count(Thread.thread_id)))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    # 1. Thống kê tổng quan số lượng
    async def get_stats_summary(self, db: AsyncSession, category_id: str) -> CategoryStatsSummary:
        # Query lấy thông tin Category + đếm Threads
        # Sử dụng subquery hoặc count trực tiếp
        
        # Lấy thông tin category
        cat_query = select(Categories).where(Categories.category_id == category_id)
        cat_result = await db.execute(cat_query)
        category = cat_result.scalar_one_or_none()
        
        if not category:
            return None # Hoặc raise Exception

        # Đếm số thread
        thread_count_query = select(func.count(Thread.thread_id)).where(Thread.category_id == category_id)
        thread_count = await db.execute(thread_count_query)
        total_threads = thread_count.scalar() or 0

        # (Option) Đếm tổng comment: Cần join bảng Comment hoặc tính sum(comment_count) từ Thread
        comment_count_query = select(func.sum(Thread.comment_count)).where(Thread.category_id == category_id)
        comment_res = await db.execute(comment_count_query)
        total_comments = comment_res.scalar() or 0

        return CategoryStatsSummary(
            category_id=category.category_id,
            name=category.name,
            total_threads=total_threads,
            total_comments=total_comments,
            last_activity=datetime.now() # Cần query thêm nếu muốn chính xác
        )

    # 2. Thống kê tăng trưởng theo thời gian
    async def get_growth_stats(
        self, 
        db: AsyncSession, 
        category_id: str, 
        start_date: date = None, 
        end_date: date = None,
        period: str = 'day' # 'day', 'month'
    ) -> CategoryGrowthResponse:
        
        # Xác định hàm truncate thời gian của Postgres
        # date_trunc('day', created_at) -> 2023-10-01 00:00:00
        trunc_func = func.date_trunc(period, Thread.created_at)

        query = (
            select(
                trunc_func.label("time_point"), 
                func.count(Thread.thread_id).label("count")
            )
            .where(Thread.category_id == category_id)
            .group_by("time_point")
            .order_by("time_point")
        )

        # Áp dụng bộ lọc thời gian nếu có
        filters = []
        if start_date:
            filters.append(Thread.created_at >= start_date)
        if end_date:
            filters.append(Thread.created_at <= end_date)
        
        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        rows = result.all()

        # Map dữ liệu sang Pydantic
        data_points = []
        for row in rows:
            # row.time_point là datetime, convert sang date hoặc string cho đẹp
            t_point = row.time_point.date() if isinstance(row.time_point, datetime) else row.time_point
            data_points.append(GrowthDataPoint(time_point=t_point, count=row.count))

        return CategoryGrowthResponse(
            category_id=category_id,
            period=period,
            data=data_points
        )
    
    async def get_category_distribution(
        self, 
        db: AsyncSession, 
        start_date: Optional[date], 
        end_date: Optional[date]
    ) -> CategoryDistributionResponse:
        
        # 1. Query: Join Category với Thread để đếm số lượng
        query = (
            select(
                Categories.category_id,
                Categories.name,
                func.count(Thread.thread_id).label("count")
            )
            .join(Thread, Categories.category_id == Thread.category_id) # Join để đếm bài viết
            .group_by(Categories.category_id, Categories.name)          # Gom nhóm theo danh mục
            .order_by(desc("count"))                                    # Sắp xếp danh mục nhiều bài nhất lên đầu
        )

        # 2. Áp dụng bộ lọc thời gian (nếu có)
        filters = []
        if start_date:
            filters.append(Thread.created_at >= start_date)
        if end_date:
            filters.append(Thread.created_at <= end_date)
        
        if filters:
            query = query.where(and_(*filters))

        # 3. Thực thi query
        result = await db.execute(query)
        rows = result.all()

        # 4. Tính toán tổng số bài viết tìm được để chia phần trăm
        total_threads = sum(row.count for row in rows)

        distribution_list = []
        for row in rows:
            # Tính %: (Số lượng / Tổng) * 100. Làm tròn 2 chữ số thập phân.
            # Lưu ý check total_threads > 0 để tránh lỗi chia cho 0
            percent = round((row.count / total_threads * 100), 2) if total_threads > 0 else 0
            
            item = CategoryDistributionItem(
                category_id=row.category_id,
                name=row.name,
                count=row.count,
                percentage=percent
            )
            distribution_list.append(item)

        # 5. Trả về kết quả theo Schema
        return CategoryDistributionResponse(
            start_date=start_date,
            end_date=end_date,
            total_threads_in_period=total_threads,
            distribution=distribution_list
        )