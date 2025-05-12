"""
app/db/session.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import conf

DATABASE_URL = (
    f"postgresql://{conf.db_user}:{conf.db_password_encoded()}"
    f"@{conf.db_host}:{conf.db_port}/{conf.db_name}"
)


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
