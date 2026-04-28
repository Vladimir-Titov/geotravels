import dataclasses
import inspect
from typing import Any, get_type_hints

from litestar.di import Provide


def from_query(model_cls: type) -> Provide:
    """Creates a Litestar Provide dependency that maps flat query params to a dataclass instance.

    Usage:
        @get('', dependencies={"filters": from_query(MyFilters)})
        async def handler(filters: MyFilters) -> ...:
    """
    dc_fields = dataclasses.fields(model_cls)
    hints = get_type_hints(model_cls)

    params = []
    for f in dc_fields:
        if f.default is not dataclasses.MISSING:
            default = f.default
        elif f.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
            default = f.default_factory()
        else:
            default = inspect.Parameter.empty

        params.append(
            inspect.Parameter(
                f.name,
                inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=hints.get(f.name, inspect.Parameter.empty),
            )
        )

    def _dependency(**kwargs: Any) -> Any:
        return model_cls(**kwargs)

    _dependency.__signature__ = inspect.Signature(params, return_annotation=model_cls)
    _dependency.__annotations__ = {f.name: hints[f.name] for f in dc_fields}
    _dependency.__annotations__['return'] = model_cls

    return Provide(_dependency, sync_to_thread=False)
