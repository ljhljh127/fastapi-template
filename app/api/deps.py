"""
/app/api/deps.py
"""

from typing import Generator

from app.db.session import SessionLocal


# 의존성 주입을 통해서 DB 세션 공유
def get_db() -> Generator:
    """
    의존성 주입을 통해 DB 세션을 모든 api 라우트에서 공유
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # 리소스 반납
        db.close()
