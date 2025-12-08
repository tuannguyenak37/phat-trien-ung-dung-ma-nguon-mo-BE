from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession # <--- 1. Dùng AsyncSession
from typing import List

# 2. Dùng get_async_db
from app.db.connection import get_async_db 
from ..schemas.category import CategoryCreate, CategoryResponse, categoryDelete, categoryEdit

# Import Controller
from app.controller.category_controller import category_controller 
# Import Permission Middleware
from ..middleware.JWT.authAdmin import require_admin 

router = APIRouter()


@router.post("/create", response_model=CategoryResponse)
async def create_category( # <--- 3. Thêm async
    category_data: CategoryCreate,         
    db: AsyncSession = Depends(get_async_db), # <--- 4. Inject AsyncSession
    payload: dict = Depends(require_admin) 
):
    # <--- 5. Thêm await
    return await category_controller.create(db=db, category_in=category_data)


@router.delete("/delete/{category_id}")
async def delete_category( # <--- Thêm async
    category_id: str,
    db: AsyncSession = Depends(get_async_db), # <--- AsyncSession
    payload: dict = Depends(require_admin)
):
    # <--- Thêm await
    return await category_controller.delete(db=db, category_id=category_id)


@router.put("/edit/{category_id}", response_model=CategoryResponse)
async def edit_category( # <--- Thêm async
    category_id: str,
    category_data: categoryEdit,
    db: AsyncSession = Depends(get_async_db), # <--- AsyncSession
    payload: dict = Depends(require_admin)
):
    # <--- Thêm await
    return await category_controller.edit(db=db, category_id=category_id, category_in=category_data)


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_async_db) # <--- AsyncSession
):
   
    return await category_controller.get_list(db=db)