# Deployment

Production is served at `https://monashhub.secureview.tech` from a Linux host running nginx and Docker Compose. This document intentionally describes the Monash Hub deployment only; unrelated services and host-specific credentials are outside the repository.

## Security boundary

- Production secrets live in the host environment / `.env` and GitHub environment secrets, never in Git.
- PostgreSQL is not published to the internet.
- Application containers bind to loopback or an internal Docker network and nginx owns the public HTTP(S) ports.
- Deployment changes must not modify unrelated services on a shared host.
- Raw crawl output, database dumps and user data are not committed.

## Server layout

The current deployment script expects the checkout at:

```text
/opt/monash-hub/
├── repo/        # checkout of this repository
├── backups/     # database backups
└── data/        # host-persistent application data
```

The path is an operational convention, not a credential. Hostname, SSH user, port, private key and known-host material are supplied through GitHub environment secrets.

## First deploy

### 1. Create the application directories

```bash
mkdir -p /opt/monash-hub/{repo,backups,data}
```

Create a read-only deploy key for the repository and clone `main` into `/opt/monash-hub/repo`.

### 2. Create the environment file

```bash
cd /opt/monash-hub/repo
cp .env.example .env
sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -base64 24)|" .env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|" .env
chmod 600 .env
```

Review the remaining variables before starting production. Do not commit the resulting `.env`.

### 3. Start / update the stack

```bash
./deployment/deploy.sh
```

The deployment script backs up the database, pulls the reviewed `main` branch, rebuilds containers, applies migrations and idempotent seed data, restarts services, and verifies the health endpoint.

### 4. TLS and nginx

The repository contains nginx templates for the application. Obtain a certificate for the production hostname before enabling a server block that references it. The exact ACME/certbot procedure depends on the host's existing nginx setup.

After the certificate exists, install the Monash Hub nginx snippets from `deployment/nginx/`, run `nginx -t`, then reload nginx.

Do not copy host-wide nginx configuration, credentials, certificates or unrelated server blocks into the repository.

## Loading official-source data

Typical commands are:

```bash
./deployment/crawl.sh handbook --all
./deployment/crawl.sh official --all
./deployment/crawl.sh seed
```

The crawler is deliberately rate-limited and resumable. Run the official crawl before reseeding translations after extractor changes so source hashes describe the current extracted content.

Test fixtures in `backend/tests/fixtures/` are intentionally minimal synthetic documents. They are not production crawl output and are not a mirror of Monash pages.

## Chinese search

After a crawl or translation update, refresh the Chinese search materialisation:

```bash
./deployment/crawl.sh reindex-zh --stats
./deployment/crawl.sh reindex-zh
```

English search continues to use its normal PostgreSQL text-search path. Chinese support combines glossary expansion with substring/trigram matching over reviewed or generated translated text.

## Email delivery

Development may use `EMAIL_PROVIDER=console`. Production should configure a real provider using environment variables such as:

```text
EMAIL_PROVIDER=resend
EMAIL_FROM_ADDRESS=<verified sender>
RESEND_API_KEY=<secret supplied outside Git>
```

SMTP can be configured instead through the corresponding `SMTP_*` variables in `.env.example`.

## Initial moderator account

The seeder can create the first moderator only when credentials are explicitly supplied at runtime:

```bash
docker compose -p monash-hub run --rm \
  -e ADMIN_EMAIL='you@example.com' \
  -e ADMIN_NICKNAME='moderator' \
  -e ADMIN_PASSWORD='<a password from your password manager>' \
  crawler python -m app.knowledge.seed
```

Do not add a real moderator password or email to repository configuration.

## Automated deployments

`.github/workflows/deploy.yml` runs only after a successful CI run on `main` (or a manual dispatch) and reads SSH connection values from GitHub environment secrets:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PORT`
- `DEPLOY_SSH_KEY`
- `DEPLOY_KNOWN_HOSTS`

The workflow contains secret *names*, not secret values.

## Routine deploy

```bash
cd /opt/monash-hub/repo
./deployment/deploy.sh
```

Do not edit application files directly on the production host. A deployment should always be reproducible from the reviewed repository plus environment-specific secrets/data.

## Rollback

Use a previously reviewed commit and restore the matching database backup if a migration requires it. Keep backups outside Git and protect them as production data.

## Verification

Useful checks include:

```bash
curl -s https://monashhub.secureview.tech/api/health | python3 -m json.tool
docker compose -p monash-hub ps
docker compose -p monash-hub logs --tail 100 api
```

`/api/health` reports service/data freshness information without exposing credentials.

## Isolation checklist

Before and after a production deploy:

- Compose project name is `monash-hub`.
- PostgreSQL has no public port.
- API/web containers are reachable only through the intended reverse-proxy path.
- Only Monash Hub containers, volumes and nginx configuration are modified.
- Secrets, dumps and raw production crawl output remain outside version control.
