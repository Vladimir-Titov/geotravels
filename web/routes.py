from __future__ import annotations

from web.api import (
    achievements_router,
    auth_router,
    countries_router,
    followers_router,
    healthcheck_router,
    users_router,
    visits_router,
)

route_handlers = [
    auth_router,
    achievements_router,
    countries_router,
    users_router,
    followers_router,
    visits_router,
    healthcheck_router,
]
