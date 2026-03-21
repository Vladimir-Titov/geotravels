from __future__ import annotations

from typing import Protocol


class OtpSenderProtocol(Protocol):
    async def send(self, contact: str, code: str) -> None: ...


class MockOtpSender:
    """Заглушка отправщика OTP. TODO: реализовать реальную отправку (email/SMS)."""

    async def send(self, contact: str, code: str) -> None:
        pass
