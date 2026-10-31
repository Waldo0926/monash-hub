"""The application version.

One place, read by the FastAPI app (so /api and the OpenAPI document report
it) and by the Release workflow, which refuses to publish a tag that does not
match it. Bump it in the same PR that moves the CHANGELOG's Unreleased
section under a version heading; see docs/RELEASING.md.
"""

__version__ = "1.0.0"
