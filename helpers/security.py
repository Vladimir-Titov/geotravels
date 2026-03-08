from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError


class TokenError(ValueError):
    pass


def hash_password(password: str) -> str:
    # MVP decision: SHA-256 without salt. Replace with Argon2id in next iteration.
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def encode_token(
    subject: str,
    token_type: str,
    secret: str,
    algorithm: str,
    ttl: timedelta,
) -> str:
    now = datetime.now(tz=UTC)
    payload: dict[str, Any] = {
        'sub': subject,
        'type': token_type,
        'iat': int(now.timestamp()),
        'exp': int((now + ttl).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(token: str, secret: str, algorithm: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
    except InvalidTokenError as exc:  # pragma: no cover - external lib path
        raise TokenError('Invalid token') from exc

    if 'sub' not in payload or 'type' not in payload:
        raise TokenError('Token payload is missing required claims')

    return payload
