from enum import StrEnum

from sqlalchemy import Column, DateTime, Integer, String, Table, Uuid, func

from app.models.base import metadata


class OtpRequestStatus(StrEnum):
    SENT = 'sent'
    FAILED = 'failed'
    DONE = 'done'


otp_requests = Table(
    'otp_requests',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('contact', String(length=320), nullable=False),
    Column('code_hash', String(length=64), nullable=False),
    Column('expires_at', DateTime(timezone=True), nullable=False),
    Column('attempts', Integer(), nullable=False, server_default='0'),
    Column('status', String(length=20), nullable=False, server_default=OtpRequestStatus.SENT),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)
