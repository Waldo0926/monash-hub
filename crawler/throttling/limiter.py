"""Politeness controls for every outbound request.

Monash is not a load test target. One process, one request at a time, a floor on
the gap between requests, jitter so the pattern is not a metronome, and
exponential backoff on failure. These limits are the default and the runner has
no flag to remove them.
"""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass

log = logging.getLogger(__name__)


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

    def backoff(self, attempt: int) -> None:
        pause = min(self.limit.backoff_base * (2 ** (attempt - 1)), self.limit.backoff_max)
        log.warning("backing off %.1fs before attempt %d", pause, attempt + 1)
        time.sleep(pause)
