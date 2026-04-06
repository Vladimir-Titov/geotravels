from __future__ import annotations

from uuid import UUID

from litestar import Router, delete, get, post

from app.services.current_user import CurrentUser
from app.services.followers import FollowersService
from web.api.schemas import (
    FollowerResponse,
    FollowersListRequest,
    FollowersListResponse,
    FollowRequest,
    PaginationResponse,
)
from web.utils import from_query


@post('', tags=['followers'], security=[{'user_auth': []}])
async def subscribe(
    data: FollowRequest,
    followers_service: FollowersService,
    current_user: CurrentUser,
) -> FollowerResponse:
    relation = await followers_service.subscribe(
        follower_id=current_user.id,
        following_id=data.following_id,
    )
    return FollowerResponse(**relation)


@delete('/{following_id:uuid}', tags=['followers'], security=[{'user_auth': []}], status_code=200)
async def unsubscribe(
    following_id: UUID,
    followers_service: FollowersService,
    current_user: CurrentUser,
) -> FollowerResponse:
    relation = await followers_service.unsubscribe(
        follower_id=current_user.id,
        following_id=following_id,
    )
    return FollowerResponse(**relation)


@get(
    '',
    tags=['followers'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(FollowersListRequest)},
)
async def list_followers(
    followers_service: FollowersService,
    current_user: CurrentUser,
    filters: FollowersListRequest,
) -> FollowersListResponse:
    repo_filters = filters.to_repo_filters()
    if repo_filters.get('follower_id') is None:
        repo_filters['follower_id'] = current_user.id

    data = await followers_service.list_followers(**repo_filters)
    return FollowersListResponse(
        items=[FollowerResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


followers_router = Router(path='/api/v1/followers', route_handlers=[subscribe, unsubscribe, list_followers])
