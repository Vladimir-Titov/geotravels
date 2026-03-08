from __future__ import annotations

from uuid import UUID

from litestar import Request
from litestar.exceptions import HTTPException

from app.services.auth import AuthService


def get_current_user_id(request: Request, auth_service: AuthService) -> UUID:
    authorization = request.headers.get('Authorization')
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization header')

    prefix, _, token = authorization.partition(' ')
    if prefix.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail='Invalid Authorization header')

    try:
        return auth_service.get_user_id_from_access_token(token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail='Invalid access token') from exc
