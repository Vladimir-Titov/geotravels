from __future__ import annotations

from litestar import Litestar, Request
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Components, SecurityScheme

from app.repositories import CountriesRepository, UsersRepository, VisitsRepository
from app.services import AuthService, CountriesService, VisitsService
from app.services.current_user import CurrentUser
from helpers import DBPool, create_db_pool_from_settings
from settings import AppSettings, get_settings
from web.routes import route_handlers


def create_app(settings: AppSettings | None = None, db_pool: DBPool | None = None) -> Litestar:
    app_settings = settings or get_settings()

    async def startup(app: Litestar) -> None:
        app.state.db_pool = db_pool or await create_db_pool_from_settings(app_settings)

    async def shutdown(app: Litestar) -> None:
        if db_pool is None and hasattr(app.state, 'db_pool'):
            await app.state.db_pool.close()

    def provide_auth_service(request: Request) -> AuthService:
        users_repository = UsersRepository(request.app.state.db_pool)
        return AuthService(
            users_repository=users_repository,
            settings=app_settings,
        )

    def provide_countries_service(request: Request) -> CountriesService:
        countries_repository = CountriesRepository(request.app.state.db_pool)
        return CountriesService(
            countries_repository=countries_repository,
            settings=app_settings,
        )

    def provide_visits_service(request: Request) -> VisitsService:
        visits_repository = VisitsRepository(request.app.state.db_pool)
        countries_repository = CountriesRepository(request.app.state.db_pool)
        return VisitsService(
            visits_repository=visits_repository,
            countries_repository=countries_repository,
        )

    def provide_current_user(request: Request, auth_service: AuthService) -> CurrentUser:
        authorization = request.headers.get('Authorization', '')
        if not authorization:
            raise HTTPException(status_code=401, detail='Missing Authorization header')

        prefix, _, token = authorization.partition(' ')
        if prefix.lower() != 'bearer' or not token:
            raise HTTPException(status_code=401, detail='Invalid Authorization header')

        try:
            user_id = auth_service.get_user_id_from_access_token(token)  # todo: handle if token expired
            return CurrentUser(id=user_id)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=401, detail='Invalid access token') from exc

    app = Litestar(
        route_handlers=route_handlers,
        on_startup=[startup],
        on_shutdown=[shutdown],
        openapi_config=OpenAPIConfig(
            title='GeoTravels API',
            version='1.0.0',
            components=Components(
                security_schemes={
                    'user_auth': SecurityScheme(type='http', scheme='bearer', bearer_format='JWT'),
                }
            ),
        ),
        dependencies={
            'auth_service': Provide(provide_auth_service, sync_to_thread=False),
            'countries_service': Provide(provide_countries_service, sync_to_thread=False),
            'visits_service': Provide(provide_visits_service, sync_to_thread=False),
            'current_user': Provide(provide_current_user, sync_to_thread=False),
        },
    )

    app.state.settings = app_settings

    return app


app = create_app()
