from web.api.auth import auth_router
from web.api.countries import countries_router
from web.api.healthcheck import healthcheck_router
from web.api.users import users_router
from web.api.visits import visits_router

__all__ = ['auth_router', 'countries_router', 'users_router', 'visits_router', 'healthcheck_router']
