import asyncio
import logging

from litestar import Request, Router, get
from sqlalchemy import select

logger = logging.getLogger(__name__)


@get('/healthcheck', tags=['health'])
async def healthcheck(request: Request) -> dict[str, bool]:
    state = request.app.state
    async with state.db_pool.connection() as connection:
        try:
            await asyncio.wait_for(connection.fetch_one(select(1)), timeout=5.0)
        except Exception:
            logger.exception('Healthcheck failed')
            return {'status': False}
    return {'status': True}


healthcheck_router = Router(path='api/v1/', route_handlers=[healthcheck])
