# Automated production deployment

Production deployment is performed by `.github/workflows/deploy.yml` after the
existing `CI` workflow succeeds for a push to `main`. Pull-request CI never
deploys. A manual `workflow_dispatch` fallback is also available from the
Actions tab.

The workflow does not contain credentials. It connects to the VPS over SSH and
runs the existing idempotent deployment script:

```text
/opt/monash-hub/repo/deployment/deploy.sh
```

That script remains the single source of truth for production deployment: it
backs up PostgreSQL, resets the checkout to `origin/main`, rebuilds the compose
images, applies migrations and curated seeds, restarts only the `monash-hub`
compose project, and waits for the API health check.

## Required GitHub Actions secrets

Configure these under **Repository Settings → Secrets and variables → Actions**:

| Secret | Required | Value |
| --- | --- | --- |
| `DEPLOY_HOST` | yes | VPS SSH hostname or IP address |
| `DEPLOY_USER` | yes | SSH user allowed to run the Monash Hub deploy script |
| `DEPLOY_SSH_KEY` | yes | Private half of a dedicated Ed25519 key used only by GitHub Actions |
| `DEPLOY_KNOWN_HOSTS` | yes | Trusted SSH host-key line for the VPS |
| `DEPLOY_PORT` | no | SSH port; omitted or empty means `22` |

Do not reuse the VPS-to-GitHub read-only deploy key. That key lets the server
pull this repository; the Actions key described here is the opposite direction
and only lets GitHub Actions reach the VPS.

## One-time SSH setup

Generate a dedicated key on a trusted workstation, not in the repository:

```bash
ssh-keygen -t ed25519 \
  -f ~/.ssh/monash_hub_actions \
  -N '' \
  -C 'monash-hub GitHub Actions'
```

Add the public key to the deployment user's `~/.ssh/authorized_keys` on the VPS.
Prefer a forced command so that this credential cannot obtain a general-purpose
shell. Replace `<PUBLIC_KEY>` with the complete contents of
`~/.ssh/monash_hub_actions.pub`:

```text
command="/opt/monash-hub/repo/deployment/deploy.sh",no-agent-forwarding,no-port-forwarding,no-X11-forwarding,no-pty <PUBLIC_KEY>
```

Keep the normal SSH permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

The selected deployment user must already have permission to read
`/opt/monash-hub/repo/.env`, write the repository checkout and backup directory,
and run the Docker commands used by `deployment/deploy.sh`. Do not loosen access
to the other projects sharing the VPS just to make this work.

## Populate the secrets

Copy the private key exactly, including its BEGIN/END lines, into
`DEPLOY_SSH_KEY`:

```bash
cat ~/.ssh/monash_hub_actions
```

For `DEPLOY_KNOWN_HOSTS`, collect the VPS host key from a trusted network/path
and verify its fingerprint against the server before storing it. For the normal
SSH port:

```bash
ssh-keyscan -H <DEPLOY_HOST>
```

For a custom port:

```bash
ssh-keyscan -H -p <DEPLOY_PORT> <DEPLOY_HOST>
```

Store the complete resulting line or lines in `DEPLOY_KNOWN_HOSTS`. The workflow
uses `StrictHostKeyChecking=yes`; it deliberately does not learn a new host key
during a deployment.

## Deployment behaviour

The deploy workflow is triggered only when all of the following are true:

1. the workflow named `CI` completed;
2. the CI run came from a `push`, not a pull request;
3. the branch was `main`; and
4. CI concluded successfully.

Deployments are serialized with a `production-deploy` concurrency group so two
production rebuilds cannot run at the same time. After the VPS script finishes,
the workflow also checks `https://monashhub.secureview.tech/api/health` from the
GitHub runner.

The `production` GitHub Environment is used for deployment history. Optional
environment protection rules can be added later if production should require a
manual approval.

## First test

Before merging the workflow, confirm that all required secrets are present.
After merge, the push to `main` runs CI; a successful CI run should then start a
`Deploy` run automatically. The final logs should show the VPS deployment and a
successful public health check.

If automatic deployment is temporarily unavailable, the manual procedure is
unchanged:

```bash
cd /opt/monash-hub/repo
./deployment/deploy.sh
```
