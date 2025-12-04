from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from sqlalchemy import desc
from typing import List, Optional

# Import Models & Schemas
from app.models.thread import Thread, ThreadMedia
from app.models.tags import Tags
from app.schemas.thread import ThreadCreateForm, ThreadUpdateForm
from app.middleware.upload.upload_file import upload_service
from app.utils.reputation_score import update_reputation
class ThreadService:

    # 1. TẠO BÀI VIẾT (CREATE)
    @staticmethod
    async def create_thread(db: Session, user_id: str, form_data: ThreadCreateForm):
        # A. Tạo Thread
        new_thread = Thread(
            user_id=user_id, 
            category_id=form_data.category_id, 
            title=form_data.title, 
            content=form_data.content,
            is_locked=False,
            is_pinned=False
        )
        db.add(new_thread)
        db.flush() # Để lấy thread_id ngay lập tức

        # B. Xử lý Tags (Many-to-Many)
        if form_data.tags:
            unique_tags = set(tag.strip() for tag in form_data.tags if tag.strip())
            for tag_name in unique_tags:
                tag_in_db = db.query(Tags).filter(Tags.name == tag_name).first()
                if not tag_in_db:
                    tag_in_db = Tags(name=tag_name)
                    db.add(tag_in_db)
                    db.flush()
                new_thread.tags.append(tag_in_db)

        # C. Xử lý Media (Upload File)
        if form_data.files: 
            valid_files = [file for file in form_data.files if file.filename]
            
            if valid_files:
                # Gọi service upload (Async)
                file_paths = await upload_service.save_multiple_files(valid_files)
                
                for idx, path in enumerate(file_paths):
                    fname = valid_files[idx].filename.lower()
                    m_type = "video" if fname.endswith(('.mp4', '.mov', '.avi')) else "image"
                    
                    new_media = ThreadMedia(
                        thread=new_thread,
                        media_type=m_type,
                        file_url=path,
                        sort_order=idx
                    )
                    db.add(new_media)

        await update_reputation(db=db, user_id=user_id, amount=5)

        

        # D. Commit & Refresh
        db.commit()
        db.refresh(new_thread) 
        return new_thread

    # 2. LẤY CHI TIẾT 1 BÀI (GET BY ID)
    @staticmethod
    async def get_thread_by_id(db: Session, thread_id: str):
        thread = db.query(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media)
        ).filter(Thread.thread_id == thread_id).first()
        
        if not thread:
            return None # Trả về None để Controller xử lý lỗi 404
        
        return thread

    # 3. CẬP NHẬT (UPDATE)
    @staticmethod
    async def update_thread(db: Session, thread_id: str, user_id: str, form_data: ThreadUpdateForm):
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        if thread.user_id != user_id:
            raise HTTPException(status_code=403, detail="You are not allowed to edit this thread")

        # Cập nhật Text
        if form_data.title: thread.title = form_data.title
        if form_data.content: thread.content = form_data.content
        if form_data.category_id: thread.category_id = form_data.category_id

        # Cập nhật Tags
        if form_data.tags is not None:
            thread.tags.clear()
            unique_tags = set(tag.strip() for tag in form_data.tags if tag.strip())
            for tag_name in unique_tags:
                tag_in_db = db.query(Tags).filter(Tags.name == tag_name).first()
                if not tag_in_db:
                    tag_in_db = Tags(name=tag_name)
                    db.add(tag_in_db)
                    db.flush()
                thread.tags.append(tag_in_db)

        db.commit()
        db.refresh(thread)
        return thread

    # 4. XÓA BÀI VIẾT (DELETE)
    @staticmethod
    async def delete_thread(db: Session, thread_id: str, user_id: str, role: str):
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        if thread.user_id != user_id and role != "admin":
             raise HTTPException(status_code=403, detail="You are not allowed to delete this thread")

        # TODO: Xóa file vật lý trong thư mục static/uploads nếu cần thiết
        
        db.delete(thread)
        db.commit()
        return {"message": "Thread deleted successfully"}
    
    # 5. LẤY DANH SÁCH (GET ALL - FEED)
    @staticmethod
    async def get_threads(
        db: Session, 
        skip: int = 0, 
        limit: int = 10, 
        category_id: Optional[str] = None,
        tag_name: Optional[str] = None
    ):
        query = db.query(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media)
        )

        if category_id:
            query = query.filter(Thread.category_id == category_id)
        
        if tag_name:
            query = query.join(Thread.tags).filter(Tags.name == tag_name)

        query = query.order_by(desc(Thread.created_at))

        total = query.count()
        
        # Thêm .unique() để tránh lỗi trùng lặp khi join 1-nhiều
        threads = query.offset(skip).limit(limit).all()

        return {
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "data": threads
        }

    # 6. LẤY BÀI VIẾT CỦA 1 USER (PROFILE)
    # 👇 Đã sửa thành async để đồng bộ với controller
    @staticmethod
    async def get_user_threads_by_page(db: Session, user_id: str, skip: int = 0, limit: int = 10):
        query = db.query(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media)
        ).filter(Thread.user_id == user_id)
        
        query = query.order_by(Thread.created_at.desc())
        
        threads = query.offset(skip).limit(limit).all() # Thêm .unique().all()

        return threads