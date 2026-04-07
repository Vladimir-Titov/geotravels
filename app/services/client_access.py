from __future__ import annotations

import asyncio
import math
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from app.services.exceptions import CountdownError


@dataclass(slots=True)
class ClientAuthContext:
    token: str


class InMemoryRateLimiter:
    def __init__(self, requests_per_window: int, window_seconds: int):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def hit(self, key: str) -> None:
        now = time.monotonic()
        boundary = now - self.window_seconds

        async with self._lock:
            events = self._events[key]
            while events and events[0] <= boundary:
                events.popleft()

            if len(events) >= self.requests_per_window:
                retry_after = max(1, math.ceil(self.window_seconds - (now - events[0])))
                raise CountdownError({'error': 'Too many requests', 'retry_after': retry_after})

            events.append(now)
