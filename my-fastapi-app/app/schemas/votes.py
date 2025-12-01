from pydantic import BaseModel, Field, validator
from typing import Optional

# Dữ liệu Frontend gửi lên để Vote
class VoteCreate(BaseModel):
    thread_id: Optional[str] = None
    comment_id: Optional[str] = None
    value: int = Field(..., description="1 for Like, -1 for Dislike")

    @validator('value')
    def validate_value(cls, v):
        if v not in [1, -1]:
            raise ValueError('Value must be 1 or -1')
        return v

# Dữ liệu Backend trả về cho Frontend hiển thị
class VoteStats(BaseModel):
   
    is_voted: int   # 1, -1, hoặc 0

    class Config:
        orm_mode = True