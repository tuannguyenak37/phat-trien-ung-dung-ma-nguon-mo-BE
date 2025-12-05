from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from sqlalchemy import select # <--- 2. Dùng select
from slugify import slugify 
from fastapi import HTTPException, status

from ..models.categories import Categories
from ..schemas.category import CategoryCreate, categoryEdit # Nhớ import categoryEdit

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
        return result.scalars().all() # <--- scalars().all() để lấy list
    
    # --- 5. GET FOR THREAD (Logic giống get_all) ---
    @staticmethod
    async def get_category_thead(db: AsyncSession):
        query = select(Categories)
        result = await db.execute(query)
        categories = result.scalars().all()
        
        if not categories: 
             return [] 
             
        return categories