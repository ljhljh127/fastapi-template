"""
/app/models/example.py
"""

from sqlalchemy import Column, Integer, String

from app.db.base_class import Base


class Example(Base):
    """
    example DB 정의
    """

    __tablename__ = "example"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
