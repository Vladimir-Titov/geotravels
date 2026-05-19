from enum import StrEnum

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table, Text, Uuid, func

from app.models.base import metadata


class CheckListStatus(StrEnum):
    TO_DO = 'to_do'
    DONE = 'done'


visits_checklist = Table(
    'visits_checklist',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('visit_id', Uuid(as_uuid=True), ForeignKey('visits.id', ondelete='CASCADE'), nullable=False),
    Column('content', Text, nullable=False),
    Column('status', String(length=16), nullable=False, server_default=CheckListStatus.TO_DO),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_visits_checklist_visit_id', 'visit_id'),
)
