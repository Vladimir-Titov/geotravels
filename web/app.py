from __future__ import annotations

import logging
from typing import Any

import aiohttp
from litestar import Litestar, MediaType, Request, Response
from litestar.config.cors import CORSConfig
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.logging.config import LoggingConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Components, SecurityScheme
from litestar.plugins.prometheus import PrometheusConfig, PrometheusController
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from app.repositories import (
    AchievementsRepository,
    CitiesRepository,
    CountriesRepository,
    DashboardRepository,
    FilesRepository,
    FollowersRepository,
    OtpRequestsRepository,
    UsersAchievementsRepository,
    UsersRepository,
    VisitsChecklistRepository,
    VisitsCitiesRepository,
    VisitsPlacesFilesRepository,
    VisitsPlacesRepository,
    VisitsRepository,
)
from app.repositories.telegram_users import TelegramUsersRepository
from app.services import (
    AchievementsService,
    AuthService,
    ClientGeoSearchService,
    CountriesService,
    DashboardService,
    FilesService,
    FollowersService,
    UsersService,
    VisitsChecklistService,
    VisitsPlacesFilesService,
    VisitsPlacesService,
    VisitsService,
)
from app.services.current_user import CurrentUser
from app.services.exceptions import AppError, ServiceError
from app.services.file_storage import FileStorage, S3FileStorage
from app.services.geonames import GeoNamesClient
from app.services.otp_sender import ResendOTPSender
from helpers import DBPool, create_db_pool_from_settings
from settings import AppSettings, LogSettings, get_settings
from web.routes import route_handlers

logger = logging.getLogger(__name__)


def _service_error_response(exc: ServiceError) -> Response[dict[str, Any]]:
    return Response(
        content={'status_code': exc.status_code, 'detail': exc.detail},
        status_code=exc.status_code,
        media_type=MediaType.JSON,
    )


def _service_error_handler(_request: Request, exc: ServiceError) -> Response[dict[str, Any]]:
    return _service_error_response(exc)


def _internal_exception_handler(_request: Request, _exc: Exception) -> Response[dict[str, Any]]:
    return _service_error_response(AppError('Internal Server Error'))


def build_logging_config(log_settings: LogSettings) -> LoggingConfig:
    level = log_settings.log_level.upper()

    loggers: dict[str, dict] = {
        'uvicorn': {'level': level, 'handlers': ['console'], 'propagate': False},
        'uvicorn.error': {'level': level, 'handlers': ['console'], 'propagate': False},
        'uvicorn.access': {'level': 'INFO', 'handlers': ['access_console'], 'propagate': False},
        'litestar': {'level': level, 'handlers': ['console'], 'propagate': False},
        'geotravels.sql': {'level': level, 'handlers': ['console'], 'propagate': False},
        'faker': {'level': 'WARNING', 'handlers': ['console'], 'propagate': False},
        'faker.factory': {'level': 'WARNING', 'handlers': ['console'], 'propagate': False},
    }

    for module, module_level in log_settings.log_module_levels.items():
        loggers[module] = {'level': module_level.upper(), 'handlers': ['console'], 'propagate': True}

    return LoggingConfig(
        root={'level': level, 'handlers': ['console']},
        formatters={
            'generic': {
                'format': '%(asctime)s (%(name)s)[%(levelname)s] %(message)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
                'class': 'logging.Formatter',
            },
            'access': {
                '()': 'uvicorn.logging.AccessFormatter',
                'format': '%(asctime)s (%(name)s)[%(levelname)s] %(client_addr)s "%(request_line)s" %(status_code)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
            },
        },
        handlers={
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': 'ext://sys.stdout',
            },
            'access_console': {
                'class': 'logging.StreamHandler',
                'formatter': 'access',
                'stream': 'ext://sys.stdout',
            },
        },
        loggers=loggers,
    )


def create_app(
    settings: AppSettings | None = None,
    db_pool: DBPool | None = None,
    file_storage: FileStorage | None = None,
    http_session: aiohttp.ClientSession | None = None,
) -> Litestar:
    app_settings = settings or get_settings()

    async def startup(app: Litestar) -> None:
        app.state.http_client_session = http_session or aiohttp.ClientSession()
        app.state.db_pool = db_pool or await create_db_pool_from_settings(app_settings)
        app.state.file_storage = file_storage or S3FileStorage(settings=app_settings.storage)
        app.state.geonames_client = GeoNamesClient(
            username=app_settings.client_geo.geonames_username,
            base_url=app_settings.client_geo.geonames_base_url,
            timeout_seconds=app_settings.client_geo.geonames_timeout_seconds,
            session=app.state.http_client_session,
        )

    async def shutdown(app: Litestar) -> None:
        if http_session is None and hasattr(app.state, 'http_client_session'):
            await app.state.http_client_session.close()
        if db_pool is None and hasattr(app.state, 'db_pool'):
            await app.state.db_pool.close()

    def provide_auth_service(request: Request) -> AuthService:
        db_pool = request.app.state.db_pool
        return AuthService(
            users_repository=UsersRepository(db_pool),
            telegram_users_repository=TelegramUsersRepository(db_pool),
            otp_requests_repository=OtpRequestsRepository(db_pool),
            otp_sender=ResendOTPSender(
                api_key=app_settings.otp.resend_api_key,
                email_from=app_settings.otp.resend_email_from,
            ),
            settings=app_settings,
        )

    def provide_countries_service(request: Request) -> CountriesService:
        countries_repository = CountriesRepository(request.app.state.db_pool)
        return CountriesService(countries_repository=countries_repository)

    def provide_client_geo_search_service(request: Request) -> ClientGeoSearchService:
        db_pool = request.app.state.db_pool
        return ClientGeoSearchService(
            countries_repository=CountriesRepository(db_pool),
            cities_repository=CitiesRepository(db_pool),
            geonames_client=request.app.state.geonames_client,
        )

    def provide_achievements_service(request: Request) -> AchievementsService:
        achievements_repository = AchievementsRepository(request.app.state.db_pool)
        users_achievements_repository = UsersAchievementsRepository(request.app.state.db_pool)
        return AchievementsService(
            achievements_repository=achievements_repository,
            users_achievements_repository=users_achievements_repository,
        )

    def provide_users_service(request: Request) -> UsersService:
        users_repository = UsersRepository(request.app.state.db_pool)
        return UsersService(users_repository=users_repository)

    def provide_visits_service(request: Request) -> VisitsService:
        db_pool = request.app.state.db_pool
        return VisitsService(
            visits_repository=VisitsRepository(db_pool),
            visits_cities_repository=VisitsCitiesRepository(db_pool),
            files_repository=FilesRepository(db_pool),
        )

    def provide_visits_checklist_service(request: Request) -> VisitsChecklistService:
        db_pool = request.app.state.db_pool
        return VisitsChecklistService(
            visits_checklist_repository=VisitsChecklistRepository(db_pool),
            visits_repository=VisitsRepository(db_pool),
        )

    def provide_visits_places_service(request: Request) -> VisitsPlacesService:
        db_pool = request.app.state.db_pool
        return VisitsPlacesService(
            visits_places_repository=VisitsPlacesRepository(db_pool),
            visits_repository=VisitsRepository(db_pool),
        )

    def provide_visits_places_files_service(request: Request) -> VisitsPlacesFilesService:
        db_pool = request.app.state.db_pool
        return VisitsPlacesFilesService(
            visits_places_files_repository=VisitsPlacesFilesRepository(db_pool),
            visits_places_repository=VisitsPlacesRepository(db_pool),
            files_repository=FilesRepository(db_pool),
        )

    def provide_dashboard_service(request: Request) -> DashboardService:
        dashboard_repository = DashboardRepository(request.app.state.db_pool)
        return DashboardService(dashboard_repository=dashboard_repository)

    def provide_followers_service(request: Request) -> FollowersService:
        users_repository = UsersRepository(request.app.state.db_pool)
        followers_repository = FollowersRepository(request.app.state.db_pool)
        return FollowersService(
            followers_repository=followers_repository,
            users_repository=users_repository,
        )

    def provide_files_service(request: Request) -> FilesService:
        files_repository = FilesRepository(request.app.state.db_pool)
        visits_repository = VisitsRepository(request.app.state.db_pool)
        return FilesService(
            files_repository=files_repository,
            visits_repository=visits_repository,
            file_storage=request.app.state.file_storage,
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

    def after_exception(exc: Exception, _scope: object) -> None:
        if not isinstance(exc, (HTTPException, ServiceError)):
            logger.exception('Unhandled exception', exc_info=exc)

    prometheus_config = PrometheusConfig(
        app_name='tripmark',
        group_path=True,
        excluded_http_methods=['OPTIONS'],
        exclude=[r'^/metrics$', r'^/api/v1/healthcheck$', r'^/schema(?:/.*)?$'],
    )
    app = Litestar(
        route_handlers=[*route_handlers, PrometheusController],
        middleware=[prometheus_config.middleware],
        on_startup=[startup],
        on_shutdown=[shutdown],
        after_exception=[after_exception],
        logging_config=build_logging_config(app_settings.log),
        openapi_config=OpenAPIConfig(
            title='Tripmark API',
            version='1.0.0',
            components=Components(
                security_schemes={
                    'user_auth': SecurityScheme(type='http', scheme='bearer', bearer_format='JWT'),
                }
            ),
        ),
        cors_config=CORSConfig(
            allow_origins=app_settings.resolved_cors_allowed_origins,
            allow_methods=['*'],
            allow_headers=['*'],
        ),
        dependencies={
            'auth_service': Provide(provide_auth_service, sync_to_thread=False),
            'achievements_service': Provide(provide_achievements_service, sync_to_thread=False),
            'countries_service': Provide(provide_countries_service, sync_to_thread=False),
            'client_geo_search_service': Provide(provide_client_geo_search_service, sync_to_thread=False),
            'users_service': Provide(provide_users_service, sync_to_thread=False),
            'followers_service': Provide(provide_followers_service, sync_to_thread=False),
            'files_service': Provide(provide_files_service, sync_to_thread=False),
            'visits_service': Provide(provide_visits_service, sync_to_thread=False),
            'visits_checklist_service': Provide(provide_visits_checklist_service, sync_to_thread=False),
            'visits_places_service': Provide(provide_visits_places_service, sync_to_thread=False),
            'visits_places_files_service': Provide(provide_visits_places_files_service, sync_to_thread=False),
            'dashboard_service': Provide(provide_dashboard_service, sync_to_thread=False),
            'current_user': Provide(provide_current_user, sync_to_thread=False),
        },
        exception_handlers={
            ServiceError: _service_error_handler,
            HTTP_500_INTERNAL_SERVER_ERROR: _internal_exception_handler,
        },
    )

    app.state.settings = app_settings

    return app


app = create_app()
