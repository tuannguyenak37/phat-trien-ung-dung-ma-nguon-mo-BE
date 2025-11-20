# app/router/user_router.py
from fastapi import APIRouter, Depends, status,Response
from sqlalchemy.orm import Session
# Dùng import tuyệt đối (app.) để tránh lỗi
from app.db.connection import get_db
from app.schemas.user import UserCreate, UserResponse,resposLogin,Login
from app.controller.user_controller import UserController


user_router  = APIRouter() 
# ---------------------------------------

@user_router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return UserController.create_user(db=db, user_data=user_data)

@user_router.post("/login",response_model=resposLogin,status_code=status.HTTP_200_OK)
def login(user_data:Login,db:Session=Depends(get_db),response: Response = Response()):
    return UserController.login_controller(db=db,user_data=user_data,response=response)