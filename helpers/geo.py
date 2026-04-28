import json
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=1)
def load_geojson(path: str) -> dict[str, Any]:
    geojson_path = Path(path)
    with geojson_path.open('r', encoding='utf-8') as source:
        return json.load(source)
