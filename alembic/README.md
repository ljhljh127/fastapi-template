Generic single-database configuration.

## 접속 정보

`alembic.ini`의 `sqlalchemy.url`은 비워 두고 `env.py`가 `app.core.config`에서 주입한다.
따라서 `alembic` 명령은 앱과 동일한 환경변수(`DB_HOST`, `DB_USER` 등)를 읽는다.

## 모델 등록

`app/db/registry.py`에 모델을 import 해야 autogenerate가 인식한다.
빠뜨리면 리비전이 빈 파일로 생성되거나 테이블을 drop 하려 한다.

```python
from app.db.base import Base
from app.domains.order.models import Order

__all__ = ["Base", "Order"]
```

## 리비전 생성 및 적용

```bash
alembic revision --autogenerate -m "create order table"
alembic upgrade head
alembic downgrade -1
```

생성된 파일은 반드시 열어서 확인한다. autogenerate는 타입 변경과
server_default 변경을 놓치는 경우가 있다.

## 드리프트 검사

```bash
alembic check
```

모델과 마이그레이션이 어긋나면 실패한다. 리비전을 만들었으면 커밋 전에 한 번 돌린다.

## 제약조건 이름

`app/db/base.py`의 명명 규칙에 따라 `pk_`, `uq_`, `ix_`, `fk_`, `ck_` 접두어가 붙는다.
마이그레이션에서 제약조건을 다룰 때는 `op.f("uq_order_code")`처럼 감싼다.
