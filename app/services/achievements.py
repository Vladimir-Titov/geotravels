from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.repositories.achievements import AchievementsRepository
from app.repositories.base import PaginatedResponse
from app.repositories.files import FilesRepository
from app.repositories.followers import FollowersRepository
from app.repositories.users import UsersRepository
from app.repositories.users_achievements import UsersAchievementsRepository
from app.repositories.visits import VisitsRepository


@dataclass(frozen=True)
class MilestoneRule:
    key: str
    title: str
    description: str
    metric: str
    target: int


MILESTONE_RULES: tuple[MilestoneRule, ...] = (
    MilestoneRule(
        key='first_visit',
        title='First Visit',
        description='Add your first visit',
        metric='visits_count',
        target=1,
    ),
    MilestoneRule(
        key='countries_5',
        title='5 Countries',
        description='Visit 5 unique countries',
        metric='countries_count',
        target=5,
    ),
    MilestoneRule(
        key='countries_10',
        title='10 Countries',
        description='Visit 10 unique countries',
        metric='countries_count',
        target=10,
    ),
    MilestoneRule(
        key='countries_25',
        title='25 Countries',
        description='Visit 25 unique countries',
        metric='countries_count',
        target=25,
    ),
    MilestoneRule(
        key='first_public_story',
        title='First Public Story',
        description='Publish your first public story',
        metric='public_stories_count',
        target=1,
    ),
    MilestoneRule(
        key='photos_10',
        title='10 Photos',
        description='Upload 10 photos',
        metric='photos_count',
        target=10,
    ),
    MilestoneRule(
        key='first_follower',
        title='First Follower',
        description='Get your first follower',
        metric='followers_count',
        target=1,
    ),
)


class AchievementsService:
    def __init__(
        self,
        achievements_repository: AchievementsRepository,
        users_achievements_repository: UsersAchievementsRepository,
        visits_repository: VisitsRepository,
        files_repository: FilesRepository,
        followers_repository: FollowersRepository,
        users_repository: UsersRepository,
    ):
        self.achievements_repository = achievements_repository
        self.users_achievements_repository = users_achievements_repository
        self.visits_repository = visits_repository
        self.files_repository = files_repository
        self.followers_repository = followers_repository
        self.users_repository = users_repository

    async def list_achievements(self, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        await self._ensure_catalog()
        return await self.achievements_repository.paginated_search(limit=limit, offset=offset, **filters)

    async def list_user_achievements(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
        **filters: Any,
    ) -> PaginatedResponse:
        await self.auto_award_for_user(user_id=user_id)
        return await self.users_achievements_repository.paginated_search(
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )

    async def get_user_achievements_with_progress(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
        **filters: Any,
    ) -> dict[str, Any]:
        achievements = await self.list_user_achievements(
            user_id=user_id,
            limit=limit,
            offset=offset,
            **filters,
        )
        progress = await self.get_next_progress(user_id=user_id)
        return {'achievements': achievements, 'next_progress': progress}

    async def auto_award_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        await self._ensure_catalog()
        metrics = await self._collect_metrics(user_id=user_id)
        achievements_by_title = await self._achievements_by_title()
        earned = await self.users_achievements_repository.search(user_id=user_id, limit=1000)
        earned_ids = {item['id'] for item in earned}
        new_achievements: list[dict[str, Any]] = []

        for rule in MILESTONE_RULES:
            metric_value = int(metrics.get(rule.metric) or 0)
            if metric_value < rule.target:
                continue

            achievement = achievements_by_title.get(rule.title)
            if achievement is None:
                continue
            if achievement['id'] in earned_ids:
                continue

            created = await self._safe_award(user_id=user_id, achievement_id=achievement['id'])
            if created is not None:
                new_achievements.append(created)
                earned_ids.add(achievement['id'])

        return new_achievements

    async def backfill_all_users(self, *, batch_size: int = 200) -> int:
        offset = 0
        total_awarded = 0

        while True:
            users = await self.users_repository.search(order_by=['id'], limit=batch_size, offset=offset)
            if not users:
                break
            for user in users:
                total_awarded += len(await self.auto_award_for_user(user_id=user['id']))
            offset += len(users)

        return total_awarded

    async def get_next_progress(self, user_id: UUID) -> dict[str, Any] | None:
        await self._ensure_catalog()
        metrics = await self._collect_metrics(user_id=user_id)
        achievements_by_title = await self._achievements_by_title()
        earned = await self.users_achievements_repository.search(user_id=user_id, limit=1000)
        earned_ids = {item['id'] for item in earned}

        pending: list[MilestoneRule] = []
        for rule in MILESTONE_RULES:
            achievement = achievements_by_title.get(rule.title)
            if achievement and achievement['id'] not in earned_ids:
                pending.append(rule)

        if not pending:
            return None

        next_rule = min(
            pending,
            key=lambda item: (
                max(item.target - int(metrics.get(item.metric) or 0), 0),
                item.target,
                item.title,
            ),
        )
        current = max(int(metrics.get(next_rule.metric) or 0), 0)
        achievement = achievements_by_title.get(next_rule.title)
        percent = min(max(int((current / next_rule.target) * 100), 0), 100) if next_rule.target > 0 else 0
        return {
            'achievement_id': achievement['id'] if achievement else None,
            'achievement_title': next_rule.title,
            'achievement_description': next_rule.description,
            'metric': next_rule.metric,
            'current_value': current,
            'target_value': next_rule.target,
            'progress_percent': percent,
        }

    async def _collect_metrics(self, user_id: UUID) -> dict[str, int]:
        countries = await self.visits_repository.list_unique_country_codes_by_user(user_id=user_id)
        return {
            'visits_count': await self.visits_repository.count_by_user(user_id=user_id),
            'countries_count': len(countries),
            'public_stories_count': await self.visits_repository.count_public_by_user(user_id=user_id),
            'photos_count': await self.files_repository.count_files_by_user(user_id=user_id),
            'followers_count': await self.followers_repository.count_followers_for_user(user_id=user_id),
        }

    async def _ensure_catalog(self) -> None:
        existing = await self._achievements_by_title()
        for rule in MILESTONE_RULES:
            if rule.title in existing:
                continue
            created = await self.achievements_repository.create(
                title=rule.title,
                description=rule.description,
            )
            existing[rule.title] = created

    async def _achievements_by_title(self) -> dict[str, dict[str, Any]]:
        existing = await self.achievements_repository.search(limit=1000)
        return {str(item['title']): item for item in existing}

    async def _safe_award(self, user_id: UUID, achievement_id: UUID) -> dict[str, Any] | None:
        try:
            return await self.users_achievements_repository.create(
                user_id=user_id,
                achievements_id=achievement_id,
            )
        except Exception:  # noqa: BLE001
            existing = await self.users_achievements_repository.search_first_row(
                user_id=user_id,
                achievements_id=achievement_id,
            )
            return existing
