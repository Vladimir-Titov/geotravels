from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import create_engine

from app.models.tables import achievements, users_achievements
from app.services.geonames import GeoNamesClient
from app.services.visits import VisitsService
from settings import to_sync_database_url


def _get_tokens(client, email: str, otp_code: str) -> dict:
    otp_response = client.post(
        '/api/v1/auth/otp/request',
        json={'contact': email},
    )
    assert otp_response.status_code == 201
    otp_id = otp_response.json()['otp_id']

    verify_response = client.post(
        '/api/v1/auth/otp/verify',
        json={'otp_id': otp_id, 'code': otp_code},
    )
    assert verify_response.status_code == 201
    return verify_response.json()


def _get_user_id_by_email(client, auth_headers: dict[str, str], email: str) -> str:
    response = client.get(f'/api/v1/users?limit=1&offset=0&email={email}', headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload['pagination']['total'] == 1
    return payload['items'][0]['id']


def _auth_headers(tokens: dict) -> dict[str, str]:
    return {'Authorization': f'Bearer {tokens["access_token"]}'}


def _prepare_followers_context(client, settings) -> dict[str, str]:
    me = _get_tokens(client, 'followers-me@example.com', settings.otp.otp_mock_code)
    other = _get_tokens(client, 'followers-other@example.com', settings.otp.otp_mock_code)
    _get_tokens(client, 'followers-target@example.com', settings.otp.otp_mock_code)

    me_headers = _auth_headers(me)
    other_headers = _auth_headers(other)

    return {
        'me_headers': me_headers,
        'other_headers': other_headers,
        'me_user_id': _get_user_id_by_email(client, me_headers, 'followers-me@example.com'),
        'other_user_id': _get_user_id_by_email(client, me_headers, 'followers-other@example.com'),
        'target_user_id': _get_user_id_by_email(client, me_headers, 'followers-target@example.com'),
    }


def _seed_achievements_for_users(settings, user_id: str, other_user_id: str) -> dict[str, str]:
    earned_id = uuid4()
    foreign_earned_id = uuid4()

    sync_engine = create_engine(to_sync_database_url(settings.db.database_url), future=True)
    try:
        with sync_engine.connect() as conn:
            conn.execute(
                achievements.insert(),
                [
                    {
                        'id': earned_id,
                        'title': 'First Trip',
                        'description': 'Complete your first trip',
                        'logo_url': 'https://cdn.example.com/first-trip.png',
                    },
                    {
                        'id': foreign_earned_id,
                        'title': 'Explorer',
                        'description': 'Visit 10 countries',
                        'logo_url': None,
                    },
                ],
            )
            conn.execute(
                users_achievements.insert(),
                [
                    {'id': uuid4(), 'user_id': UUID(user_id), 'achievements_id': earned_id},
                    {'id': uuid4(), 'user_id': UUID(other_user_id), 'achievements_id': foreign_earned_id},
                ],
            )
            conn.commit()
    finally:
        sync_engine.dispose()

    return {'earned_id': str(earned_id), 'foreign_earned_id': str(foreign_earned_id)}


def test_auth_and_visit_flow(client, settings) -> None:
    tokens = _get_tokens(client, 'api@example.com', settings.otp.otp_mock_code)

    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    auth_headers = {'Authorization': f'Bearer {access_token}'}

    countries_response = client.get('/api/v1/countries', headers=auth_headers)
    assert countries_response.status_code == 200
    assert countries_response.json()['items']
    assert countries_response.json()['pagination']['offset'] == 0

    unauthorized = client.get('/api/v1/visits')
    assert unauthorized.status_code == 401

    create_response = client.post(
        '/api/v1/visits',
        headers=auth_headers,
        json={'country_code': 'FR', 'trip_date': '2024-06-01'},
    )
    assert create_response.status_code == 201
    visit_id = create_response.json()['id']

    get_response = client.get(f'/api/v1/visits/{visit_id}', headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()['country_code'] == 'FR'

    visits_response = client.get('/api/v1/visits', headers=auth_headers)
    assert visits_response.status_code == 200
    payload = visits_response.json()
    assert len(payload['items']) == 1
    assert payload['pagination']['total'] == 1

    patch_response = client.patch(
        f'/api/v1/visits/{visit_id}',
        headers=auth_headers,
        json={'trip_date': '2024-07-01'},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()['trip_date'] == '2024-07-01'

    delete_response = client.delete(f'/api/v1/visits/{visit_id}', headers=auth_headers)
    assert delete_response.status_code in {200, 204}

    after_delete_response = client.get('/api/v1/visits', headers=auth_headers)
    assert after_delete_response.status_code == 200
    assert after_delete_response.json()['items'] == []
    assert after_delete_response.json()['pagination']['total'] == 0

    refresh_response = client.post(
        '/api/v1/auth/refresh',
        json={'refresh_token': refresh_token},
    )
    assert refresh_response.status_code == 201
    assert refresh_response.json()['access_token']


def test_visits_are_user_scoped(client, settings) -> None:
    owner = _get_tokens(client, 'owner@example.com', settings.otp.otp_mock_code)
    stranger = _get_tokens(client, 'stranger@example.com', settings.otp.otp_mock_code)

    owner_headers = {'Authorization': f'Bearer {owner["access_token"]}'}
    stranger_headers = {'Authorization': f'Bearer {stranger["access_token"]}'}

    created = client.post('/api/v1/visits', headers=owner_headers, json={'country_code': 'FR'})
    assert created.status_code == 201
    visit_id = created.json()['id']

    assert client.get(f'/api/v1/visits/{visit_id}', headers=stranger_headers).status_code == 404

    patch_response = client.patch(
        f'/api/v1/visits/{visit_id}',
        headers=stranger_headers,
        json={'country_code': 'DE'},
    )
    assert patch_response.status_code == 404

    delete_response = client.delete(f'/api/v1/visits/{visit_id}', headers=stranger_headers)
    assert delete_response.status_code == 404


def test_files_crud_for_owner(client, settings) -> None:
    tokens = _get_tokens(client, 'files-owner@example.com', settings.otp.otp_mock_code)
    auth_headers = _auth_headers(tokens)

    created_visit = client.post('/api/v1/visits', headers=auth_headers, json={'country_code': 'FR'})
    assert created_visit.status_code == 201
    visit_id = created_visit.json()['id']

    create_file_response = client.post(
        '/api/v1/files',
        headers=auth_headers,
        data={
            'visit_id': visit_id,
            'is_private': False,
        },
        files={'file': ('paris.jpg', b'fake-image-content', 'image/jpeg')},
    )
    assert create_file_response.status_code == 201
    created_file = create_file_response.json()
    assert created_file['visit_id'] == visit_id
    assert created_file['filename'] == 'paris.jpg'

    download_response = client.get(f"/api/v1/files/{created_file['id']}/download", headers=auth_headers)
    assert download_response.status_code == 200
    assert download_response.content == b'fake-image-content'
    assert download_response.headers['content-type'] == 'image/jpeg'
    assert download_response.headers['content-disposition'] == 'attachment; filename="paris.jpg"'

    mine_response = client.get('/api/v1/files/mine?limit=10&offset=0', headers=auth_headers)
    assert mine_response.status_code == 200
    mine_payload = mine_response.json()
    assert mine_payload['pagination']['total'] == 1
    assert mine_payload['items'][0]['id'] == created_file['id']

    update_response = client.patch(
        f"/api/v1/files/{created_file['id']}",
        headers=auth_headers,
        json={'filename': 'eiffel.jpg'},
    )
    assert update_response.status_code == 200
    assert update_response.json()['filename'] == 'eiffel.jpg'

    delete_response = client.delete(f"/api/v1/files/{created_file['id']}", headers=auth_headers)
    assert delete_response.status_code == 200

    after_delete = client.get('/api/v1/files/mine?limit=10&offset=0', headers=auth_headers)
    assert after_delete.status_code == 200
    assert after_delete.json()['pagination']['total'] == 0


def test_files_visibility_and_ownership(client, settings) -> None:
    owner_tokens = _get_tokens(client, 'files-owner2@example.com', settings.otp.otp_mock_code)
    stranger_tokens = _get_tokens(client, 'files-stranger@example.com', settings.otp.otp_mock_code)

    owner_headers = _auth_headers(owner_tokens)
    stranger_headers = _auth_headers(stranger_tokens)
    owner_user_id = _get_user_id_by_email(client, owner_headers, 'files-owner2@example.com')

    created_visit = client.post('/api/v1/visits', headers=owner_headers, json={'country_code': 'IT'})
    assert created_visit.status_code == 201
    visit_id = created_visit.json()['id']

    public_file = client.post(
        '/api/v1/files',
        headers=owner_headers,
        data={
            'visit_id': visit_id,
            'is_private': False,
        },
        files={'file': ('public.jpg', b'public-bytes', 'image/jpeg')},
    )
    assert public_file.status_code == 201
    public_file_id = public_file.json()['id']

    private_file = client.post(
        '/api/v1/files',
        headers=owner_headers,
        data={
            'visit_id': visit_id,
            'is_private': True,
        },
        files={'file': ('private.jpg', b'private-bytes', 'image/jpeg')},
    )
    assert private_file.status_code == 201

    public_list = client.get(
        f'/api/v1/files/users/{owner_user_id}?limit=10&offset=0',
        headers=stranger_headers,
    )
    assert public_list.status_code == 200
    public_payload = public_list.json()
    assert public_payload['pagination']['total'] == 1
    assert public_payload['items'][0]['id'] == public_file_id
    assert public_payload['items'][0]['is_private'] is False

    foreign_update = client.patch(
        f'/api/v1/files/{public_file_id}',
        headers=stranger_headers,
        json={'filename': 'hacked.jpg'},
    )
    assert foreign_update.status_code == 404

    foreign_download = client.get(f'/api/v1/files/{public_file_id}/download', headers=stranger_headers)
    assert foreign_download.status_code == 404

    foreign_delete = client.delete(f'/api/v1/files/{public_file_id}', headers=stranger_headers)
    assert foreign_delete.status_code == 404


def test_countries_and_users_list_require_auth_and_support_filters(client, settings) -> None:
    tokens = _get_tokens(client, 'lists@example.com', settings.otp.otp_mock_code)
    auth_headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

    assert client.get('/api/v1/countries').status_code == 401
    assert client.get('/api/v1/users').status_code == 401

    countries_response = client.get('/api/v1/countries?limit=5&offset=0&iso_a2=FR', headers=auth_headers)
    assert countries_response.status_code == 200
    countries_payload = countries_response.json()
    assert countries_payload['pagination']['limit'] == 5
    assert countries_payload['pagination']['offset'] == 0
    assert countries_payload['pagination']['total'] == 1
    assert countries_payload['items'][0]['iso_a2'] == 'FR'

    users_response = client.get('/api/v1/users?limit=10&offset=0&email=lists@example.com', headers=auth_headers)
    assert users_response.status_code == 200
    users_payload = users_response.json()
    assert users_payload['pagination']['limit'] == 10
    assert users_payload['pagination']['offset'] == 0
    assert users_payload['pagination']['total'] == 1
    assert users_payload['items'][0]['email'] == 'lists@example.com'


def test_countries_in_filter_works_with_repeated_query_params(client, settings) -> None:
    tokens = _get_tokens(client, 'countries-in@example.com', settings.otp.otp_mock_code)
    auth_headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

    response = client.get(
        '/api/v1/countries?limit=10&offset=0&iso_a2_in=FR&iso_a2_in=DE',
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['pagination']['total'] == 2
    assert [item['iso_a2'] for item in payload['items']] == ['DE', 'FR']


def test_visits_user_id_filter_is_ignored(client, settings) -> None:
    tokens = _get_tokens(client, 'visit-filter@example.com', settings.otp.otp_mock_code)
    auth_headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

    created = client.post('/api/v1/visits', headers=auth_headers, json={'country_code': 'FR'})
    assert created.status_code == 201

    response = client.get('/api/v1/visits?user_id=00000000-0000-0000-0000-000000000000', headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload['items']) == 1
    assert payload['pagination']['total'] == 1


def test_countries_geojson_removed(client) -> None:
    response = client.get('/api/v1/countries/geojson')
    assert response.status_code == 404


def test_client_geo_endpoints_require_user_auth(client, settings) -> None:
    unauthorized = client.get('/api/v1/client/geo/countries?limit=5&offset=0&iso_a2=FR')
    assert unauthorized.status_code == 401

    invalid_auth = client.get(
        '/api/v1/client/geo/countries?limit=5&offset=0&iso_a2=FR',
        headers={'Authorization': 'Bearer invalid-token'},
    )
    assert invalid_auth.status_code == 401


def test_client_geo_countries_fallback_to_geonames_and_persists_meta(client, settings, monkeypatch) -> None:
    async def _mock_search_countries(self, *, query, country_codes, limit, offset):  # noqa: ARG001
        return [
            {
                'iso_a2': 'ZZ',
                'name': 'Zedland',
                'meta': {'geonameId': 999001, 'countryCode': 'ZZ', 'countryName': 'Zedland'},
            }
        ]

    monkeypatch.setattr(GeoNamesClient, 'search_countries', _mock_search_countries)
    tokens = _get_tokens(client, 'client-geo-countries@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)

    first = client.get('/api/v1/client/geo/countries?limit=5&offset=0&iso_a2=ZZ', headers=headers)
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload['pagination']['total'] == 1
    assert first_payload['items'][0]['iso_a2'] == 'ZZ'
    assert first_payload['items'][0]['meta']['geonameId'] == 999001

    second = client.get('/api/v1/client/geo/countries?limit=5&offset=0&iso_a2=ZZ', headers=headers)
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload['pagination']['total'] == 1
    assert second_payload['items'][0]['meta']['geonameId'] == 999001


def test_client_geo_cities_fallback_to_geonames_and_persists_meta(client, settings, monkeypatch) -> None:
    calls = {'count': 0}

    async def _mock_search_cities(self, *, query, country_code, limit, offset):  # noqa: ARG001
        calls['count'] += 1
        return [
            {
                'id': UUID('05f1e4a3-0d4a-5ea0-a368-bf7e70f5b8ec'),
                'country_code': 'FR',
                'name': 'Paris',
                'name_normalized': 'paris',
                'latitude': Decimal('48.8566'),
                'longitude': Decimal('2.3522'),
                'population': 2148327,
                'meta': {'geonameId': 2988507, 'countryCode': 'FR', 'countryName': 'France', 'name': 'Paris'},
            }
        ]

    monkeypatch.setattr(GeoNamesClient, 'search_cities', _mock_search_cities)
    tokens = _get_tokens(client, 'client-geo-cities@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)

    first = client.get('/api/v1/client/geo/cities?limit=5&offset=0&name_ilike=Paris', headers=headers)
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload['pagination']['total'] == 1
    assert first_payload['items'][0]['name'] == 'Paris'
    assert first_payload['items'][0]['country_code'] == 'FR'
    assert first_payload['items'][0]['meta']['geonameId'] == 2988507

    second = client.get('/api/v1/client/geo/cities?limit=5&offset=0&name_ilike=Paris', headers=headers)
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload['pagination']['total'] == 1
    assert second_payload['items'][0]['name'] == 'Paris'
    assert calls['count'] == 1


def test_client_geo_repeated_requests_are_allowed(client, settings) -> None:
    tokens = _get_tokens(client, 'client-geo-repeat@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)

    first = client.get('/api/v1/client/geo/countries?limit=5&offset=0&iso_a2=FR', headers=headers)
    assert first.status_code == 200

    second = client.get('/api/v1/client/geo/countries?limit=5&offset=0&iso_a2=FR', headers=headers)
    assert second.status_code == 200


def test_service_error_status_code_passthrough(client, settings) -> None:
    first = client.post('/api/v1/auth/otp/request', json={'contact': 'ratelimit@example.com'})
    assert first.status_code == 201

    second = client.post('/api/v1/auth/otp/request', json={'contact': 'ratelimit@example.com'})
    assert second.status_code == 429
    payload = second.json()
    assert payload['status_code'] == 429
    assert payload['detail']['error'] == 'Please wait before requesting a new code'


def test_unhandled_runtime_is_wrapped_into_service_error(client, settings, monkeypatch) -> None:
    tokens = _get_tokens(client, 'boom@example.com', settings.otp.otp_mock_code)
    auth_headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

    async def _raise_runtime_error(*_args, **_kwargs):
        raise RuntimeError('boom')

    monkeypatch.setattr(VisitsService, 'list_visits', _raise_runtime_error)

    response = client.get('/api/v1/visits', headers=auth_headers)
    assert response.status_code == 500
    payload = response.json()
    assert payload['status_code'] == 500
    assert payload['detail'] == 'Internal Server Error'


def test_followers_endpoints_require_auth(client) -> None:
    assert client.get('/api/v1/followers').status_code == 401

    create = client.post(
        '/api/v1/followers',
        json={'following_id': '00000000-0000-0000-0000-000000000000'},
    )
    assert create.status_code == 401

    delete = client.delete('/api/v1/followers/00000000-0000-0000-0000-000000000000')
    assert delete.status_code == 401


def test_achievements_endpoints_require_auth(client) -> None:
    assert client.get('/api/v1/achievements').status_code == 401
    assert client.get('/api/v1/achievements/my').status_code == 401


def test_achievements_list_and_my_achievements_are_user_scoped(client, settings) -> None:
    me = _get_tokens(client, 'achievements-me@example.com', settings.otp.otp_mock_code)
    other = _get_tokens(client, 'achievements-other@example.com', settings.otp.otp_mock_code)

    me_headers = _auth_headers(me)
    other_headers = _auth_headers(other)

    me_user_id = _get_user_id_by_email(client, me_headers, 'achievements-me@example.com')
    other_user_id = _get_user_id_by_email(client, me_headers, 'achievements-other@example.com')

    seeded = _seed_achievements_for_users(settings, user_id=me_user_id, other_user_id=other_user_id)

    list_response = client.get('/api/v1/achievements?limit=10&offset=0&order_by=title', headers=me_headers)
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload['pagination']['total'] == 2
    assert [item['title'] for item in list_payload['items']] == ['Explorer', 'First Trip']
    assert {item['id'] for item in list_payload['items']} == {
        seeded['earned_id'],
        seeded['foreign_earned_id'],
    }

    filtered_list = client.get('/api/v1/achievements?limit=10&offset=0&title=Explorer', headers=me_headers)
    assert filtered_list.status_code == 200
    filtered_payload = filtered_list.json()
    assert filtered_payload['pagination']['total'] == 1
    assert filtered_payload['items'][0]['id'] == seeded['foreign_earned_id']

    my_response = client.get('/api/v1/achievements/my?limit=10&offset=0&title=First%20Trip', headers=me_headers)
    assert my_response.status_code == 200
    my_payload = my_response.json()
    assert my_payload['pagination']['total'] == 1
    assert my_payload['items'][0]['id'] == seeded['earned_id']
    assert my_payload['items'][0]['complete_at']

    my_foreign_filtered = client.get(
        f'/api/v1/achievements/my?limit=10&offset=0&id={seeded["foreign_earned_id"]}',
        headers=me_headers,
    )
    assert my_foreign_filtered.status_code == 200
    assert my_foreign_filtered.json()['pagination']['total'] == 0

    other_response = client.get('/api/v1/achievements/my?limit=10&offset=0', headers=other_headers)
    assert other_response.status_code == 200
    other_payload = other_response.json()
    assert other_payload['pagination']['total'] == 1
    assert other_payload['items'][0]['id'] == seeded['foreign_earned_id']


def test_followers_subscribe_creates_relation_and_lists_own(client, settings) -> None:
    ctx = _prepare_followers_context(client, settings)

    create_response = client.post(
        '/api/v1/followers',
        headers=ctx['me_headers'],
        json={'following_id': ctx['target_user_id']},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created['follower_id'] == ctx['me_user_id']
    assert created['following_id'] == ctx['target_user_id']

    me_list = client.get('/api/v1/followers?limit=10&offset=0', headers=ctx['me_headers'])
    assert me_list.status_code == 200
    me_payload = me_list.json()
    assert me_payload['pagination']['total'] == 1
    assert me_payload['items'][0]['following_id'] == ctx['target_user_id']


def test_followers_subscribe_validations(client, settings) -> None:
    ctx = _prepare_followers_context(client, settings)

    self_follow_response = client.post(
        '/api/v1/followers',
        headers=ctx['me_headers'],
        json={'following_id': ctx['me_user_id']},
    )
    assert self_follow_response.status_code == 400

    not_found_response = client.post(
        '/api/v1/followers',
        headers=ctx['me_headers'],
        json={'following_id': '00000000-0000-0000-0000-000000000000'},
    )
    assert not_found_response.status_code == 404

    created = client.post(
        '/api/v1/followers',
        headers=ctx['me_headers'],
        json={'following_id': ctx['target_user_id']},
    )
    assert created.status_code == 201

    duplicate = client.post(
        '/api/v1/followers',
        headers=ctx['me_headers'],
        json={'following_id': ctx['target_user_id']},
    )
    assert duplicate.status_code == 409


def test_followers_list_supports_foreign_filter(client, settings) -> None:
    ctx = _prepare_followers_context(client, settings)

    other_empty = client.get('/api/v1/followers?limit=10&offset=0', headers=ctx['other_headers'])
    assert other_empty.status_code == 200
    assert other_empty.json()['pagination']['total'] == 0

    other_create = client.post(
        '/api/v1/followers',
        headers=ctx['other_headers'],
        json={'following_id': ctx['target_user_id']},
    )
    assert other_create.status_code == 201

    foreign_filtered = client.get(
        f'/api/v1/followers?limit=10&offset=0&follower_id={ctx["other_user_id"]}',
        headers=ctx['me_headers'],
    )
    assert foreign_filtered.status_code == 200
    foreign_payload = foreign_filtered.json()
    assert foreign_payload['pagination']['total'] == 1
    assert foreign_payload['items'][0]['follower_id'] == ctx['other_user_id']


def test_followers_unsubscribe_returns_removed_relation(client, settings) -> None:
    ctx = _prepare_followers_context(client, settings)

    create_response = client.post(
        '/api/v1/followers',
        headers=ctx['me_headers'],
        json={'following_id': ctx['target_user_id']},
    )
    assert create_response.status_code == 201
    created = create_response.json()

    delete_response = client.delete(
        f'/api/v1/followers/{ctx["target_user_id"]}',
        headers=ctx['me_headers'],
    )
    assert delete_response.status_code == 200
    deleted = delete_response.json()
    assert deleted['id'] == created['id']
    assert deleted['follower_id'] == ctx['me_user_id']
    assert deleted['following_id'] == ctx['target_user_id']

    after_delete = client.get('/api/v1/followers?limit=10&offset=0', headers=ctx['me_headers'])
    assert after_delete.status_code == 200
    assert after_delete.json()['pagination']['total'] == 0

    delete_missing = client.delete(
        f'/api/v1/followers/{ctx["target_user_id"]}',
        headers=ctx['me_headers'],
    )
    assert delete_missing.status_code == 404
