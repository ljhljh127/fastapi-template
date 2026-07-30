from typing import Annotated

from fastapi import Depends

from app.db.deps import SessionDep
from app.domains.example.repository import ExampleRepository
from app.domains.example.service import ExampleService


def get_example_service(db: SessionDep) -> ExampleService:
    return ExampleService(db, ExampleRepository(db))


ExampleServiceDep = Annotated[ExampleService, Depends(get_example_service)]
