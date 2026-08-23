# Deployment

Production is `https://monashhub.secureview.tech`, served from the VPS that
already hosts two other projects. Everything below is written on the assumption
that **those other projects must not be disturbed**.

## What is already on that host

Check before you change anything:

```bash
ss -tlnp | grep -E ':(80|443) '        # nginx, on the host, not in a container
ls /etc/nginx/sites-enabled/           # existing server blocks
docker ps                              # existing containers
docker network ls && docker volume ls  # existing networks and volumes
certbot certificates                   # existing certificates
```

nginx runs on the host and owns 80/443. **Do not install a second proxy.**
Monash Hub adds one server block and binds its own containers to loopback only.

## Layout on the server

```
/opt/monash-hub/
├── repo/        git checkout of main (this repository)
├── backups/     nightly pg_dump output, 14 days retained
└── data/        anything else that must live on the host
```

## First deploy

1. **Directory and deploy key**

   ```bash
   mkdir -p /opt/monash-hub/{repo,backups,data}
   ssh-keygen -t ed25519 -f /root/.ssh/monash_hub_deploy -N '' -C 'monash-hub deploy key'
   cat /root/.ssh/monash_hub_deploy.pub
   ```

   Add that public key to the repository under **Settings → Deploy keys**, read
   only. The server pulls; it never pushes.

   ```bash
   cat >> /root/.ssh/config <<'EOF'
   Host github.com-monashhub
       HostName github.com
       User git
       IdentityFile /root/.ssh/monash_hub_deploy
       IdentitiesOnly yes
   EOF

   git clone git@github.com-monashhub:<owner>/monash-hub.git /opt/monash-hub/repo
   ```

2. **Environment**

   ```bash
   cd /opt/monash-hub/repo
   cp .env.example .env
   sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -base64 24)|" .env
   sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|" .env
   chmod 600 .env
   ```

3. **Bring the stack up**

   ```bash
   ./deployment/deploy.sh
   ```

   That backs up, pulls, builds, migrates, restarts, and waits for
   `/api/health`. It is safe to re-run.

4. **TLS first, then nginx**

   The site config references the certificate, so the certificate has to exist
   before nginx will load it. Serve the ACME challenge from a throwaway block:

   ```bash
   cat > /etc/nginx/sites-available/monash-hub-bootstrap <<'EOF'
   server {
       listen 80;
       listen [::]:80;
       server_name monashhub.secureview.tech;
       location ^~ /.well-known/acme-challenge/ { allow all; root /var/www/html; }
       location / { return 503; }
   }
   EOF
   ln -sf /etc/nginx/sites-available/monash-hub-bootstrap /etc/nginx/sites-enabled/
   nginx -t && systemctl reload nginx

   certbot certonly --webroot -w /var/www/html -d monashhub.secureview.tech
   ```

   Then swap in the real config:

   ```bash
   rm -f /etc/nginx/sites-enabled/monash-hub-bootstrap
   cp deployment/nginx/monash-hub-limits.conf /etc/nginx/conf.d/
   cp deployment/nginx/monash-hub.conf /etc/nginx/sites-available/monash-hub
   ln -s /etc/nginx/sites-available/monash-hub /etc/nginx/sites-enabled/
   nginx -t && systemctl reload nginx
   ```

   `certonly` is used rather than `certbot --nginx` so the server block stays
   exactly what is in Git instead of something certbot rewrote. The existing
   `certbot.timer` renews it.

5. **Load data**

   ```bash
   ./deployment/crawl.sh handbook       # 20 fixture units
   ./deployment/crawl.sh official --all # 40 seed pages
   ./deployment/crawl.sh seed           # curated FAQ and Chinese translations
   ```

   **Order matters, and `--all` matters.** Run the official crawl before the
   seed, and run it with `--all` after any release that changes
   `app/knowledge/cleaner.py`:

   * The structured blocks a guide page renders from only exist once the page
     has been crawled by the current extractor. A page still holding the old
     flat text falls back to showing that text, so nothing breaks - it just
     stays ugly until the crawl runs. `EXTRACTOR_VERSION` in `cleaner.py` is
     what makes the crawl treat every page as changed; without `--all`, a page
     whose refresh interval has not elapsed is not fetched at all and keeps the
     old shape.
   * Each translation is stamped with the content hash of the English it was
     made from, and the seeder reads that hash off the crawled page. Seeding
     before the crawl leaves every translation unable to tell whether it is
     still current, and the site marks them all stale. The seeder warns by name
     about any page in that state.

## Machine-translated Chinese

Optional, run by hand, never part of a deploy. Without it the Chinese interface
still works — the field values, guide titles, FAQ and the hand-written pages are
all translated — and the long prose stays in English.

Order matters: **crawl first**. Guides are translated from their extracted
blocks, which only exist after `crawl.sh official --all` has run, and every
translation is stamped with the source's content hash.

```bash
cd /opt/monash-hub/repo
./deployment/crawl.sh translate --what guides --dry-run
./deployment/crawl.sh translate --what guides
./deployment/crawl.sh translate --what units --limit 200
```

`--dry-run` needs no API key. It runs the whole pipeline with a translator that
returns the source, writes nothing, and reports the **character count** a real
run would send — which is the unit every provider bills in. Use it to size a
batch before spending quota on one.

### Quota, measured

| | characters |
| --- | --- |
| All 40 official guides | ~250,000 after the new extractor drops the duplicated tab content |
| All 2,596 Handbook units | ~5,400,000 |

DeepL's free tier is 500,000 characters a month. So the guides fit inside a
single free month with room to spare; the units are about eleven free months, or
roughly €120 once on a Pro key. `--limit` is how you stay inside a month:
translate in batches, and a re-run only sends what has not been done yet.

Set `DEEPL_API_KEY` in `.env`. A Pro key also needs
`DEEPL_API_URL=https://api.deepl.com/v2/translate`; the default is the free
endpoint.

### Reading the summary

* `repaired` — the service rendered a reserved Monash term the wrong way and it
  was substituted back. Expected occasionally, not a problem.
* `leaked` — a reserved term is still in English in the output. The pages are
  named in the log. Worth a look.
* Rows are stamped `method='machine'` and the page says so, in different words
  and a different colour from a hand-written translation. Never edit that column
  to `human` to make the notice go away — the notice and the link to the
  original are what make a machine translation acceptable to publish at all.

A target that already has a hand-written translation is skipped, so running this
cannot downgrade a reviewed page.

## Email delivery

Registration and password reset send a six-digit code. With
`EMAIL_PROVIDER=console` the code goes to the API log and nobody outside the
server can finish a signup, so production needs a real provider:

```bash
cd /opt/monash-hub/repo
cat >> .env <<'EOF'
EMAIL_PROVIDER=resend
EMAIL_FROM_ADDRESS=no-reply@secureview.tech
RESEND_API_KEY=<key>
EOF
./deployment/deploy.sh
```

`GET /api/health` does not report this, but the client does: the
`verification-code` endpoint returns `delivery_configured`, and the signup form
says plainly that the code will not arrive when it is false.

## Creating the first moderator

Reports and hidden posts need someone who can act on them. The seed script
creates that account, and only when both variables are present - so a default
password can never end up on a public server:

```bash
cd /opt/monash-hub/repo
docker compose -p monash-hub run --rm \
  -e ADMIN_EMAIL='you@example.com' \
  -e ADMIN_NICKNAME='moderator' \
  -e ADMIN_PASSWORD='<a password you choose>' \
  crawler python -m app.knowledge.seed
```

Use a password manager. Do not put it in `.env`.

## Routine deploys

```bash
cd /opt/monash-hub/repo && ./deployment/deploy.sh
```

The server only ever checks out `main`. Do not edit files there — a change made
on the server is lost on the next deploy, and worse, it is invisible to everyone
else.

## Rollback

```bash
cd /opt/monash-hub/repo
git log --oneline -10
git checkout <previous-sha>
docker compose -p monash-hub build && docker compose -p monash-hub up -d
```

If a migration is involved, restore the dump `deploy.sh` took first:

```bash
gunzip -c /opt/monash-hub/backups/monashhub-<stamp>.sql.gz \
  | docker compose -p monash-hub exec -T postgres psql -U monashhub monashhub
```

## Checks that matter

```bash
curl -s https://monashhub.secureview.tech/api/health | python3 -m json.tool
docker compose -p monash-hub ps
docker compose -p monash-hub logs --tail 100 api
```

`/api/health` reports row counts and the last crawl, so it answers both "is it
up" and "is the data current".

## Isolation checklist

Before and after any deploy:

- Compose project is `monash-hub`; no other project's containers restarted.
- Network is `monash-hub-internal`; volume is `monash-hub-postgres-data`.
- PostgreSQL publishes no port: `docker compose -p monash-hub ps` shows nothing
  under PORTS for it.
- API and web bind `127.0.0.1` only.
- The FYP and tracker nginx server blocks are untouched.
