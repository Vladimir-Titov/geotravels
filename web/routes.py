from __future__ import annotations

from web.api import auth_router, countries_router, healthcheck_router, visits_router

route_handlers = [auth_router, countries_router, visits_router, healthcheck_router]
