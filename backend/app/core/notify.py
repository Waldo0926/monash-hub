"""Tell the operator something needs a person.

    python -m app.core.notify "subject" "body"

Sends one email to ``ALERT_EMAIL`` through the same provider the verification
codes use. With no ``ALERT_EMAIL`` set it only logs, so an unconfigured
deployment is quiet rather than broken.
"""
from __future__ import annotations

import logging
import sys

from app.core.config import get_settings
from app.core.email import Emailer, Message

log = logging.getLogger("notify")


def notify(subject: str, body: str) -> bool:
    settings = get_settings()
    if not settings.alert_email:
        log.warning("ALERT_EMAIL is not set; not emailing: %s", subject)
        return False
    Emailer(settings).send(Message(to=settings.alert_email, subject=subject, text=body))
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m app.core.notify SUBJECT BODY")
    notify(sys.argv[1], sys.argv[2])
