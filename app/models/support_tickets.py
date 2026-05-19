from enum import StrEnum

from sqlalchemy import Column, DateTime, String, Table, Text, Uuid, func

from app.models.base import metadata


class SupportTicketStatus(StrEnum):
    OPEN = 'open'
    CLOSED = 'closed'


support_tickets = Table(
    'support_tickets',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('contact', Text, nullable=False),
    Column('content', Text, nullable=False),
    Column('status', String(length=16), nullable=False, server_default=SupportTicketStatus.OPEN),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)
