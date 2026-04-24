from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.models.tables import VisitVisibility
from app.services.dashboard import DashboardService


class StubDashboardRepository:
    def __init__(
        self,
        *,
        user_snapshot: dict | None = None,
        stats: dict | None = None,
        recent_stories: list[dict] | None = None,
        top_countries: list[dict] | None = None,
    ) -> None:
        self._user_snapshot = user_snapshot
        self._stats = stats or {}
        self._recent_stories = recent_stories or []
        self._top_countries = top_countries or []

    async def get_user_snapshot(self, user_id):  # noqa: ARG002
        return self._user_snapshot

    async def get_stats(self, user_id):  # noqa: ARG002
        return self._stats

    async def list_recent_story_proxies(self, user_id, limit=3):  # noqa: ARG002
        return self._recent_stories[:limit]

    async def list_top_countries(self, user_id, limit=3):  # noqa: ARG002
        return self._top_countries[:limit]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('user_snapshot', 'expected_display_name'),
    [
        (
            {
                'first_name': 'Ada',
                'last_name': 'Lovelace',
                'username': 'adal',
                'email': 'ada@example.com',
            },
            'Ada Lovelace',
        ),
        (
            {
                'first_name': ' ',
                'last_name': '',
                'username': 'adal',
                'email': 'ada@example.com',
            },
            'adal',
        ),
        (
            {
                'first_name': None,
                'last_name': None,
                'username': None,
                'email': 'person@example.com',
            },
            'person',
        ),
        (
            {
                'first_name': None,
                'last_name': None,
                'username': None,
                'email': None,
            },
            None,
        ),
    ],
)
async def test_display_name_fallback_order(user_snapshot, expected_display_name) -> None:
    service = DashboardService(
        dashboard_repository=StubDashboardRepository(
            user_snapshot=user_snapshot,
            stats={'countries_count': 0, 'cities_count': 0, 'stories_count': 0},
        )
    )

    dashboard = await service.get_dashboard(user_id=uuid4())

    assert dashboard['me']['display_name'] == expected_display_name


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('countries_count', 'expected_percent'),
    [
        (-4, 0),
        (0, 0),
        (3, 30),
        (10, 100),
        (15, 100),
    ],
)
async def test_progress_percent_is_clamped(countries_count, expected_percent) -> None:
    service = DashboardService(
        dashboard_repository=StubDashboardRepository(
            user_snapshot=None,
            stats={
                'countries_count': countries_count,
                'cities_count': 0,
                'stories_count': 0,
            },
        )
    )

    dashboard = await service.get_dashboard(user_id=uuid4())

    assert dashboard['next_milestone']['progress_percent'] == expected_percent


@pytest.mark.asyncio
async def test_recent_story_keeps_location_and_omits_title() -> None:
    now = datetime.now(tz=timezone.utc)
    service = DashboardService(
        dashboard_repository=StubDashboardRepository(
            user_snapshot=None,
            stats={'countries_count': 0, 'cities_count': 0, 'stories_count': 2},
            recent_stories=[
                {
                    'id': uuid4(),
                    'country_code': 'FR',
                    'country_name': 'France',
                    'city_id': None,
                    'city_name': None,
                    'created': now,
                    'cover_file_id': None,
                },
                {
                    'id': uuid4(),
                    'country_code': 'ZZ',
                    'country_name': None,
                    'city_id': None,
                    'city_name': None,
                    'created': now,
                    'cover_file_id': None,
                },
            ],
        )
    )

    dashboard = await service.get_dashboard(user_id=uuid4())

    first_story = dashboard['recent_stories'][0]
    second_story = dashboard['recent_stories'][1]

    assert first_story['location']['country_name'] == 'France'
    assert second_story['location']['country_name'] is None
    assert 'title' not in first_story
    assert 'title' not in second_story


@pytest.mark.asyncio
async def test_recap_inbox_and_story_counters_are_stable_placeholders() -> None:
    now = datetime.now(tz=timezone.utc)
    service = DashboardService(
        dashboard_repository=StubDashboardRepository(
            user_snapshot=None,
            stats={'countries_count': 0, 'cities_count': 0, 'stories_count': 1},
            recent_stories=[
                {
                    'id': uuid4(),
                    'country_code': 'FR',
                    'country_name': 'France',
                    'city_id': None,
                    'city_name': None,
                    'created': now,
                    'cover_file_id': uuid4(),
                }
            ],
        )
    )

    dashboard = await service.get_dashboard(user_id=uuid4())

    assert dashboard['recap']['is_ready'] is False
    assert dashboard['recap']['share_url'] is None
    assert dashboard['recap']['share_route'] is None
    assert 'title' not in dashboard['recap']
    assert 'summary_line' not in dashboard['recap']

    assert dashboard['inbox_preview']['unread_count'] == 0
    assert dashboard['inbox_preview']['items'] == []

    story = dashboard['recent_stories'][0]
    assert story['visibility'] == VisitVisibility.PRIVATE
    assert story['excerpt'] is None
    assert story['counters'] == {'views': None, 'likes': None, 'comments': None}
    assert story['cover'].startswith('/api/v1/files/')
    assert story['cover'].endswith('/download')
