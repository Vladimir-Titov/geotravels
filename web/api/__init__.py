from web.api.achievements import achievements_router
from web.api.auth import auth_router
from web.api.client_geo import client_geo_router
from web.api.countries import countries_router
from web.api.files import files_router
from web.api.followers import followers_router
from web.api.healthcheck import healthcheck_router
from web.api.users import users_router
from web.api.visits import visits_router

__all__ = [
    'auth_router',
    'achievements_router',
    'client_geo_router',
    'countries_router',
    'files_router',
    'followers_router',
    'users_router',
    'visits_router',
    'healthcheck_router',
]
