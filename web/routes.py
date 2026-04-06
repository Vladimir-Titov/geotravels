from __future__ import annotations

from web.api import (
    auth_router,
    countries_router,
    files_router,
    followers_router,
    healthcheck_router,
    users_router,
    visits_router,
)

route_handlers = [
    auth_router,
    countries_router,
    users_router,
    followers_router,
    files_router,
    visits_router,
    healthcheck_router,
]
