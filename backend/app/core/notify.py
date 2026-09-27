"""Tell the operator something needs a person.

    python -m app.core.notify "subject" "body"

Sends one email to each address in ``ALERT_EMAIL`` (comma separated) through
the same provider the verification codes use. With no ``ALERT_EMAIL`` set it
only logs, so an unconfigured deployment is quiet rather than broken.
"""
from __future__ import annotations

import logging
import sys

from app.core.config import get_settings
from app.core.email import Emailer, Message

log = logging.getLogger("notify")


def recipients(value: str | None) -> list[str]:
    return [address.strip() for address in (value or "").split(",") if address.strip()]


def notify(subject: str, body: str) -> bool:
    settings = get_settings()
    to = recipients(settings.alert_email)
    if not to:
        log.warning("ALERT_EMAIL is not set; not emailing: %s", subject)
        return False
    emailer = Emailer(settings)
    # One message each, so no recipient sees the others' addresses.
    for address in to:
        emailer.send(Message(to=address, subject=subject, text=body))
    log.info("alert sent to %d address(es): %s", len(to), subject)
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m app.core.notify SUBJECT BODY")
    notify(sys.argv[1], sys.argv[2])
