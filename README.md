# FastAPI Template
fastapi-template


## 디렉토리 구조
```
app/
├── main.py                # FastAPI 애플리케이션 엔트리포인트
├── core/                  # 설정, 보안, 유틸성 모듈
│   └── config.py          # 환경 변수 로드, 전역 설정
├── db/
│   ├── base_class.py      # Base = declarative_base() 등
|   ├── base.py            # alembic 마이그레이션을 위해 테이블 import 하는 곳
│   └── session.py         # DB 연결 엔진, 세션 생성
├── env/
│   └── .env.dev           # config 설정을 하는 환경변수 파일 저장 디렉토리 
│
├── models/                # SQLAlchemy 모델 정의 (실질적 모델 테이블 정의)
│   ├── example.py
│   └── ...
├── schemas/               # Pydantic 스키마 (Request or Response Body 등등..)
│   ├── example.py
│   └── ...
├── crud/                  # DB 처리 로직 (Create, Read, Update, Delete)
│   ├── example.py
│   └── ...
└── api/
    ├─ deps.py             # db 세션을 공유해 쓰기 위해서 정의
    └── v1/                # 버전별 API (v1, v2 등)
        ├── endpoints/     # 실제 라우트(엔드포인트)들을 모아둔 디렉토리
        │   ├── example.py
        │   └── ...
        └── routers.py     # v1 라우터들을 모아 FastAPI에 등록하는 모듈


alembic/
├── versions/              # DB 마이그레이션 정보를 version 별로 관리
│   └── config.py     
└── env.py                 # alembic에 들어가는 각종 설정들을 관리하는 파일

infra/
├── compose/               # 각종 컴포즈 관련 파일이 저장 될 디렉토리
├── ├─ compose.yaml        # 컴포즈 파일   
│   ├── env.db             # 컴포즈 환경변수 중 노출하면 안될 정보가 담기는 env
│   └── ...
└── dockerfiles/           # 도커파일들이 저장 될 디렉토리  
```