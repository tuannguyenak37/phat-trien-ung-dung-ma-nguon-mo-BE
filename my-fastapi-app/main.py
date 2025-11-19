from fastapi import FastAPI
from app.router.user_router import user_router # Import file user_router.py# Khởi tạo ứng dụng
app = FastAPI()

# Định nghĩa một route (đường dẫn) cơ bản
@app.get("/")
def read_root():
    return {"message": "Xin chào, đây là FastAPI!"}

app.include_router(user_router, prefix="/api/users", tags=["user"])
# Định nghĩa route có tham số
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}