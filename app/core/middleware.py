import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.exceptions import AppError, error_response
from app.core.logging import request_id_ctx

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
PROCESS_TIME_HEADER = "X-Process-Time-Ms"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """로그와 에러 응답이 같은 request_id를 쓰게 한다. 클라이언트가 X-Request-ID를 보내면 그 값을 이어받는다."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        token = request_id_ctx.set(request_id)
        started = time.perf_counter()
        try:
            # ServerErrorMiddleware가 이 미들웨어보다 바깥이라, 거기까지 예외가 올라가면
            # request_id가 이미 reset된 뒤에 응답이 만들어지고 헤더도 붙지 않는다.
            # debug=True일 때는 스택트레이스가 그대로 나가기도 해서 여기서 잡는다.
            try:
                response = await call_next(request)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Unhandled error on %s %s", request.method, request.url.path)
                response = error_response(500, "internal_error", AppError.message)

            elapsed_ms = (time.perf_counter() - started) * 1000
            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers[PROCESS_TIME_HEADER] = f"{elapsed_ms:.2f}"
            logger.info(
                "%s %s %s %.2fms",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )
            return response
        finally:
            request_id_ctx.reset(token)
