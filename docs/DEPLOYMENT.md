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
   ./deployment/crawl.sh seed           # curated FAQ
   ```

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
