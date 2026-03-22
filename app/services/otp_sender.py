import asyncio
import logging
from typing import Protocol

import resend

logger = logging.getLogger(__name__)


class OtpSenderProtocol(Protocol):
    async def send(self, contact: str, code: str) -> None: ...


class ResendOTPSender(OtpSenderProtocol):
    def __init__(self, api_key: str, email_from: str):
        self.email_from = email_from
        self.api_key = api_key
        resend.api_key = api_key

    async def send(self, contact: str, code: str) -> None:
        result = await asyncio.to_thread(
            resend.Emails.send,
            {
                'from': self.email_from,
                'to': [contact],
                'subject': 'Your verification code',
                'html': f'<h1>Your verification code is <b>{code}</b></h1>',
            },
        )
        logger.debug('OTP sent to %s, response: %s', contact, result)


class MockOtpSender:
    async def send(self, contact: str, code: str) -> None:  # noqa: ARG002
        logger.debug('MockOtpSender: skipping send to %s', contact)
