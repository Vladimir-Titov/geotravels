from litestar import Router, post

from app.services.supports_service import SupportsService
from web.api.supports.schemas import SupportTicketRequest, SupportTicketResponse


@post('ticket', tags=['support'])
async def support_ticket(data: SupportTicketRequest, support_service: SupportsService) -> SupportTicketResponse:
    payload = await support_service.create_support_ticket(**data.model_dump(exclude_none=True))
    return SupportTicketResponse(**payload)


supports_router = Router(
    path='/api/v1/support',
    route_handlers=[
        support_ticket,
    ],
)
