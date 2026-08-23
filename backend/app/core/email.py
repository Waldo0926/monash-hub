"""Transactional email.

Three providers: ``console`` for development, ``resend`` and ``smtp`` for real
delivery. The message body is never logged - it contains the verification code,
and a code sitting in a log file is a code anyone with log access can use.
"""
from __future__ import annotations

import json
import logging
import smtplib
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.config import Settings, get_settings

log = logging.getLogger(__name__)

USER_AGENT = "MonashHub/0.1 (+https://monashhub.secureview.tech)"


class EmailDeliveryError(RuntimeError):
    """The message could not be handed to the configured provider."""


@dataclass(frozen=True, slots=True)
class Message:
    to: str
    subject: str
    text: str


def _redact(address: str) -> str:
    name, _, domain = address.partition("@")
    return f"{name[:2]}***@{domain}" if domain else "***"


class Emailer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def send(self, message: Message) -> None:
        provider = self.settings.email_provider
        if provider == "console":
            self._console(message)
        elif provider == "resend":
            self._resend(message)
        elif provider == "smtp":
            self._smtp(message)
        else:
            raise EmailDeliveryError(f"Unknown email provider: {provider}")

    def _console(self, message: Message) -> None:
        # Development only. The body is printed because a developer with no mail
        # provider still has to be able to finish a signup; production settings
        # should never leave the provider here.
        log.warning(
            "EMAIL_PROVIDER=console - not delivered. To %s, subject %r:\n%s",
            message.to, message.subject, message.text,
        )

    def _from_header(self) -> str:
        return f"{self.settings.email_from_name} <{self.settings.email_from_address}>"

    def _resend(self, message: Message) -> None:
        payload: dict[str, object] = {
            "from": self._from_header(),
            "to": [message.to],
            "subject": message.subject,
            "text": message.text,
        }
        if self.settings.email_reply_to:
            payload["reply_to"] = self.settings.email_reply_to

        request = urllib.request.Request(
            self.settings.resend_api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.resend_api_key}",
                "Content-Type": "application/json",
                # urllib's default user agent is refused at Resend's edge before
                # the request ever reaches the API.
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.settings.email_timeout_seconds):
                pass
        except urllib.error.HTTPError as exc:
            raise EmailDeliveryError(f"Resend returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise EmailDeliveryError(f"Resend unreachable: {exc.reason}") from exc
        log.info("sent %r to %s via resend", message.subject, _redact(message.to))

    def _smtp(self, message: Message) -> None:
        payload = EmailMessage()
        payload["From"] = self._from_header()
        payload["To"] = message.to
        payload["Subject"] = message.subject
        if self.settings.email_reply_to:
            payload["Reply-To"] = self.settings.email_reply_to
        payload.set_content(message.text)

        timeout = self.settings.email_timeout_seconds
        try:
            if self.settings.smtp_use_ssl:
                client = smtplib.SMTP_SSL(
                    self.settings.smtp_host, self.settings.smtp_port,
                    timeout=timeout, context=ssl.create_default_context(),
                )
            else:
                client = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port,
                                      timeout=timeout)
            with client:
                if self.settings.smtp_use_tls and not self.settings.smtp_use_ssl:
                    client.starttls(context=ssl.create_default_context())
                if self.settings.smtp_username:
                    client.login(self.settings.smtp_username, self.settings.smtp_password)
                client.send_message(payload)
        except (smtplib.SMTPException, OSError) as exc:
            raise EmailDeliveryError(f"SMTP delivery failed: {exc}") from exc
        log.info("sent %r to %s via smtp", message.subject, _redact(message.to))
