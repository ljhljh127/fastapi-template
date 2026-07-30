from fastapi import APIRouter, status

from app.core.pagination import Page, PaginationDep
from app.domains.example.deps import ExampleServiceDep
from app.domains.example.schemas import ExampleCreate, ExampleRead, ExampleUpdate

router = APIRouter(prefix="/examples", tags=["examples"])


@router.post("", response_model=ExampleRead, status_code=status.HTTP_201_CREATED)
def create_example(payload: ExampleCreate, service: ExampleServiceDep) -> ExampleRead:
    return ExampleRead.model_validate(service.create(payload))


@router.get("", response_model=Page[ExampleRead])
def list_examples(pagination: PaginationDep, service: ExampleServiceDep) -> Page[ExampleRead]:
    examples, total = service.list(pagination)
    return Page.create(
        [ExampleRead.model_validate(example) for example in examples], total, pagination
    )


@router.get("/{example_id}", response_model=ExampleRead)
def get_example(example_id: int, service: ExampleServiceDep) -> ExampleRead:
    return ExampleRead.model_validate(service.get(example_id))


@router.patch("/{example_id}", response_model=ExampleRead)
def update_example(
    example_id: int, payload: ExampleUpdate, service: ExampleServiceDep
) -> ExampleRead:
    return ExampleRead.model_validate(service.update(example_id, payload))


@router.delete("/{example_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_example(example_id: int, service: ExampleServiceDep) -> None:
    service.delete(example_id)
