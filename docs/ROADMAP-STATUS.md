# Roadmap status

Tracks this repository against the product roadmap. Update it when a stage
moves.

## Where we are

**Stage 0 complete. Stage 1A and 1B delivered at seed scale. Stages 2 and 3
have working first versions.**

| Stage | State | Notes |
| --- | --- | --- |
| 0 · Foundation | Done | Repo, Docker Compose, PostgreSQL, FastAPI, Nuxt shell, design tokens, CI, production deploy |
| 1A · Handbook Core | Done at fixture scale | Parser + 20 fixture units, Unit Search and Unit Detail. Expanding to all 2026 units is the next data step |
| 1B · Official Knowledge Seed | Done at seed scale | 40 curated pages, clean text, hashes, Official Search |
| 2 · Unified Search + Zero-AI QA | First version | Grouped search, bilingual intent router, answer templates |
| 3 · Community | First version | Posts, answers, tags, votes, bookmarks, reports, moderation |
| 4 · Public Beta | In progress | Deployed and public at monashhub.secureview.tech; no promotion yet |
| 5 · Knowledge Expansion | Not started | Driven by real search queries, not by crawling more |
| 6 · Monetise | Not started | Needs real traffic first |
| 7 · Intelligence | Not started | Deliberately last. See AGENTS.md |
| 8 · Mini Program | Not started | Reuses the same API |

## Definition of done — MVP acceptance

- [x] `https://monashhub.secureview.tech` loads over HTTPS
- [x] No horizontal overflow on phone or desktop
- [x] Home search reaches Unit / Official / Community results
- [x] Unit Detail shows the structured fields, source and last-checked date
- [x] SC / WAM / visa / exchange queries reach the right official page
- [x] Handbook, official and community are visually distinct
- [x] Loading, empty, error and stale states implemented
- [x] Anonymous reading; sign-in only for writing
- [x] PostgreSQL not exposed; API same-origin under `/api`; crawler has no port
- [x] Basic SEO: titles, meta, canonical, sitemap, robots

## Next, in order

1. **Widen the Handbook crawl.** Spot-check the fixture units first, then one
   faculty, then all 2026 units. Do not skip the spot check.
2. **Watch real queries.** Log searches that return nothing and let that decide
   the next official seed pages.
3. **Seed the community.** An empty forum stays empty. A handful of genuinely
   useful threads is what makes the first visitors post.
4. **Then, and only then**, consider historical Handbook years and change
   tracking.

## Explicitly not now

Advertising, sponsorship, an app, WeChat mini program, course planner, credit
matching, and anything involving a language model. Each has a stage; none of
them is this one.
