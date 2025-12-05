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
    
    # 👇 THÊM 2 TRƯỜNG NÀY
    new_files: Optional[List[UploadFile]] = None 
    delete_media_ids: Optional[List[str]] = None

    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        content: Optional[str] = Form(None),
        category_id: Optional[str] = Form(None),
        tags: Optional[str] = Form(None),
        
        # 👇 Nhận file mới từ Form Data
        new_files: Optional[List[UploadFile]] = File(None),
        
        # 👇 Nhận danh sách ID cần xóa (Dạng string JSON ["id1", "id2"] hoặc string tách phẩy "id1,id2")
        delete_media_ids: Optional[str] = Form(None) 
    ):
        # 1. Xử lý Tags (như cũ)
        parsed_tags = None
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except:
                parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]
        
        # 2. Xử lý Delete Media IDs
        parsed_delete_ids = None
        if delete_media_ids:
            try:
                # Cố gắng parse JSON: '["media_1", "media_2"]'
                parsed_delete_ids = json.loads(delete_media_ids)
                if not isinstance(parsed_delete_ids, list):
                     parsed_delete_ids = [str(parsed_delete_ids)]
            except:
                # Nếu không phải JSON thì tách dấu phẩy: "media_1,media_2"
                parsed_delete_ids = [m.strip() for m in delete_media_ids.split(",") if m.strip()]

        return cls(
            title=title,
            content=content,
            category_id=category_id,
            tags=parsed_tags,
            new_files=new_files,        # <--- Gán vào model
            delete_media_ids=parsed_delete_ids # <--- Gán vào model
        )

# --- 3. RESPONSE SCHEMA (QUAN TRỌNG NHẤT) ---

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