"""统一错误结构：{"error": {"code", "message", "field"?}}，见公共设计约定 5.4。"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """业务错误。field 仅在错误能定位到请求字段时提供。"""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        field: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.field = field


def error_response(exc: ApiError) -> JSONResponse:
    payload: dict = {"code": exc.code, "message": exc.message}
    if exc.field:
        payload["field"] = exc.field
    return JSONResponse(
        status_code=exc.status_code, content={"error": payload}
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError):
        return error_response(exc)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError):
        # 把 FastAPI/Pydantic 的校验错误折叠成统一结构，取第一个错误定位字段。
        for item in exc.errors():
            field = ".".join(str(part) for part in item.get("loc", [])[1:])
            message = _validation_message(item, field)
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": message,
                        "field": field or None,
                    }
                },
            )
        return JSONResponse(
            status_code=422,
            content={
                "error": {"code": "VALIDATION_ERROR", "message": "请求参数无效"}
            },
        )

    @app.exception_handler(Exception)
    async def handle_internal(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": {"code": "INTERNAL_ERROR", "message": "系统内部错误，请稍后重试"}
            },
        )


def _validation_message(item: dict, field: str) -> str:
    """按字段给常见校验错误配中文说明。"""
    msg = str(item.get("msg", ""))
    # 自定义校验器抛出的 ValueError：消息形如 "Value error, 两次密码不一致"。
    if msg.startswith("Value error, "):
        return msg[len("Value error, "):]
    error_type = item.get("type")
    if error_type == "missing":
        return f"缺少必填字段 {field}" if field else "缺少必填字段"
    if error_type == "literal_error":
        return "取值无效，应为 public 或 private" if field == "visibility" else "取值无效"
    if "email" in msg.lower():
        return "邮箱格式无效"
    if "not a valid integer" in msg.lower() or error_type == "int_parsing":
        return "需为整数"
    return "请求字段校验失败"
