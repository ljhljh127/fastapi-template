# alembic autogenerate는 여기 import된 모델만 인식한다. 도메인을 추가하면 한 줄 추가.
from app.db.base import Base
from app.domains.example.models import Example

__all__ = ["Base", "Example"]
