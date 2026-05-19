from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import SupportTicketStatus


class SupportTicketRequest(BaseModel):
    contact: str = Field(min_length=1)
    content: str = Field(min_length=1, max_length=1500)


class SupportTicketResponse(BaseModel):
    id: UUID
    contact: str
    content: str
    status: SupportTicketStatus
    created: datetime
    updated: datetime
