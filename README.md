# FastAPI Template

FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL 서비스 템플릿.
도메인 단위 수직 슬라이스 구조를 따른다.

## 요구사항

- Python 3.12+
- Docker / Docker Compose

## 빠른 시작 (Docker)

```bash
cp .env.example .env
cp infra/compose/.env.db.example infra/compose/.env.db

docker compose -f infra/compose/compose.yaml up -d --build
docker compose -f infra/compose/compose.yaml exec was alembic upgrade head
```

- API: http://localhost:8000/api/v1
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

`.env`의 `DB_HOST`는 컨테이너 안에서 compose가 `postgres`로 덮어쓴다. 로컬 실행 시에만 `localhost`가 쓰인다.

## 빠른 시작 (로컬)

```bash
python -m venv .venv && source .venv/bin/activate
make install       # pip install -e ".[dev]" + pre-commit install

cp .env.example .env
docker compose -f infra/compose/compose.yaml up -d postgres

make migrate       # alembic upgrade head
make run           # uvicorn --reload
```

## 디렉토리 구조

```
app/
├── main.py                     FastAPI 앱 팩토리
├── core/
│   ├── config.py               환경변수 로드, 설정 검증
│   ├── logging.py              로깅 설정, request_id 컨텍스트
│   ├── exceptions.py           도메인 예외 기반 클래스, 전역 핸들러
│   ├── middleware.py           request_id 발급, 액세스 로그
│   └── pagination.py           Page[T], PaginationParams
├── db/
│   ├── base.py                 DeclarativeBase, TimestampMixin, 제약조건 명명 규칙
│   ├── session.py              엔진, 세션 팩토리
│   ├── deps.py                 SessionDep
│   └── registry.py             alembic autogenerate용 모델 취합
├── api/
│   ├── health.py               liveness / readiness
│   └── v1.py                   v1 라우터 취합
└── domains/                    도메인 1개 = 디렉토리 1개
    └── example/                참조 구현. 파생 프로젝트는 rename 또는 삭제한다
        ├── models.py           SQLAlchemy 모델
        ├── schemas.py          Pydantic 스키마
        ├── repository.py       select / flush 까지만
        ├── service.py          비즈니스 규칙, 트랜잭션 경계
        ├── exceptions.py       도메인 예외
        ├── deps.py             서비스 주입
        └── router.py           엔드포인트

alembic/versions/               마이그레이션
tests/
├── conftest.py                 SQLite 인메모리 엔진, get_db 오버라이드
├── test_health.py
├── test_error_handling.py      미처리 예외 응답 포맷, debug 모드 유출 방지
├── test_pagination.py          Page 봉투, limit/offset 경계값
└── domains/example/            example 도메인 API 테스트
infra/compose/                  compose.yaml, .env.db
infra/dockerfiles/              Dockerfile
```

## 레이어 규칙

| 레이어 | 책임 | 금지 |
|---|---|---|
| `router` | 요청/응답 변환, 상태코드 | 비즈니스 로직, ORM 직접 접근 |
| `service` | 비즈니스 규칙, `commit`/`rollback` | HTTP 개념 (`HTTPException` 등) |
| `repository` | 쿼리, `flush` | `commit`, 비즈니스 분기 |

HTTP 상태코드는 `app/core/exceptions.py`의 예외 클래스가 결정한다.
서비스가 `NotFoundError` 계열을 던지면 전역 핸들러가 응답으로 변환한다.
`router`에서 `HTTPException`을 직접 던지지 않는다.

## example 도메인 처리

`app/domains/example/`은 위 규칙을 그대로 보여주는 참조 구현이다.
첫 도메인이 필요하면 삭제보다 rename을 권한다. 배선이 이미 되어 있다.

```bash
git mv app/domains/example app/domains/order
git mv tests/domains/example tests/domains/order
# Example -> Order 일괄 치환, 0001 마이그레이션 재생성
```

삭제할 경우 4곳을 함께 정리한다. 4번을 빠뜨리면 쓰지 않는 `example` 테이블이 생성된다.

```
1. rm -rf app/domains/example tests/domains/example
2. app/db/registry.py  ->  Example import 삭제
3. app/api/v1.py       ->  example_router 등록 삭제
4. rm alembic/versions/0001_create_example_table.py
```

## 도메인 추가

`app/domains/<name>/`을 만들고 아래 6개 파일을 둔다. `example/`을 복사하는 것이 가장 빠르다.

```
models.py       SQLAlchemy 모델. app/db/base.py의 Base, TimestampMixin 상속
schemas.py      Pydantic 스키마. Create / Update / Read 분리
repository.py   select / flush 까지만. commit 금지
service.py      비즈니스 규칙과 트랜잭션 경계. commit은 여기서만
exceptions.py   app/core/exceptions.py의 NotFoundError, ConflictError 상속
router.py       엔드포인트. service 호출과 응답 변환만
```

각 레이어 골격:

```python
# models.py
class Order(TimestampMixin, Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, index=True)


# repository.py
class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, order_id: int) -> Order | None:
        return self.db.get(Order, order_id)

    def add(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order


# service.py
class OrderService:
    def __init__(self, db: Session, repository: OrderRepository) -> None:
        self.db = db
        self.repository = repository

    def get(self, order_id: int) -> Order:
        order = self.repository.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order


# deps.py
def get_order_service(db: SessionDep) -> OrderService:
    return OrderService(db, OrderRepository(db))


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


# router.py
router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, service: OrderServiceDep) -> OrderRead:
    return OrderRead.model_validate(service.get(order_id))


@router.get("", response_model=Page[OrderRead])
def list_orders(pagination: PaginationDep, service: OrderServiceDep) -> Page[OrderRead]:
    orders, total = service.list(pagination)
    return Page.create([OrderRead.model_validate(o) for o in orders], total, pagination)
```

배선 3곳을 잊지 않는다.

```
1. app/db/registry.py  →  from app.domains.order.models import Order 추가
                          (빠뜨리면 alembic autogenerate가 테이블을 못 만든다)
2. app/api/v1.py       →  api_router.include_router(order_router)
3. alembic revision --autogenerate -m "create order table"
```

## 에러 응답 형식

```json
{
  "error": {
    "code": "order_not_found",
    "message": "Order 9999 does not exist.",
    "details": { "order_id": 9999 }
  },
  "request_id": "8f14e45fceea167a5a36dedd4bea2543"
}
```

`request_id`는 미처리 500에서도 유지되고 `X-Request-ID` 응답 헤더로도 나간다.
클라이언트가 `X-Request-ID`를 보내면 그 값을 이어받으므로 로그와 바로 대조된다.

## 환경변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `APP_NAME` | `fastapi-template` | OpenAPI 문서 제목 |
| `APP_ENV` | `local` | `local` / `dev` / `prod` |
| `DEBUG` | `false` | `prod`에서 `true`면 기동 실패 |
| `LOG_LEVEL` | `INFO` | 루트 로거 레벨 |
| `API_V1_PREFIX` | `/api/v1` | v1 라우터 prefix |
| `CORS_ORIGINS` | `[]` | JSON 배열. 비어 있으면 미들웨어 미등록 |
| `DB_HOST` | `localhost` | |
| `DB_PORT` | `5432` | |
| `DB_USER` | `postgres` | |
| `DB_PASSWORD` | `postgres` | `prod`에서 기본값이면 기동 실패 |
| `DB_NAME` | `app` | |
| `DB_POOL_SIZE` | `5` | |
| `DB_MAX_OVERFLOW` | `10` | |
| `DB_POOL_RECYCLE` | `1800` | 커넥션 재생성 주기(초) |
| `DB_ECHO` | `false` | SQL 로깅 |

`APP_ENV=prod`에서는 `/docs`, `/redoc`, `/openapi.json`이 비활성화된다.

## 마이그레이션

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
alembic check
```

`alembic check`은 모델과 마이그레이션의 불일치를 검출한다. DB를 띄운 상태에서 돌린다.

## 테스트 / 린트

```bash
make fmt      # black + isort
make lint     # black/isort 검사 + pylint + mypy
make test     # pytest
make check    # lint + test
```

품질 게이트는 pre-commit이 커밋 시점에 강제한다. `make install`이 훅을 등록하며,
이후 모든 커밋에서 포맷·pylint·mypy·pytest가 돌고 하나라도 실패하면 커밋이 거부된다.

`mypy`는 `app`에 strict를 적용한다. 타입 힌트는 실행 시 검사되지 않으므로
`None` 처리 누락 같은 결함은 mypy만 잡는다. pylint는 이름 규칙·구조를 본다.

테스트는 SQLite 인메모리를 사용하므로 PostgreSQL 없이 실행된다.
PostgreSQL 전용 타입을 쓰기 시작하면 `tests/conftest.py`의 엔진을 교체해야 한다.

## 구조 확장 기준

도메인이 20개를 넘거나 도메인 간 의존이 순환하기 시작하면
`app/domains/<bounded-context>/<domain>/` 2단 구조로 분리를 검토한다.
