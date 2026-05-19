from litestar import Router, get

from app.services.achievements import AchievementsService
from app.services.current_user import CurrentUser
from web.api.achievements.schemas import (
    AchievementResponse,
    AchievementsListRequest,
    AchievementsListResponse,
    EarnedAchievementResponse,
    EarnedAchievementsListResponse,
    PaginationResponse,
    UserAchievementsListRequest,
)
from web.utils import from_query


@get(
    '',
    tags=['achievements'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(AchievementsListRequest)},
)
async def list_achievements(
    achievements_service: AchievementsService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: AchievementsListRequest,
) -> AchievementsListResponse:
    data = await achievements_service.list_achievements(**filters.to_repo_filters())
    return AchievementsListResponse(
        items=[AchievementResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get(
    '/my',
    tags=['achievements'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(UserAchievementsListRequest)},
)
async def list_my_achievements(
    achievements_service: AchievementsService,
    current_user: CurrentUser,
    filters: UserAchievementsListRequest,
) -> EarnedAchievementsListResponse:
    repo_filters = filters.to_repo_filters()
    data = await achievements_service.list_user_achievements(
        user_id=current_user.id,
        **repo_filters,
    )
    return EarnedAchievementsListResponse(
        items=[EarnedAchievementResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


achievements_router = Router(
    path='/api/v1/achievements',
    route_handlers=[list_achievements, list_my_achievements],
)
