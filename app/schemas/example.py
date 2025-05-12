"""
/app/schemas/example.py
"""

from pydantic import BaseModel


class ExampleBase(BaseModel):
    """
    pydantic example base
    """

    name: str


class ExampleCreate(ExampleBase):
    """
    pydantic example create
    """


class ExampleRead(ExampleBase):
    """
    pydantic example read
    """

    id: int

    class Config:
        """
        객체의 속성(예: ORM 객체)에서 데이터를 읽어 Pydantic 모델을 생성할 수 있도록 허용
        """

        from_attributes = True
