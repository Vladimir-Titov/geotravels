from __future__ import annotations

from uuid import UUID

from litestar import Router, get, post
from litestar.exceptions import HTTPException

from app.services.exceptions import ServiceError
from app.services.visits import VisitsService
from web.api.schemas import MarkVisitRequest, VisitEventResponse, VisitsResponse


@post('', tags=['visits'])
async def mark_visit(
    data: MarkVisitRequest,
    visits_service: VisitsService,
    current_user_id: UUID,
) -> VisitEventResponse:
    try:
        visit = await visits_service.mark_visited(
            user_id=current_user_id,
            country_code=data.country_code,
            trip_date=data.trip_date,
        )
        return VisitEventResponse(**visit)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@get('', tags=['visits'])
async def list_visits(visits_service: VisitsService, current_user_id: UUID) -> VisitsResponse:
    data = await visits_service.list_visits(user_id=current_user_id)
    return VisitsResponse(
        visits=[VisitEventResponse(**item) for item in data['visits']],
        visited_country_codes=data['visited_country_codes'],
    )


visits_router = Router(path='/api/v1/visits', route_handlers=[mark_visit, list_visits])
