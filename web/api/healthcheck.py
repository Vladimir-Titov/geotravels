import asyncio
import logging

from litestar import Request, Response, Router, get
from sqlalchemy import select

from web.api.schemas import HealthcheckResponse

logger = logging.getLogger(__name__)


@get('/healthcheck', tags=['health'])
async def healthcheck(request: Request) -> Response[HealthcheckResponse]:
    state = request.app.state
    status = True
    async with state.db_pool.connection() as connection:
        try:
            await asyncio.wait_for(connection.fetch_one(select(1)), timeout=5.0)
        except Exception:
            logger.exception('Healthcheck failed')
            status = False
    return Response(
        content=HealthcheckResponse(status=status),
        media_type='application/json',
        status_code=200 if status else 503,
    )


healthcheck_router = Router(path='/api/v1', route_handlers=[healthcheck])
