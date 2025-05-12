"""
/app/api/v1/endpoints.py
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.example import (
    create_example,
    delete_example,
    get_example,
    get_example_by_name,
    get_examples,
    update_example,
)
from app.schemas.example import ExampleCreate, ExampleRead

router = APIRouter()


@router.post("/", response_model=ExampleRead)
def create_example_endpoint(example: ExampleCreate, db: Session = Depends(get_db)):
    """
    api post endpoint : create_example_endpoint
    """

    db_example = get_example_by_name(db, name=example.name)
    if db_example:
        raise HTTPException(status_code=400, detail="이미 존재하는 예제 이름입니다")
    return create_example(db=db, example=example)


@router.get("/", response_model=List[ExampleRead])
def read_examples_endpoint(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    api get endpoint : read_examples_endpoint
    """
    tests = get_examples(db, skip=skip, limit=limit)
    return tests


@router.get("/{example_id}", response_model=ExampleRead)
def read_example_endpoint(example_id: int, db: Session = Depends(get_db)):
    """
    api get endpoint : read_example_endpoint
    """
    db_example = get_example(db, example_id=example_id)
    if db_example is None:
        raise HTTPException(status_code=404, detail="예제를 찾을 수 없습니다")
    return db_example


@router.put("/{example_id}", response_model=ExampleRead)
def update_example_endpoint(
    example_id: int, example: ExampleCreate, db: Session = Depends(get_db)
):
    """
    api put endpoint : update_example_endpoint
    """
    db_example = update_example(db, example_id=example_id, example=example)
    if db_example is None:
        raise HTTPException(status_code=404, detail="예제를 찾을 수 없습니다")
    return db_example


@router.delete("/{example_id}")
def delete_example_ednpoint(example_id: int, db: Session = Depends(get_db)):
    """
    api delete endpoint : delete_example_ednpoint
    """
    success = delete_example(db, example_id=example_id)
    if not success:
        raise HTTPException(status_code=404, detail="예제를 찾을 수 없습니다")
    return {"detail": f"삭제되었습니다 id:{example_id}"}
