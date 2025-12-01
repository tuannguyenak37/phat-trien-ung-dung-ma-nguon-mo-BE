from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router.user_router import user_router
from app.middleware.JWT.refresh_token import router_token
from app.router.category_router import router
from app.router.thread_router import router_thead
from app.router.public_router import router_public
app = FastAPI()
from fastapi.staticfiles import StaticFiles
from app.router.vote import router as router_vote
from app.router.comment_router import router as router_cmt
# Cấu hình CORS
origins = [
    "http://localhost:3000",  # URL front-end của bạn
    "http://127.0.0.1:3000",  # Thêm nếu cần
    # "https://my-frontend.com" # URL deploy production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Cho phép các domain này
    allow_credentials=True, #cho phép cooki
    allow_methods=["*"],  # Cho phép GET, POST, PUT, DELETE,...
    allow_headers=["*"],  # Cho phép tất cả headers
)

# Routes cơ bản
@app.get("/")
def read_root():
    return {"message": "Xin chào, đây là FastAPI!"}

# Include router
app.include_router(user_router, prefix="/api/users", tags=["user"])
app.include_router(router_token,prefix="/api/token",tags=["token"])
app.include_router(router_public, prefix="/api", tags=["public"])
app.include_router(router_thead, prefix="/api", tags=["threads"])
app.include_router(router, prefix="/api/catcategory", tags=["category"])
app.include_router(router_cmt, prefix="/api/cmt")
app.include_router(router_vote,prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route có tham số
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
