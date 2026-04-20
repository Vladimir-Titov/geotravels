from litestar import Router, get

from app.services.current_user import CurrentUser
from app.services.dashboard import DashboardService
from web.api.schemas import DashboardResponse


@get('/dashboard', tags=['dashboard'], security=[{'user_auth': []}])
async def get_dashboard(
    dashboard_service: DashboardService,
    current_user: CurrentUser,
) -> DashboardResponse:
    dashboard = await dashboard_service.get_dashboard(user_id=current_user.id)
    return DashboardResponse(**dashboard)


me_router = Router(path='/api/v1/me', route_handlers=[get_dashboard])
