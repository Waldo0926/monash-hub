# 0005. Accounts are a nickname and a verified email

Status: Accepted (written down 2026-10, for a decision made earlier)

## Context

The community needs accounts so a question has an author and an answer can
be marked helpful. Monash SSO is not available to a student project, and
collecting real names or student IDs would mean holding data with no public
value and real risk if leaked. Registration friction is also what leaves a
forum empty.

## Decision

An account is a nickname, an email address and a password. No real name, no
student ID. Registration and password reset are gated on a six-digit code
sent to the address, stored only as an HMAC bound to the address, with a
ten-minute expiry and five attempts.

Sessions are JWTs carrying the account's `token_version`; a password reset
bumps the column, which invalidates every token already issued.

The endpoints do not reveal whether an address has an account (requesting a
code always returns the same body) or which half of a sign-in was wrong.

## Consequences

- Nothing in the user table identifies a person beyond an email address.
- Sign-out-everywhere works without a session table.
- A forgotten password is recoverable, because the address was verified at
  registration. Without that step a lost password is a lost account.
- Moderation has less to go on than a real-name forum. That is accepted:
  hidden posts and a moderator role cover what has come up.
- Email delivery is a production dependency. With the `console` provider
  nobody outside the server can finish a signup, so production must set a real
  one; the API reports `delivery_configured` so the frontend can say so.

## Revisit when

Monash offers an OAuth or OIDC login a student project can use (tracked as
issue #64 for Google sign-in), or the forum's size makes abuse a steady
problem rather than an occasional one.
