from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# Import async
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import settings  

engine = create_engine(settings.DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================
# 2. SETUP CHO ASYNC (Code mới)
# ============================
# Dùng thuộc tính DB_URL_ASYNC chúng ta vừa tạo (postgresql+asyncpg://...)
async_engine = create_async_engine(
    settings.DB_URL_ASYNC, # <--- Tự động lấy URL chuẩn Async
    echo=False, 
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ============================
# 3. BASE & DEPENDENCY
# ============================
Base = declarative_base()

# Dependency cho Sync (DB cũ)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency cho Async (DB mới - Dùng cho Router ban-account)
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()