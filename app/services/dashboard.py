from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.repositories.dashboard import DashboardRepository


class DashboardService:
    MILESTONE_TARGET_VALUE = 10

    def __init__(self, dashboard_repository: DashboardRepository):
        self.dashboard_repository = dashboard_repository

    async def get_dashboard(self, user_id: UUID) -> dict[str, Any]:
        user_snapshot = await self.dashboard_repository.get_user_snapshot(user_id=user_id) or {}
        stats = await self.dashboard_repository.get_stats(user_id=user_id)
        recent_story_rows = await self.dashboard_repository.list_recent_story_proxies(user_id=user_id, limit=3)
        top_country_rows = await self.dashboard_repository.list_top_countries(user_id=user_id, limit=3)

        countries_count = max(int(stats.get('countries_count') or 0), 0)
        cities_count = max(int(stats.get('cities_count') or 0), 0)
        stories_count = max(int(stats.get('stories_count') or 0), 0)

        return {
            'me': {
                'display_name': self._resolve_display_name(user_snapshot),
                'username': user_snapshot.get('username'),
            },
            'stats': {
                'countries_count': countries_count,
                'cities_count': cities_count,
                'stories_count': stories_count,
            },
            'next_milestone': {
                'progress_percent': self._compute_progress_percent(
                    current_value=countries_count,
                    target_value=self.MILESTONE_TARGET_VALUE,
                ),
                'current_value': countries_count,
                'target_value': self.MILESTONE_TARGET_VALUE,
            },
            'recap': {
                'period': datetime.now().strftime('%Y-%m'),
                'is_ready': False,
                'share_url': None,
                'share_route': None,
            },
            'recent_stories': [self._build_recent_story(item) for item in recent_story_rows],
            'inbox_preview': {
                'unread_count': 0,
                'items': [],
            },
            'most_visited': self._build_most_visited(top_country_rows),
        }

    def _resolve_display_name(self, user_snapshot: dict[str, Any]) -> str | None:
        first_name = (user_snapshot.get('first_name') or '').strip()
        last_name = (user_snapshot.get('last_name') or '').strip()
        full_name = ' '.join(part for part in (first_name, last_name) if part)
        if full_name:
            return full_name

        username = (user_snapshot.get('username') or '').strip()
        if username:
            return username

        email = (user_snapshot.get('email') or '').strip()
        if email:
            return email.split('@', 1)[0] or email

        return None

    def _compute_progress_percent(self, current_value: int, target_value: int) -> int:
        if target_value <= 0:
            return 0

        raw_percent = int((current_value / target_value) * 100)
        return min(max(raw_percent, 0), 100)

    def _build_recent_story(self, row: dict[str, Any]) -> dict[str, Any]:
        city_name = row.get('city_name')
        country_name = row.get('country_name')

        cover_file_id = row.get('cover_file_id')
        cover = f'/api/v1/files/{cover_file_id}/download' if cover_file_id else None

        return {
            'id': row['id'],
            'excerpt': None,
            'visibility': row.get('visibility') or 'private',
            'created_at': row['created'],
            'location': {
                'country_code': row['country_code'],
                'country_name': country_name,
                'city_id': row.get('city_id'),
                'city_name': city_name,
            },
            'cover': cover,
            'counters': {
                'views': None,
                'likes': None,
                'comments': None,
            },
        }

    def _build_most_visited(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            return []

        max_trips_count = max(int(row.get('trips_count') or 0) for row in rows)
        if max_trips_count <= 0:
            return [
                {
                    'country_name': row.get('country_name'),
                    'trips_count': int(row.get('trips_count') or 0),
                    'relative_bar_value': 0,
                }
                for row in rows
            ]

        normalized: list[dict[str, Any]] = []
        for row in rows:
            trips_count = int(row.get('trips_count') or 0)
            relative_bar_value = int((trips_count / max_trips_count) * 100)
            normalized.append(
                {
                    'country_name': row.get('country_name'),
                    'trips_count': trips_count,
                    'relative_bar_value': min(max(relative_bar_value, 0), 100),
                }
            )
        return normalized
