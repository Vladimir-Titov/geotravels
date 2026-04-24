from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4, uuid7

from sqlalchemy import create_engine

from app.models.tables import FileVisibility, VisitVisibility, cities, files, files_visits, visits
from settings import to_sync_database_url


def _get_tokens(client, email: str, otp_code: str) -> dict:
    otp_response = client.post('/api/v1/auth/otp/request', json={'contact': email})
    assert otp_response.status_code == 201

    verify_response = client.post(
        '/api/v1/auth/otp/verify',
        json={'otp_id': otp_response.json()['otp_id'], 'code': otp_code},
    )
    assert verify_response.status_code == 201
    return verify_response.json()


def _auth_headers(tokens: dict) -> dict[str, str]:
    return {'Authorization': f'Bearer {tokens["access_token"]}'}


def _get_user_id_by_email(client, auth_headers: dict[str, str], email: str) -> UUID:
    response = client.get(f'/api/v1/users?limit=1&offset=0&email={email}', headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload['pagination']['total'] == 1
    return UUID(payload['items'][0]['id'])


def test_dashboard_requires_auth(client) -> None:
    response = client.get('/api/v1/me/dashboard')

    assert response.status_code == 401


def test_dashboard_empty_returns_stable_placeholders(client, settings) -> None:
    tokens = _get_tokens(client, 'dashboard-empty@example.com', settings.otp.otp_mock_code)
    response = client.get('/api/v1/me/dashboard', headers=_auth_headers(tokens))

    assert response.status_code == 200
    payload = response.json()

    assert set(payload.keys()) == {
        'me',
        'stats',
        'next_milestone',
        'recap',
        'recent_stories',
        'inbox_preview',
        'most_visited',
    }

    assert payload['me']['display_name'] == 'dashboard-empty'
    assert payload['me']['username'] is None

    assert payload['stats'] == {'countries_count': 0, 'cities_count': 0, 'stories_count': 0}

    assert payload['next_milestone']['current_value'] == 0
    assert payload['next_milestone']['target_value'] == 10
    assert payload['next_milestone']['progress_percent'] == 0
    assert 'title' not in payload['next_milestone']
    assert 'description' not in payload['next_milestone']

    assert payload['recap']['period'] == datetime.now().strftime('%Y-%m')
    assert payload['recap']['is_ready'] is False
    assert payload['recap']['share_url'] is None
    assert payload['recap']['share_route'] is None
    assert 'title' not in payload['recap']
    assert 'summary_line' not in payload['recap']

    assert payload['recent_stories'] == []
    assert payload['inbox_preview'] == {'unread_count': 0, 'items': []}
    assert payload['most_visited'] == []


def test_dashboard_filled_returns_aggregates_and_recent_limit(client, settings) -> None:
    tokens = _get_tokens(client, 'dashboard-filled@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)
    user_id = _get_user_id_by_email(client, headers, 'dashboard-filled@example.com')

    paris_id = uuid4()
    berlin_id = uuid4()
    rome_id = uuid4()

    visit_fr_with_city_id = uuid4()
    visit_fr_no_city_id = uuid4()
    visit_de_id = uuid4()
    visit_it_id = uuid4()

    old_cover_file_id = uuid4()
    latest_cover_file_id = uuid4()
    secondary_cover_file_id = uuid4()

    sync_engine = create_engine(to_sync_database_url(settings.db.database_url), future=True)
    try:
        with sync_engine.begin() as conn:
            conn.execute(
                cities.insert(),
                [
                    {
                        'id': paris_id,
                        'country_code': 'FR',
                        'name': 'Paris',
                        'name_normalized': 'paris',
                    },
                    {
                        'id': berlin_id,
                        'country_code': 'DE',
                        'name': 'Berlin',
                        'name_normalized': 'berlin',
                    },
                    {
                        'id': rome_id,
                        'country_code': 'IT',
                        'name': 'Rome',
                        'name_normalized': 'rome',
                    },
                ],
            )
            conn.execute(
                visits.insert(),
                [
                    {
                        'id': visit_fr_with_city_id,
                        'user_id': user_id,
                        'country_code': 'FR',
                        'title': 'Paris story',
                        'visibility': VisitVisibility.PRIVATE,
                        'date_from': datetime(2025, 1, 10, 8, 0, tzinfo=timezone.utc).date(),
                        'city_id': paris_id,
                        'created': datetime(2025, 1, 10, 8, 0, tzinfo=timezone.utc),
                    },
                    {
                        'id': visit_fr_no_city_id,
                        'user_id': user_id,
                        'country_code': 'FR',
                        'title': 'France story',
                        'visibility': VisitVisibility.PRIVATE,
                        'date_from': datetime(2025, 1, 11, 8, 0, tzinfo=timezone.utc).date(),
                        'city_id': None,
                        'created': datetime(2025, 1, 11, 8, 0, tzinfo=timezone.utc),
                    },
                    {
                        'id': visit_de_id,
                        'user_id': user_id,
                        'country_code': 'DE',
                        'title': 'Berlin story',
                        'visibility': VisitVisibility.PRIVATE,
                        'date_from': datetime(2025, 1, 12, 8, 0, tzinfo=timezone.utc).date(),
                        'city_id': berlin_id,
                        'created': datetime(2025, 1, 12, 8, 0, tzinfo=timezone.utc),
                    },
                    {
                        'id': visit_it_id,
                        'user_id': user_id,
                        'country_code': 'IT',
                        'title': 'Rome story',
                        'visibility': VisitVisibility.PRIVATE,
                        'date_from': datetime(2025, 1, 13, 8, 0, tzinfo=timezone.utc).date(),
                        'city_id': rome_id,
                        'created': datetime(2025, 1, 13, 8, 0, tzinfo=timezone.utc),
                    },
                ],
            )
            conn.execute(
                files.insert(),
                [
                    {'id': old_cover_file_id, 'file_url': 'memory://old-cover.jpg', 'filename': 'old-cover.jpg'},
                    {
                        'id': latest_cover_file_id,
                        'file_url': 'memory://latest-cover.jpg',
                        'filename': 'latest-cover.jpg',
                    },
                    {
                        'id': secondary_cover_file_id,
                        'file_url': 'memory://secondary-cover.jpg',
                        'filename': 'secondary-cover.jpg',
                    },
                ],
            )
            conn.execute(
                files_visits.insert(),
                [
                    {
                        'id': uuid7(),
                        'file_id': old_cover_file_id,
                        'visit_id': visit_it_id,
                        'user_id': user_id,
                        'is_private': True,
                        'visibility': FileVisibility.PRIVATE,
                        'is_cover': True,
                    },
                    {
                        'id': uuid7(),
                        'file_id': latest_cover_file_id,
                        'visit_id': visit_it_id,
                        'user_id': user_id,
                        'is_private': False,
                        'visibility': FileVisibility.PUBLIC,
                        'is_cover': False,
                    },
                    {
                        'id': uuid7(),
                        'file_id': secondary_cover_file_id,
                        'visit_id': visit_fr_no_city_id,
                        'user_id': user_id,
                        'is_private': True,
                        'visibility': FileVisibility.PRIVATE,
                        'is_cover': False,
                    },
                ],
            )
    finally:
        sync_engine.dispose()

    response = client.get('/api/v1/me/dashboard', headers=headers)

    assert response.status_code == 200
    payload = response.json()

    assert payload['stats'] == {'countries_count': 3, 'cities_count': 3, 'stories_count': 4}

    recent_stories = payload['recent_stories']
    assert len(recent_stories) == 3
    assert [item['id'] for item in recent_stories] == [
        str(visit_it_id),
        str(visit_de_id),
        str(visit_fr_no_city_id),
    ]
    assert recent_stories[0]['cover'] == f'/api/v1/files/{old_cover_file_id}/download'
    assert recent_stories[1]['cover'] is None
    assert recent_stories[2]['cover'] == f'/api/v1/files/{secondary_cover_file_id}/download'
    assert all('title' not in item for item in recent_stories)

    most_visited = payload['most_visited']
    assert [item['country_name'] for item in most_visited] == ['France', 'Germany', 'Italy']
    assert [item['trips_count'] for item in most_visited] == [2, 1, 1]
    assert [item['relative_bar_value'] for item in most_visited] == [100, 50, 50]


def test_dashboard_is_strictly_scoped_to_current_user(client, settings) -> None:
    my_tokens = _get_tokens(client, 'dashboard-scope-me@example.com', settings.otp.otp_mock_code)
    _get_tokens(client, 'dashboard-scope-other@example.com', settings.otp.otp_mock_code)
    my_headers = _auth_headers(my_tokens)

    my_user_id = _get_user_id_by_email(client, my_headers, 'dashboard-scope-me@example.com')
    other_user_id = _get_user_id_by_email(client, my_headers, 'dashboard-scope-other@example.com')

    my_visit_id = uuid4()
    other_visit_id = uuid4()
    my_file_id = uuid4()
    other_file_id = uuid4()

    sync_engine = create_engine(to_sync_database_url(settings.db.database_url), future=True)
    try:
        with sync_engine.begin() as conn:
            conn.execute(
                visits.insert(),
                [
                    {
                        'id': my_visit_id,
                        'user_id': my_user_id,
                        'country_code': 'FR',
                        'title': 'My scope story',
                        'visibility': VisitVisibility.PRIVATE,
                        'date_from': datetime(2025, 2, 1, 12, 0, tzinfo=timezone.utc).date(),
                        'city_id': None,
                        'created': datetime(2025, 2, 1, 12, 0, tzinfo=timezone.utc),
                    },
                    {
                        'id': other_visit_id,
                        'user_id': other_user_id,
                        'country_code': 'DE',
                        'title': 'Other scope story',
                        'visibility': VisitVisibility.PRIVATE,
                        'date_from': datetime(2025, 2, 2, 12, 0, tzinfo=timezone.utc).date(),
                        'city_id': None,
                        'created': datetime(2025, 2, 2, 12, 0, tzinfo=timezone.utc),
                    },
                ],
            )
            conn.execute(
                files.insert(),
                [
                    {'id': my_file_id, 'file_url': 'memory://my-file.jpg', 'filename': 'my-file.jpg'},
                    {'id': other_file_id, 'file_url': 'memory://other-file.jpg', 'filename': 'other-file.jpg'},
                ],
            )
            conn.execute(
                files_visits.insert(),
                [
                    {
                        'id': uuid7(),
                        'file_id': my_file_id,
                        'visit_id': my_visit_id,
                        'user_id': my_user_id,
                        'is_private': True,
                        'visibility': FileVisibility.PRIVATE,
                    },
                    {
                        'id': uuid7(),
                        'file_id': other_file_id,
                        'visit_id': other_visit_id,
                        'user_id': other_user_id,
                        'is_private': False,
                        'visibility': FileVisibility.PUBLIC,
                    },
                ],
            )
    finally:
        sync_engine.dispose()

    response = client.get('/api/v1/me/dashboard', headers=my_headers)

    assert response.status_code == 200
    payload = response.json()

    assert payload['stats'] == {'countries_count': 1, 'cities_count': 0, 'stories_count': 1}
    assert len(payload['recent_stories']) == 1
    assert payload['recent_stories'][0]['id'] == str(my_visit_id)
    assert payload['recent_stories'][0]['cover'] == f'/api/v1/files/{my_file_id}/download'

    assert payload['most_visited'] == [
        {
            'country_name': 'France',
            'trips_count': 1,
            'relative_bar_value': 100,
        }
    ]
