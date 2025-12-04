# app/router/user_router.py
from fastapi import APIRouter, Depends, status,Response
from sqlalchemy.orm import Session
# Dùng import tuyệt đối (app.) để tránh lỗi
from app.db.connection import get_db,get_async_db
from app.schemas.user import UserCreate, UserResponse,resposLogin,Login,UpdateAvatarRequest, UpdateBackgroundRequest,  UpdateInfoRequest, ChangePasswordRequest, ChangeEmailRequest
from app.controller.user_controller import UserController
from fastapi import APIRouter, Depends, UploadFile, File
from typing import Dict
from app.middleware.upload.upload_file import upload_service
from app.middleware.JWT.auth import get_current_user, get_current_user_or_guest
from ..services.user_service import UserService


user_router  = APIRouter() 
# ---------------------------------------

@user_router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return UserController.create_user(db=db, user_data=user_data)

@user_router.post("/login",response_model=resposLogin,status_code=status.HTTP_200_OK)
def login(user_data:Login,db:Session=Depends(get_db),response: Response = Response()):
    return UserController.login_controller(db=db,user_data=user_data,response=response)


# --- 1. API Đổi Avatar ---
@user_router.put("/me/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    url_path = await upload_service.save_file(file)
    data = UpdateAvatarRequest(url_avatar=url_path)
    
    # SỬA Ở ĐÂY: Dùng ["user_id"] thay vì .user_id
    return UserService.update_avatar(db, current_user["user_id"], data)


# --- 2. API Đổi Background ---
@user_router.put("/me/background")
async def update_background(
    file: UploadFile = File(...),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    url_path = await upload_service.save_file(file)
    data = UpdateBackgroundRequest(url_background=url_path)
    
    # SỬA Ở ĐÂY
    return UserService.update_background(db, current_user["user_id"], data)




@user_router.put("/me/info")
def update_info(
    data: UpdateInfoRequest, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    return UserService.update_info(db, current_user["user_id"], data)


# --- 4. API Đổi Mật khẩu ---
@user_router.put("/me/password")
def change_password(
    data: ChangePasswordRequest, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    # SỬA Ở ĐÂY
    return UserService.change_password(db, current_user["user_id"], data)


# --- 5. API Đổi Email ---
@user_router.put("/me/email")
def change_email(
    data: ChangeEmailRequest, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    # SỬA Ở ĐÂY
    return UserService.change_email(db, current_user["user_id"], data)