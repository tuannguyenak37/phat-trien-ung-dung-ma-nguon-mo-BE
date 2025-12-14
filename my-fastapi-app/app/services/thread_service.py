from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete, func,or_,desc,case
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import joinedload, selectinload
# Import Models & Schemas
from app.models.thread import Thread, ThreadMedia
from app.models.tags import Tags
from app.models.categories import Categories # Import để join khi tìm theo slug
from app.schemas.thread import ThreadCreateForm, ThreadUpdateForm
from app.middleware.upload.upload_file import upload_service
from app.utils.reputation_score import update_reputation
from datetime import datetime, timedelta
from app.services.admin.email_service import EmailService 
class ThreadService:

    # --- 1. TẠO BÀI VIẾT ---
    @staticmethod
    async def create_thread(db: AsyncSession, user_id: str, form_data: ThreadCreateForm):
        # A. Tạo Thread Object
        # Lưu ý: Slug sẽ được Model tự động tạo từ Title
        new_thread = Thread(
            user_id=user_id, 
            category_id=form_data.category_id, 
            title=form_data.title, 
            content=form_data.content,
            is_locked=False,
            is_pinned=False,
            # 👇 QUAN TRỌNG: Khởi tạo list rỗng để tránh lỗi MissingGreenlet
            tags=[] 
        )
        db.add(new_thread)
        await db.flush() 

        # B. Xử lý Tags
        if form_data.tags:
            unique_tags = set(tag.strip() for tag in form_data.tags if tag.strip())
            tags_to_add = []
            
            for tag_name in unique_tags:
                query_tag = select(Tags).filter(Tags.name == tag_name)
                result = await db.execute(query_tag)
                tag_in_db = result.scalar_one_or_none()
                
                if not tag_in_db:
                    tag_in_db = Tags(name=tag_name)
                    db.add(tag_in_db)
                    await db.flush() 
                
                tags_to_add.append(tag_in_db)
            
            # Gán list tag
            new_thread.tags = tags_to_add

        # C. Xử lý Media (Upload File)
        if form_data.files: 
            valid_files = [file for file in form_data.files if file.filename]
            if valid_files:
                file_paths = await upload_service.save_multiple_files(valid_files)
                for idx, path in enumerate(file_paths):
                    fname = valid_files[idx].filename.lower()
                    m_type = "video" if fname.endswith(('.mp4', '.mov', '.avi')) else "image"
                    
                    new_media = ThreadMedia(
                        thread_id=new_thread.thread_id, 
                        media_type=m_type,
                        file_url=path,
                        sort_order=idx
                    )
                    db.add(new_media)

        # Tăng uy tín user
        await update_reputation(db=db, user_id=user_id, amount=5)

        # D. Commit & Refresh
        await db.commit()
        await db.refresh(new_thread) 
        
        # Load lại đầy đủ quan hệ để trả về API
        query = select(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media),
            joinedload(Thread.user),   
            joinedload(Thread.category) 
        ).filter(Thread.thread_id == new_thread.thread_id)
        
        result = await db.execute(query)
        return result.unique().scalar_one()

    # --- 2. LẤY CHI TIẾT THEO ID ---
    @staticmethod
    async def get_thread_by_id(db: AsyncSession, thread_id: str):
        query = select(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media),
            joinedload(Thread.user),
            joinedload(Thread.category)
        ).filter(Thread.thread_id == thread_id)
        
        result = await db.execute(query)
        thread = result.unique().scalar_one_or_none()
        
        return thread

    # --- 3. LẤY CHI TIẾT THEO SLUG (Cho SEO) ---
    @staticmethod
    async def get_thread_by_slug(db: AsyncSession, slug: str):
        query = select(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media),
            joinedload(Thread.user),
            joinedload(Thread.category)
        ).filter(Thread.slug == slug)
        
        result = await db.execute(query)
        return result.unique().scalar_one_or_none()

    # --- 4. LẤY CHI TIẾT THEO CATEGORY SLUG + THREAD SLUG (SEO Chuẩn nhất) ---
    @staticmethod
    async def get_thread_by_slug_and_category(db: AsyncSession, category_slug: str, thread_slug: str):
        query = (
            select(Thread)
            .join(Thread.category) # Join để check slug của category
            .options(
                joinedload(Thread.tags),
                joinedload(Thread.media),
                joinedload(Thread.user),
                joinedload(Thread.category)
            )
            .filter(
                Thread.slug == thread_slug, 
                Categories.slug == category_slug
            )
        )
        
        result = await db.execute(query)
        return result.unique().scalar_one_or_none()

    # --- 5. CẬP NHẬT BÀI VIẾT (Update) ---
    @staticmethod
    async def update_thread(db: AsyncSession, thread_id: str, user_id: str, form_data: ThreadUpdateForm):
        # Tìm bài viết
        query = select(Thread).options(joinedload(Thread.tags)).filter(Thread.thread_id == thread_id)
        result = await db.execute(query)
        thread = result.unique().scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        if thread.user_id != user_id:
            raise HTTPException(status_code=403, detail="You are not allowed to edit this thread")

        # Cập nhật thông tin cơ bản
        # (Model sẽ tự update slug nếu title thay đổi)
        if form_data.title: thread.title = form_data.title
        if form_data.content: thread.content = form_data.content
        if form_data.category_id: thread.category_id = form_data.category_id

        # Cập nhật Tags
        if form_data.tags is not None:
            thread.tags.clear()
            unique_tags = set(tag.strip() for tag in form_data.tags if tag.strip())
            for tag_name in unique_tags:
                tag_query = select(Tags).filter(Tags.name == tag_name)
                tag_res = await db.execute(tag_query)
                tag_in_db = tag_res.scalar_one_or_none()
                if not tag_in_db:
                    tag_in_db = Tags(name=tag_name)
                    db.add(tag_in_db)
                    await db.flush()
                thread.tags.append(tag_in_db)

        # Xử lý Media: Xóa cũ
        if form_data.delete_media_ids:
            stmt = delete(ThreadMedia).where(
                ThreadMedia.media_id.in_(form_data.delete_media_ids),
                ThreadMedia.thread_id == thread_id
            )
            await db.execute(stmt)

        # Xử lý Media: Thêm mới
        if form_data.new_files:
            valid_files = [file for file in form_data.new_files if file.filename]
            if valid_files:
                file_paths = await upload_service.save_multiple_files(valid_files)
                
                # Lấy max sort_order hiện tại
                max_order_query = select(func.max(ThreadMedia.sort_order)).filter(ThreadMedia.thread_id == thread_id)
                max_order_res = await db.execute(max_order_query)
                current_max_order = max_order_res.scalar() or 0
                start_order = current_max_order + 1

                for idx, path in enumerate(file_paths):
                    fname = valid_files[idx].filename.lower()
                    m_type = "video" if fname.endswith(('.mp4', '.mov', '.avi')) else "image"
                    new_media = ThreadMedia(
                        thread_id=thread_id,
                        media_type=m_type,
                        file_url=path,
                        sort_order=start_order + idx
                    )
                    db.add(new_media)

        await db.commit()
        await db.refresh(thread)
        
        # Load lại full data để trả về
        query_full = select(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media),
            joinedload(Thread.user),
            joinedload(Thread.category)
        ).filter(Thread.thread_id == thread_id)
        
        result_full = await db.execute(query_full)
        return result_full.unique().scalar_one()

    # --- 6. XÓA BÀI VIẾT (Cập nhật quyền Admin/Mod) ---
    @staticmethod
    async def delete_thread(db: AsyncSession, thread_id: str, user_id: str, role: str):
        query = select(Thread).filter(Thread.thread_id == thread_id)
        result = await db.execute(query)
        thread = result.scalar_one_or_none()
        
        if not thread:
            raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

        # Logic quyền: Chính chủ HOẶC là Admin HOẶC là Moderator
        allowed_roles = ["admin", "moderator"]
        
        # Chuyển role về chữ hoa để so sánh cho chắc chắn
        user_role_upper = role.upper() if role else ""

        if thread.user_id != user_id and user_role_upper not in allowed_roles:
             raise HTTPException(status_code=403, detail="Bạn không có quyền xóa bài viết này")

        await db.delete(thread)
        await db.commit()
        return {"message": "Đã xóa bài viết thành công"}
    
    # --- LẤY DANH SÁCH (HOME FEED & SEARCH) ---
    @staticmethod
    async def get_threadsHome(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        category_id: Optional[str] = None,
        tag_name: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "mix",
        ):
        
       
        # 1. Base Query
        # Dùng selectinload cho Tags (quan hệ 1-N) để tối ưu và tránh duplicates
        query = select(Thread).options(
            selectinload(Thread.tags),
            joinedload(Thread.media),
            joinedload(Thread.user),
            joinedload(Thread.category)
        )

        # 2. Filter & Join
        # Chỉ join khi cần filter để tăng tốc độ
        if tag_name:
            query = query.join(Thread.tags).filter(Tags.name == tag_name)
        
        if category_id:
            query = query.filter(Thread.category_id == category_id)

        # 3. Search Logic
        if search:
            search_fmt = f"%{search}%"
            # Outerjoin để tìm kiếm không bị mất bài viết nếu chưa có tag/category
            query = query.outerjoin(Thread.category).outerjoin(Thread.tags)
            query = query.filter(
                or_(
                    Thread.title.ilike(search_fmt),
                    Thread.content.ilike(search_fmt),
                    Categories.name.ilike(search_fmt),
                    Tags.name.ilike(search_fmt)
                )
            )

        # 4. GROUP BY (Thay thế DISTINCT)
        # Bắt buộc dùng Group By nếu có join 1-N (Tags) hoặc Search để tránh lỗi logic SQL khi Sort
        if tag_name or search:
             query = query.group_by(Thread.thread_id)

        # 5. SORTING ALGORITHM
        if sort_by == "trending":
            # Logic: Chỉ tính điểm cho bài trong 7 ngày qua
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            # Dùng 'case' của SQL: Nếu bài cũ hơn 7 ngày -> điểm = 0
            is_recent = case((Thread.created_at >= seven_days_ago, 1), else_=0)
            
            # Công thức: (Upvote + Comment*2) * (1 hoặc 0)
            trending_score = (Thread.upvote_count + (Thread.comment_count * 2)) * is_recent
            
            query = query.order_by(desc(trending_score), desc(Thread.created_at))

        elif sort_by == "newest":
            query = query.order_by(desc(Thread.created_at))

        else: # "mix" (Mặc định)
            # Logic: Hackernews/Reddit simplify style
            # extract('epoch') đổi thời gian ra số giây
            post_time = func.extract('epoch', Thread.created_at)
            
            # 1 Upvote = "trẻ lại" 1 giờ (3600s), 1 Comment = 2 giờ
            bonus_time = (Thread.upvote_count * 3600) + (Thread.comment_count * 7200)
            
            mix_score = post_time + bonus_time
            query = query.order_by(desc(mix_score))

    
        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # 7. EXECUTE & PAGINATION
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        threads = result.unique().scalars().all()

        return {
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "data": threads
        }

    # --- 8. LẤY BÀI VIẾT CỦA USER (Profile) ---
    @staticmethod
    async def get_user_threads_by_page(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 10):
        query = select(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media),
            joinedload(Thread.user),
            joinedload(Thread.category)
        ).filter(Thread.user_id == user_id)
        
        query = query.order_by(Thread.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        threads = result.unique().scalars().all()

        return threads
    
   # --- 7. LẤY DANH SÁCH (FULL-TEXT SEARCH VECTOR) ---
    @staticmethod
    async def get_threads(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10, 
        category_id: Optional[str] = None,
        tag_name: Optional[str] = None,
        search: Optional[str] = None
    ):
        # 1. Base Query: Load các quan hệ để hiển thị
        query = select(Thread).options(
            joinedload(Thread.tags),
            joinedload(Thread.media),
            joinedload(Thread.user),
            joinedload(Thread.category)
        )

        # 2. Join bảng để phục vụ tìm kiếm/lọc
        # Dùng outerjoin để không bị mất bài viết nếu chưa có tag/category
        query = query.outerjoin(Thread.category).outerjoin(Thread.tags)

        # 3. Filter Cứng
        if category_id:
            query = query.filter(Thread.category_id == category_id)
        
        if tag_name:
            query = query.filter(Tags.name == tag_name)

        # 4. Global Search (ILIKE)
        if search:
            search_format = f"%{search}%"
            query = query.filter(
                or_(
                    Thread.title.ilike(search_format),
                    Thread.content.ilike(search_format),
                    Categories.name.ilike(search_format),
                    Tags.name.ilike(search_format)
                )
            )

        # 5. Sắp xếp & Phân trang
        if search:
            # ✅ Fix lỗi DISTINCT ON: order_by phải có cột distinct ở đầu
            query = query.distinct(Thread.thread_id).order_by(Thread.thread_id, desc(Thread.created_at))
        else:
            # Feed bình thường: chỉ cần order by ngày tạo
            query = query.order_by(desc(Thread.created_at))
        
        # 6. Đếm tổng (Subquery để đảm bảo chính xác với distinct/join)
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # 7. Lấy dữ liệu
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        threads = result.unique().scalars().all()

        return {
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "data": threads
        }
    # --- 9. CẢNH BÁO & KHÓA BÀI ---
    @staticmethod
    async def warn_and_lock_thread(
        db: AsyncSession, 
        thread_id: str, 
        reason: str, 
        performer_role: str
    ):
        # 1. Check quyền (như cũ)
        allowed_roles = ["ADMIN", "MODERATOR"]
        if performer_role.upper() not in allowed_roles:
            raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện hành động này")

        # 2. Tìm bài viết + User (như cũ)
        query = select(Thread).options(joinedload(Thread.user)).filter(Thread.thread_id == thread_id)
        result = await db.execute(query)
        thread = result.scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

        # 3. Khóa bài
        thread.is_locked = True
        await db.commit()

        # 4. Gửi Email (Cập nhật phần này) 👇
        if thread.user and thread.user.email:
            # Lấy tên hiển thị (ưu tiên full_name, nếu ko có thì dùng username)
            display_name = thread.user.full_name if thread.user.full_name else thread.user.username

            await EmailService.send_post_warning_email(
                email_to=thread.user.email,
                full_name=display_name,
                thread_title=thread.title, # Truyền tiêu đề bài viết
                reason=reason
            )

        return {
            "message": "Đã khóa bài viết và gửi email cảnh báo",
            "thread_id": thread.thread_id
        }