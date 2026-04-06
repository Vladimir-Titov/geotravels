import asyncio
import logging

from litestar import Request, Response, Router, get
from sqlalchemy import select

from web.api.schemas import HealthcheckResponse

logger = logging.getLogger(__name__)


async def _check_db(state: object) -> bool:
    try:
        async with state.db_pool.connection() as connection:
            await connection.fetch_one(select(1))
        return True
    except Exception:
        logger.exception('Healthcheck db check failed')
        return False


async def _check_s3(state: object) -> bool:
    try:
        return await state.file_storage.check_connection()
    except Exception:
        logger.exception('Healthcheck s3 check failed')
        return False


@get('/healthcheck', tags=['health'])
async def healthcheck(request: Request) -> Response[HealthcheckResponse]:
    state = request.app.state
    try:
        db_status, s3_status = await asyncio.wait_for(
            asyncio.gather(_check_db(state), _check_s3(state)),
            timeout=5.0,
        )
    except TimeoutError:
        logger.exception('Healthcheck timed out')
        db_status, s3_status = False, False

    status = db_status and s3_status
    return Response(
        content=HealthcheckResponse(status=status),
        media_type='application/json',
        status_code=200 if status else 503,
    )


healthcheck_router = Router(path='/api/v1', route_handlers=[healthcheck])
