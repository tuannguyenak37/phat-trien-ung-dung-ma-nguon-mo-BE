from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..db.connection import get_db
from ..schemas.category import CategoryCreate, CategoryResponse,categoryDelete,categoryEdit
# Import Controller
from app.controller.category_controller import category_controller 
# Import Permission Middleware
from ..middweare.JWT.authAdmin import require_admin 
router = APIRouter()


@router.post("/create", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,         # 1. Validate Input bằng Schema
    db: Session = Depends(get_db),         # 2. Inject DB
    payload: dict = Depends(require_admin) # 3. Check quyền Admin (Middleware)
):
   
    return category_controller.create(db=db, category_in=category_data)

@router.delete("/delete/{category_id}")
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_admin)
):
    return category_controller.delete(db=db, category_id=category_id)
@router.put("/edit/{category_id}", response_model=CategoryResponse)
def edit_category(
    category_id: str,
    category_data: categoryEdit,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_admin)
):
    return category_controller.edit(db=db, category_id=category_id, category_in=category_data)


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return category_controller.get_list(db=db)
