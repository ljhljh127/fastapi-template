from collections.abc import Sequence
from typing import Annotated, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Query()를 빼면 쿼리 파라미터가 아니라 request body로 해석된다.
PaginationDep = Annotated[PaginationParams, Query()]


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PaginationParams) -> "Page[T]":
        return cls(items=list(items), total=total, limit=params.limit, offset=params.offset)
