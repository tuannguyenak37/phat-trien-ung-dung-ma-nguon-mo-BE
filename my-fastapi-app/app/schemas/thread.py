from fastapi import Form, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

# --- 1. CÁC SCHEMA CON (Dùng để lồng vào ThreadResponse) ---

# Để hiển thị thông tin người đăng (Avatar, Tên)
class UserBasicResponse(BaseModel):
    user_id: str
    firstName: str
    lastName: str
    url_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

# Để hiển thị thông tin danh mục (Tên, Slug)
class CategoryBasicResponse(BaseModel):
    category_id: str
    name: str
    slug: str  # <--- Slug của category
    
    class Config:
        from_attributes = True

class TagResponse(BaseModel):
    tag_id: str
    name: str
    class Config:
        from_attributes = True

class MediaResponse(BaseModel):
    media_id: str
    media_type: str
    file_url: str
    class Config:
        from_attributes = True

# --- 2. INPUT FORM (Create & Update) ---
# ⚠️ Lưu ý: Không cần thêm 'slug' vào Form input
# Vì slug sẽ được Backend tự động tạo từ title (như ta đã cấu hình ở Model)

class ThreadCreateForm(BaseModel):
    title: str
    content: str
    category_id: str
    tags: Optional[List[str]] = None
    files: Optional[List[UploadFile]] = None

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        content: str = Form(...),
        category_id: str = Form(...),
        tags: Optional[str] = Form(None),
        files: Optional[List[UploadFile]] = File(None)
    ):
        parsed_tags: Optional[List[str]] = None
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except:
                parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]
        return cls(
            title=title,
            content=content,
            category_id=category_id,
            tags=parsed_tags,
            files=files
        )
class ThreadUpdateForm(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    new_files: Optional[List[UploadFile]] = None 
    delete_media_ids: Optional[List[str]] = None

    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        content: Optional[str] = Form(None),
        category_id: Optional[str] = Form(None),
        
        # 👇 QUAN TRỌNG: Đổi sang List[str] để nhận mảng từ Frontend
        tags: Optional[List[str]] = Form(None), 
        
        # 👇 Nhận mảng file
        new_files: Optional[List[UploadFile]] = File(None),
        
        # 👇 Nhận mảng ID (Frontend gửi nhiều dòng 'delete_media_ids')
        delete_media_ids: Optional[List[str]] = Form(None) 
    ):
        # 1. Xử lý Tags
        # Frontend có thể gửi:
        # - Nhiều dòng tags: tags=['a', 'b'] -> FastAPI nhận là List -> OK
        # - Một dòng gộp: tags=['a,b'] -> Cần split
        parsed_tags = []
        if tags:
            for item in tags:
                # Phòng trường hợp Frontend gửi chuỗi gộp "tag1, tag2" trong 1 phần tử
                if "," in item:
                    parsed_tags.extend([t.strip() for t in item.split(",") if t.strip()])
                else:
                    parsed_tags.append(item.strip())

        # 2. Xử lý Delete Media IDs
        # Tương tự, đảm bảo nhận đúng list
        parsed_delete_ids = []
        if delete_media_ids:
            # Nếu Frontend gửi JSON string '["id1", "id2"]' (code cũ) -> vẫn support
            # Nếu Frontend gửi List native ['id1', 'id2'] (code mới) -> nhận luôn
            for item in delete_media_ids:
                try:
                    # Thử parse JSON phòng hờ
                    loaded = json.loads(item)
                    if isinstance(loaded, list):
                        parsed_delete_ids.extend(loaded)
                    else:
                        parsed_delete_ids.append(str(loaded))
                except:
                    
                    parsed_delete_ids.append(item)

        return cls(
            title=title,
            content=content,
            category_id=category_id,
            tags=parsed_tags if parsed_tags else None,
            new_files=new_files,
            delete_media_ids=parsed_delete_ids if parsed_delete_ids else None
        )

# --- 3. RESPONSE SCHEMA 

class ThreadResponse(BaseModel):
    thread_id: str
    title: str
    
    # ✅ THÊM SLUG VÀO ĐÂY
    slug: str 
    
    content: str
    created_at: datetime
    
    # ✅ Thống kê
    comment_count: int = 0
    upvote_count: int = 0
    downvote_count: int = 0

    # ✅ Quan hệ mở rộng (Nested Objects)
    # Thay vì chỉ trả về ID, ta trả về cả object để Frontend dễ hiển thị
    user: Optional[UserBasicResponse] = None      # Thông tin người đăng
    category: Optional[CategoryBasicResponse] = None # Thông tin danh mục
    
    tags: List[TagResponse] = []   
    media: List[MediaResponse] = []  
    
    class Config:
        from_attributes = True

# --- 4. LIST RESPONSE ---
class ThreadListResponse(BaseModel):
    total: int
    page: int
    size: int
    data: List[ThreadResponse]