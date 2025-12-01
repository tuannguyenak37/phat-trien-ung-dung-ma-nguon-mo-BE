from fastapi import Form, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
from .votes import VoteStats

# --- INPUT FORM (Giữ nguyên) ---
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

# --- RESPONSE SCHEMAS ---

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

# 👇 CẬP NHẬT CLASS NÀY QUAN TRỌNG NHẤT
class ThreadResponse(BaseModel):
    thread_id: str
    user_id: str
    category_id: str
    title: str
    content: str
    created_at: datetime
    
    # ✅ 1. Thêm 3 trường đếm (Counter) mới từ Database
    # Frontend sẽ dùng cái này để hiển thị số lượng ngay lập tức
    comment_count: int = 0
    upvote_count: int = 0
    downvote_count: int = 0

    # ✅ 2. Các quan hệ (Relationships)
    tags: List[TagResponse] = []   
    media: List[MediaResponse] = []  
    
    
    
    class Config:
        from_attributes = True


class ThreadUpdateForm(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        content: Optional[str] = Form(None),
        category_id: Optional[str] = Form(None),
        tags: Optional[str] = Form(None)
    ):
        parsed_tags = None
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except:
                parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]
        
        return cls(
            title=title,
            content=content,
            category_id=category_id,
            tags=parsed_tags
        )

class ThreadListResponse(BaseModel):
    total: int
    page: int
    size: int
    data: List[ThreadResponse] # Sẽ sử dụng cấu trúc mới ở trên