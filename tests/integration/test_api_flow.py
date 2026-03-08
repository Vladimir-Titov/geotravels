from __future__ import annotations


def test_auth_and_visit_flow(client) -> None:
    register_response = client.post(
        '/api/v1/auth/register',
        json={'email': 'api@example.com', 'password': 'secret123'},
    )
    assert register_response.status_code == 201
    tokens = register_response.json()

    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    countries_response = client.get('/api/v1/countries')
    assert countries_response.status_code == 200
    assert countries_response.json()['items']

    unauthorized = client.get('/api/v1/visits')
    assert unauthorized.status_code == 401

    mark_response = client.post(
        '/api/v1/visits',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'country_code': 'FR', 'trip_date': '2024-06-01'},
    )
    assert mark_response.status_code == 201

    visits_response = client.get(
        '/api/v1/visits',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert visits_response.status_code == 200
    payload = visits_response.json()
    assert len(payload['visits']) == 1
    assert payload['visited_country_codes'] == ['FR']

    refresh_response = client.post(
        '/api/v1/auth/refresh',
        json={'refresh_token': refresh_token},
    )
    assert refresh_response.status_code == 201
    assert refresh_response.json()['access_token']


def test_mark_unknown_country_returns_404(client) -> None:
    register_response = client.post(
        '/api/v1/auth/register',
        json={'email': 'api2@example.com', 'password': 'secret123'},
    )
    access_token = register_response.json()['access_token']

    mark_response = client.post(
        '/api/v1/visits',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'country_code': 'ZZ'},
    )
    assert mark_response.status_code == 404
