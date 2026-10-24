# Browser tests

Playwright drives Chromium through the three things a student does most: reading
a unit page, building a plan, and rating a unit. Each test runs twice, at a
desktop size and at a phone size.

They run against the real stack, not mocks: PostgreSQL, the FastAPI app, the
production build of the Nuxt app, and `proxy.mjs`, which puts the API under
`/api` on the same origin the way nginx does in production. `seed.py` loads
three synthetic units (FIT1008, FIT2004, FIT2102) into an otherwise empty
database before the API starts, so every run begins from the same data.

## Running them locally

You need PostgreSQL with an empty database for the tests, the backend's Python
packages installed, and the frontend built.

```sh
createdb monashhub_e2e
pip install -r backend/requirements.txt
(cd frontend && npm ci && npm run build)
cd e2e
npm ci
npx playwright install chromium
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/monashhub_e2e npx playwright test
```

`seed.py` empties the units and ratings tables of the database it is given, so
never point `DATABASE_URL` at a database you want to keep.

Playwright starts all three servers itself and stops them afterwards. If one is
already running on its port (8100 for the API, 3101 for Nuxt, 3100 for the
proxy), it is reused, which is handy while writing a test but means a stale
build or stale data. Rebuild the frontend after changing it.

`npx playwright test --project=desktop` skips the phone run, and
`npx playwright show-report` opens the last report. In CI a failed run keeps
the report, with a trace of each failed test, as the `playwright-report`
artifact.
