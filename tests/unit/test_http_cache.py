from app.services.http_cache import matches_etag


def test_matches_etag_accepts_strong_and_weak_validators() -> None:
    etag = '"thumb-abc"'

    assert matches_etag('"thumb-abc"', etag)
    assert matches_etag('W/"thumb-abc"', etag)
    assert matches_etag('"other", W/"thumb-abc"', etag)


def test_matches_etag_accepts_wildcard() -> None:
    assert matches_etag('*', '"thumb-abc"')


def test_matches_etag_rejects_missing_or_different_validators() -> None:
    assert not matches_etag(None, '"thumb-abc"')
    assert not matches_etag('"other"', '"thumb-abc"')
