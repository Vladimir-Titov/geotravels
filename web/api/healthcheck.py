import asyncio
import logging

from litestar import Request, Response, Router, get
from sqlalchemy import select

from web.api.schemas import HealthcheckResponse

logger = logging.getLogger(__name__)


@get('/healthcheck', tags=['health'])
async def healthcheck(request: Request) -> Response[HealthcheckResponse]:
    state = request.app.state
    db_status = True
    try:
        async with state.db_pool.connection() as connection:
            await asyncio.wait_for(connection.fetch_one(select(1)), timeout=5.0)
    except Exception:
        logger.exception('Healthcheck db check failed')
        db_status = False

    s3_status = True
    try:
        s3_status = await state.file_storage.check_connection()
    except Exception:
        logger.exception('Healthcheck s3 check failed')
        s3_status = False

    status = db_status and s3_status
    return Response(
        content=HealthcheckResponse(status=status),
        media_type='application/json',
        status_code=200 if status else 503,
    )


healthcheck_router = Router(path='/api/v1', route_handlers=[healthcheck])
