"""
/app/crud/example.py
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.example import Example
from app.schemas.example import ExampleCreate


# create
def create_example(db: Session, example: ExampleCreate) -> Example:
    """
    db create example 예제
    """
    db_example = Example(name=example.name)
    db.add(db_example)
    db.commit()
    # db.refresh는 커밋 후 최신 상태로 갱신
    db.refresh(db_example)
    return db_example


# read
def get_example(db: Session, example_id: int) -> Optional[Example]:
    """
    db get example 예제
    """
    return db.query(Example).filter(Example.id == example_id).first()


def get_examples(db: Session, skip: int = 0, limit: int = 100) -> List[Example]:
    """
    db get_examples 예제
    """
    return db.query(Example).offset(skip).limit(limit).all()


def get_example_by_name(db: Session, name: str) -> Optional[Example]:
    """
    db  get_example_by_name 예제
    """
    return db.query(Example).filter(Example.name == name).first()


# update
def update_example(
    db: Session, example_id: int, example: ExampleCreate
) -> Optional[Example]:
    """
    db update_example 예제
    """
    db_example = get_example(db, example_id)
    if db_example:
        db_example.name = example.name
        db.commit()
        db.refresh(db_example)
    return db_example


# delete
def delete_example(db: Session, example_id: int) -> bool:
    """
    db delete 예제
    """
    db_example = get_example(db, example_id)
    if db_example:
        db.delete(db_example)
        db.commit()
        return True
    return False
