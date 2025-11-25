from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    # Lưu ý: Không cần gửi slug, Backend sẽ tự tạo

# Khuôn cho dữ liệu trả về Client
class CategoryResponse(BaseModel):
    category_id: str
    name: str
    slug: str
    description: Optional[str] = None

   

class categoryEdit(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class categoryDelete(BaseModel):
    category_id: str


    class Config:
        from_attributes = True