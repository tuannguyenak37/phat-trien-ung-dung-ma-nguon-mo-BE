from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# 1. Tạo Engine
engine = create_engine(settings.DB_URL)

# 2. Tạo SessionLocal (Nhà máy tạo phiên làm việc)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Tạo Base (Lớp cha cho các Model)
Base = declarative_base()

# 4. Dependency (Hàm cấp phát DB cho Router)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()