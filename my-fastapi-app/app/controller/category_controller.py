from sqlalchemy.orm import Session
from ..schemas.category import CategoryCreate
from ..services.category_service import CategoryService

class CategoryController:
    
    def __init__(self):
       
        self.service = CategoryService()

    def create(self, db: Session, category_in: CategoryCreate):
        # Gọi xuống Service để xử lý
        return self.service.create_category(db, category_in)

    def get_list(self, db: Session):
        return self.service.get_all(db)
    
    def delete(self, db: Session, category_id: str):
        return self.service.delete_category(db =db, category_id = category_id)
    def edit(self, db: Session, category_id: str, category_in: CategoryCreate):
        return self.service.edit_category(db = db, category_id = category_id, category_in = category_in)
    


category_controller = CategoryController()