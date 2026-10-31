# Public release checklist

This repository is designed so the application source can be reviewed publicly while production credentials and user/operational data remain private.

## Safe to publish

- application source (`backend/`, `frontend/`, crawler/parsers);
- database models and migrations;
- Docker / nginx templates;
- CI and deployment workflow definitions that reference GitHub secret *names* only;
- `.env.example` placeholders;
- synthetic parser/cleaner fixtures;
- tests and architecture documentation;
- links to public official sources.

## Must never be committed

- real `.env` files;
- passwords, API tokens, SSH private keys or Basic Auth files;
- database dumps or backups;
- raw production crawl output;
- private user/account exports;
- private community moderation data;
- server-wide configuration for unrelated services;
- copied production logs containing email addresses, tokens or request bodies.

## Third-party source material

Parser tests use deliberately small synthetic HTML/JSON fixtures. Do not reintroduce full saved copies of Handbook or monash.edu pages as fixtures. The crawler should fetch public source pages at runtime, extract the minimum structured/text representation needed by the product, preserve the source URL, and link users back to the original.

Human-reviewed translation/glossary entries may contain short source strings needed for exact matching. Those source excerpts remain attributable to their original publisher and are not relicensed by this repository. Keep them no longer than necessary for the matching/test purpose.

## Secrets

Production secrets are provided through environment variables and GitHub environment secrets. `.gitignore` excludes common credential/key formats in addition to `.env` files. Before changing repository visibility, scan both the working tree and Git history with a secret scanner such as `gitleaks`.

## Git history and personal information

Changing or deleting a file on `main` does not remove old versions from Git history. Before making the repository public, review commit messages as well as file contents.

Some existing historical commit messages contain contributor email metadata. A public email intentionally listed on the owner's GitHub profile is not considered a release blocker. Old or unintended email addresses, secret values, private production notes, or personal data should be removed by rewriting history or by publishing from a clean-history repository if necessary.

History rewriting changes commit SHAs and can invalidate existing PR references, CI links and local clones. Do not rewrite the production repository merely for cosmetic changes; only do it for information that should genuinely not become public.

## Visibility decision

Do not change repository visibility until:

1. CI passes on the public-release cleanup branch;
2. a secret scan finds no credentials in the current tree/history;
3. no full third-party page snapshots remain in tracked test fixtures;
4. production documentation contains no unnecessary information about unrelated services;
5. the owner has reviewed historical commit messages for personal/private operational details.
