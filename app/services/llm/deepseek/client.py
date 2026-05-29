from typing import Any

from aiohttp import ClientSession

from app.services.llm.deepseek.types import DeepSeekCompletionRequest, DeepSeekCompletionResponse, JsonObject
from settings import DeepSeekSettings


class DeepSeekClient:
    def __init__(
        self,
        *,
        settings: DeepSeekSettings,
        session: ClientSession,
    ):
        self.settings = settings
        self.session = session
        self.base_url = settings.base_url.rstrip('/')

    async def completions(self, request: DeepSeekCompletionRequest) -> DeepSeekCompletionResponse:
        if not self.settings.api_key:
            raise ValueError('DeepSeek API key is not configured')
        if request.stream:
            raise ValueError('DeepSeekClient.completions does not support streaming responses yet')

        payload = await self._request('chat/completions', json=request.to_dict(), api_key=self.settings.api_key)
        return DeepSeekCompletionResponse.from_dict(payload)

    async def create_completion(self, request: DeepSeekCompletionRequest) -> DeepSeekCompletionResponse:
        return await self.completions(request)

    async def _request(self, path: str, *, json: JsonObject, api_key: str) -> JsonObject:
        async with self.session.post(
            f'{self.base_url}/{path.lstrip("/")}',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json=json,
            timeout=self.settings.timeout_seconds,
        ) as response:
            response.raise_for_status()
            payload: Any = await response.json(content_type=None)

        return payload if isinstance(payload, dict) else {}
