# Releasing

Production does not wait for a release: every merge to `main` deploys
(`docs/AUTOMATED-DEPLOYMENT.md`). A release is a name for a commit that is
already live, with the notes for it in one place, so a reader can see what
changed between two dates without reading the PR list.

## Cutting one

1. Open a PR that does two things:
   - in `CHANGELOG.md`, rename `## Unreleased` to `## <version> - <date>`
     and add an empty `## Unreleased` above it;
   - in `backend/app/version.py`, set `__version__` to the same version.
   Merge it like any other PR. That merge deploys.
2. Tag the merge commit and push the tag:

   ```bash
   git fetch origin main
   git tag -a v<version> -m "Monash Hub <version>" origin/main
   git push origin v<version>
   ```

3. The Release workflow checks that the tag, `__version__` and the CHANGELOG
   heading agree, runs CI on the tagged commit, and publishes a GitHub
   Release whose notes are that CHANGELOG section. If any check fails, fix
   it on `main`, delete the tag, and tag again.

Versions follow the usual major.minor.patch. A data refresh or a translation
pass is not a release; a change to what the site does is.

## What a tag does not do

It does not deploy, build an image or run a migration. Those happen when the
PR merges. The tag only has to point at a commit `main` already has, which
the `--verify-tag` on the release step and the CI run on the tag both assume.

## Where the numbering starts

`v1.0.0` was tagged by hand on 2026-10-10, before this workflow existed, and
has no CHANGELOG section of its own. `__version__` is set to match it. The
first release made with the workflow is the next one, `1.1.0` or `1.0.1`
depending on what the Unreleased section holds by then.
