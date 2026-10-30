<p align="center"><img src="./frontend/public/favicon.svg" alt="Monash Hub Logo" width="120" /></p>

<h1 align="center">Monash Hub</h1>
<p align="center">Making Monash information easier to find and understand</p>

<p align="center">
  <a href="https://monashhub.secureview.tech"><img src="https://img.shields.io/badge/live-monash--hub-1e5eff?style=for-the-badge" alt="Live site" /></a>
  <a href="https://github.com/Waldo0926/monash-hub/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Waldo0926/monash-hub/ci.yml?branch=main&style=for-the-badge&label=CI" alt="CI" /></a>
  <img src="https://img.shields.io/badge/status-in%20production-2ea44f?style=for-the-badge" alt="Status: in production" />
  <a href="https://waldo0926.github.io/uptime/history/monash-hub"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FWaldo0926%2Fuptime%2FHEAD%2Fapi%2Fmonash-hub%2Fuptime.json&style=for-the-badge" alt="Uptime" /></a>
  <img src="https://img.shields.io/badge/unofficial-not%20affiliated%20with%20Monash-black?style=for-the-badge" alt="Unofficial" />
</p>

<p align="center"><a href="https://monashhub.secureview.tech">Visit Monash Hub</a></p>
<p align="center"><strong>English</strong> | <a href="./README.zh-CN.md">简体中文</a></p>

---

<p align="center"><img src="./docs/images/home-en.webp" alt="Monash Hub home page: search box with eight entries under it, key dates, guides for this part of the semester and the 马莫百科 block" width="900" /></p>

## What is Monash Hub?

Monash Hub brings Monash student essentials into one place: units, degrees, study planning, WAM/GPA tools, key dates, Malaysia tuition fees, official guides and a student community. It is designed especially to help non-native English speakers search for, understand and verify information about study and campus life.

Instead of switching between the Handbook, university websites, policy pages and student discussions, students can begin in one place and see clearly where each result comes from.

> Monash Hub is not affiliated with or endorsed by Monash University. For enrolment, visas, assessment and academic-policy decisions, always confirm details through Monash websites, the Handbook, Moodle or WES.

## Why another site?

Before Monash Hub, a student with a question had three places to look, and each covered part of it:

| Where | Good at | Missing |
| --- | --- | --- |
| [Monash Handbook](https://handbook.monash.edu) | The official record for units and courses | English only, and only units and courses: policies, visas and key dates are elsewhere |
| monash.edu and monash.edu.my | Official guides for each campus | About 3,100 pages across two sites, and the campuses' rules differ (visas, insurance, unit changes) |
| Student group chats and shared docs | Quick answers in Chinese | No source, and often a past year or the other campus |

Student tools came before this one. [MonPlan](https://github.com/MonPlan) was a student-built course planner; its open scrapers ([MonScrape](https://github.com/MonPlan/MonScrape)) were last updated in 2017 and read the old Handbook pages. monashcoding's [TheBetterHandbookAPI](https://github.com/monashcoding/TheBetterHandbookAPI) documents the Handbook's search endpoint (last commit September 2022). Neither covers policies or a second language.

Monash Hub keeps what they got right, data straight from the Handbook, and adds the rest: official pages from both sites next to the units, every result labelled with its source and the date it was last checked, Malaysia and Australia shown side by side when they differ, and a Chinese translation linked to the English original. The Ask panel searches these sources and does not use a generative model to write answers. It also passes the question to the 马莫百科 WeChat bot, which answers from what its owner has taught it and from the account's posts. When those have nothing, the bot may let a free language model pick sentences from official pages, and each sentence is checked word for word against the page before it is sent. The bot's reply sits in its own block, labelled 来自马莫百科.

## Technology stack

The current production stack is:

- **Frontend:** Nuxt 4, Vue 3 and TypeScript, rendered with SSR
- **Backend:** FastAPI and Python
- **Database and search:** PostgreSQL 17, using `tsvector`, GIN indexes and `pg_trgm` for full-text and fuzzy search
- **Infrastructure:** Docker Compose, Nginx and HTTPS
- **Testing:** pytest against a real PostgreSQL, Vitest, and Playwright browser tests at desktop and phone sizes, all run in CI before a deploy
- **Data pipeline:** Python crawlers with hash-based incremental synchronisation and failure-safe persistence
- **Production:** [monashhub.secureview.tech](https://monashhub.secureview.tech)

The production request path is Nginx → Nuxt SSR for the web interface and Nginx → FastAPI for `/api/*`, with PostgreSQL on a private Docker network. See [architecture](docs/ARCHITECTURE.md) for the current system design.

## By the numbers (29 October 2026)

| | |
| --- | --- |
| Official pages in the guides | 2,917 listed from both sites' sitemaps, up from 662 |
| Backend tests | 891 test functions, run against a real PostgreSQL in CI |
| Frontend and browser tests | 77 Vitest tests; 22 Playwright tests at desktop and phone sizes |
| Translation model | Zhipu's free `glm-4.5-flash`, chosen after reading three free models against the English over 70 paragraphs (`glm-4-flash` turned conditions around) |
| Deploys | Every merge to `main`; a smoke check of the live site after each, and the previous version goes back if it fails |

Sources: the [changelog](CHANGELOG.md) and the test files in `backend/tests`, `frontend` and `e2e`.

## What can you do here?

### Find unit information

- Search by unit code or title
- Check campuses, teaching periods, assessments, exams, requisites, learning outcomes and workload
- Verify details through the Handbook link and last-checked date

<p align="center"><img src="./docs/images/unit-en.webp" alt="Unit page for FIT2004: faculty notice, credit points, campus, assessment, offerings and the Handbook source link" width="900" /></p>
<p align="center"><sub>The home page screenshot comes from the live site. The other screenshots come from the browser-test stack, which runs the real site on three invented units (FIT1008, FIT2004, FIT2102) and an invented degree. Names, marks and plans are made up; the live site shows the Handbook.</sub></p>

### Find official Monash information

- Search WAM, Special Consideration, census dates, visas, exchange and campus services
- Read curated official content with its source link and last-checked date
- Prioritise results labelled `Official Handbook` or `Official source`

### Understand information more easily

- Use the interface in English or Simplified Chinese
- Read translated support for Handbook and official-guide content
- See translation provenance and links to the original page

### Plan your degree

- **Degrees**: what a degree is made of, how many credit points each group of requirements is worth, and which of its units your campus does not actually teach
- **Course map**: put units into semesters and have each one checked for you: whether your campus offers it, whether that teaching period offers it, and whether what it requires is sitting earlier in the plan
- **Unit tree**: follow a unit back to what it needs, or forward to what it unlocks; units your campus does not teach are marked rather than hidden

The three of them sit under **Planning** in the header.

A plan is stored only in your own browser and is never saved to an account. Each check sends the plan to the API so it can be compared with the Handbook, and nothing is kept once the answer comes back. To open a plan on another device, use **Copy plan code** in the course map's More menu: it copies a link with the plan written after the `#`, which the browser never sends to the server. Open the link on the other device, or paste it into **Paste plan code** there. Export still works if you would rather keep a file.

<p align="center"><img src="./docs/images/plan-en.webp" alt="Course map: four units placed in semesters, each checked against the campus, teaching period and prerequisites, with progress against the degree on the right" width="900" /></p>

### Work out your WAM / GPA

- Type a unit code and the credit points and level come from the Handbook; you do not have to remember the level weighting
- Malaysia uses CGPA, which is a different scale, so you can switch between them
- You can also upload a screenshot of your WES results or paste the text, and have it read into the table
- Marks are worked out in your browser and never stored on your account. Only the unit codes you type are sent to the API, to look up credit points and level; the marks themselves stay on your device

<p align="center"><img src="./docs/images/marks-en.webp" alt="WAM / GPA calculator: three units with marks, grouped by level, WAM and CGPA on the right" width="900" /></p>

### Check Malaysia tuition fees

- `/fees` lists every row of Monash Malaysia's undergraduate and postgraduate fee pages, grouped by level and school, with a filter by course name
- Each fee says whether it is per year or for the whole course, and how it moved since 2026 (for example "vs 2026: +RM 2,880 (+5.3%)")
- A degree page viewed as Malaysia shows that degree's own fee
- The amounts are read from the fee pages the site already indexes, which are re-read every two days, so a change on monash.edu.my shows up without anyone typing it in. An amount that does not read as a number is shown as Monash printed it, with a warning

### Key dates

- The home page shows the next few academic dates for your campus: census, withdrawal, SWOT vac, exams and results
- `/dates` lists every upcoming date by month, including Allocate+ and WES re-enrolment windows, with public holidays you can hide

### A page for parents

`/parents` is written in Chinese for parents looking at the Malaysia campus: the campus in numbers and its SETARA rating, rankings, the degree certificate, entry scores by 高考, A-Level, IB, AP, SAT, ACT, MUFY and CIMP, the MUFY and diploma routes, scholarships, transferring to an Australian campus, exchange, tuition with the 6% service tax and a yuan estimate, the visa fee, living costs, campus life and what the university can tell parents. Each official fact links the English page it came from and says when it was checked.

### Ask a question

Every page except search has an Ask button in the corner. The panel answers from the Handbook, official pages and 马莫百科 posts, and also shows what the 马莫百科 bot knows (see [Why another site?](#why-another-site)). When neither has an answer, it shows the account's QR code so the question can be sent there and answered later.

### Join the student community

- Browse and search public questions and discussions
- Sign in to post, answer, vote, bookmark or report
- Read student experience linked to a particular unit
- Find study partners, activity companions or people with shared interests

Community content is student experience, not Monash University policy.

### MUM Guide

An index of the articles from the 马莫百科 WeChat account: searchable, grouped by topic, and linked back to the original post. Like the community, it is a student's write-up rather than official policy.

## How to use it

1. Search from the home page with a unit code, keyword or question, or pick one of the eight entries under the search box.
2. Start with official results and open source links for important decisions.
3. Read results labelled `Community` when you need student experience.
4. Register with an email address to ask or answer questions.

## Source labels

| Label | Meaning |
| --- | --- |
| `Official Handbook` | Structured information from the Monash Handbook |
| `Official source` | Curated information from official Monash web pages |
| `Community` | Student questions, discussions and personal experience |

## Source and privacy boundary

The repository contains application source code, schema/migrations, deployment templates, tests and small synthetic parser fixtures. Production credentials, database dumps, user exports and raw crawl output do not belong in Git. The crawler links back to official sources rather than mirroring binary content. It sends one request at a time, a few seconds apart, under its own name (`MonashHubBot`), and checks `robots.txt` before reading an official Monash page. See [crawling](docs/CRAWLING.md).

See [Public release checklist](docs/PUBLIC-RELEASE.md) for the repository's privacy, secret and third-party-content boundary.

## For developers and contributors

This README is for product users. See [architecture](docs/ARCHITECTURE.md), [decision records](docs/adr/README.md), [deployment](docs/DEPLOYMENT.md), [crawling](docs/CRAWLING.md), [public-release checklist](docs/PUBLIC-RELEASE.md), [roadmap](docs/ROADMAP-STATUS.md), [contribution rules](AGENTS.md) and the [changelog](CHANGELOG.md) for project work.

Development changes should use `feat/*`, `fix/*` or `chore/*` branches, with a Pull Request reviewed before merging into `main`.

### Run it locally

The browser tests ship with everything needed to run the real stack on synthetic data: PostgreSQL, the API, the production build of the frontend and a small proxy that puts them on one origin, as nginx does in production.

```sh
createdb monashhub_e2e
pip install -r backend/requirements.txt
(cd frontend && npm ci && npm run build)
(cd e2e && npm ci && npx playwright install chromium)
cd e2e && DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/monashhub_e2e npx playwright test
```

Playwright migrates the database, loads `e2e/seed.py`, starts the three servers on ports 8100, 3101 and 3100, runs the tests and stops them. To keep the site up for a look, start the same commands yourself; they are listed in [e2e/README.md](e2e/README.md). Real Handbook and official-page data comes from the crawler, see [crawling](docs/CRAWLING.md). Backend tests run with `pytest` in `backend/`, frontend tests with `npm test` in `frontend/`.

## License and copyright

**Public visibility does not make this project open source.**

Copyright © 2026 Waldo. All rights reserved.

The source code in this repository is made publicly visible for portfolio presentation, educational review and code inspection. Unless you have prior written permission from the copyright holder, no permission is granted to copy, modify, distribute, sublicense, sell, commercially use, deploy as a competing service, or create derivative products from this software.

GitHub features such as viewing, cloning or forking a public repository do not constitute an additional software licence from the copyright holder.

Third-party names, trademarks and source material, including Monash University names, marks and source content, remain the property of their respective rights holders and are not relicensed by this repository.

See [COPYRIGHT.md](COPYRIGHT.md) and [NOTICE.md](NOTICE.md) for the detailed ownership boundary.
