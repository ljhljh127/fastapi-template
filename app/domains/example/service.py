from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.pagination import PaginationParams
from app.domains.example.exceptions import ExampleNameConflictError, ExampleNotFoundError
from app.domains.example.models import Example
from app.domains.example.repository import ExampleRepository
from app.domains.example.schemas import ExampleCreate, ExampleUpdate


class ExampleService:
    """비즈니스 규칙과 트랜잭션 경계를 갖는다. commit은 이 레이어에서만 한다."""

    def __init__(self, db: Session, repository: ExampleRepository) -> None:
        self.db = db
        self.repository = repository

    def get(self, example_id: int) -> Example:
        example = self.repository.get(example_id)
        if example is None:
            raise ExampleNotFoundError(example_id)
        return example

    def list(self, params: PaginationParams) -> tuple[Sequence[Example], int]:
        return (
            self.repository.list(limit=params.limit, offset=params.offset),
            self.repository.count(),
        )

    def create(self, payload: ExampleCreate) -> Example:
        # unique 제약에 맡기면 IntegrityError가 500으로 샌다.
        if self.repository.get_by_name(payload.name) is not None:
            raise ExampleNameConflictError(payload.name)
        example = self.repository.add(Example(**payload.model_dump()))
        self.db.commit()
        self.db.refresh(example)
        return example

    def update(self, example_id: int, payload: ExampleUpdate) -> Example:
        """본문에 없는 필드는 건드리지 않는다. 이름을 자기 자신으로 바꾸는 건 충돌이 아니다."""
        example = self.get(example_id)
        changes = payload.model_dump(exclude_unset=True)

        new_name = changes.get("name")
        if new_name is not None and new_name != example.name:
            if self.repository.get_by_name(new_name) is not None:
                raise ExampleNameConflictError(new_name)

        for field, value in changes.items():
            setattr(example, field, value)

        self.db.commit()
        self.db.refresh(example)
        return example

    def delete(self, example_id: int) -> None:
        self.repository.delete(self.get(example_id))
        self.db.commit()
