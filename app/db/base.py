"""
/app/db/base.py
"""

# alembic 마이그레이션에 필요한 테이블을 이쪽에 import
from app.db.base_class import Base  # pylint: disable=unused-import
from app.models.example import Example  # pylint: disable=unused-import
