from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.example.models import Example


class ExampleRepository:
    """쿼리와 flush까지만 한다. 여기서 commit하면 트랜잭션 경계가 깨진다."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, example_id: int) -> Example | None:
        return self.db.get(Example, example_id)

    def get_by_name(self, name: str) -> Example | None:
        return self.db.scalar(select(Example).where(Example.name == name))

    def list(self, limit: int, offset: int) -> Sequence[Example]:
        statement = select(Example).order_by(Example.id).limit(limit).offset(offset)
        return self.db.scalars(statement).all()

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Example)) or 0

    def add(self, example: Example) -> Example:
        self.db.add(example)
        self.db.flush()
        return example

    def delete(self, example: Example) -> None:
        self.db.delete(example)
        self.db.flush()
