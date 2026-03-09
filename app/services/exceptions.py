from __future__ import annotations


class ServiceError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class AuthenticationError(ServiceError):
    status_code = 401


class ConflictError(ServiceError):
    status_code = 409


class NotFoundError(ServiceError):
    status_code = 404


class AppError(ServiceError):
    status_code = 500
