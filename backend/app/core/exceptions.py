from fastapi import Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base class for expected, user-facing errors."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotAuthenticatedError(DomainError):
    def __init__(self, message: str = "Não autenticado."):
        super().__init__(message, status_code=401)


class NotAuthorizedError(DomainError):
    def __init__(self, message: str = "Sem permissão para este recurso."):
        super().__init__(message, status_code=403)


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Nunca vazar detalhes internos (stack trace, queries, etc.) para o cliente.
    return JSONResponse(status_code=500, content={"detail": "Erro interno inesperado."})
