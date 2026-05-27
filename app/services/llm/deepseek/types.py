from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Self

JsonObject = dict[str, Any]

DeepSeekCompletionModel = Literal['deepseek-v4-pro', 'deepseek-v4-flash', 'deepseek-chat']
DeepSeekCompletionObject = Literal['text_completion', 'chat.completion']
DeepSeekCompletionFinishReason = Literal['stop', 'length', 'content_filter', 'insufficient_system_resource']


def _optional_object(value: Any) -> JsonObject | None:
    if isinstance(value, Mapping):
        return dict(value)
    return None


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, str):
        return value
    return ()


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except TypeError, ValueError:
        return default


def _as_float_or_none(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except TypeError, ValueError:
        return None


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    return tuple(item for item in _sequence(value) if isinstance(item, str))


@dataclass(frozen=True, slots=True)
class DeepSeekCompletionStreamOptions:
    include_usage: bool = False

    def to_dict(self) -> JsonObject:
        return {'include_usage': self.include_usage}


@dataclass(frozen=True, slots=True)
class DeepSeekCompletionRequest:
    model: DeepSeekCompletionModel
    prompt: str
    echo: bool | None = None
    logprobs: int | None = None
    max_tokens: int | None = None
    stop: str | tuple[str, ...] | None = None
    stream: bool | None = False
    stream_options: DeepSeekCompletionStreamOptions | None = None
    suffix: str | None = None
    temperature: float | None = None
    top_p: float | None = None

    def __post_init__(self) -> None:
        # if self.model != 'deepseek-v4-pro':
        #     raise ValueError('DeepSeek completions only support model="deepseek-v4-pro"')
        if not self.prompt:
            raise ValueError('DeepSeekCompletionRequest.prompt must not be empty')
        if self.logprobs is not None and not 0 <= self.logprobs <= 20:
            raise ValueError('DeepSeekCompletionRequest.logprobs must be between 0 and 20')
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError('DeepSeekCompletionRequest.max_tokens must be greater than 0')
        if self.temperature is not None and not 0 <= self.temperature <= 2:
            raise ValueError('DeepSeekCompletionRequest.temperature must be between 0 and 2')
        if self.top_p is not None and not 0 <= self.top_p <= 1:
            raise ValueError('DeepSeekCompletionRequest.top_p must be between 0 and 1')
        if isinstance(self.stop, tuple) and len(self.stop) > 16:
            raise ValueError('DeepSeekCompletionRequest.stop supports up to 16 sequences')

    def to_dict(self) -> JsonObject:
        payload: JsonObject = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': self.prompt,
                }
            ],
        }

        if self.max_tokens is not None:
            payload['max_tokens'] = self.max_tokens
        if self.stop is not None:
            payload['stop'] = list(self.stop) if isinstance(self.stop, tuple) else self.stop
        if self.stream is not None:
            payload['stream'] = self.stream
        if self.stream_options is not None:
            payload['stream_options'] = self.stream_options.to_dict()
        if self.temperature is not None:
            payload['temperature'] = self.temperature
        if self.top_p is not None:
            payload['top_p'] = self.top_p

        return payload


@dataclass(frozen=True, slots=True)
class DeepSeekCompletionLogprobs:
    text_offset: tuple[int, ...] = ()
    token_logprobs: tuple[float | None, ...] = ()
    tokens: tuple[str, ...] = ()
    top_logprobs: tuple[JsonObject, ...] = ()

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        return cls(
            text_offset=tuple(_as_int(item) for item in _sequence(data.get('text_offset'))),
            token_logprobs=tuple(_as_float_or_none(item) for item in _sequence(data.get('token_logprobs'))),
            tokens=_as_str_tuple(data.get('tokens')),
            top_logprobs=tuple(dict(item) for item in _sequence(data.get('top_logprobs')) if isinstance(item, Mapping)),
        )


@dataclass(frozen=True, slots=True)
class DeepSeekCompletionChoice:
    finish_reason: DeepSeekCompletionFinishReason | str
    index: int
    text: str
    logprobs: DeepSeekCompletionLogprobs | None = None

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        logprobs = _optional_object(data.get('logprobs'))
        text = data.get('text')
        message = _optional_object(data.get('message'))
        content = message.get('content') if message is not None else None
        return cls(
            finish_reason=str(data.get('finish_reason', '')),
            index=_as_int(data.get('index')),
            logprobs=DeepSeekCompletionLogprobs.from_dict(logprobs) if logprobs is not None else None,
            text=content if isinstance(content, str) else text if isinstance(text, str) else '',
        )


@dataclass(frozen=True, slots=True)
class DeepSeekCompletionTokensDetails:
    reasoning_tokens: int | None = None

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        reasoning_tokens = data.get('reasoning_tokens')
        return cls(reasoning_tokens=_as_int(reasoning_tokens) if reasoning_tokens is not None else None)


@dataclass(frozen=True, slots=True)
class DeepSeekCompletionUsage:
    completion_tokens: int = 0
    prompt_tokens: int = 0
    prompt_cache_hit_tokens: int = 0
    prompt_cache_miss_tokens: int = 0
    total_tokens: int = 0
    completion_tokens_details: DeepSeekCompletionTokensDetails | None = None

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        details = _optional_object(data.get('completion_tokens_details'))
        return cls(
            completion_tokens=_as_int(data.get('completion_tokens')),
            prompt_tokens=_as_int(data.get('prompt_tokens')),
            prompt_cache_hit_tokens=_as_int(data.get('prompt_cache_hit_tokens')),
            prompt_cache_miss_tokens=_as_int(data.get('prompt_cache_miss_tokens')),
            total_tokens=_as_int(data.get('total_tokens')),
            completion_tokens_details=(
                DeepSeekCompletionTokensDetails.from_dict(details) if details is not None else None
            ),
        )


@dataclass(frozen=True, slots=True)
class DeepSeekCompletionResponse:
    id: str
    choices: tuple[DeepSeekCompletionChoice, ...]
    created: int
    model: str
    object: DeepSeekCompletionObject | str
    system_fingerprint: str | None = None
    usage: DeepSeekCompletionUsage | None = None

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        usage = _optional_object(data.get('usage'))
        return cls(
            id=str(data.get('id', '')),
            choices=tuple(
                DeepSeekCompletionChoice.from_dict(dict(choice))
                for choice in _sequence(data.get('choices'))
                if isinstance(choice, Mapping)
            ),
            created=_as_int(data.get('created')),
            model=str(data.get('model', '')),
            system_fingerprint=(
                data.get('system_fingerprint') if isinstance(data.get('system_fingerprint'), str) else None
            ),
            object=str(data.get('object', '')),
            usage=DeepSeekCompletionUsage.from_dict(usage) if usage is not None else None,
        )
