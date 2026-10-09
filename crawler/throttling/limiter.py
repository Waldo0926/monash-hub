"""Politeness controls for every outbound request.

Monash is not a load test target. One process, one request at a time, a floor on
the gap between requests, jitter so the pattern is not a metronome, and
exponential backoff on failure. The runners expose ``--min-interval``, floored
at one second; nothing removes the gap altogether.

Every request also says who is asking. The same User-Agent goes to the
Handbook and to the student sites, and names the site it is for.
"""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass

log = logging.getLogger(__name__)

USER_AGENT = (
    "MonashHubBot/0.1 (+https://monashhub.secureview.tech; student information index)"
)

#: The longest a Retry-After is honoured before the attempt is given up on.
MAX_PAUSE = 600.0


@dataclass(slots=True)
class RateLimit:
    #: Minimum seconds between the start of one request and the next.
    min_interval: float = 3.0
    #: Extra random delay, so a run is not a perfectly regular pattern.
    jitter: float = 1.5
    #: Attempts per URL before we give up and keep the last good copy.
    max_attempts: int = 3
    #: First backoff pause; doubles per retry.
    backoff_base: float = 5.0
    backoff_max: float = 120.0


class Throttle:
    """Sequential pacing. Deliberately not concurrent."""

    def __init__(self, limit: RateLimit | None = None) -> None:
        self.limit = limit or RateLimit()
        self._last_request: float | None = None

    def wait(self) -> None:
        if self._last_request is not None:
            elapsed = time.monotonic() - self._last_request
            delay = self.limit.min_interval - elapsed
            if delay > 0:
                time.sleep(delay)
        if self.limit.jitter:
            time.sleep(random.uniform(0, self.limit.jitter))
        self._last_request = time.monotonic()

    def backoff(self, attempt: int, at_least: float = 0.0) -> None:
        """Exponential pause, or longer when the server named a Retry-After."""
        pause = min(self.limit.backoff_base * (2 ** (attempt - 1)), self.limit.backoff_max)
        pause = min(max(pause, at_least), MAX_PAUSE)
        log.warning("backing off %.1fs before attempt %d", pause, attempt + 1)
        time.sleep(pause)
