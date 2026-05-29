import pytest

from app.services.llm.deepseek import (
    DeepSeekClient,
    DeepSeekCompletionRequest,
    DeepSeekCompletionStreamOptions,
)
from settings import DeepSeekSettings


class FakeDeepSeekResponse:
    def __init__(self, payload: dict | None = None, exc: Exception | None = None) -> None:
        self.payload = payload or {}
        self.exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    def raise_for_status(self) -> None:
        if self.exc is not None:
            raise self.exc

    async def json(self, *args, **kwargs) -> dict:  # noqa: ANN002, ANN003, ARG002
        return self.payload


class FakeDeepSeekSession:
    def __init__(self, response: FakeDeepSeekResponse) -> None:
        self.response = response
        self.calls: list[dict] = []

    def post(self, url: str, *, headers: dict, json: dict, timeout: float) -> FakeDeepSeekResponse:
        self.calls.append(
            {
                'url': url,
                'headers': headers,
                'json': json,
                'timeout': timeout,
            }
        )
        return self.response


def _settings() -> DeepSeekSettings:
    return DeepSeekSettings(
        base_url='https://deepseek.example.test/beta/',
        api_key='test-key',
        timeout_seconds=3.5,
    )


@pytest.mark.asyncio
async def test_completions_sends_deepseek_request_and_parses_response() -> None:
    session = FakeDeepSeekSession(
        FakeDeepSeekResponse(
            {
                'id': 'cmpl-1',
                'choices': [
                    {
                        'finish_reason': 'stop',
                        'index': 0,
                        'logprobs': {
                            'text_offset': [0],
                            'token_logprobs': [-0.1],
                            'tokens': ['hello'],
                            'top_logprobs': [{'hello': -0.1}],
                        },
                        'message': {
                            'role': 'assistant',
                            'content': 'hello',
                        },
                    }
                ],
                'created': 1_705_651_092,
                'model': 'deepseek-chat',
                'system_fingerprint': 'fp-test',
                'object': 'chat.completion',
                'usage': {
                    'completion_tokens': 1,
                    'prompt_tokens': 3,
                    'prompt_cache_hit_tokens': 2,
                    'prompt_cache_miss_tokens': 1,
                    'total_tokens': 4,
                    'completion_tokens_details': {'reasoning_tokens': 0},
                },
            }
        )
    )
    client = DeepSeekClient(settings=_settings(), session=session)

    response = await client.completions(
        DeepSeekCompletionRequest(
            model='deepseek-chat',
            prompt='Say hello',
            max_tokens=8,
            stop=('</s>',),
            stream_options=DeepSeekCompletionStreamOptions(include_usage=True),
            temperature=0.2,
        )
    )

    assert session.calls == [
        {
            'url': 'https://deepseek.example.test/beta/chat/completions',
            'headers': {
                'Authorization': 'Bearer test-key',
                'Content-Type': 'application/json',
            },
            'json': {
                'model': 'deepseek-chat',
                'messages': [
                    {
                        'role': 'user',
                        'content': 'Say hello',
                    }
                ],
                'max_tokens': 8,
                'stop': ['</s>'],
                'stream': False,
                'stream_options': {'include_usage': True},
                'temperature': 0.2,
            },
            'timeout': 3.5,
        }
    ]
    assert response.id == 'cmpl-1'
    assert response.choices[0].text == 'hello'
    assert response.choices[0].logprobs is not None
    assert response.choices[0].logprobs.tokens == ('hello',)
    assert response.usage is not None
    assert response.usage.total_tokens == 4
    assert response.usage.completion_tokens_details is not None
    assert response.usage.completion_tokens_details.reasoning_tokens == 0


@pytest.mark.asyncio
async def test_create_completion_alias_uses_completions_endpoint() -> None:
    session = FakeDeepSeekSession(FakeDeepSeekResponse({'choices': []}))
    client = DeepSeekClient(
        settings=DeepSeekSettings(api_key='test-key'),
        session=session,
    )

    await client.create_completion(DeepSeekCompletionRequest(model='deepseek-v4-pro', prompt='prefix'))

    assert session.calls[0]['url'] == 'https://api.deepseek.com/chat/completions'


@pytest.mark.asyncio
async def test_completions_rejects_streaming_response() -> None:
    session = FakeDeepSeekSession(FakeDeepSeekResponse())
    client = DeepSeekClient(settings=_settings(), session=session)

    with pytest.raises(ValueError, match='streaming'):
        await client.completions(DeepSeekCompletionRequest(model='deepseek-v4-pro', prompt='prefix', stream=True))

    assert session.calls == []


@pytest.mark.asyncio
async def test_completions_requires_api_key_from_settings() -> None:
    session = FakeDeepSeekSession(FakeDeepSeekResponse())
    client = DeepSeekClient(settings=DeepSeekSettings(api_key=''), session=session)

    with pytest.raises(ValueError, match='API key'):
        await client.completions(DeepSeekCompletionRequest(model='deepseek-v4-pro', prompt='prefix'))

    assert session.calls == []


def test_completion_request_validates_deepseek_limits() -> None:
    with pytest.raises(ValueError, match='logprobs'):
        DeepSeekCompletionRequest(model='deepseek-v4-pro', prompt='prefix', logprobs=21)

    with pytest.raises(ValueError, match='temperature'):
        DeepSeekCompletionRequest(model='deepseek-v4-pro', prompt='prefix', temperature=2.1)

    with pytest.raises(ValueError, match='stop'):
        DeepSeekCompletionRequest(model='deepseek-v4-pro', prompt='prefix', stop=tuple(str(i) for i in range(17)))
