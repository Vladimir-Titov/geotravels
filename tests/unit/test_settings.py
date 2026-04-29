from settings import to_sync_database_url


def test_to_sync_database_url_converts_bare_postgres_url() -> None:
    assert (
        to_sync_database_url('postgresql://postgres:postgres@localhost:54441/postgres')
        == 'postgresql+psycopg://postgres:postgres@localhost:54441/postgres'
    )
