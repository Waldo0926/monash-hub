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

## Chinese search

Searching in Chinese needs one step that a crawl does not do for you:

```bash
cd /opt/monash-hub/repo
./deployment/crawl.sh reindex-zh --stats   # coverage, writes nothing
./deployment/crawl.sh reindex-zh
```

**Run it after a crawl and after any translation batch.** Translations live in
`content_translations`; search runs against `units` and `official_pages`. The
reindex copies the Chinese onto those rows, where `pg_trgm` can index it. It is
idempotent and only writes rows whose text actually changed, so a run after a
quiet crawl costs nothing.

Forgetting it is not an outage. Chinese search keeps working through the
glossary expansion below — it just stops finding pages by their translated body
until the reindex catches up.

### How a Chinese query is answered

PostgreSQL cannot tokenise Chinese: `to_tsvector('english', '选课与注册')` yields
one meaningless token, and the extensions that fix that (`zhparser`, `pg_jieba`)
are server-side installs we do not have. So two mechanisms run side by side.

1. **Glossary expansion.** The query is matched against the Chinese side of
   `app/knowledge/glossary.py`, and the English terms it translates are OR-ed
   into the text query. 休学 also searches for "intermission", which finds the
   page whether or not anybody has translated it. This works with no reindex at
   all, and it grows on its own as terms are added for the translator.
2. **Trigram match on `search_zh`.** For pages that *are* translated, the query
   is matched as a substring against the stored Chinese. For a language with no
   word boundaries substring is the natural query, not a fallback.

English search is untouched: an English query expands to nothing and keeps its
original AND semantics.

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
