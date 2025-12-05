from fastapi import APIRouter, Depends, status, Response, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession # <--- Dùng AsyncSession
from typing import Dict

# 1. Đổi import connection
from app.db.connection import get_async_db 
from app.schemas.user import (
    UserCreate, UserResponse, resposLogin, Login, 
    UpdateAvatarRequest, UpdateBackgroundRequest, 
    UpdateInfoRequest, ChangePasswordRequest, ChangeEmailRequest
)
from app.controller.user_controller import UserController
from app.services.user_service import UserService
from app.middleware.upload.upload_file import upload_service
from app.middleware.JWT.auth import get_current_user

user_router = APIRouter() 

# ---------------------------------------

# 1. Đăng ký
@user_router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, 
    db: AsyncSession = Depends(get_async_db) # <--- Async DB
):
    # Nhớ thêm await
    return await UserController.create_user(db=db, user_data=user_data)

# 2. Đăng nhập
@user_router.post("/login", response_model=resposLogin, status_code=status.HTTP_200_OK)
async def login(
    user_data: Login, 
    response: Response,
    db: AsyncSession = Depends(get_async_db)
):
    # Nhớ thêm await
    return await UserController.login_controller(db=db, user_data=user_data, response=response)


# --- 3. API Đổi Avatar ---
@user_router.put("/me/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db), 
    current_user = Depends(get_current_user)
):
    # Upload file (đã là async sẵn)
    url_path = await upload_service.save_file(file)
    data = UpdateAvatarRequest(url_avatar=url_path)
    
    # Gọi Service update (thêm await)
    return await UserService.update_avatar(db, current_user["user_id"], data)


# --- 4. API Đổi Background ---
@user_router.put("/me/background")
async def update_background(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db), 
    current_user = Depends(get_current_user)
):
    url_path = await upload_service.save_file(file)
    data = UpdateBackgroundRequest(url_background=url_path)
    
    return await UserService.update_background(db, current_user["user_id"], data)


# --- 5. API Đổi Thông tin cá nhân ---
@user_router.put("/me/info")
async def update_info(
    data: UpdateInfoRequest, 
    db: AsyncSession = Depends(get_async_db), 
    current_user = Depends(get_current_user)
):
    return await UserService.update_info(db, current_user["user_id"], data)


# --- 6. API Đổi Mật khẩu ---
@user_router.put("/me/password")
async def change_password(
    data: ChangePasswordRequest, 
    db: AsyncSession = Depends(get_async_db), 
    current_user = Depends(get_current_user)
):
    return await UserService.change_password(db, current_user["user_id"], data)


# --- 7. API Đổi Email ---
@user_router.put("/me/email")
async def change_email(
    data: ChangeEmailRequest, 
    db: AsyncSession = Depends(get_async_db), 
    current_user = Depends(get_current_user)
):
    return await UserService.change_email(db, current_user["user_id"], data)