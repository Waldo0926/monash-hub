# Security Policy

Monash Hub is an independent student project with a public-facing production service. Security reports are welcome and should be handled privately until a fix is available.

## Reporting a vulnerability

Please do **not** open a public GitHub issue for a suspected security vulnerability.

Email: **wensx0926@gmail.com**

A useful report includes:

- the affected route, component or feature;
- clear reproduction steps;
- expected vs. observed behaviour;
- impact you believe is possible;
- screenshots or a minimal proof of concept when useful.

Do not include passwords, session tokens, private student content or other third-party personal data unless it is strictly necessary to explain the issue. Redact such material where possible.

## Responsible testing

Please avoid actions that could affect other users or the availability of the service. In particular, do not:

- access or modify another user's account or private data;
- run destructive tests against production data;
- perform denial-of-service or high-volume automated traffic;
- attempt social engineering;
- publish a vulnerability before there has been a reasonable opportunity to investigate and fix it.

If demonstrating an issue requires an authenticated account, use an account you control.

## Secrets and production data

The public repository is not intended to contain production credentials, database dumps, user exports or raw crawl output. If you find a credential or private dataset in Git history or the current tree, please report it privately using the address above rather than using it.

## Third-party services

Issues in Monash University systems, GitHub, email providers or other third-party services are outside this project's security boundary and should be reported to the relevant provider through its own disclosure process.
