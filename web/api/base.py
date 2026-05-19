from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


@dataclass(eq=False)
class BaseListRequest:
    limit: int = field(default=100)
    offset: int = field(default=0)

    def to_repo_filters(self) -> dict[str, Any]:
        return {name: value for name, value in vars(self).items() if value is not None}


class PaginationResponse(BaseModel):
    limit: int | None
    offset: int
    total: int
