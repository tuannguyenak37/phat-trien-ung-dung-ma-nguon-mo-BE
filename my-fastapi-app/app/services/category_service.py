from sqlalchemy.orm import Session
from slugify import slugify # pip install python-slugify
from fastapi import HTTPException, status

from ..models.categories import Categories
from ..schemas.category import CategoryCreate
class CategoryService:

    

    @staticmethod
    def create_category(db: Session, category_in: CategoryCreate):
        # 1. Xử lý Logic nghiệp vụ: Tạo slug
        slug = slugify(category_in.name)

        # 2. Kiểm tra trùng lặp (Logic DB)
        existing_category = db.query(Categories).filter(Categories.slug == slug).first()
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
       
        # 4. Lưu và commit
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        return new_category
    
    @staticmethod
    def delete_category(db: Session, category_id: str):
        category = db.query(Categories).filter(Categories.category_id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        db.delete(category)
        db.commit()
        return {"detail": "Category deleted successfully"}
    @staticmethod
    def edit_category(db: Session, category_id: str, category_in: CategoryCreate):
        category = db.query(Categories).filter(Categories.category_id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        if category_in.name:
            category.name = category_in.name
            category.slug = slugify(category_in.name)
        if category_in.description:
            category.description = category_in.description
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all(db: Session):
        return db.query(Categories).all()
    
    @staticmethod
    def get_category_thead(db: Session):
        categories = db.query(Categories).all()
        # Lưu ý: Nếu muốn trả về rỗng thay vì lỗi 404 khi không có category nào
        # thì bỏ đoạn check len == 0 đi. Thường list rỗng vẫn là valid response (200 OK).
        if not categories: 
             # Tùy logic: Có thể raise lỗi hoặc return []
             # Nếu raise 404 ở đây thì client sẽ nhận lỗi thay vì list rỗng
             # raise HTTPException(status_code=404, detail="Category not found")
             return [] 
             
        return categories