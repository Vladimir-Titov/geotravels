from __future__ import annotations

from app.services.visits import VisitsService


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


def test_followers_flow_supports_own_and_foreign_listing(client, settings) -> None:
    me = _get_tokens(client, 'followers-me@example.com', settings.otp.otp_mock_code)
    other = _get_tokens(client, 'followers-other@example.com', settings.otp.otp_mock_code)
    _get_tokens(client, 'followers-target@example.com', settings.otp.otp_mock_code)

    me_headers = {'Authorization': f'Bearer {me["access_token"]}'}
    other_headers = {'Authorization': f'Bearer {other["access_token"]}'}

    target_user_id = _get_user_id_by_email(client, me_headers, 'followers-target@example.com')
    other_user_id = _get_user_id_by_email(client, me_headers, 'followers-other@example.com')

    assert client.get('/api/v1/followers').status_code == 401

    create_response = client.post(
        '/api/v1/followers',
        headers=me_headers,
        json={'following_id': target_user_id},
    )
    assert create_response.status_code == 201

    duplicate_response = client.post(
        '/api/v1/followers',
        headers=me_headers,
        json={'following_id': target_user_id},
    )
    assert duplicate_response.status_code == 409

    self_follow_response = client.post(
        '/api/v1/followers',
        headers=me_headers,
        json={'following_id': _get_user_id_by_email(client, me_headers, 'followers-me@example.com')},
    )
    assert self_follow_response.status_code == 400

    not_found_response = client.post(
        '/api/v1/followers',
        headers=me_headers,
        json={'following_id': '00000000-0000-0000-0000-000000000000'},
    )
    assert not_found_response.status_code == 404

    me_list = client.get('/api/v1/followers?limit=10&offset=0', headers=me_headers)
    assert me_list.status_code == 200
    me_payload = me_list.json()
    assert me_payload['pagination']['total'] == 1
    assert me_payload['items'][0]['following_id'] == target_user_id

    other_empty = client.get('/api/v1/followers?limit=10&offset=0', headers=other_headers)
    assert other_empty.status_code == 200
    assert other_empty.json()['pagination']['total'] == 0

    other_create = client.post(
        '/api/v1/followers',
        headers=other_headers,
        json={'following_id': target_user_id},
    )
    assert other_create.status_code == 201

    foreign_filtered = client.get(
        f'/api/v1/followers?limit=10&offset=0&follower_id={other_user_id}',
        headers=me_headers,
    )
    assert foreign_filtered.status_code == 200
    foreign_payload = foreign_filtered.json()
    assert foreign_payload['pagination']['total'] == 1
    assert foreign_payload['items'][0]['follower_id'] == other_user_id

    delete_response = client.delete(f'/api/v1/followers/{target_user_id}', headers=me_headers)
    assert delete_response.status_code in {200, 204}

    delete_missing = client.delete(f'/api/v1/followers/{target_user_id}', headers=me_headers)
    assert delete_missing.status_code == 404
