from dataclasses import dataclass
from uuid import UUID


@dataclass
class CurrentUser:
    id: UUID
