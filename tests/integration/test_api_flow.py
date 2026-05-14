from decimal import Decimal
from urllib.parse import urlencode
from uuid import UUID, uuid4

from sqlalchemy import create_engine

from app.models.tables import (
    CheckListStatus,
    FileVisibility,
    VisitStatus,
    VisitVisibility,
    achievements,
    cities,
    countries,
    users_achievements,
)
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


def _sample_image_bytes() -> bytes:
    import pyvips

    return pyvips.Image.black(8, 8).new_from_image(255).write_to_buffer('.png')


def _create_visit(client, auth_headers: dict[str, str], **payload) -> dict:
    response = client.post('/api/v1/visits', headers=auth_headers, json=payload)
    assert response.status_code == 201
    return response.json()


def _upload_file_for_visit(
    client,
    auth_headers: dict[str, str],
    visit_id: str,
    filename: str,
    content: bytes,
    is_private: bool = False,
) -> dict:
    response = client.post(
        f'/api/v1/visits/{visit_id}/file',
        headers=auth_headers,
        data={
            'visibility': FileVisibility.PRIVATE.value if is_private else FileVisibility.PUBLIC.value,
        },
        files={'file': (filename, content, 'image/jpeg')},
    )
    assert response.status_code == 201
    return response.json()


def _assert_imgproxy_url(url: str | None, variant: str) -> None:
    options_by_variant = {
        'full': '/rs:fit:1600:1600:0/q:80/',
        'preview': '/rs:fit:1280:1280:0/q:84/',
        'thumb': '/rs:fit:720:720:0/q:82/',
    }

    assert url is not None
    assert url.startswith('http://localhost:8080/')
    assert options_by_variant[variant] in url
    assert '/plain/' in url
    assert url.endswith('@webp')


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
        json={'country_code': 'FR', 'trip_start': '2024-06-01'},
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
        json={'trip_start': '2024-07-01', 'status': VisitStatus.PLANNED},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()['trip_start'] == '2024-07-01'
    assert patch_response.json()['status'] == VisitStatus.PLANNED

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


def test_visits_v2_contract_and_cover_file_management(client, settings) -> None:
    tokens = _get_tokens(client, 'api-v2@example.com', settings.otp.otp_mock_code)
    auth_headers = _auth_headers(tokens)

    paris_id = uuid4()
    lyon_id = uuid4()

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
                    },
                    {
                        'id': lyon_id,
                        'country_code': 'FR',
                        'name': 'Lyon',
                    },
                ],
            )
    finally:
        sync_engine.dispose()

    create_response = client.post(
        '/api/v1/visits',
        headers=auth_headers,
        json={
            'country_code': 'FR',
            'title': 'France spring trip',
            'description': 'Paris and Lyon',
            'visibility': VisitVisibility.FOLLOWERS,
            'trip_start': '2025-03-10',
            'trip_end': '2025-03-15',
            'city_ids': [str(paris_id), str(lyon_id)],
        },
    )
    assert create_response.status_code == 201
    created_visit = create_response.json()
    visit_id = created_visit['id']

    assert created_visit['title'] == 'France spring trip'
    assert created_visit['description'] == 'Paris and Lyon'
    assert created_visit['visibility'] == VisitVisibility.FOLLOWERS
    assert created_visit['status'] == VisitStatus.VISITED
    assert created_visit['trip_start'] == '2025-03-10'
    assert created_visit['trip_end'] == '2025-03-15'
    assert created_visit['city_ids'] == [str(paris_id), str(lyon_id)]
    assert 'city_id' not in created_visit
    assert created_visit['cover_file_id'] is None

    upload_cover_response = client.post(
        f'/api/v1/visits/{visit_id}/file',
        headers=auth_headers,
        data={
            'visibility': FileVisibility.PUBLIC.value,
        },
        files={'file': ('cover.jpg', _sample_image_bytes(), 'image/jpeg')},
    )
    assert upload_cover_response.status_code == 201
    cover_file_payload = upload_cover_response.json()
    cover_file_id = cover_file_payload['id']
    assert cover_file_payload['is_cover'] is False

    set_cover_response = client.patch(
        f'/api/v1/visits/{visit_id}',
        headers=auth_headers,
        json={'cover_file_id': cover_file_id, 'visibility': VisitVisibility.PUBLIC},
    )
    assert set_cover_response.status_code == 200
    assert set_cover_response.json()['cover_file_id'] == cover_file_id
    assert set_cover_response.json()['visibility'] == VisitVisibility.PUBLIC

    covered_files_response = client.get(
        f'/api/v1/files/mine?limit=10&offset=0&visit_id={visit_id}',
        headers=auth_headers,
    )
    assert covered_files_response.status_code == 200
    covered_files = covered_files_response.json()['items']
    assert len(covered_files) == 1
    assert covered_files[0]['id'] == cover_file_id
    assert covered_files[0]['is_cover'] is True

    get_response = client.get(f'/api/v1/visits/{visit_id}', headers=auth_headers)
    assert get_response.status_code == 200
    loaded = get_response.json()
    assert loaded['city_ids'] == [str(paris_id), str(lyon_id)]
    assert loaded['cover_file_id'] == cover_file_id
    assert loaded['visibility'] == VisitVisibility.PUBLIC

    list_response = client.get('/api/v1/visits?limit=10&offset=0', headers=auth_headers)
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload['pagination']['total'] == 1
    assert list_payload['items'][0]['title'] == 'France spring trip'
    assert list_payload['items'][0]['city_ids'] == [str(paris_id), str(lyon_id)]

    unset_cover_response = client.patch(
        f'/api/v1/visits/{visit_id}',
        headers=auth_headers,
        json={'cover_file_id': None},
    )
    assert unset_cover_response.status_code == 200
    assert unset_cover_response.json()['cover_file_id'] is None

    uncovered_files_response = client.get(
        f'/api/v1/files/mine?limit=10&offset=0&visit_id={visit_id}',
        headers=auth_headers,
    )
    assert uncovered_files_response.status_code == 200
    assert uncovered_files_response.json()['items'][0]['is_cover'] is False

    foreign_cover_response = client.patch(
        f'/api/v1/visits/{visit_id}',
        headers=auth_headers,
        json={'cover_file_id': str(uuid4())},
    )
    assert foreign_cover_response.status_code == 400


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


def test_visits_status_filters_and_trip_date_payload_is_rejected(client, settings) -> None:
    tokens = _get_tokens(client, 'visit-status@example.com', settings.otp.otp_mock_code)
    auth_headers = _auth_headers(tokens)

    created = _create_visit(
        client,
        auth_headers,
        country_code='FR',
        status=VisitStatus.IN_TRIP,
        trip_start='2025-05-01',
    )
    assert created['status'] == VisitStatus.IN_TRIP

    filtered = client.get(
        f'/api/v1/visits?limit=10&offset=0&status={VisitStatus.IN_TRIP}',
        headers=auth_headers,
    )
    assert filtered.status_code == 200
    filtered_payload = filtered.json()
    assert filtered_payload['pagination']['total'] == 1
    assert filtered_payload['items'][0]['id'] == created['id']

    rejected_date_from_create = client.post(
        '/api/v1/visits',
        headers=auth_headers,
        json={'country_code': 'FR', 'date_from': '2025-05-02'},
    )
    assert rejected_date_from_create.status_code == 400

    rejected_date_to_create = client.post(
        '/api/v1/visits',
        headers=auth_headers,
        json={'country_code': 'FR', 'date_to': '2025-05-02'},
    )
    assert rejected_date_to_create.status_code == 400

    rejected_city_id_create = client.post(
        '/api/v1/visits',
        headers=auth_headers,
        json={'country_code': 'FR', 'city_id': str(uuid4())},
    )
    assert rejected_city_id_create.status_code == 400

    rejected_create = client.post(
        '/api/v1/visits',
        headers=auth_headers,
        json={'country_code': 'FR', 'trip_date': '2025-05-02'},
    )
    assert rejected_create.status_code == 400

    rejected_patch = client.patch(
        f'/api/v1/visits/{created["id"]}',
        headers=auth_headers,
        json={'trip_date': '2025-05-03'},
    )
    assert rejected_patch.status_code == 400

    rejected_date_from_patch = client.patch(
        f'/api/v1/visits/{created["id"]}',
        headers=auth_headers,
        json={'date_from': '2025-05-03'},
    )
    assert rejected_date_from_patch.status_code == 400

    rejected_city_id_patch = client.patch(
        f'/api/v1/visits/{created["id"]}',
        headers=auth_headers,
        json={'city_id': str(uuid4())},
    )
    assert rejected_city_id_patch.status_code == 400


def test_trip_cards_details_statistics_and_nullable_dates(client, settings) -> None:
    tokens = _get_tokens(client, 'trip-read-models@example.com', settings.otp.otp_mock_code)
    auth_headers = _auth_headers(tokens)

    paris_id = uuid4()
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
                    }
                ],
            )
    finally:
        sync_engine.dispose()

    memory_visit = _create_visit(
        client,
        auth_headers,
        country_code='FR',
        title='Paris memory',
        status=VisitStatus.VISITED,
        city_ids=[str(paris_id)],
    )
    assert memory_visit['trip_start'] is None

    dated_memory = _create_visit(
        client,
        auth_headers,
        country_code='FR',
        title='France return',
        status=VisitStatus.VISITED,
        trip_start='2025-04-10',
    )
    plan = _create_visit(
        client,
        auth_headers,
        country_code='IT',
        title='Rome plan',
        status=VisitStatus.PLANNED,
        trip_start='2026-05-01',
    )

    _upload_file_for_visit(
        client,
        auth_headers,
        memory_visit['id'],
        'paris.jpg',
        _sample_image_bytes(),
    )

    checklist_response = client.post(
        '/api/v1/visits/checklist',
        headers=auth_headers,
        json={'visit_id': memory_visit['id'], 'content': 'Upload photos'},
    )
    assert checklist_response.status_code == 201
    checklist_id = checklist_response.json()['id']
    checklist_done = client.patch(
        f'/api/v1/visits/checklist/{checklist_id}',
        headers=auth_headers,
        json={'status': CheckListStatus.DONE},
    )
    assert checklist_done.status_code == 200

    place_response = client.post(
        '/api/v1/visits/places',
        headers=auth_headers,
        json={'visit_id': memory_visit['id'], 'title': 'Louvre'},
    )
    assert place_response.status_code == 201
    place_id = place_response.json()['id']
    place_visited = client.patch(
        f'/api/v1/visits/places/{place_id}',
        headers=auth_headers,
        json={'is_visited': True},
    )
    assert place_visited.status_code == 200

    visited_cards = client.get('/api/v1/visits/cards?status=visited&limit=10&offset=0', headers=auth_headers)
    assert visited_cards.status_code == 200
    visited_payload = visited_cards.json()
    assert visited_payload['pagination']['total'] == 2
    assert [item['id'] for item in visited_payload['items']] == [dated_memory['id'], memory_visit['id']]

    memory_card = next(item for item in visited_payload['items'] if item['id'] == memory_visit['id'])
    assert memory_card['trip_start'] is None
    _assert_imgproxy_url(memory_card['cover_url'], 'thumb')
    assert memory_card['photos_count'] == 1
    assert memory_card['checklist_total'] == 1
    assert memory_card['checklist_done'] == 1
    assert memory_card['places_total'] == 1
    assert memory_card['places_visited'] == 1
    assert memory_card['cities'] == [{'id': str(paris_id), 'name': 'Paris', 'country_code': 'FR'}]

    city_filtered = client.get(f'/api/v1/visits?limit=10&offset=0&city_ids_in={paris_id}', headers=auth_headers)
    assert city_filtered.status_code == 200
    city_filtered_payload = city_filtered.json()
    assert city_filtered_payload['pagination']['total'] == 1
    assert city_filtered_payload['items'][0]['id'] == memory_visit['id']

    planned_cards = client.get('/api/v1/visits/cards?status=planned&limit=10&offset=0', headers=auth_headers)
    assert planned_cards.status_code == 200
    planned_payload = planned_cards.json()
    assert planned_payload['pagination']['total'] == 1
    assert planned_payload['items'][0]['id'] == plan['id']

    details = client.get(f'/api/v1/visits/{memory_visit["id"]}/details', headers=auth_headers)
    assert details.status_code == 200
    details_payload = details.json()
    _assert_imgproxy_url(details_payload['visit']['cover_url'], 'thumb')
    _assert_imgproxy_url(details_payload['photos'][0]['file_url'], 'full')
    _assert_imgproxy_url(details_payload['photos'][0]['thumbnail_url'], 'thumb')
    _assert_imgproxy_url(details_payload['photos'][0]['preview_url'], 'preview')
    assert details_payload['checklist'][0]['status'] == CheckListStatus.DONE
    assert details_payload['places'][0]['is_visited'] is True
    assert details_payload['cities'][0]['name'] == 'Paris'

    statistics = client.get('/api/v1/visits/statistics', headers=auth_headers)
    assert statistics.status_code == 200
    stats_payload = statistics.json()
    assert stats_payload['visited_count'] == 2
    assert stats_payload['planned_count'] == 1
    assert stats_payload['countries_count'] == 1
    assert stats_payload['cities_count'] == 1
    assert stats_payload['repeated_countries_count'] == 1
    assert stats_payload['favorite_city']['city_name'] == 'Paris'
    assert stats_payload['trips_by_country'] == [{'country_name': 'France', 'trips_count': 2}]


def test_visits_checklist_crud(client, settings) -> None:
    owner_tokens = _get_tokens(client, 'checklist-owner@example.com', settings.otp.otp_mock_code)
    stranger_tokens = _get_tokens(client, 'checklist-stranger@example.com', settings.otp.otp_mock_code)
    owner_headers = _auth_headers(owner_tokens)
    stranger_headers = _auth_headers(stranger_tokens)

    visit = _create_visit(client, owner_headers, country_code='FR')

    assert client.get('/api/v1/visits/checklist?limit=10&offset=0').status_code == 401

    created = client.post(
        '/api/v1/visits/checklist',
        headers=owner_headers,
        json={'visit_id': visit['id'], 'content': '  Pack passport  '},
    )
    assert created.status_code == 201
    created_payload = created.json()
    checklist_id = created_payload['id']
    assert created_payload['content'] == 'Pack passport'
    assert created_payload['status'] == CheckListStatus.TO_DO

    loaded = client.get(f'/api/v1/visits/checklist/{checklist_id}', headers=owner_headers)
    assert loaded.status_code == 200
    assert loaded.json()['id'] == checklist_id

    listed = client.get(
        f'/api/v1/visits/checklist?limit=10&offset=0&visit_id={visit["id"]}&status=to_do',
        headers=owner_headers,
    )
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert listed_payload['pagination']['total'] == 1
    assert listed_payload['items'][0]['id'] == checklist_id

    updated = client.patch(
        f'/api/v1/visits/checklist/{checklist_id}',
        headers=owner_headers,
        json={'content': '  Passport ready  ', 'status': CheckListStatus.DONE},
    )
    assert updated.status_code == 200
    updated_payload = updated.json()
    assert updated_payload['content'] == 'Passport ready'
    assert updated_payload['status'] == CheckListStatus.DONE

    empty_patch = client.patch(
        f'/api/v1/visits/checklist/{checklist_id}',
        headers=owner_headers,
        json={},
    )
    assert empty_patch.status_code == 400

    assert client.get(f'/api/v1/visits/checklist/{checklist_id}', headers=stranger_headers).status_code == 404

    foreign_create = client.post(
        '/api/v1/visits/checklist',
        headers=stranger_headers,
        json={'visit_id': visit['id'], 'content': 'Should fail'},
    )
    assert foreign_create.status_code == 404

    deleted = client.delete(f'/api/v1/visits/checklist/{checklist_id}', headers=owner_headers)
    assert deleted.status_code == 204

    after_delete = client.get('/api/v1/visits/checklist?limit=10&offset=0', headers=owner_headers)
    assert after_delete.status_code == 200
    assert after_delete.json()['pagination']['total'] == 0


def test_visits_places_crud_and_duplicate_validation(client, settings) -> None:
    owner_tokens = _get_tokens(client, 'places-owner@example.com', settings.otp.otp_mock_code)
    stranger_tokens = _get_tokens(client, 'places-stranger@example.com', settings.otp.otp_mock_code)
    owner_headers = _auth_headers(owner_tokens)
    stranger_headers = _auth_headers(stranger_tokens)

    visit = _create_visit(client, owner_headers, country_code='IT')

    assert client.get('/api/v1/visits/places?limit=10&offset=0').status_code == 401

    created = client.post(
        '/api/v1/visits/places',
        headers=owner_headers,
        json={'visit_id': visit['id'], 'title': '  Trevi Fountain  '},
    )
    assert created.status_code == 201
    created_payload = created.json()
    place_id = created_payload['id']
    assert created_payload['title'] == 'Trevi Fountain'
    assert created_payload['is_visited'] is False

    duplicate = client.post(
        '/api/v1/visits/places',
        headers=owner_headers,
        json={'visit_id': visit['id'], 'title': 'Trevi Fountain'},
    )
    assert duplicate.status_code == 409

    listed = client.get(
        f'/api/v1/visits/places?limit=10&offset=0&visit_id={visit["id"]}&is_visited=false',
        headers=owner_headers,
    )
    assert listed.status_code == 200
    assert listed.json()['pagination']['total'] == 1

    updated = client.patch(
        f'/api/v1/visits/places/{place_id}',
        headers=owner_headers,
        json={'title': 'Trevi Fountain at Night', 'is_visited': True},
    )
    assert updated.status_code == 200
    updated_payload = updated.json()
    assert updated_payload['title'] == 'Trevi Fountain at Night'
    assert updated_payload['is_visited'] is True

    empty_patch = client.patch(
        f'/api/v1/visits/places/{place_id}',
        headers=owner_headers,
        json={},
    )
    assert empty_patch.status_code == 400

    assert client.get(f'/api/v1/visits/places/{place_id}', headers=stranger_headers).status_code == 404

    deleted = client.delete(f'/api/v1/visits/places/{place_id}', headers=owner_headers)
    assert deleted.status_code == 204

    after_delete = client.get('/api/v1/visits/places?limit=10&offset=0', headers=owner_headers)
    assert after_delete.status_code == 200
    assert after_delete.json()['pagination']['total'] == 0


def test_visits_places_files_crud_and_constraints(client, settings) -> None:
    owner_tokens = _get_tokens(client, 'place-files-owner@example.com', settings.otp.otp_mock_code)
    stranger_tokens = _get_tokens(client, 'place-files-stranger@example.com', settings.otp.otp_mock_code)
    owner_headers = _auth_headers(owner_tokens)
    stranger_headers = _auth_headers(stranger_tokens)

    owner_visit = _create_visit(client, owner_headers, country_code='FR')
    second_owner_visit = _create_visit(client, owner_headers, country_code='IT')
    stranger_visit = _create_visit(client, stranger_headers, country_code='DE')

    place_response = client.post(
        '/api/v1/visits/places',
        headers=owner_headers,
        json={'visit_id': owner_visit['id'], 'title': 'Louvre'},
    )
    assert place_response.status_code == 201
    place_id = place_response.json()['id']
    stranger_place_response = client.post(
        '/api/v1/visits/places',
        headers=stranger_headers,
        json={'visit_id': stranger_visit['id'], 'title': 'Brandenburg Gate'},
    )
    assert stranger_place_response.status_code == 201
    stranger_place_id = stranger_place_response.json()['id']

    owner_file = _upload_file_for_visit(
        client,
        owner_headers,
        owner_visit['id'],
        'owner-place.jpg',
        _sample_image_bytes(),
    )
    foreign_visit_file = _upload_file_for_visit(
        client,
        owner_headers,
        second_owner_visit['id'],
        'other-visit.jpg',
        _sample_image_bytes(),
    )
    stranger_file = _upload_file_for_visit(
        client,
        stranger_headers,
        stranger_visit['id'],
        'stranger.jpg',
        _sample_image_bytes(),
    )

    assert client.get('/api/v1/visits/places-files?limit=10&offset=0').status_code == 401

    created = client.post(
        '/api/v1/visits/places-files',
        headers=owner_headers,
        json={'visit_place_id': place_id, 'file_id': owner_file['id']},
    )
    assert created.status_code == 201
    relation_id = created.json()['id']

    duplicate = client.post(
        '/api/v1/visits/places-files',
        headers=owner_headers,
        json={'visit_place_id': place_id, 'file_id': owner_file['id']},
    )
    assert duplicate.status_code == 409

    listed = client.get(
        f'/api/v1/visits/places-files?limit=10&offset=0&visit_place_id={place_id}',
        headers=owner_headers,
    )
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert listed_payload['pagination']['total'] == 1
    assert listed_payload['items'][0]['id'] == relation_id

    loaded = client.get(f'/api/v1/visits/places-files/{relation_id}', headers=owner_headers)
    assert loaded.status_code == 200
    assert loaded.json()['file_id'] == owner_file['id']

    cross_visit = client.post(
        '/api/v1/visits/places-files',
        headers=owner_headers,
        json={'visit_place_id': place_id, 'file_id': foreign_visit_file['id']},
    )
    assert cross_visit.status_code == 400

    foreign_place = client.post(
        '/api/v1/visits/places-files',
        headers=owner_headers,
        json={'visit_place_id': stranger_place_id, 'file_id': owner_file['id']},
    )
    assert foreign_place.status_code == 404

    foreign_file = client.post(
        '/api/v1/visits/places-files',
        headers=owner_headers,
        json={'visit_place_id': place_id, 'file_id': stranger_file['id']},
    )
    assert foreign_file.status_code == 404

    assert client.get(f'/api/v1/visits/places-files/{relation_id}', headers=stranger_headers).status_code == 404

    deleted = client.delete(f'/api/v1/visits/places-files/{relation_id}', headers=owner_headers)
    assert deleted.status_code == 204

    mine_after_delete = client.get(
        f'/api/v1/files/mine?limit=10&offset=0&visit_id={owner_visit["id"]}',
        headers=owner_headers,
    )
    assert mine_after_delete.status_code == 200
    assert mine_after_delete.json()['pagination']['total'] == 1
    assert mine_after_delete.json()['items'][0]['id'] == owner_file['id']

    download_after_delete = client.get(f'/api/v1/files/{owner_file["id"]}/download', headers=owner_headers)
    assert download_after_delete.status_code == 404


def test_files_crud_for_owner(client, settings) -> None:
    tokens = _get_tokens(client, 'files-owner@example.com', settings.otp.otp_mock_code)
    auth_headers = _auth_headers(tokens)

    created_visit = client.post('/api/v1/visits', headers=auth_headers, json={'country_code': 'FR'})
    assert created_visit.status_code == 201
    visit_id = created_visit.json()['id']

    create_file_response = client.post(
        f'/api/v1/visits/{visit_id}/file',
        headers=auth_headers,
        data={
            'visibility': FileVisibility.PUBLIC.value,
        },
        files={'file': ('paris.jpg', _sample_image_bytes(), 'image/jpeg')},
    )
    assert create_file_response.status_code == 201
    created_file = create_file_response.json()
    assert created_file['visit_id'] == visit_id
    assert created_file['filename'] == 'paris.webp'
    _assert_imgproxy_url(created_file['file_url'], 'full')

    download_response = client.get(f'/api/v1/files/{created_file["id"]}/download', headers=auth_headers)
    assert download_response.status_code == 404

    mine_response = client.get('/api/v1/files/mine?limit=10&offset=0', headers=auth_headers)
    assert mine_response.status_code == 200
    mine_payload = mine_response.json()
    assert mine_payload['pagination']['total'] == 1
    assert mine_payload['items'][0]['id'] == created_file['id']
    _assert_imgproxy_url(mine_payload['items'][0]['file_url'], 'full')

    update_response = client.patch(
        f'/api/v1/files/{created_file["id"]}',
        headers=auth_headers,
        json={'filename': 'eiffel.jpg'},
    )
    assert update_response.status_code == 200
    assert update_response.json()['filename'] == 'eiffel.jpg'
    _assert_imgproxy_url(update_response.json()['file_url'], 'full')

    delete_response = client.delete(f'/api/v1/files/{created_file["id"]}', headers=auth_headers)
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
        f'/api/v1/visits/{visit_id}/file',
        headers=owner_headers,
        data={
            'visibility': FileVisibility.PUBLIC.value,
        },
        files={'file': ('public.jpg', _sample_image_bytes(), 'image/jpeg')},
    )
    assert public_file.status_code == 201
    public_file_id = public_file.json()['id']

    private_file = client.post(
        f'/api/v1/visits/{visit_id}/file',
        headers=owner_headers,
        data={
            'visibility': FileVisibility.PRIVATE.value,
        },
        files={'file': ('private.jpg', _sample_image_bytes(), 'image/jpeg')},
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
    _assert_imgproxy_url(public_payload['items'][0]['file_url'], 'full')

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
    unauthorized = client.get('/api/v1/geo/countries?limit=5&offset=0&iso_a2=FR')
    assert unauthorized.status_code == 401

    invalid_auth = client.get(
        '/api/v1/geo/countries?limit=5&offset=0&iso_a2=FR',
        headers={'Authorization': 'Bearer invalid-token'},
    )
    assert invalid_auth.status_code == 401


def test_client_geo_countries_fallback_to_geonames_and_persists_meta(client, settings, monkeypatch) -> None:
    async def _mock_search_countries(self, *, query, country_codes, limit, offset, lang):  # noqa: ARG001
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

    first = client.get('/api/v1/geo/countries?limit=5&offset=0&iso_a2=ZZ', headers=headers)
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload['pagination']['total'] == 1
    assert first_payload['items'][0]['iso_a2'] == 'ZZ'
    assert first_payload['items'][0]['meta']['geonameId'] == 999001

    second = client.get('/api/v1/geo/countries?limit=5&offset=0&iso_a2=ZZ', headers=headers)
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload['pagination']['total'] == 1
    assert second_payload['items'][0]['meta']['geonameId'] == 999001


def test_client_geo_countries_searches_localized_labels_and_keeps_canonical_name(
    client,
    settings,
    monkeypatch,
) -> None:
    calls = {'count': 0}

    async def _mock_search_countries(self, *, query, country_codes, limit, offset, lang):  # noqa: ARG001
        calls['count'] += 1
        assert query == 'Росс'
        assert lang == 'ru'
        return [
            {
                'iso_a2': 'RU',
                'name': 'Russia',
                'labels': {'en': 'Russia', 'ru': 'Россия'},
                'meta': {'geonameId': 2017370, 'countryCode': 'RU', 'countryName': 'Россия'},
            }
        ]

    monkeypatch.setattr(GeoNamesClient, 'search_countries', _mock_search_countries)
    tokens = _get_tokens(client, 'client-geo-country-labels@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)
    query = urlencode({'limit': 5, 'offset': 0, 'lang': 'ru', 'name_ilike': '%Росс%'})

    first = client.get(f'/api/v1/geo/countries?{query}', headers=headers)
    assert first.status_code == 200
    first_item = first.json()['items'][0]
    assert first_item['iso_a2'] == 'RU'
    assert first_item['name'] == 'Russia'
    assert first_item['display_name'] == 'Россия'
    assert first_item['labels']['ru'] == 'Россия'

    second = client.get(f'/api/v1/geo/countries?{query}', headers=headers)
    assert second.status_code == 200
    second_item = second.json()['items'][0]
    assert second_item['name'] == 'Russia'
    assert second_item['display_name'] == 'Россия'
    assert calls['count'] == 1


def test_client_geo_cities_fallback_to_geonames_and_persists_meta(client, settings, monkeypatch) -> None:
    calls = {'count': 0}

    async def _mock_search_cities(self, *, query, country_code, limit, offset, lang):  # noqa: ARG001
        calls['count'] += 1
        return [
            {
                'id': UUID('05f1e4a3-0d4a-5ea0-a368-bf7e70f5b8ec'),
                'country_code': 'FR',
                'name': 'Paris',
                'latitude': Decimal('48.8566'),
                'longitude': Decimal('2.3522'),
                'population': 2148327,
                'meta': {'geonameId': 2988507, 'countryCode': 'FR', 'countryName': 'France', 'name': 'Paris'},
            }
        ]

    monkeypatch.setattr(GeoNamesClient, 'search_cities', _mock_search_cities)
    tokens = _get_tokens(client, 'client-geo-cities@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)

    first = client.get('/api/v1/geo/cities?limit=5&offset=0&name_ilike=Paris', headers=headers)
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload['pagination']['total'] == 1
    assert first_payload['items'][0]['name'] == 'Paris'
    assert first_payload['items'][0]['country_code'] == 'FR'
    assert first_payload['items'][0]['meta']['geonameId'] == 2988507

    second = client.get('/api/v1/geo/cities?limit=5&offset=0&name_ilike=Paris', headers=headers)
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload['pagination']['total'] == 1
    assert second_payload['items'][0]['name'] == 'Paris'
    assert calls['count'] == 1


def test_client_geo_cities_searches_localized_labels_and_keeps_canonical_name(
    client,
    settings,
    monkeypatch,
) -> None:
    calls = {'count': 0}

    async def _mock_search_cities(self, *, query, country_code, limit, offset, lang):  # noqa: ARG001
        calls['count'] += 1
        assert query == 'Рим'
        assert country_code == 'IT'
        assert lang == 'ru'
        return [
            {
                'id': UUID('8168e736-cc26-56f4-a573-1a6e7e5e0ea7'),
                'country_code': 'IT',
                'name': 'Rome',
                'latitude': Decimal('41.8931'),
                'longitude': Decimal('12.4828'),
                'population': 2873000,
                'labels': {'en': 'Rome', 'ru': 'Рим'},
                'meta': {'geonameId': 3169070, 'countryCode': 'IT', 'countryName': 'Италия', 'name': 'Рим'},
            }
        ]

    monkeypatch.setattr(GeoNamesClient, 'search_cities', _mock_search_cities)
    tokens = _get_tokens(client, 'client-geo-city-labels@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)
    query = urlencode({'limit': 5, 'offset': 0, 'lang': 'ru', 'country_code': 'IT', 'name_ilike': '%Рим%'})
    sync_engine = create_engine(to_sync_database_url(settings.db.database_url), future=True)
    try:
        with sync_engine.connect() as conn:
            conn.execute(countries.update().where(countries.c.iso_a2 == 'IT').values(name='IT'))
            conn.commit()
    finally:
        sync_engine.dispose()

    first = client.get(f'/api/v1/geo/cities?{query}', headers=headers)
    assert first.status_code == 200
    first_item = first.json()['items'][0]
    assert first_item['country_code'] == 'IT'
    assert first_item['name'] == 'Rome'
    assert first_item['display_name'] == 'Рим'
    assert first_item['labels']['ru'] == 'Рим'

    second = client.get(f'/api/v1/geo/cities?{query}', headers=headers)
    assert second.status_code == 200
    second_item = second.json()['items'][0]
    assert second_item['name'] == 'Rome'
    assert second_item['display_name'] == 'Рим'
    assert calls['count'] == 1

    countries_response = client.get('/api/v1/geo/countries?limit=5&offset=0&iso_a2=IT', headers=headers)
    assert countries_response.status_code == 200
    country_item = countries_response.json()['items'][0]
    assert country_item['name'] == 'Италия'
    assert country_item['name'] != 'IT'


def test_client_geo_repeated_requests_are_allowed(client, settings) -> None:
    tokens = _get_tokens(client, 'client-geo-repeat@example.com', settings.otp.otp_mock_code)
    headers = _auth_headers(tokens)

    first = client.get('/api/v1/geo/countries?limit=5&offset=0&iso_a2=FR', headers=headers)
    assert first.status_code == 200

    second = client.get('/api/v1/geo/countries?limit=5&offset=0&iso_a2=FR', headers=headers)
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
