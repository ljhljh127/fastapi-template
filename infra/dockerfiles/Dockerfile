FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /workspace

# 의존성 레이어. app/ 없이 먼저 깔아야 코드 수정이 이 레이어를 무효화하지 않는다.
COPY pyproject.toml README.md ./
RUN mkdir app && touch app/__init__.py \
    && pip install . \
    && rm -rf build *.egg-info

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
RUN pip install --no-deps . \
    && rm -rf build *.egg-info

RUN useradd --create-home --uid 1000 app && chown -R app:app /workspace
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
