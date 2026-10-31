"""What stops a translation run, as opposed to failing one string.

The engine catches an ordinary exception per string so one bad sentence
cannot end a pass of five thousand units. Against a key that was refused or a
provider that has stopped answering, that would quietly record every remaining
string as untranslatable, so those conditions are raised as ``Blocked``, which
is a ``BaseException`` on purpose: it gets past ``except Exception``.
"""
from __future__ import annotations

#: Consecutive failed requests, after retries, before a run gives up.
MAX_CONSECUTIVE_FAILURES = 8


class Blocked(BaseException):
    """The provider has stopped answering. Not an ``Exception`` on purpose."""
