from pydantic import BaseModel
from typing import Optional
from typing import List, Optional
from datetime import date, datetime
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
        

class CategoryStatsSummary(BaseModel):
    category_id: str
    name: str
    total_threads: int          # Tổng số bài viết
    total_comments: int         # Tổng bình luận trong danh mục này (optional)
    last_activity: Optional[datetime] = None # Bài viết mới nhất lúc nào

# Schema cho từng điểm dữ liệu biểu đồ (ví dụ: ngày 2023-10-01 có 5 bài)
class GrowthDataPoint(BaseModel):
    time_point: date | str      # Mốc thời gian (Ngày hoặc Tháng)
    count: int                  # Số lượng bài viết

# Schema trả về cho API tăng trưởng
class CategoryGrowthResponse(BaseModel):
    category_id: str
    period: str                 # 'day', 'month', 'year'
    data: List[GrowthDataPoint]


# 1. Item con: Đại diện cho 1 miếng của biểu đồ tròn
class CategoryDistributionItem(BaseModel):
    category_id: str
    name: str
    count: int          # Số lượng bài viết của danh mục này
    percentage: float   # Tỷ lệ phần trăm (VD: 30.5 nghĩa là 30.5%)

# 2. Response tổng: Chứa danh sách các Item và thông tin metadata
class CategoryDistributionResponse(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    total_threads_in_period: int        # Tổng số bài viết tìm thấy trong khoảng tgian này
    distribution: List[CategoryDistributionItem] # Danh sách dữ liệu để vẽ biểu đồ