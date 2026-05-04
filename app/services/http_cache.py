def matches_etag(if_none_match: str | None, etag: str) -> bool:
    if not if_none_match:
        return False

    def normalize_validator(value: str) -> str:
        value = value.strip()
        return value[2:].strip() if value.startswith('W/') else value

    current_etag = normalize_validator(etag)
    for candidate in if_none_match.split(','):
        validator = normalize_validator(candidate)
        if validator == '*' or validator == current_etag:
            return True
    return False
