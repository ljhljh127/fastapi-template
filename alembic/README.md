Generic single-database configuration.

## 사용방법
alembic에 대한 사용 방법을 명시하는 README 입니다.

## 테이블 정의 및 import
1. models/하위에 `from app.db.base_class import Base`를 Base로 하는 원하는 테이블의 class를 생성합니다.
2. db/base.py 파일에 만든 class를 import 합니다.


## 마이그레이션 및 리비전 생성
 `alembic revision --autogenerate -m "create 테이블명 tables"` 을 진행해 마이그레이션  
ex) `alembic revision --autogenerate -m "create example tables"`

### DB에 마이그레이션 적용
`alembic upgrade head`

### 이전 버전으로 되돌리기
`alembic downgrade -1`

