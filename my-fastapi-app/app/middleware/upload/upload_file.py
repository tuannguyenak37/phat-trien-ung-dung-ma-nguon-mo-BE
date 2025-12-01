import os
import aiofiles
from datetime import datetime
from uuid import uuid4
from fastapi import UploadFile, HTTPException, status
from typing import List

class FileUploader:
    def __init__(self, upload_dir: str = "static/uploads", allowed_extensions: list = None):
        self.upload_dir = upload_dir
        # Mặc định cho phép các đuôi file này
        self.allowed_extensions = allowed_extensions or ["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi","avif"]
        self.max_size_mb = 10 

    async def validate_file(self, file: UploadFile):
        """Kiểm tra đuôi file"""
        filename = file.filename
        if not filename:
             raise HTTPException(status_code=400, detail="Filename is missing")

        # Lấy đuôi file an toàn hơn
        extension = filename.split(".")[-1].lower() if "." in filename else ""
        
        if extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"File type '{extension}' not allowed. Allowed: {self.allowed_extensions}"
            )
        return True

    async def save_file(self, file: UploadFile) -> str:
        """Lưu 1 file và trả về đường dẫn tương đối"""
        await self.validate_file(file)

        # Tạo folder theo ngày: 2025/11/25
        today = datetime.now()
        # Sử dụng os.path.join để tạo đường dẫn thư mục vật lý (tránh lỗi Windows/Linux)
        relative_folder = os.path.join(str(today.year), f"{today.month:02d}", f"{today.day:02d}")
        full_dir_path = os.path.join(self.upload_dir, relative_folder)
        
        # Tạo thư mục nếu chưa có
        os.makedirs(full_dir_path, exist_ok=True)

        # Đổi tên file: uuid.ext
        extension = file.filename.split(".")[-1].lower()
        new_filename = f"{uuid4()}.{extension}"
        
        # Đường dẫn vật lý để lưu file
        file_path = os.path.join(full_dir_path, new_filename)

        # Ghi file async bằng aiofiles
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await file.read(1024 * 1024): # Đọc từng cục 1MB
                    await out_file.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
        
        # Reset con trỏ file
        await file.seek(0)

        # Trả về đường dẫn dạng URL (dùng dấu /) để lưu vào Database
        # Ví dụ: static/uploads/2025/11/25/abc-xyz.jpg
        # Lưu ý: f-string bên dưới dùng dấu / cứng để đảm bảo chuẩn URL
        return f"{self.upload_dir}/{today.year}/{today.month:02d}/{today.day:02d}/{new_filename}".replace("\\", "/")

    async def save_multiple_files(self, files: List[UploadFile]) -> List[str]:
        """Lưu danh sách file"""
        results = []
        for file in files:
            # Bỏ qua file rỗng nếu có
            if file.filename:
                path = await self.save_file(file)
                results.append(path)
        return results

# --- KHỞI TẠO INSTANCE ĐỂ DÙNG Ở NƠI KHÁC ---
# Đây là biến bạn sẽ import vào Service
upload_service = FileUploader()