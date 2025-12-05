from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from ..schemas.category import CategoryCreate, categoryEdit
from ..services.category_service import CategoryService

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
    

category_controller = CategoryController()