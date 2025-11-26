from pydantic import BaseModel
from typing import Optional
from typing import List, Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
   

# Khuôn cho dữ liệu trả về Client
class CategoryResponse(BaseModel):
    category_id: str
    name: str
    slug: str
    description: Optional[str] = None
    class Config:
        from_attributes = True

   

class categoryEdit(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class categoryDelete(BaseModel):
    category_id: str


    class Config:
        from_attributes = True

class CategoryThead (BaseModel):
    list_thread: List[CategoryResponse]
    class Config:
        from_attributes = True