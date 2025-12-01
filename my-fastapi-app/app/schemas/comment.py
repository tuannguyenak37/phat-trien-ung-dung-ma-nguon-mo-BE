from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .votes import VoteStats

# --- INPUT FORMS ---

# 1. Tạo comment
class CommentCreateForm(BaseModel):
    thread_id: str
    content: str
    parent_comment_id: Optional[str] = None # Có thể null nếu là comment gốc

# 2. Sửa comment (Chỉ cho sửa nội dung)
class CommentUpdateForm(BaseModel):
    content: str

# --- OUTPUT RESPONSES ---

# 3. Chi tiết 1 comment
class CommentResponse(BaseModel):
    comment_id: str
    user_id: str
    thread_id: str
    parent_comment_id: Optional[str] = None
    
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Các cột đếm (Counters) lấy từ DB
    reply_count: int = 0
    upvote_count: int = 0
    downvote_count: int = 0
    
    # Trạng thái vote của người xem (Controller gắn vào)
    vote_stats: Optional[VoteStats] = None

    class Config:
        from_attributes = True

# 4. Danh sách comment (Phân trang)
class CommentListResponse(BaseModel):
    total: int
    page: int
    size: int
    data: List[CommentResponse]