from __future__ import annotations

from litestar import Router, get

from app.services.achievements import AchievementsService
from app.services.current_user import CurrentUser
from web.api.schemas import (
    AchievementResponse,
    AchievementsListResponse,
    BaseListRequest,
    EarnedAchievementResponse,
    EarnedAchievementsListResponse,
    PaginationResponse,
)
from web.utils import from_query


@get(
    '',
    tags=['achievements'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(BaseListRequest)},
)
async def list_achievements(
    achievements_service: AchievementsService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: BaseListRequest,
) -> AchievementsListResponse:
    data = await achievements_service.list_achievements(limit=filters.limit, offset=filters.offset)
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
    dependencies={'filters': from_query(BaseListRequest)},
)
async def list_my_achievements(
    achievements_service: AchievementsService,
    current_user: CurrentUser,
    filters: BaseListRequest,
) -> EarnedAchievementsListResponse:
    data = await achievements_service.list_user_achievements(
        user_id=current_user.id,
        limit=filters.limit,
        offset=filters.offset,
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
