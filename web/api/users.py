from litestar import Router, get

from app.services.current_user import CurrentUser
from app.services.users import UsersService
from web.api.schemas import PaginationResponse, UserResponse, UsersListRequest, UsersListResponse
from web.utils import from_query


@get(
    '',
    tags=['users'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(UsersListRequest)},
)
async def list_users(
    users_service: UsersService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: UsersListRequest,
) -> UsersListResponse:
    data = await users_service.list_users(**filters.to_repo_filters())
    return UsersListResponse(
        items=[UserResponse(**user) for user in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


users_router = Router(path='/api/v1/users', route_handlers=[list_users])
