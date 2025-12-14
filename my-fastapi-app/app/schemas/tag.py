from pydantic import BaseModel

# Schema hiển thị Tag cơ bản
class TagResponse(BaseModel):
    tag_id: str
    name: str
    
    class Config:
        from_attributes = True

# Schema cho thống kê (kế thừa hoặc chứa TagResponse)
class TagStatsResponse(BaseModel):
    tag: TagResponse
    count: int # Số lượng bài viết sử dụng tag này