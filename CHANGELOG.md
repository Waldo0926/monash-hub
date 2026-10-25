# Changelog

All notable changes to Monash Hub are documented here.

## Unreleased

### Fixed (searching a unit that has closed)

- Searching a unit code that an earlier Handbook has but this year's does not
  (FIT1008, gone from 2027) used to say only that the Handbook has no such
  unit. It now says which Handbook last had it, shows the faculty's teach-out
  notice word for word (Monash Malaysia's and the Australian campuses' lists,
  the reader's campus first), cites both faculty pages and links to the unit's
  last page. A code in no Handbook at all is still treated as a typo.

### Fixed (pages about past years)

- 152 pages about a year that is over leave the guides: OSHC price lists
  and SSAF from 2016-2025, past re-enrolment, unit discontinuation and
  non-standard dates, timetables and results release dates, past intakes and
  principal dates, and past events and student representatives. Course maps
  stay for students who started in the last five years (2021 on, in 2026),
  since a student follows the map of the year they commenced; older ones go.
  Course codes such as C2001 and "students who commenced from 2014" are not
  read as years. The rule runs on every coverage build, so each January the
  previous year's pages drop out.

### Fixed (Malaysia pages checked by hand)

- Monash Malaysia's exam rules and its five eExam pages under
  examinations-results answer "Access Denied" even to a signed-in student, so
  they leave the guides instead of keeping their old text. eExam questions are
  answered from Monash Malaysia IT services' public Online assessment (eExams)
  pages.
- The fee calculator is listed as a link to the calculator app
  (fin-feescalc.monash.edu.my), which needs a Monash sign-in, under its own
  title. It used to be stored as "Student association".
- The Malaysia special consideration page is empty and the Malaysia menu now
  links to the University-wide page, so the home page's Malaysia list shows
  that page and the Malaysia copy is retired.
- The talent release form (a photo and video consent form) leaves the guides.

### Fixed (guides that are not guidance)

- 174 pages from the Monash Malaysia schools' sites leave the guides: their
  about sections (leadership, staff lists, departments, vision and mission,
  rankings), competitions and their galleries, the 2005-2017 study-trip
  posts, lab and research team pages, CMS listings and site maps, news posts
  and test copies. Accreditation pages and the study-trips overview stay.
  They are retired at the next scheduled refresh; nothing is fetched for it.
- A school's page is filed under enrolment only when its address is about
  courses (course, unit, enrol, timetable, current students...); the rest go
  under support. Every faculty page used to default to enrolment, which made
  选课与课程规划 hold 1,331 pages.

### Fixed (answers that hold for one country only)

- The curated answers on intermission, withdrawing from a unit, work hours,
  the CoE and census dates are written in an Australia part and a Malaysia
  part, each from that campus's official page, and cite both pages. The
  intermission answer used to tell every student on a student visa that
  intermission changes their CoE; a CoE is Australian, and in Malaysia the
  Student Pass rules apply (medical intermission can stay, any other cancels
  the pass, and coming back needs a new eVAL 4 to 2 months before the
  semester). Such an answer carries no single-campus label.
- New answer: do international students need health insurance (OSHC in
  Australia; the medical insurance Monash Malaysia buys with the Student Pass).
- New answers: underload on a student visa, and overload, each for both
  campuses. The Malaysia parts give the SORS forms, the Friday of Week 2
  deadline and the International Student Pass Office, from the notes on the
  forms.
- The GPA answer said N is worth 0. A fail is 0.3 on Monash's scale; the
  answer now gives the whole scale and Malaysia's CGPA values.
- The automatic conferral answer adds how to delay conferral (3 months in the
  system, up to 12 through Monash Connect), as the graduations office
  confirmed in October 2026; no page says it yet.
- A test fails when an answer names a rule of one country (CoE, OSHC,
  Student Pass, eVAL...) without naming the country, in English or Chinese.

### Changed (official pages)

- The guides cover both Monash sites from their sitemaps: about 3,100
  pages, up from 662 - Monash Malaysia's whole site and monash.edu's student
  pages, less research news and research sections, staff and alumni pages,
  testimonials, conference and campaign sites, event sign-ups, CMS drafts
  and the 2020-22 COVID-19 notices. A page already listed stays when it is in
  no sitemap but still has its text (the Malaysia eExam pages). A listed page
  Monash moved keeps its slug and translations at the address the sitemap
  gives now, unless that address is a school's copy of a central page.
- A page Monash writes as a paragraph inside a list ("April 2026 ceremony in
  Malaysia, you'll get:" before its items) keeps the paragraph.
- A list inside a list item stays under that item, indented, and the outer
  list goes on below it with its numbering. It came after the whole outer
  list, so Monash Malaysia's work rules showed the allowed places and banned
  jobs under the last rule. The page text numbers an ordered list 1, 2, 3
  instead of 1, 1, 1. Pages with such lists show as changed once.
- Among pages that match a question equally, the hand-picked ones come first.
  With the long tail listed, 全日制 found a science honours FAQ before the
  study load page.
- Monash Malaysia's site refuses the server's address since 2026-10-25. Its
  pages can be read on another computer (`crawler.official.harvest`) and
  stored by the server with its own code (`deployment/crawl.sh
  official-harvest FILE`).
- A harvest stopped mid-write no longer loses the pages after it. Each page
  is now its own gzip member, and a file torn by an earlier stop is read up
  to each tear and on from the next member; before, reading stopped at the
  first tear, so the server loaded none of 680 pages and a resumed run read
  them again. A torn member is never read on into the next one, which can
  come out as valid lines with the wrong fields. The server reads a harvest
  one page at a time and keeps each compressed until it is stored; 723
  pages held whole took more than the crawler's 2 GB.
- A page that is short on Monash's site too - a hub of links such as
  Malaysia's enrol and re-enrol page, or a short answer - is stored when
  there is no longer copy to keep. A long page that suddenly reads short
  still keeps its last good copy (Malaysia's special consideration page now
  holds only its title and a link to the central page).
- A page that a script sends on to another site while it loads is not
  stored: cms-academic/checkmk was stored as the Okta sign-in form. Link
  reports, a backup copy, a safety-video list and the open-day event pages
  are left out of coverage (3,102 rows).
- A full re-crawl (`--all`) no longer clears the date a page was last read
  before fetching it. On 2026-10-25 the 359 Malaysia pages it was refused on
  lost their "last checked" date; a page now keeps it until a read works.

- Tables keep their shape. A cell that spans rows or columns is drawn merged,
  as on monash.edu, instead of moving every cell below it one column left; a
  second header row ("Malaysian / International" under "Tuition fees") and a
  table's footer row are kept; a cell with its own line breaks keeps them.
- Collapsed content is read in full. The question of each accordion item was
  the text of its toggle button and was dropped with the other page controls,
  so the student pass page had 75 answers and no questions. An accordion is
  now read as sections, so an answer keeps its paragraphs, lists and tables.
- On a phone, a table wider than the screen shows a shadow at the edge it
  continues past and a line saying to swipe it sideways.
- A page whose article is only a title no longer shows the cookie banner as
  its text, and "Content cannot be accessed", a sign-in widget's placeholder
  at the top of students/admin, /dates and /timetables, is left out.
- Every official page is re-extracted on its next fetch (extractor version 7).

### Changed (Chinese translation)

- A stored translation that lost a web or email address, or carried the
  prompt with it, is not reused: a `--refresh` pass on 2026-10-25 put 179
  of them back, such as forms.Monash.edu/选课注册-amendment for
  forms.monash.edu/enrolment-amendment. They are translated again, and the
  official pass picks them out of pages that are otherwise up to date.
- The chat-model translator defaults to Zhipu's free `glm-4.5-flash`. Read
  against the English over 70 paragraphs of the guides, `glm-4-flash` turned
  conditions around ("provided you have one semester left") and
  `glm-4.7-flash` was refused with 429 37 times in 30 paragraphs on the free
  tier; `glm-4.5-flash` was the fastest and the most accurate.
  `TRANSLATE_LLM_MODEL` still overrides it. The scheduled passes send two
  strings at a time instead of four, since the free tier refused 17 of 40
  requests with three in flight and none with two; `TRANSLATE_WORKERS` in
  `.env` changes it.
- Web addresses are kept as written. The glossary keeps "Monash" in English
  and matched it inside addresses too, so 1,174 stored translations read
  `www.Monash.edu`, and a path such as `mon2750-monash-innovation-guarantee`
  is case-sensitive. Stored strings are repaired when a pass reuses them.
- A paragraph that opens with a bold label ("**How to apply** Visit: …") is
  translated as the label and the sentence, joined with a colon. Whole, it
  came back as 如何申请访问 (how to apply to visit), or without the label.
- A reply that repeats the prompt's GLOSSARY or TEXT lines is rejected. The
  check was skipped whenever the prompt carried a glossary, and one stored
  string had another string's prompt appended to it.
- "course of action" is 行动方案, not 学位课程的行动; "semester break" and
  "mid-semester break" keep the break (学期假期, 学期中假期).
- On-campus and Off-campus are pinned only on Handbook pages, where they are
  attendance modes. On a guide "off-campus accommodation" came back as
  校外授课住宿.
- The prompt no longer says an award is always a degree, so a scholarship
  award is a scholarship.
- A reply carrying an abbreviation the English did not have is rejected:
  LKM, the Malaysian qualifications agency's form, came back once as LLM.
- `python -m crawler.translate.compare` puts several models side by side on
  stored paragraphs, without writing anything, for the next time.

### Fixed (a crawl that goes wrong costs less)

- One failed fetch of an official page no longer takes it off the site. It
  used to be marked as an error, which hid it from the guides, search, key
  dates and the assistant until a later fetch worked, so a single timeout or
  bot challenge hid text that was still right. The last good copy now stays
  up with the date it was last read, and only a 404 or 410 takes a page down.
  Pages already hidden this way come back on their next attempt.
- An official page that now redirects to the section above it, or to the
  home page, is not stored. That is what a removed page usually does, and the
  landing page reads fine, so it would replace the seed's text without anyone
  noticing. It is recorded as failed with the new address.
- A `robots.txt` that the WAF refuses over `httpx` is read again with the
  browser in `auto` mode. Since unreadable robots files close the host, a
  monash.edu.my that refuses `httpx` everything would otherwise never be
  crawled again.
- A Handbook index page that fails is retried like a unit page. One timeout
  in the roughly 180 index requests of a weekly refresh used to end the run,
  and the degree crawl, search reindex and translation after it.
- One run marks at most 25 units, degrees or areas of study inactive (or 2%
  of its targets if that is more). A Handbook answering 404 for everything
  would otherwise have taken every unit off the site for a week.
  `--max-withdrawals` raises the cap after a person has checked.
- `scheduled-refresh.sh` runs every step even when one fails, and still exits
  non-zero so systemd shows the run as failed.

### Added (a crawl that goes wrong is reported)

- A Handbook run stops after 30 units, degrees or areas of study fail in a
  row and records why. A Handbook that was down used to cost three attempts
  for each of 5,000 units, far past the 10 hours systemd allows. The official
  run has no such stop, since one site refusing says nothing about the next.
- A run stopped by systemd is recorded as failed, and a job left "running"
  by an older run is closed when the next one of its kind starts.
- `scheduled-refresh.sh` mails `ALERT_EMAIL` when the last run of that kind
  failed, is still marked running, or more than 5% of its targets (and at
  least five) failed. At most one email a day for each kind.
- `/api/health` shows the last run of each kind under `crawls` and says
  whether the weekly Handbook refresh is more than eight days old
  (`handbook_overdue`). `last_crawl` is still there.
- The browser transport opens a new page when Chromium's page crashes, up
  to twice a run. It used to keep the dead page, so every page after it
  failed.

### Fixed (course transfer for Malaysia students)

- 转专业 from a Monash Malaysia student was answered with the Australian
  admissions page. `POST /v1/ask` now takes an optional `campus`
  (`malaysia` or `australia`); that campus's own official pages come before
  the ones listed for every campus, and a campus named in the question still
  wins. The Malaysia group chat bot can pass `campus: "malaysia"`.
- Malaysia's Internal Course Transfer page and the university's Course or
  campus transfer page have reviewed Chinese titles with 转专业 in them; the
  machine title 转学位课程 never matched what students type.
- A long Chinese question ranks the page whose Chinese title names its topic
  first, so 转专业是符合要求就可以还是择优录取 behaves like 转专业.
- ICP, what Malaysia students call an internal course transfer, finds those
  pages. Monash's own pages do not use the abbreviation.

### Changed (AskMira is gone)

- Monash Malaysia replaced AskMira with MoVA, the Monash Connect virtual
  assistant, and the Student Hub counter with Monash Connect. The footer's
  Malaysia links and the assistant's "ask Monash" link now go to
  monash.edu.my/student-services/connect with the chat open, and the link
  text says you can also visit Monash Connect on campus.

### Added (add to home screen)

- The site can be added to a phone's home screen and opens full screen like an
  app, with its own icon. The manifest's description and shortcuts (units,
  degrees, guides, course map) follow the interface language.
- Unit, degree and guide pages, the home page and the course map, tree and
  marks pages open with no network once they have been read. Pages and the API
  still come from the network first; a saved copy is used only when there is
  no connection, and the page then says it may be out of date. Only successful
  answers are saved, and ratings, community, accounts, notifications, search
  and the assistant are never saved.
- A page that was never saved shows an offline page in the reader's language,
  listing the pages that are.
- An app left open picks up a new deploy: it checks when it comes back to the
  front and reloads on the next link.
- On phones, after a few pages, a one-line hint explains how to add the site
  for iPhone Safari, Android browsers (including Huawei, Xiaomi, OPPO and vivo)
  and WeChat. "Don't show again" hides it for good; the same steps are in the
  footer.
- The unit, degree and guide lists answer 503 when the API is down, like the
  detail pages, so an error is never saved over a good copy.

### Fixed (special consideration answers)

- The special consideration answer gave a deadline of two university working
  days after the assessment and said short extensions go through the teaching
  team. Monash's page says to apply by 11.55pm on the day the assessment is due
  or scheduled, that one form covers a short extension and an extension through
  special consideration, and that you can't ask your chief examiner for one.
- The supporting documents answer named a Monash Health Professional Report,
  which the official page no longer mentions, and said screenshots are not
  accepted (they are, with timestamps, for technical problems). It now says
  what the page says: a medical certificate for a medical condition, what is
  not accepted, the NAATI translation rule, the impact statement and the rule
  for campuses outside Australia.
- The deferred final assessment answer said there is no separate form. Deferral
  has its own form (deferred and rescheduled assessments), due by 11.55pm on
  the day the assessment is set.
- The supplementary assessment answer said special arrangements can move it.
  It cannot be rescheduled; special arrangements only cover a time-zone clash.

### Added (browser tests)

- Playwright tests for the unit page, the course map and unit ratings, run in
  CI against PostgreSQL, the API and the production build of the web app, at a
  desktop and a phone size. See `e2e/README.md`.

### Fixed (course map)

- A unit placed in a semester or campus it is not taught in named the other
  semesters and campuses in English ("Second semester", "Clayton") inside an
  otherwise Chinese, Japanese or Korean sentence. They now follow the
  interface language.

### Added (Monash Malaysia General Studies and transport)

- Monash Malaysia's General Studies page (the MPU units a Malaysia campus
  student must pass to graduate) and its maps and transport page are indexed.
- Search and the assistant understand 通识课, 通识, MPU and General Study, and
  交通, 校车, 公交, 轻轨, 停车场 and 校园地图.
- Three assistant answers: which MPU units to take, how to get to the campus
  and around Sunway, and where a classroom is (the Monash Study app).
- The hurdle answer follows the Assessment Regime Procedure for teaching periods
  from 27 July 2026 (additional assessment capped at 50% on a weighted hurdle,
  N below 45), and a new answer says what changed: threshold hurdles are gone
  from every unit by 31 December 2026. The hurdles page has a Chinese title.
- The assistant ignores greetings and words like 您好, 孩子, 家长 and 啥, so a
  parent's question finds the same answer as a student's.
- 怎么去机场 and other airport questions get the Malaysia transport answer
  (KL Sentral, then the express train to KLIA).
- The hurdles page headings have a checked Chinese translation. The first one
  had been machine translated into a sentence about course codes.

### Security

- Pillow 13.0.0, which fixes 24 advisories against 12.3.0 that pip-audit
  started reporting on 2026-10-22.

### Added (Malaysia teach-out notices)

- Monash Malaysia's School of IT list of closing and renamed units is indexed
  next to the Faculty of IT list on monash.edu. The two differ: FIT1043 is gone
  in Australia but runs once more in Malaysia, and FIT1055 is only on the
  Malaysian list.
- A unit page shows the notice for the reader's campus (Malaysia unless their
  plan says otherwise), with the campus next to the title and a button to see
  the other campus's list. A degree page tags units from the list for the campus
  it is showing.

### Changed (crawler image)

- The crawler image is built from `python:3.14-slim`, the same Python as the
  API image, and installs its own Chromium with `playwright install`. The
  playwright pin no longer waits for a matching prebuilt image, so it is on
  1.64. A new workflow builds the image and launches the browser whenever the
  crawler or its requirements change.

### Changed (frontend dependencies)

- `vue-router` 5.4 and `@types/node` 26, the versions Nuxt 4.6 already ships
  with, so the tree has one copy of each.
- TypeScript 6.0, the last release of the JavaScript compiler. 7 is the Go
  compiler and has no programmatic API until 7.1, so `vue-tsc` cannot run on
  it yet; Dependabot skips 7 until it can.

### Added (issue templates, Dependabot and decision records)

- Three issue forms: a bug, wrong information on a page (which asks for the
  Monash page that has it right), and a feature request. Security problems
  are pointed at SECURITY.md instead of a public issue.
- Dependabot opens one grouped PR a month per ecosystem (backend and crawler
  pip, frontend npm, GitHub Actions, the three Dockerfiles). CI audits and
  tests each one like any other change.
- `docs/adr/` records five decisions and why: the monolith, search in
  PostgreSQL, answers without a language model, the glossary in front of
  machine translation, and accounts without real names.

### Added (a release workflow)

- Pushing a tag `v<version>` publishes a GitHub Release. The workflow checks
  that the tag matches `backend/app/version.py` and that the CHANGELOG has a
  `## <version>` section, runs CI on the tagged commit, and uses that
  section as the release notes. Steps are in `docs/RELEASING.md`. Nothing
  about deployment changes: `main` still deploys on merge.
- The API version now lives in one place, `backend/app/version.py`, and
  `/api` reports it. It is set to 1.0.0 to match the tag that already
  exists; the API used to call itself 0.1.0.

### Added (a deploy now proves the right commit is live)

- `/api/health` and `/api` report the git commit the API was built from.
  `deploy.sh` passes the SHA it checked out as the `APP_COMMIT` build
  argument.
- `deployment/smoke.sh` asks a running site what a visitor would: the home
  page in English and Chinese, a unit page, a unit search, a search for WAM,
  robots.txt and the sitemap, and 404s for a missing unit and a missing path.
  With `--commit` it also checks the commit the API reports.
- `deploy.sh` runs it against the new containers after the health check and
  rolls back on failure. The Deploy workflow runs it again through the public
  hostname, so "deployed" now means the public site answers from the commit
  CI tested, not just that something answered `/api/health`.

### Security (dependency upgrades, and an audit on every build)

- The API moves to Pillow 12.3.0, python-multipart 0.0.31 and PyJWT 2.15.0.
  Each of the old versions had published advisories (Pillow three,
  python-multipart six, PyJWT fourteen); pip-audit now reports none.
- The web app moves to Nuxt 4.6.2, Vue 3.5.44 and Vitest 5. The old lockfile
  carried 26 advisories, among them an XSS in Vue's server renderer, which
  is what renders every page here, and others in devalue, undici, svgo and
  the dev tooling. Two remain, braces and node-forge, which have no fixed
  release yet; neither is in the server bundle that runs in production, and
  `frontend/scripts/audit.mjs` lists both with the reason.
- CI runs pip-audit over the API pins and npm audit over the web lockfile on
  every push and pull request, so a new advisory fails the build instead of
  waiting to be noticed.

### Changed (scroll hint on degree panels)

- A degree panel whose list is taller than its box now shows a small bar at
  the bottom, "还有 N 个，下滑查看" (in all four languages). The count drops
  as you scroll, the bar goes away at the end of the list, and clicking it
  scrolls the list down. The bottom fade stays.

### Removed (dead Monash Malaysia career pages)

- 19 Monash Malaysia Career Services pages are gone from the seed list.
  Monash took them down (17 return 404) or moved them behind staff sign-in
  (2 now redirect to Okta), so every refresh logged them as failures. The
  next official refresh retires them; the Career Services overview and the
  jobs board stay.

### Fixed (Korean particles and a few mistranslated terms)

- Korean particles now match the glossary term in front of them (과목을,
  not 과목를). The model chose the particle for its own word, and the term
  put back afterwards often ends differently.
- *testamur*, *Department of Home Affairs* and *full-time load* have agreed
  wording. Korean had transliterated testamur, and both languages read the
  department as an academic one.
- The prompts say an award is a degree, not a prize.

### Fixed (Japanese and Korean translation quality)

- Korean kept none of its spaces. A rule that joins Chinese and Japanese
  words after a glossary term was also running over Korean.
- Japanese no longer doubles words around a glossary term
  (マレーシアキャンパスキャンパス, 履修取消するする). Verb terms such as
  *withdraw* and *enrol* are now nouns in Japanese and Korean, so the model
  adds the verb ending itself.
- Dates are written year first (2026年12月, not 12月2026年).
- A Japanese answer with Simplified Chinese characters in it is dropped and
  the English stays.
- "apply to graduate" has agreed wording, so Japanese no longer says
  graduate school. The prompts also tell the model not to leave clauses out.

### Fixed (machine translation into Japanese and Korean)

- The chat-model engine refused every language but Chinese, so the
  Japanese and Korean passes stopped as soon as they started. It now has a
  Japanese and a Korean prompt.
- Table cells with no words in them ("E116 - E140") are no longer sent to
  the model. It explained them instead of copying them, and enough of
  those in a row stopped the Chinese guide pass half way.
- Every string is sent marked as text to translate, so a FAQ question is
  translated rather than answered. A run of rejected replies now has to be
  three times longer before it stops a pass.
- In the scheduled refreshes, one failed translation pass no longer stops
  the passes after it or the search reindex.

### Fixed (a degree page nobody could link to)

- M6011 is published as "M6011 M6019". The pair was stored as the course
  code, so its page sat at /courses/M6011 M6019. The crawl now keeps the
  first code, and a migration renames the stored row (or drops it where
  the year already has M6011) along with its translations.

### Fixed (translation no longer blocks the weekly crawl)

- Scheduled translation now runs after the crawl lock is released, under
  its own lock that `translate.sh` shares. The first Japanese and Korean
  fill takes hours, and while it held the crawl lock the weekly Handbook
  refresh would have skipped itself. The weekly run waits for a running
  pass; the six-hourly official run leaves its pages for the next one.

### Fixed (Handbook names left in English)

- Every faculty, school and department the Handbook names (120 of them)
  now has a checked name in Chinese, Japanese and Korean. The faculty and
  school filters on the unit search page showed about 45 of them in
  English, such as School of Mathematics and Psychology.
- The filters now take their labels from the API, so Japanese and Korean
  get them too, and a name reads the same in the filter and on the unit
  page.
- Unit, degree and area of study pages use the glossary's wording for
  closed-list values (campus, teaching period, level, faculty, AQF level,
  type of area of study) even where an older machine translation said
  something else. In Japanese and Korean these values were all English.
- Added the campuses, teaching periods, assessment types and AQF levels
  that were missing, and the attendance modes, assessment types and
  activity types in Japanese and Korean.
- In Korean, Term 1 and Teaching period 1 no longer read the same as
  First semester (all three were 1학기).
- The marks calculator's level heading was still "Level 2" in Chinese,
  Japanese and Korean.
- The weekly Handbook refresh now translates the units and degrees it
  changed, and both scheduled refreshes cover Japanese and Korean as well
  as Chinese (`TRANSLATE_LOCALES` in `.env`).
- On a unit page, the part of each major that lists the unit ("Level 2 and
  3 elective units") now uses the major's own translation. It was English
  on about a third of Chinese unit pages.
- The faculty's advice in a unit's learning resources ("There are required
  texts for this unit...") is translated. Book citations stay English, and
  a line whose translation lost a link is shown in English.
- A guide names its publisher in the reader's language (Monash University
  Malaysia was English on 355 Chinese guides).
- The home page key dates card works in Japanese and Korean, and links its
  sources by their translated titles. The example faculties, search
  suggestions and dates on the home page are translated too.
- The exchange page text and the footer copyright line were English in
  every language. The teach-out tags on degree pages are now translated in
  Japanese and Korean as well as Chinese.

### Changed (footer points to 马莫百科)

- In the footer line about the 马莫百科 WeChat account, the account name
  now opens the 马莫百科 page, and a new blue "扫码关注、加好友" button opens it at
  the QR codes for following the account and adding the WeChat. All four
  languages.

### Changed (unit search filters fold away)

- The filters on the unit search page are now headings that open and
  close, with + and − on the right. Year and campus start open, the rest
  start closed unless a filter in them is set, so every heading fits on one
  screen. The panel scrolls on its own beside the results.
- Options are checkboxes with the number of units each one leaves, worked
  out with the other filters applied. Long lists show the six biggest
  values first and hide the rest behind "Show more". School and subject
  lists have a box to type into.
- New Faculty and School or department filters, from the Faculty and
  Organisational unit fields the Handbook already gives every unit.
- Several values can be ticked in one filter, such as Malaysia and
  Clayton, and mean any of them. Links with a single value still work.
- On a phone the filters open in a drawer from the side, with a button at
  the bottom to see the results.
- New `/api/v1/units/facets` endpoint for the counts. `/units/filters`
  now also lists faculties and schools, biggest first.

### Changed (degree type links in two rows)

- The type links above the degree panels are a grid of five equal columns.
  The first row holds the undergraduate types (specialist, comprehensive,
  double, Honours, diploma) and the second the vertical double degrees and
  postgraduate types, so ten types make two even rows. Each count sits in a
  pill on the right. Phones keep the single sideways-scrolling row.

### Changed (tools on the first screen of the home page)

- The eight tools (units, guides, unit tree, course map, degrees, WAM/GPA,
  community, 马莫百科) move from further down the page to under the search
  box, as two columns of tiles with an icon and one line each. A first
  visit sees what the site does without scrolling past the key dates.
- On a phone they are a four-across grid of icons under the search box.
- The old "Start here" section further down is removed, so they are not
  listed twice. The one-line descriptions now exist in all four languages.

### Added (Ask button on every page)

- An Ask button in the bottom right corner opens a chat panel. Questions
  go to the same zero-AI router as the search page, so answers still come
  from the Handbook, the FAQ, official pages and student posts, each with
  its source. No model and no API key.
- On a unit page the unit is filled in, so "有期末考试吗" is about that unit.
- Answers also point at the site's own tools when a question names one
  (WAM 怎么算 shows the calculator, "plan my units" shows the course map)
  and at matching 马莫百科 posts. When nothing matches, the panel says so
  and links to the community and AskMira.
- Full screen on phones, above the tab bar and the calculator's summary
  bar otherwise. Hidden on /search, which already does the same thing.
  All four languages.

### Changed (Honours degrees on the left)

- On the degree page the one-year Honours panel moves to the left column,
  under the undergraduate double degrees, with the vertical double degrees
  and diplomas after it. The right column was much longer than the left.

### Changed (search understands more of what students type)

- Traditional Chinese and full-width input are folded to Simplified and
  ASCII before anything else, so 簽證, 學費 and ＦＩＴ２００４ find what
  签证, 学费 and FIT2004 find. 12 of 180 test queries found nothing at all
  before; one does now (雅思, which no stored page mentions).
- English slang and abbreviations are searched in Monash's words as well:
  supp exam and resit reach Supplementary assessments, drop reaches
  withdraw, RPL reaches credit, comp sci and CS reach Computer Science,
  master of IT reaches Master of Information Technology, honors and MBA
  work. The query as typed is always searched too.
- Admin questions (学费, 毕业, how to enroll, census date) no longer list
  units and degrees. 毕业 listed 258 units and 83 Graduate Certificates.
- 毕业 means graduation, not "graduate": it leads with Graduations. The
  Chinese table has more campus words (毕业证, 在读证明, 续签, 缓考, 成绩复查,
  开学, 退费) and common unit topics (数据结构, 操作系统, 机器学习 and others).
- Degrees: a single bachelor comes before double degrees and graduate
  certificates unless a level is asked for. "computer science" listed two
  double degrees first. "double degree" and "honors" found nothing.
- Units: a title that says the query comes first, first year before
  honours and research units. "psychology" led with three PSY4xxx units.
  "accounting" no longer counts "IT account" as a match.
- Official pages: a page called what was asked comes first, then pages
  with the typed words as whole words. "supp exam" led with the eExam pages.
- 在读证明 no longer answers with the special consideration documents FAQ.
- Two-letter Chinese unit searches skip a trigram scan that never matched
  and took about a second.

### Changed (WAM/GPA calculator layout)

- The calculator now looks like the course map: units on the left, grouped
  by level with each level's weight and average, and a summary panel on the
  right with the WAM in a ring, the GPA or CGPA, a grade mix bar and the
  "what do I need" box. Each grade shows as a coloured tag, and clicking it
  sets a grade by hand (WN, SFR and so on).
- One add line at the bottom replaces the four empty rows. It looks the unit
  up in the Handbook first, so the row lands in the right level straight away.
- "Paste from WES" and "Read a screenshot" are under one Import button. The
  campus scale is a two-button switch. Removing a unit or clearing the list can
  be undone.
- On a phone each unit is a small card, and a bar above the tab bar shows the
  WAM, GPA and credit points while the summary is off screen.
- The calculation and the saved data are unchanged. Empty rows saved by the
  old page are dropped when it loads.
### Changed (degree list layout)

- The degree page groups degrees into panels by type, two columns on a wide
  screen: undergraduate types on the left, postgraduate and Honours on the
  right. Each panel shows six degrees and scrolls inside itself, so the whole
  list fits on about one screen instead of one long column.
- A row of type links with counts sits above the panels and jumps to a type,
  reopening the panel if it was folded. Panels fold from their header.
- On a phone the panels stack in one column, the type links scroll sideways,
  and each panel is shorter.
- The search box, campus and Handbook year controls are all 44px high. On a
  phone the campus and year selects split one row evenly.

### Changed (header controls)

- The search box in the header is one soft pill with the search button
  inside it, and the whole pill gets the focus ring.
- Language and account share one tray on the right. The language picker has
  a globe and a caret instead of a bordered box, sign in is a raised chip,
  and once signed in the tray holds the bell, your avatar and name, and an
  icon to sign out. Phones hide the sign out icon, which is also on the
  profile page.

### Changed (tab titles)

- Every browser tab reads "Page | Monash Hub", for example "选课规划 | Monash
  Hub", so a row of open tabs still shows which site each one is. The suffix
  comes from one title template in `app.vue`; pages set only their own name.
  The old " — Monash Hub" endings on some pages are gone, the unit tree page
  and the error page now have a title, and the home page reads
  "Monash Hub | Handbook, official guides and student community".

### Fixed (some part headings still had a full stop)

- Course translations the crawler stored before the change still read
  "B 部分。核心课程", so some degrees showed both separators. Stored strings
  that start with a part heading are now read with the colon.

### Fixed (course map Handbook year)

- The add-a-unit dialog on the course map searches the Handbook of the year
  the slot is in. It used to search the site's current Handbook, 2027 since
  October 2026, so a 2026 slot could not find FIT1058, which is taught in 2026
  but not listed in 2027. A year with no Handbook loaded uses the latest one
  before it, the same rule the plan check uses, and the hint names the year.
- The degree picker and the "against your degree" bars read the Handbook of
  the plan's start year, the course version the student enrolled in.

### Changed (plainer interface copy)

- Page intros, empty states, notices and error text in all four locales are
  shorter and plainer. Nothing uses a dash as punctuation any more, and the
  wording no longer leans on slogans. Meaning and behaviour are unchanged.
- Chinese degree part titles read "A 部分：基础课程" instead of
  "A 部分。基础课程", in `structure_zh.py` and in the composed labels. The
  seed on deploy writes the new wording.
- The course map status pill says "还没有课程" / "No units yet" without a full
  stop, and the notification panel no longer joins its two lines with a dash.

### Added (student ratings of units)

- Each unit page has a Student ratings section, labelled as community content:
  the average out of 5, how many students gave each score, and averages for
  teaching, content and assessment, plus difficulty and workload on their own
  scale. Below it are the reviews, sortable by newest, highest or lowest.
- Anyone can rate, signed in or not. One rating per account or per browser
  for each unit, and rating again edits it. A signed-out rating belongs to a
  random key the browser keeps, stored only as a keyed hash, and signed-out
  saves are limited per network address.
- Ratings can be reported and hidden like posts, and the moderation queue
  labels them. A hidden rating leaves the average but its author still sees it.
- The unit header shows the average next to the Handbook chips, unit cards in
  search show it too, and "Is it hard?" quotes the students' difficulty score.
- New table `unit_reviews` (migration `e7b3c5a19f42`). `GET /v1/units` results
  carry `rating`, and the sign-in page returns to the page in `?next=`.

### Changed (unit search)

- Results come in pages of 24 with numbered pages, and the page number is in
  the URL, so a filtered search can be shared and Back returns to the same
  page. A new search or filter starts again from page 1.
- Active filters show as chips above the results, each removable on its own.
- Campus, level and exam are one-tap pills instead of dropdowns, and there is
  a new subject filter (FIT, MAT and so on) from the existing `prefix` option.
- Sort sits next to the result count, and a list view shows one unit per row
  for scanning codes, with the student rating when a unit has one. The
  choice of view is remembered in the browser.

### Added (graduation)

- A curated answer to "Do I still need to apply to graduate?" in English and
  Chinese. It covers Monash's notice that from December 2026 awards are
  conferred automatically each month, testamurs follow shortly after and
  graduating in absentia ends, and points Malaysia campus students to their own
  pages, which still describe applying. Questions such as 还需要申请毕业吗,
  怎么申请毕业, 自动授予学位, "apply to graduate" and "testamur" now get it.
- A reviewed Chinese translation of the notice on the Graduations guide, which
  was shown in machine translation. The notice uses curly apostrophes, so the
  keys do too.

### Added (more than one course plan)

- A browser can keep up to 20 plans. `/plans` lists them as cards: the
  plan's name (editable in place), degree, credit points against the degree,
  problems, last updated, and a small grid of its semesters and unit codes.
  Each card can be opened on the map, duplicated, deleted (after a prompt) or
  exported to CSV.
- The course map shows the plan's name at the top, editable, with a link to
  all plans. Importing a JSON plan adds it as a new plan instead of replacing
  the one on screen.
- "Plan this degree" starts a new plan when the open one already has units
  for a different degree.
- Plans are stored under `mh_plans_v1`. A plan saved under the old
  `mh_plan_v1` key becomes the first plan; the old key is left in place.

### Fixed (the fee band said "Band SCA Band 2")

- The live Handbook labels the band "SCA Band 2", not "Band 2" as the fixture
  had it, so the parser kept the whole label and the unit page put its own
  "Band" in front. The parser now strips "SCA" as well, and migration
  `a3d7e2b95c41` cleans the rows the first crawl already wrote.

### Changed (马莫百科 page)

- Added the 2026-10-17 post on automatic monthly conferral, so all seven posts
  on the account are listed.
- The page opens with the account, its stats and a follow box with two QR
  codes: the 马莫百科 WeChat (MonashGuide) for the group chat, and the official
  account. Each has a copy button for readers already on their phone.
- The newest post is shown large with its cover, and the rest sit in a grid of
  cover cards that can be filtered by topic. Covers are the account's own,
  resized into `frontend/public/img/mamo/`.

### Changed (the course map is laid out like a map)

- Each year is a dark bar and each teaching period a row: the period's name,
  unit count and credit points on the left, the units across as cards. Empty
  slots up to a four-unit load are drawn so a row reads as a semester.
- A card shows the code, the Handbook title, credit points and which part of
  the degree it counts towards, as a coloured stripe and a letter that match
  the bars in the side panel. Problems are written inside the card.
- The side panel opens with a ring of credit points against the degree, with
  counts of units, problems and things worth a look.
- Campus, degree and start year sit at the top of the map with a pill that
  says whether the plan has problems. The toolbar is icons with labels.

### Added (moving units, undo, CSV, print)

- Drag a card to another teaching period, or use its move menu, a native
  select that works with a keyboard and on a phone.
- Undo and redo, from the toolbar or Ctrl/Cmd+Z and Shift+Ctrl/Cmd+Z, for the
  last 50 changes in this visit. Clear asks first.
- CSV export (year, period, code, title, credit points, part, issues) and a
  print layout that keeps each year on one page and drops the site chrome.
- "Saved on this device" under the map, and a "Plan this degree" button on
  degree pages that opens the map with that degree and campus picked.
- `POST /v1/plan/check` returns `unit_titles`, the Handbook title of every
  unit it found.

### Changed (the unit page reads faster)

- The header opens with four facts: credit points, when the unit is taught at
  the reader's campus, whether the Handbook lists an exam and how many items,
  and level.
- Every section has an icon, and the contents on the right follow the scroll.
- Assessment is a bar of how the marks are split, with each item, its type
  and any hurdle underneath, instead of a five-column table.
- Offerings are grouped by teaching period, with the reader's campus first and
  shaded. Workload shows the expected study time and each activity as tiles.

### Added (reading lists, where a unit fits, common questions)

- The parser keeps `learning_resources_grouped`, `highest_sca_band` and
  `study_abroad_unit`. A reading list keeps its links; a yes/no field the
  Handbook leaves out stays unknown. The new columns change every unit's
  content hash, so the next crawl rewrites each unit once.
- `GET /v1/units/{code}` returns `areas`: the majors, minors and
  specialisations whose curriculum lists the unit, and which part of it.
- New unit page sections: Learning resources, Where it fits (cards linking to
  each area of study), Common questions and More details (SCA band, study
  abroad, Handbook years). Common questions are written from the fields on the
  page, "is it hard" included: Monash Hub says it does not rate units and
  points to the workload and to Community. The same answers go out as
  FAQPage structured data.

### Changed (see a unit before adding it to the course map)

- "Add unit" on `/plan` opens a dialog instead of an inline list. Results are
  tagged S1, S2 and so on at the plan's campus, and picking one shows its
  overview, offerings by teaching period and requisites, with a line at the top
  saying whether it fits the semester you opened. That line comes from the
  same `/plan/check` the map runs, with the unit added, so the two always
  agree. Arrow keys move through the results, Enter adds, Esc closes, and the
  dialog stays open after adding so the next unit can be searched straight away.
- Unit search results carry each offering's untranslated campus and period and
  a short period label. "Semester 1" and "Semester 2" now shorten to S1 and S2
  the same way "First semester" and "Second semester" do.
### Added (what comes after a unit)

- `GET /v1/units/{code}/unlocks` lists the units that name a unit as a
  prerequisite or corequisite, each with the campus mark the tree uses, and
  how many units the whole downstream walk reaches. Withdrawn units and
  prohibitions are not counted.
- The requisites section on a unit page is split into Before and After. After
  shows the first eight units, the rest behind Show more, and links to the
  graph. The same list sits under the graph on `/tree`, whose zoom buttons now
  sit on the canvas instead of the section so the list does not move them.

### Fixed (asking about "this unit" on a unit page)

- The ask box on a unit page sent only the text, so "How good is this unit?"
  reached the router with no code and fell through to the official pages
  search. The page now sends its unit code and Handbook year; the router uses
  them only when the question names no unit, and a policy question asked on a
  unit page still gets the policy answer.

### Docs (crawling policy matches the fetcher)

- `docs/CRAWLING.md` now says who the crawler is (`MonashHubBot`), how
  `robots.txt` is read, and that a 429 waits for `Retry-After` on the same
  transport instead of switching to the browser. The four READMEs say the same
  in one line under the privacy boundary.

### Changed (what gets deployed is what CI tested)

- The deploy workflow passed nothing to the VPS, and the script reset the
  checkout to `origin/main`, so a push that landed between CI finishing and
  the SSH session opening went live untested. The workflow now passes the CI
  run's `head_sha`; `deploy.sh` checks that commit out (it also reads it from
  `SSH_ORIGINAL_COMMAND`, for the forced-command setup), refuses a commit
  that is not on `origin/main`, and re-executes the copy of itself that came
  with the commit rather than reading the rest of a file it just replaced.
- The images that were running are tagged `:previous` before the build, and
  if the new API never reports healthy they are put back before the script
  fails. The database keeps the release's migrations; the backup taken at the
  start is for the rest.
- The MTH2051 and FIT1055 refresh-and-assert steps, and the launch of the
  2026 requisite audit, are out of `deploy.sh` and `deploy.yml` and into
  `deployment/verify-handbook-parser.sh`. They were one-off repairs that made
  every deploy depend on the Handbook answering and on two units looking a
  particular way; the parser's unit tests cover both bugs.

### Changed (the crawler says who it is, and the unofficial engine is gone)

- The official-page fetcher sent a Chrome User-Agent and never read
  `robots.txt`. It now sends the same `MonashHubBot` name the Handbook fetcher
  always did, on the HTTP client and in the browser engine alike, reads each
  host's `robots.txt` once and does not fetch what it disallows (recorded in
  `crawl_history` as such). A 429 no longer flips the transport: it means
  slower, so the fetcher waits for `Retry-After` and tries the same way. An
  explicit `--transport httpx` is kept whatever the server says; only `auto`
  moves to the browser, and only on a 403.
- `--engine google`, the unofficial `translate_a/single` web endpoint with no
  key and no terms, is removed. `google-cloud` (keyed, billed) and `llm`
  remain. `Blocked` and the failure cap live in `crawler/translate/errors.py`
  rather than being imported from the Google module by the LLM one.
- A crawl whose failure was the database's own (a refused flush) could not
  mark its job failed: the handler committed without rolling back and raised
  `PendingRollbackError` over the real error. The job wrapper rolls back
  first, and the unit crawl skips a unit the schema refuses the way the
  course crawl already did, instead of ending the run.
- `.dockerignore` excludes `.env` files, so a local one cannot be copied into
  an image. A duplicate `_stored_strings` in the translation runner is gone.

### Changed (the frontend checks itself)

- `npm run typecheck` exists and runs in CI, with `vue-tsc`, `typescript` and
  `@types/node` as dev dependencies. It found fifteen errors: `error.generic`
  defined twice in every locale (the second definition won, so the error page
  and the action failures shared one sentence; the page's is `error.pageBroken`
  now), `avatar_url` missing from `SessionUser`, a return type in `apiFetch`,
  an index that could be undefined in the tree layout, and `process` without
  Node types. `npm test` runs Vitest over the pure utilities, starting with
  the password policy and the API error mapping.
- Three async handlers had `try/finally` and no `catch`, so a failed unit
  search, plan check or question left the reader with nothing and the console
  with an unhandled rejection. They say what went wrong now, as the profile
  page already did, and the notification panel does too.
- Storage is read through one `readToken()` that survives a browser with site
  data blocked, where every page that fetched used to throw. The token key is
  defined once.
- A unit, guide, degree, area of study or post the API does not have renders
  the same error card, but the response is now a 404 (and a 503 when the API
  is down) instead of a 200 with a canonical link, so search engines stop
  indexing pages for things that do not exist.
- An imported or stored plan is taken field by field: years are clamped to
  ten, periods must be a list of strings, entries must have a code, a year and
  a period. `years: 1e9` in a hand-edited export used to freeze the tab.
- The sitemap escapes what it puts in XML, and answers 503 rather than caching
  a half-walked list for an hour when the API fails part way.
- Smaller: unit codes typed on the marks page are URL-encoded; the plan and
  degrees page titles follow the language switch; the error page sits inside
  the layout; the home page's three fetches run together; ten translation
  keys nothing read are gone; a no-op `definePageMeta` is gone.

### Fixed (the forum's state machine at its edges, and what a guess costs)

- A hidden post's replies were still readable through the answers endpoint,
  which only checked the replies' own visibility. Accepting a nested reply
  marked the post solved without marking anything accepted, and is now
  refused; accepting a second answer clears the first wherever it sits. A
  reply its author deleted left the answer count once, and left it again when
  a moderator hid it. A moderator deleting someone else's post stamped it as
  author-deleted, so it could never be unhidden; a moderator's takedown is now
  a hide. Replies had no depth limit, and the thread loader and serialiser
  recurse, so a long enough chain was a thread nobody could open: past five
  levels a reply goes under the deepest ancestor with room. Marking an empty
  list of notifications read marked all of them.
- Password reset checks the code once before the nickname rule and once to
  spend it, and both counted as attempts, so the right code on the last
  allowed attempt passed the first check and was refused, uncaught, by the
  second. The attempt is now taken by one UPDATE that also enforces the cap,
  a check that only looks does not spend it, and the second call is caught.
  A verification email the provider failed to send no longer counts against
  the resend interval, so "try again shortly" is not answered with 429.
- Sign-in, code and report limits now take a transaction-level advisory lock
  on the key, so guesses arriving together queue instead of all passing the
  same count. `X-Real-IP` is believed only from `TRUSTED_PROXIES` when that
  is set.
- Avatars: a decompression bomb is refused as a bad image rather than a 503,
  the pixel cap is 16 million, phone photos follow their EXIF rotation, and
  transparency lands on white instead of black.
- Official-page links are resolved against the page they came from and kept
  only when they are web addresses, so a relative link no longer points at
  the Hub's own domain and `JavaScript:` in any spelling is dropped.

### Changed (docs say what the code does; reads are rate limited too)

- The README's privacy wording matched an earlier version of the code. A plan
  is still stored only in the browser, but each check sends it to the API to
  be compared with the Handbook; marks stay on the device, but the unit codes
  are looked up through the API. All four READMEs now say exactly that. The
  Chinese, Japanese and Korean READMEs carry the same badge strip as the
  English one, with a live CI badge, and the Japanese and Korean ones gained
  the technology stack, source boundary and licence sections the English one
  already had.
- `docs/ROADMAP-STATUS.md` said the course planner and anything involving a
  language model were explicitly not now, while both have shipped (the model
  only translates and never answers a reader). `docs/CRAWLING.md` still described the 20-unit,
  40-page seed. Both match the repository again.
- nginx: `/api/v1/community/posts`, `/api/v1/auth/` and the avatar upload are
  more specific than `/api/`, and the write zone does not count GET, so reads
  of those paths were not limited at all. They now carry the per-address API
  zone as well.

### Changed (light footer)

- The footer is a light grey surface with a rule above it instead of a deep
  navy block. It was the only dark surface on the site, and on a short page it
  was as tall as the content and outweighed it. Text, headings and links use
  the page's own ink and muted colours, links turn brand blue on hover, and the
  WeChat line keeps its accent bar in brand blue. The disclaimer is unchanged.
  The logo's `onDeep` tone, which only the dark footer used, is gone.

### Added (`/ask` names the guide page of an FAQ answer)

- An `official_faq` answer now carries `page_slug`, the official page the FAQ
  comes from. That page's guide (`/guides/{slug}`) shows the FAQ with the
  whole page, so a client outside the site, such as the WeChat bot, can send
  the reader there instead of only to the English original. `null` when the
  FAQ has no indexed page.

### Fixed (official-page search order: tags and past years)

- Among the pages a query is *about*, the order was decided by text rank, so a
  page that merely said the words in its summary could beat the page curated
  for them: 转专业 led with "Current Students - Pharmacy" instead of "Internal
  Course Transfer", 心理咨询 with one counsellor's profile instead of the
  counselling service. A page whose curated tag the query names now comes next
  after the title match. Pages whose title names a past year ("Principal dates
  (2022)") go after current ones, so 考试时间表 no longer opens on the 2022
  calendar. Checked read-only against the live index on 30 common queries:
  挂科, 抄袭, 学生准证, 医保, 退课 and 选课 also lead with the page for them now;
  none got worse.

### Added (faculty teach-out notices for closing units)

- The Faculty of IT's table of closing, renamed and changing units and the
  approved replacement for each (monash.edu/it ... /re-enrolment/undergraduate)
  is now an indexed official page, re-checked on the dynamic tier. A unit in it
  shows the faculty's notice at the top of its page, word for word with the
  page and when it was last checked, and a tag on its line in a degree ("Final
  offering S2 2027", "No longer offered", "Renamed"). Nothing is worked out by
  the site: no row, no notice, and the notice tells the reader to confirm with
  their faculty that it applies to their campus and intake year.
  `app/knowledge/teach_out.py` reads the tables from the stored page, so another
  faculty is one more page listed in `SOURCES` and in the seed list.

### Fixed (English left on degree pages; which Handbook to read)

- Degree and area-of-study pages listed double-degree parts ("Bachelor of
  Business"), majors, minors, specialisations and honours under the English the
  structure printed, although each has a page with a reviewed Chinese title
  (~245 distinct names in the live catalogue). A line now borrows the title of
  its own page; one whose page is not loaded stays in English rather than
  guessed. 13 area-of-study titles and 16 dropped units that no loaded year has
  (Artificial intelligence, Strategic marketing, Business environment, Arts study
  abroad and others) were added to the reviewed structure table.
- Degree pages, area-of-study pages and the unit tree carry a note: the {year}
  Handbook is for students starting in {year}; earlier intakes follow the
  Handbook of their own year (use the year picker). Where a unit is not listed it
  adds that replacements apply once a unit closes, that the faculty is expected to
  email which unit replaces which, and that faculty staff can be asked. The site
  names no replacement itself.

### Fixed (degree lines for units the year no longer lists keep their name)

- A degree that still names a unit the Handbook has dropped (or not yet added)
  showed that line in the English the degree page printed, e.g. ENG1005 and
  BEX3730 under a 2027 degree. The line stays tagged "not in this year", but its
  title now comes from the same code in the nearest other Handbook year (newer
  first on a tie), with that year's reviewed Chinese. Nothing else is borrowed:
  credit points, offerings and campus availability still say "not offered".
- "Not in this year" / 本年度未开设 named no year, and while 2026 is running a
  reader of the 2027 Handbook could take it to mean the unit is gone now. The tag
  on degree and area-of-study lines and the missing-unit wording in the unit tree
  now name the Handbook year ("Not in the 2027 Handbook" / 2027 Handbook 未列出),
  and say "not listed" rather than "not offered": the Handbook not listing a unit
  can also mean it was renumbered.
- A degree line for a unit the year does not list now offers the years that do:
  "Open in 2026 · 2025" beside it, each opening the unit in that Handbook. The
  line itself opens the latest year that has the unit (a year in the address is
  strict and would 404).

### Fixed (Chinese degree structure that was still English)

- Every degree and area of study in the 2026 and 2027 Handbooks was checked
  against the live Chinese pages. 174 rule paragraphs, notes and part titles
  (B2026 and its double degrees, Peninsula business degrees, accounting
  accreditation notes, computer science parts, nursing and health units,
  earth science options and the shared "Core units" / "Capstone units" style
  headings) had no wording and showed in English. They are now in the
  reviewed structure table.
- Guides: 56 sentences and 3 titles that were still English are translated
  (Malaysia re-enrolment, restricted transfer period, double degree pathway
  and others).
- A translation that is the model echoing its own prompt
  (`GLOSSARY: ... TEXT: Next`) is no longer shown: the translator rejects it,
  and the reader side ignores any already stored.
- Unit pages: activity durations read `24 小时` instead of `24 hours`; the
  assessment types Work integrated and Assignment have wording; assessment
  names and descriptions use the unit's translated strings where there are any.
- A unit listed in a degree or area of study whose item had no translation of
  its own now uses the translated title of the unit itself, so a new Handbook
  year no longer lists every unit in English beside a Chinese unit page.

### Changed (home page redesign: key dates, one voice, no template look)

- The home page leads with a **Key dates** card for the student's campus
  (Malaysia / Australia switch, remembered in a cookie): census and withdrawal
  deadlines, end of teaching, swot vac, exams, results and public holidays,
  soonest first, each with its source page and when it was last checked.
  `GET /v1/key-dates` reads the census, final-assessment and principal-dates
  tables already in the index; nothing new is crawled. A Sunday holiday and its
  Monday replacement are one item. Anything that does not parse is left out.
- "Units in the index" (which showed the first eight codes alphabetically, all
  ACB accounting) is now **Units across the faculties**: one example unit per
  faculty, a different list for Malaysia and Australia because Business is
  ACW/MKW at Malaysia and ACC/MKC at Clayton, each with every campus it runs
  at. `GET /v1/units?codes=` and `GET /v1/guides?slugs=` return hand-picked
  lists in the order given.
- The three entry cards and five tool tiles are one ruled **Start here**
  index of all eight tools, each with a line saying what it does. The footer
  (project, credits, disclaimer, official sources, Monash and Malaysia systems,
  WeChat note) is unchanged apart from colour.
- Palette: the Tailwind slate/blue defaults are gone. One blue (the Monash
  blue) for links and the mark, ink for primary buttons, greys leaning toward
  the brand. Header is white with a hairline instead of a solid blue bar.
- Type: Source Serif 4 / Noto Serif SC for page and section headings, IBM Plex
  Sans for text, IBM Plex Mono for unit codes and dates.

### Changed (Student Pass is 学生签证; pages keep the seed list's title)

- Monash Malaysia's Student Pass is now 学生签证（Student Pass） everywhere - the
  glossary, the hand-written guide and FAQ Chinese, the campus notice - and a
  polish rule rewrites 学生准证 in stored machine translations. That is what
  the students who hold one call it. 特别准证 (the Special Pass) is unchanged.
  学生签证 now also finds Malaysia's Student Pass pages; a campus in the
  question picks between the two countries' documents.
- A page is called what the seed list calls it, not what the fetched page
  calls itself: Monash Malaysia's student pass page titles itself "Before You
  Arrive", and "student pass" did not find it. The original title stays in the
  page's version history.
- A guide title's "(Monash Malaysia)" is put back as 「（马来西亚校区）」 after the
  rest is translated, never sent to the model: it returned 费用支付方式（Monash
  Malaysia（马来西亚校区）） and, once, 常见问题解答（新国际学生（Monash Malaysia
  （马来西亚校区））学生）. Stored titles translated that way are found and redone.
- A Chinese query ranks by the Chinese title: 学生签证 puts 学生签证（Student Pass）
  ahead of the PASS study-group page its English expansion also reaches.
- Among the pages a query is about, one whose title contains the whole query
  comes first: "student pass" now leads with Student Pass (Monash Malaysia), not
  "After Your Studies", which only mentions it.
- No two guides share a title any more. A heading that says nothing on its own
  ("Eligibility" x5, "WHAT YOU SHOULD KNOW" x4, "IMPORTANT", "FAQs") gets its
  section - "Eligibility - OS-HELP Loans", "What you should know - School of IT
  (International Exchange, undergraduate)" - and a title two pages share gets
  the same treatment (`coverage.disambiguate`). Research-supervisor profile
  pages and one-off career events are left out: people and dates, not guidance.
- The official translation pass translates only the strings a page has never
  had - a renamed title - when its English is otherwise unchanged, instead of
  skipping it or sending the whole page to the model again.
  中文：Student Pass 的中文统一为「学生签证」；页面标题以我们定的为准（马莫
  Student Pass 页不再叫 Before You Arrive），改名后只补译标题。

### Fixed (search: a campus in the question)

- Search now reads a campus in the question. 马莫, 大马, 马来西亚, 吉隆坡, Monash
  Malaysia (and 澳莫, 澳洲, Clayton, Melbourne) are taken out of the query and
  narrow it to that campus's pages and the all-campus ones, falling back to every
  page only when that finds nothing; both campuses named narrow nothing. Words
  only one campus has - 学生准证, Student Pass, EMGS, JomPAY / OSHC, HECS, CSP -
  point the search at it without being removed. Before: 马莫怎么交学费 listed
  Australian fee pages, 学生准证续签 led with the Australian visa page, and
  转校区 马来西亚 澳洲 found Malaysia's calendars. Synonyms for 转校区, 换校区,
  转校, 交费 and payment methods; 马莫 and 澳莫 alone search for the campus.
  中文：搜索能识别「马莫」「澳莫」等校区说法，优先显示对应校区和全校通用的页面。

### Fixed (translation: a content-filter refusal no longer stops the pass)

- Zhipu answers a sentence its content filter refuses with HTTP 400, code 1301.
  The LLM engine treated that like an outage - four retries, then a count
  toward "eight failures in a row, stop the run" - so a handful of sentences
  on one sexual-health page ended the official-pages pass twice and left the
  fifteen pages after it untranslated. A refusal now fails that sentence once
  (it stays in English) and the run goes on; other 400s are still retried.
  中文：智谱内容审核拒绝某句时，只让这一句保留英文，不再连带中止整轮翻译。

### Added (choose the Handbook year, like handbook.monash.edu)

- Students still studying commenced in 2025 or 2026, and a unit's rules,
  offerings and assessment are the ones of the year they took it. The unit
  and degree lists, unit, degree and area-of-study pages, and the prerequisite
  graph now have a year picker (2025, 2026 and 2027 once 2025 is loaded). The
  default stays the newest Handbook. A detail page only offers the years that
  list the code, so the picker never leads to "not found".
- The chosen year travels in `?year=` and every unit, degree and
  area-of-study link on the page keeps it, so following a 2025 unit's
  prerequisites stays in 2025. Changing campus no longer drops it.
- API: unit, degree, area-of-study and graph responses carry
  `available_years`; `/courses/filters` returns `years` and `academic_year`.
### Fixed (loading another Handbook year now gets its English translated)

- A unit's translation was stamped with its newest year's English only, so a
  unit already translated for 2026 and 2027 was skipped when the 2025 Handbook
  was loaded, and every sentence 2025 worded differently would have stayed
  English. A unit in several years is now stamped with a digest of all of
  them (`years_marker`), so adding a year makes it due once.
- Each pass first loads the translations already stored for a unit, degree or
  area of study into the translator (`Translator.prime`), so only sentences
  nobody has translated yet go to the model - re-visiting the 10,000 units
  already done costs no Zhipu calls. Reviewed labels in `structure_zh` still
  win over a stored machine string. This also ends the degrees' years taking
  turns at looking out of date and being re-sent every run.

### Fixed (the course planner checks each unit against the Handbook of the year it is placed in)

- The planner checked a whole plan against the current Handbook. Once the site
  moved to 2027, a plan with FIT1058 and FIT1043 in 2026 second semester -
  exactly what Monash taught in 2026 - reported FIT1058 as "not in this
  Handbook year" (it is gone from 2027) and FIT1043 as not taught that
  semester (2027 runs it in first semester only). Each unit is now read from
  the Handbook of its calendar year; a year with none loaded uses the latest
  one before it (2028 reads 2027) or the earliest loaded. The response lists
  which Handbook each year was checked against, and "not in the Handbook" now
  names the year.
- The prerequisite graph opens on FIT2086 (in both the 2026 and 2027
  Handbooks, taught at Malaysia, 10 units upstream and 57 downstream) instead
  of FIT2004, which the 2027 Handbook dropped. The unit-code examples in the
  placeholders and error messages follow.
### Fixed (deploys failed on a moved official page)

- Monash moved "Travel health, safety and security" from
  `study-abroad/overseas/...` to `study-abroad/outbound/...`, and the coverage
  rebuild (#127) kept its slug. Registering seeds matched pages by URL only, so
  it inserted a second row with the same slug and hit the unique constraint;
  every deploy since #128 stopped there, leaving production on an older build.
  A seed that matches no URL but an existing slug now moves that row to the new
  address (keeping its translations) and is fetched from there on the next
  refresh. Checked against production: it is the only seed whose address moved.

### Fixed (a unit dropped from next year's Handbook no longer reads "not found")

- With the site on the 2027 Handbook, every unit Monash renumbered or withdrew
  for 2027 - FIT2004 and FIT1008 among them, still in 2026 and still being
  taught - answered 404, and the prerequisite graph, which opens on FIT2004,
  showed "加载失败 / not found" by default. Without `?year=`, a unit, degree or
  area of study missing from the current Handbook is now read from the latest
  Handbook that lists it (`backend/app/handbook/years.py`), and the response
  carries `not_in_year`. The unit, degree, area-of-study and graph pages show
  a notice in all four languages naming both years, so nobody plans 2027
  around a 2026 page without knowing. An explicit `?year=` is still answered
  exactly, and a code in no Handbook is still a 404.

### Changed (official pages: campus from the page's own text; the tooling is in the repo)

- A monash.edu page is now labelled from what it says (`crawler/official/scope.py`):
  *All campuses* when it states it covers every campus, speaks to Malaysia
  alongside, or is a University-wide rule (assessment, academic integrity and
  misconduct, academic progress, complaints, the Handbook) with nothing
  Australian in it; *Australia* when it carries something only Australia has
  (HECS, CSP, OSHC, the subclass 500 visa, Home Affairs, Centrelink, TFN/USI) or
  sends Malaysia students elsewhere. Defaulting every monash.edu page to
  Australia told Malaysia students that rules binding them were not theirs.
  Graduation (one process for every campus - Malaysia students can also
  graduate at the Jakarta and Suzhou ceremonies) and results/WAM count as
  University-wide; New Colombo Plan pages are Australian whatever host country
  they list. Where the text misleads - Malaysia named only as a destination -
  `coverage.SCOPE_OVERRIDES` records the decision and why. Result: 391 Malaysia,
  52 all campuses, 258 Australia among the generated pages; in `seeds.py` the
  Engineering, Business and Arts course maps (they include Malaysia's) become
  all campuses, and Fees and Fee payment dates become Australia.
- The discovery walk and the filters that built `seeds_coverage.py` are now
  `crawler/official/discover.py` and `crawler/official/coverage.py` (rebuild:
  see the module docstrings), with tests. A rebuild keeps every registered
  page's slug. It adds Monash Malaysia's library, IT services and accommodation
  pages and the schools' remaining current-student pages, and leaves out
  staff-only pages and the Monash Online support page (it redirects to
  online.monash.edu, behind a Cloudflare bot challenge that refuses every fetch).
- Pages Monash keeps behind its Okta sign-in are now *listed, not copied*: a
  seed with `sign_in=` is never fetched; it is stored with its title, a
  description written here and its link, flagged `requires_sign_in`, and shown
  with a "sign-in required" notice instead of page text. The first two: the
  Faculty of Arts' course transfer page and Monash Malaysia's "Apply to
  graduate" (both looked blocked by the WAF; both redirect to Okta).
  中文：官方页面的校区改为按正文判定——写明适用所有校区、同时讲到马来西亚、或属于
  全校统一规章的标「全部校区」，含澳洲专属内容（HECS、OSHC、500 签证等）的才标
  「澳大利亚」；发现与筛选脚本正式入库；需要 Monash 登录的页面只列标题、简介和官方链接，
  标注「需登录」，不转载正文。

### Added (official pages: the whole student sites, Monash Malaysia first)

- 620 more official pages in `crawler/official/seeds_coverage.py`, found by
  walking www.monash.edu.my (student services, the schools' current-student
  pages, study abroad) and www.monash.edu (student admin, study success,
  support, study abroad, course and campus transfer) and kept where they carry
  real content. Left out: landing pages, duplicates, contact/login pages,
  application agents, and individual exchange programs and partner lists -
  those are monash-abroad-tracker's job; the Hub links to Monash's program
  search instead (Monash Global Campus programs in Prato are kept).
- Campus is tracked per page: monash.edu.my pages and monash.edu pages about
  Malaysia (its graduation ceremonies) are Malaysia; other monash.edu pages are
  Australia. The guides list gains a campus filter and "show more"; two new
  categories, Graduation and Student support & services.
- The official translation pass runs in seed order, so Monash Malaysia's pages
  are translated first.
  中文：新增 620 个官方页面（马莫优先：学生服务、各学院、毕业、缴费、学生准证、
  交换等；澳莫同步），按校区标注并可在官方指南页按校区筛选；交换只收政策与流程，
  不收各交换院校项目页。

### Added (official pages: hurdles, supplementary assessment, progress and appeals)

- 21 more official pages in the seed list, chosen for the rules that decide
  whether a student passes, progresses or graduates: hurdles (Monash's guidance
  on competency and threshold hurdles - threshold hurdles are removed from every
  unit by 31 December 2026, and a failed competency hurdle ends in NH 45),
  supplementary assessments, eExam rules and arrangements, results release and
  feedback, the assessment policy list, unsatisfactory-progress notices, APC
  hearings and decisions, exclusion appeals, academic misconduct (process,
  penalties, appeals), student complaints, the Handbook glossary, graduation
  eligibility and course completion. Three curated FAQ entries answer "what is a
  hurdle", "can I get a supplementary assessment" and "what does an
  unsatisfactory progress email mean", each tied to its page. The glossary pins
  threshold/competency hurdle, Hurdle Fail, additional assessment (额外考核, not
  补考), academic misconduct, APC, EAP and the Student Misconduct Panel.
  中文：新增 21 个官方页面（hurdle 及格门槛、补考、eExam 考试规则、成绩发布、学业
  进度预警与听证、退学申诉、学术不端、投诉、毕业资格等）和 3 条 FAQ，并在术语表里
  固定 hurdle 相关译法。

### Fixed (Chinese translations: the structure of a degree)

- The offline translator was rendering the words a degree page is built from
  differently in every sentence: *Breadth studies* as 面包研究 (bakery studies),
  *Robotics and mechatronics engineering* as 机器人和中程器工程 and, in other
  sentences of the same page, 中子医学, 中医药学 and 中杂技, *Curating* as 惩罚,
  a *stream* as 溪流 or 流, *Level 5 - Diploma*-style labels and "You will receive
  credit for ..." as a loan (贷款). `backend/app/knowledge/structure_zh.py` now
  holds one wording for each of the 2,600 distinct short labels and stock
  sentences that appear in the structure of a course or area of study (and in
  the Handbook's stock unit boilerplate); `structure.py` builds the next year's
  `Part X. <title>`, AQF level and `N words` labels from the same tables;
  `degrees.py` names 122 more disciplines fixed rather than left to the model
  (and separates *Pharmaceutical Science* 药物科学 from *Pharmacy* 药学,
  *Teaching* 教学 from *Education* 教育); the glossary pins mechatronics,
  curating, cervical/lumbar spine, microcredential and breadth study, and pins
  *stream* and *discipline* on the pages where they mean the academic sense.
  中文：修复学位结构页的中文翻译。此前离线翻译器对同一个词在每个句子里给出不同
  的错误答案，例如 Breadth studies 被译成“面包研究”，mechatronics 被译成“中程器、
  中子医学、中医药学、中杂技”，Curating 被译成“惩罚”，stream 被译成“溪流”。现在
  每个学位结构标签和 Handbook 通用句子都有固定译法。
- New provenance `curated`: wording that was written down and checked against the
  English but has not been read by anybody who reads Chinese. It beats the machine
  and is beaten by a human row, and a page that uses only it is still labelled
  machine translation - it is not called "checked".
  中文：新增 `curated` 来源等级：对照英文核对过、但未经中文母语者审阅的译文，优先于
  机器翻译、低于人工翻译，页面上仍标注为机器翻译，不会写成“已人工校对”。

### Added

- Added `--units CODE [CODE ...]` to `crawler.translate.run --targets units`, to
  re-translate specific units instead of a full-catalogue pass. This was
  missing when FIT1008 needed re-translating after Monash republished its
  Semester 2, 2026 description mid-cycle: the only way to pick it up was a
  full `--fields all --refresh` run, which takes 1.5-7 hours depending on the
  CPU cap and would have re-translated all ~5,200 units to fix one.
  中文：给 `crawler.translate.run --targets units` 增加了 `--units 课程代码...`
  参数，可以只针对指定课程重新翻译，不用跑全量。起因是 FIT1008 被 Monash 在
  学期中重新发布了 2026 年第二学期的课程简介，之前唯一的补救办法是跑一次全量
  的 `--fields all --refresh`，视 CPU 上限要花 1.5 到 7 小时，为了修一门课要
  把全部约5200门课重新翻译一遍。

### Fixed

- Fixed the question box missing a unit code written right up against
  Chinese text, e.g. `FIT2004有期末考试吗？` or `请问FIT2004…`. The unit-code
  pattern used `\b`, and Python's regex treats CJK characters as word
  characters, so there was no word boundary between `2004` and `有` and no code
  was found: `/api/v1/ask` fell back to an official-page search instead of the
  Handbook assessment answer it gives for `FIT2004 有期末考试吗？`. Both the
  search and the Handbook parser's unit-code patterns now use ASCII-only
  lookarounds, so `fit 2102`, `FIT-2102` and codes joined by `和` all work,
  and an 8-digit number still does not match.
  中文：修复了问答框识别不出紧贴中文的课程代码的问题，比如
  `FIT2004有期末考试吗？` 或 `请问FIT2004…`。课程代码的正则用的是 `\b`，
  而 Python 正则把中日韩文字也当作单词字符，所以 `2004` 和 `有` 之间没有
  单词边界，代码识别不到：`/api/v1/ask` 会退回到官方页面搜索，而不是像
  `FIT2004 有期末考试吗？` 那样给出 Handbook 考核信息。现在搜索和 Handbook
  解析器里的课程代码正则都改成只看 ASCII 字符的前后断言，`fit 2102`、
  `FIT-2102`、用 `和` 连起来的两个代码都能识别，8 位数字仍然不会被误认。
- Fixed a crash in `upsert_unit` when a unit's content reverts to a hash it
  had several versions ago - a Handbook edit undone, or a parser fix (like the
  FIT1055 one above) making today's output match an even older, correct
  crawl. It only compared the incoming hash against the unit's *current* one
  to decide whether anything changed, then unconditionally inserted a new
  `unit_versions` row - which collided with the unique `(unit_id,
  content_hash)` constraint whenever that exact hash had already been
  recorded further back in the unit's history, not just last time. Surfaced
  by the full-catalogue reparse this release's FIT1055 fix kicked off:
  `--fail-on-errors` meant one such unit (ADS1001) took the entire background
  pass down with it. The unit and its children still refresh normally; the
  redundant history row is now skipped instead of crashing.
  中文：修复了 `upsert_unit` 在课程内容"变回了历史上更早出现过的某个版本"时
  会崩溃的问题——比如 Monash 撤回了一次修改，或者是一次解析器修复（比如本次
  的 FIT1055 修复）让今天解析出的结果正好和更早、正确的某次抓取结果一致。
  原来的判断只拿新哈希和课程*当前*的哈希比较来决定"是否有变化"，然后无条件
  往 `unit_versions` 插一条新记录——只要这个哈希在这门课更早的历史里（不一
  定是上一次）出现过，就会撞上 `(unit_id, content_hash)` 的唯一约束而报错。
  这次 FIT1055 修复触发的全量重新解析就撞上了这个问题：`--fail-on-errors`
  下，ADS1001 这一门课踩中就把整个后台任务拖垮了。课程本身和它的子数据照常
  刷新，重复的历史记录现在会被跳过，而不是直接崩溃。
- Fixed the machine-translation coverage tracker (source hash + field scope,
  stored in each unit's `content_translations.note`) being silently wiped on
  every single deploy. The 2026-08-30 title-baseline import and
  `crawler.translate.run` share one machine row per unit - a unit gets exactly
  one machine translation, not one per producer - and the baseline seed step
  (which runs on every deploy, not just once) overwrote that row's `note` and
  `source_hash` with its own attribution regardless of whether a real
  `--fields all` translation already lived there. That told the coverage
  check every baseline-covered unit's translation had gone stale immediately
  after it was correctly done, which is why a routine `--fields all` run
  reported 0 units skipped instead of nearly all of them. Only a row the
  baseline itself creates now gets its attribution; a row `crawler.translate.run`
  already wrote keeps its coverage state and only gains the title string.
  中文：修复了每次部署都会悄悄清空翻译覆盖率追踪标记（源内容哈希+字段范围，
  存在每门课 `content_translations.note` 里）的问题。8月30日的课程名称基线
  导入和 `crawler.translate.run` 共用同一行机器翻译记录——一门课只有一条机器
  翻译，不是每个来源一条——而基线的种子步骤（每次部署都会跑，不是只跑一次）
  会无条件用自己的署名覆盖掉这一行的 `note` 和 `source_hash`，不管这一行是不
  是已经有一次真正的 `--fields all` 翻译。这会让覆盖率检查以为每门在基线里的
  课程翻译"刚做完就过期了"，也是为什么一次正常的 `--fields all` 运行会报告
  0 门课被跳过，而不是几乎全部跳过。现在只有基线自己新建的行才会打上它的署
  名；`crawler.translate.run` 已经写过的行会保留自己的覆盖率状态，只是新增
  这一个标题的翻译。
- Fixed a Handbook parser bug where units publishing their prerequisite and
  prohibition rules under `enrolment_rules` (rather than the structured
  `requisites` block) leaked CMS metadata into the rule text. FIT1055 was the
  reported case: its own unit code, plus raw `cl_id` identifiers and literal
  labels like `code` and `Enrolment Rule`, were being read as if they were
  part of the rule prose, which listed FIT1055 as prohibiting itself and
  broke study plans containing it. The parser now reads only the `description`
  field of each rule entry, and a defensive check strips any unit from its own
  requisite/prohibition groups regardless of source. This affects every unit
  whose rules are published in that shape, not just FIT1055.
  中文：修复先修图解析器的一个 bug——当课程的先修/互斥规则发布在
  `enrolment_rules` 字段（而非结构化的 `requisites` 字段）时，解析器会把
  CMS 元数据一并当作规则正文读入。以 FIT1055 为例：它自己的课程代码、原始
  `cl_id` 内部标识符，以及“code”“Enrolment Rule”这类字段标签，都被误当作
  规则文字的一部分，导致 FIT1055 被列为与自己互斥，选课规划里只要放入
  FIT1055 就会报错。现在解析器只读取每条规则的 `description` 字段，并新增
  一道防御性检查，无论数据来源如何都会把课程自身从其先修/互斥列表中剔除。
  这个问题影响所有采用该数据格式发布规则的课程，不只是 FIT1055。
- Gave the English header search field the space previously wasted by the
  oversized Search button, while preserving the full button label. Intermediate
  desktop widths now tighten their navigation spacing, and narrow tablets use
  the existing compact navigation instead of overflowing horizontally. Footer
  credits now distinguish the original concept by @Laceyxinx from the build
  and ongoing maintenance by @Waldo0926, with both GitHub profiles linked.
  中文：压缩英文页头“Search”按钮的多余留白，把空间还给搜索输入框；同时修复
  中等宽度桌面和平板的导航横向溢出。页脚新增清晰分行的署名，区分
  @Laceyxinx 提出的创意与 @Waldo0926 的搭建和持续维护，并链接双方 GitHub 主页。
- Moved Official Guides to the first navigation position beside the Monash Hub
  logo, ahead of Units, while retaining the clearer Chinese label `先修图` for
  the prerequisite and unlock graph. The footer now uses a deep brand navy
  instead of black, and its WeChat introduction spans the full row rather than
  wrapping into three lines inside the narrow first column.
  中文：将“官方指南”移到 Logo 旁并排在“课程”之前；关系图继续使用更准确的
  “先修图”。页脚由黑色改为品牌深蓝，微信公众号介绍改为横跨整行显示。
- Audited the rendered body structure of all 45 official guides and removed 98
  leaked interface controls across 10 affected pages. Nested-accordion buttons
  no longer append `View` / `Close` to real headings or appear as standalone
  paragraphs; hidden decision-tree actions such as `Go back`, placeholder text
  such as `No banners found`, and the duplicated topic selector on the course
  advice page are no longer presented as guide content. Existing reviewed
  Chinese heading translations are preserved under the cleaned English source
  keys, and the extractor version bump forces the next crawl to replace stored
  legacy blocks.
- Audited the Simplified-Chinese output of all 45 official guides, with
  page-specific human translations for policy labels, table cells and academic
  result terminology. This replaces misleading literal output such as `Yes` →
  `对`, `Pencil cases` → `笔会案件`, `First Class Honours` → `头等舱荣誉学位`,
  and weekday cells such as `Sat 01` → `卫星1号`; critical exam-rule sentences
  also retain their conditions and disciplinary consequences instead of being
  shortened into a different rule.
- Replaced the inconsistent unit-title output with a complete Simplified-Chinese
  baseline covering all 4,212 distinct titles in the 5,228-record 2026
  catalogue, so the Chinese interface no longer falls back to English names.
  The baseline remains explicitly machine-labelled and is overlaid by exact
  human-reviewed corrections, including `Accounting in business` → `商业会计`,
  `Assurance and audit services` → `鉴证与审计服务`, and high-risk curating,
  assurance, academic-literacy and communication terminology. Degree categories
  now use exact bilingual labels rather than renderings such as `大师研究型` and
  `PG主控制器`; changing the site language also reloads once so the selector
  and every navigation item cannot remain in different languages.
- Audited all 503 active degree records against their 2026 Handbook English
  titles and added 93 exact, human-reviewed Chinese title corrections, covering
  95 course codes. This fixes recurring errors such as *Business and Commerce*
  becoming 工商业, *Digital Media and Communication* becoming 数字媒体和通信,
  *Cardiovascular Perfusion* becoming 心血管输血, and *Aeromedical Retrieval*
  becoming 空中医疗检索, as well as broken partner names and Science Advanced
  subtitles. Curated seed rows now explicitly use human provenance, so they
  reliably override older machine translations and remain searchable.
- Chinese titles are searchable for units, degrees and official guides. The
  unified search did not include degrees at all, so a parent searching `理学学士`
  could not reach *Bachelor of Science*; translated unit and guide titles also
  depended on a separately refreshed index and exact title matches could sit
  below loosely related prose. Exact Chinese titles now rank first, the degree
  picker accepts Chinese too, and deploy/translation jobs refresh the longer
  Chinese content index automatically.
- Search direct answers now refresh when the language changes. The rest of the
  search page switched languages immediately, but a unit answer such as FIT2004
  kept its old translated title until the query itself changed.
- Unit titles whose subject is a list ("Introduction to the history and theory
  of art") are reordered too. Only a subtitle after a colon is left alone now;
  skipping every title with an "and" in it had left ten reading 导论对艺术的历史和理论.
- A double degree whose second subject contains "and" is split correctly.
  *Master of Global Business and Master of Regulation and Compliance* had been
  cut at every "and", so nothing paired up and the whole name went to the
  translator as one subject - producing 大师 in front of 硕士.

- Degree and unit names are now composed rather than translated whole. English
  names a qualification front-to-back and Chinese back-to-front, and a general
  translator handled the words without the order: *Bachelor of Science* had lost
  its subject entirely (学士), *Master of Teaching* read 师傅 (a craftsman),
  *Master of Accounting* 大师会计 (a guru), and *Doctor of Podiatric Medicine*
  had become a paediatrician. 452 of the 502 degrees are now built from an
  award, a subject and any qualifiers; the rest are left to the ordinary path.
  The same reordering fixes unit titles - 65 of 123 "Introduction to X" units
  read 导论到X, and one read 导论改为学术研究, "the introduction was changed to
  academic research".
- A search that matches units no longer opens with "No official answer indexed
  for this yet". Searching *2102* showed that notice above five Handbook
  results, because the answer router looks up FAQs and official pages and never
  sees what the result list found.
- A prerequisite made of nested groups is written out instead of coming up
  blank. FIT2004 needs one of FIT1008/FIT1054/FIT2085 *and* one of
  MAT1830/FIT1058; its outer group names no units of its own, so the planner had
  been showing "需要先修完 。" with nothing after it.
- The WAM/GPA calculator is usable on a phone. Its seven columns had been
  squeezed to about thirty pixels each, so the values could not be read; each
  row is now its own labelled block. The page also stopped scrolling sideways -
  a grid column had been sized to its widest child's minimum, pushing a 375px
  phone to 497px.

### Added

- Mobile navigation now includes a More menu with every destination from the
  desktop header, and the home page shows the same eight destinations directly
  in a responsive quick-access grid.

### Fixed

- Production deploys now apply the curated seed automatically, so
  human-reviewed unit titles such as `FIT2085` (工程师算法基础), `FIT1054`
  (算法基础（进阶）), and `ENG1014` (工程数值分析) cannot remain hidden behind
  older machine translations merely because a separate seed command was
  missed.
- A free elective part of a degree is now credited with the units no other part
  uses, instead of only the handful it happens to list. "Part E. Free elective
  studies" read 0/48 for a student whose plan held twelve units that counted
  towards it. 55 degrees have such a part.
- The plan checker reports what each unit is worth, not only the total, so units
  the degree does not name are no longer scored as zero credit points.
- The degree progress card no longer disappears when /plan is opened directly or
  reloaded. Which degree to load comes from the browser's own storage, so it is
  now fetched in the browser rather than on the server, which had no way to know
  it and was rendering the page against the API's index document.
- "major" and "minor" are translated as the academic senses in the prose
  describing how a degree is assembled, where that is what they always mean, and
  left to the translator elsewhere, where they are usually ordinary adjectives.
  "complete a major or minor from other courses" had been reading as an army
  rank and a child.
- "partner degree" no longer translates as a spouse.

### Documentation

- Added a direct production-site link to every language version of the README.
- Reworked the primary README as a Simplified Chinese, user-facing guide for students who need help finding and understanding Monash information.
- Added English, Japanese and Korean README versions, linked from every README.
- Clarified the separation between official Handbook data, official Monash sources and student community content.
- Documented community participation, including finding study partners, activity companions and students with shared interests, as a supporting feature.
- Moved developer-oriented references to the existing documentation set instead of placing local setup instructions in the user-facing README.

## Pull request history / PR 历史

This index records every pull request, including small fixes that do not need a
long release note. A closed PR that was not merged is labelled explicitly and
is not presented as shipped code.

这里记录每一个 PR，包括不需要单独撰写长篇发布说明的小修复。未合并就关闭的
PR 会明确标注，不会被误写成已经上线的功能。

### 2026-08-31

- [#79](https://github.com/Waldo0926/monash-hub/pull/79) Audit Chinese translations across all official guides / 全面审查 45 篇官方指南的简体中文翻译，修复考试规则、成绩等级、日历日期及其他政策术语误译。

### 2026-08-30

- [#78](https://github.com/Waldo0926/monash-hub/pull/78) Review Chinese unit titles and degree categories / 为 2026 Handbook 全部课程名称提供完整简体中文基线，校正会计课程与高风险错译，并修复学位分类和语言切换不一致。
- [#77](https://github.com/Waldo0926/monash-hub/pull/77) Audit every Chinese degree title / 全面检查 503 条在用学位记录，人工校对 93 个中文名称并确保其覆盖旧机器译文。
- [#76](https://github.com/Waldo0926/monash-hub/pull/76) Make Chinese titles searchable and refresh answers after language changes / 支持用中文搜索课程、学位和官方指南，切换语言后刷新直达答案，并补齐 #68–#75 的 Changelog 记录。

### 2026-08-29

- [#75](https://github.com/Waldo0926/monash-hub/pull/75) Describe the half of the site the README never mentioned / 补全 README 中遗漏的核心功能说明。
- [#74](https://github.com/Waldo0926/monash-hub/pull/74) Do not compose a name around a full stop / 遇到完整句号时不再错误拼接课程名称。
- [#73](https://github.com/Waldo0926/monash-hub/pull/73) Put the brand blue back in the footer mark / 恢复页脚标志的品牌蓝色。
- [#72](https://github.com/Waldo0926/monash-hub/pull/72) Point the footer at the WeChat account, and sign it / 在页脚加入微信公众号说明和作者署名。
- [#71](https://github.com/Waldo0926/monash-hub/pull/71) Finish the degree and title composition / 完善学位名称与课程名称的组合翻译。
- [#70](https://github.com/Waldo0926/monash-hub/pull/70) Build a degree's name instead of translating it / 按中文语序组合学位名称，不再整句直译。
- [#69](https://github.com/Waldo0926/monash-hub/pull/69) A unit code is a request for the unit / 输入课程代码时直接展示对应课程答案。
- [#68](https://github.com/Waldo0926/monash-hub/pull/68) Stop a narrow pass from deleting a wide one / 防止局部翻译修正覆盖更完整的已有结果。
- [#67](https://github.com/Waldo0926/monash-hub/pull/67) Complete mobile navigation and clarify the home page / 补全手机导航，并明确首页主要与次要功能层级。
- [#66](https://github.com/Waldo0926/monash-hub/pull/66) Apply curated translations on every deploy / 每次部署时自动应用人工校对翻译。
- [#65](https://github.com/Waldo0926/monash-hub/pull/65) Fix long degree cards and add a bilingual PR template / 修复长学位卡片被挤成逐字竖排的问题，并新增中英文 PR 模板。
- [#64](https://github.com/Waldo0926/monash-hub/pull/64) Let people sign in with Google / 新增 Google 登录（尚未合并，需配置 OAuth 客户端后才会显示）。
- [#63](https://github.com/Waldo0926/monash-hub/pull/63) Count the units a free elective part is actually free to count / 让自由选修部分正确计算未被其他要求占用的课程。
- [#62](https://github.com/Waldo0926/monash-hub/pull/62) Blue header, black footer, and a mark that is not a monogram / 更新蓝色页眉、黑色页脚及新的品牌标志。
- [#61](https://github.com/Waldo0926/monash-hub/pull/61) Give someone a page of their own / 新增个人主页及相关账户展示。
- [#60](https://github.com/Waldo0926/monash-hub/pull/60) Credit a specialisation to the part that asks for one, and stop computers having buildings / 将专精方向计入正确的学位要求，并修正线上课程被误标为实体地点的问题。
- [#59](https://github.com/Waldo0926/monash-hub/pull/59) Screenshot import, the browser-translation note, and room for Chinese to breathe / 新增成绩截图导入、浏览器翻译提示，并改善中文界面排版空间。
- [#58](https://github.com/Waldo0926/monash-hub/pull/58) Let a Chinese query find something / 让中文关键词可以找到对应的英文官方内容及中文索引。
- [#57](https://github.com/Waldo0926/monash-hub/pull/57) A WAM and GPA calculator, and one row for the planner's filters / 新增 WAM/GPA 计算器，并整理选课规划器筛选栏。
- [#56](https://github.com/Waldo0926/monash-hub/pull/56) A hand-written paragraph was never being read / 修复人工翻译段落未被读取的问题。
- [#55](https://github.com/Waldo0926/monash-hub/pull/55) Let the hand-written sentence win / 让人工翻译句子优先于机器翻译结果。
- [#54](https://github.com/Waldo0926/monash-hub/pull/54) Anonymous posts, threaded replies, and a like button that works / 新增匿名发帖、嵌套回复，并修复点赞功能。
- [#53](https://github.com/Waldo0926/monash-hub/pull/53) Keep the nesting in a requisite rule / 保留先修规则的嵌套结构，避免复杂条件被错误扁平化。
- [#52](https://github.com/Waldo0926/monash-hub/pull/52) Fix the headings the full pass exposed / 修复完整翻译流程暴露出的标题问题。
- [#51](https://github.com/Waldo0926/monash-hub/pull/51) Refetch when the controls change / 在筛选条件变化时重新获取对应数据。

### 2026-08-28

- [#50](https://github.com/Waldo0926/monash-hub/pull/50) Pin the words a degree structure uses for itself / 固定学位结构中的关键术语，避免机器误译。
- [#49](https://github.com/Waldo0926/monash-hub/pull/49) Translate what the page shows, not what it stores / 只翻译页面显示值，不改动数据库中的官方原始值。
- [#48](https://github.com/Waldo0926/monash-hub/pull/48) Add the course map, and check it against the Handbook / 新增学位课程地图，并依据 Handbook 校验结构。
- [#47](https://github.com/Waldo0926/monash-hub/pull/47) Show a degree, in Chinese, marked for your campus / 以中文展示学位结构，并标明课程是否在所选校区开设。
- [#46](https://github.com/Waldo0926/monash-hub/pull/46) Widen `aqf_level`: a double degree carries two of them / 扩展 `aqf_level` 字段以支持双学位的两个 AQF 等级。
- [#45](https://github.com/Waldo0926/monash-hub/pull/45) Crawl what a degree is made of / 抓取并保存学位组成、要求组和专业方向。
- [#44](https://github.com/Waldo0926/monash-hub/pull/44) Write out the unit titles the machine cannot do / 为机器无法可靠处理的课程名称提供人工译文。
- [#43](https://github.com/Waldo0926/monash-hub/pull/43) Draw the prerequisite graph, scoped to a campus / 新增按校区筛选的先修课程关系图。
- [#42](https://github.com/Waldo0926/monash-hub/pull/42) Pin a term in the plural, not only in the singular / 让术语表同时保护单数和复数形式。
- [#41](https://github.com/Waldo0926/monash-hub/pull/41) Make a grade a whole value, not a word inside a sentence / 将成绩等级作为完整字段处理，避免被当成句中普通单词翻译。
- [#40](https://github.com/Waldo0926/monash-hub/pull/40) Scope the guides by category, fix credit, and close the blank-line gaps / 按类别限定指南搜索，修正学分显示并清理多余空行。
- [#39](https://github.com/Waldo0926/monash-hub/pull/39) Put the Malaysia systems in their own column, beside the others / 将马来西亚校区系统入口整理为独立页脚栏。
- [#38](https://github.com/Waldo0926/monash-hub/pull/38) Reject a mask the model repeated instead of copying / 拒绝机器重复占位符而未正确还原术语的翻译结果。

### 2026-08-27

- [#37](https://github.com/Waldo0926/monash-hub/pull/37) Give the footer columns the widths they each need / 根据内容为页脚各栏分配合适宽度。
- [#36](https://github.com/Waldo0926/monash-hub/pull/36) Find a unit by part of its code, and line the footer up / 支持按部分课程代码搜索，并对齐页脚布局。
- [#35](https://github.com/Waldo0926/monash-hub/pull/35) Let every grid column shrink below its content / 允许网格列缩小到内容最小宽度以下，防止页面横向溢出。
- [#34](https://github.com/Waldo0926/monash-hub/pull/34) Stop the page scrolling sideways, and scope the visa answers / 修复移动端横向滚动，并限制签证答案的适用范围。
- [#33](https://github.com/Waldo0926/monash-hub/pull/33) Malaysia pages translated, and the systems students log into / 翻译马来西亚校区页面，并加入学生常用系统入口。
- [#32](https://github.com/Waldo0926/monash-hub/pull/32) Put the campus migration back on the end of the chain / 修正校区数据库迁移的依赖顺序。
- [#31](https://github.com/Waldo0926/monash-hub/pull/31) Say which campus a guide page is for / 在指南页面明确标注适用校区。
- [#30](https://github.com/Waldo0926/monash-hub/pull/30) Give the Mamo Guide page its logo / 为马莫指南页面加入品牌标志。
- [#29](https://github.com/Waldo0926/monash-hub/pull/29) Every guide page written by a person / 为所有指南页面提供人工撰写的中文内容。
- [#28](https://github.com/Waldo0926/monash-hub/pull/28) Hand-written Chinese for the guides, and the Mamo Guide page / 为指南及马莫指南页面加入人工中文翻译。
- [#25](https://github.com/Waldo0926/monash-hub/pull/25) Full Chinese on the Chinese site, and a unit filter that means what it says / 完善中文站内容，并修复课程筛选条件与界面文字不一致的问题。

### 2026-08-26

- [#27](https://github.com/Waldo0926/monash-hub/pull/27) Add the production site link / 在 README 中加入生产网站链接。
- [#26](https://github.com/Waldo0926/monash-hub/pull/26) Add a multilingual user README / 新增面向用户的中、英、日、韩多语言 README。

### 2026-08-24

- [#24](https://github.com/Waldo0926/monash-hub/pull/24) Do not let the model sign its work with the name of a language / 清理机器翻译意外附加的语言名称。
- [#23](https://github.com/Waldo0926/monash-hub/pull/23) Keep the university's own name, and every date, out of the model's hands / 保护大学专名和日期，不交由机器翻译。
- [#22](https://github.com/Waldo0926/monash-hub/pull/22) Write the sentences the machine is not allowed to guess at / 为禁止机器猜测的关键句子提供人工译文。
- [#21](https://github.com/Waldo0926/monash-hub/pull/21) Only let a costly term hold a sentence back / 仅让真正影响学费或学业决定的术语阻止自动翻译。
- [#20](https://github.com/Waldo0926/monash-hub/pull/20) Stop the tidying from closing a paragraph break / 防止翻译清理过程吞掉段落换行。
- [#19](https://github.com/Waldo0926/monash-hub/pull/19) Tidy a string that was all terms and no translation / 正确处理完全由受保护术语组成的文本。
- [#18](https://github.com/Waldo0926/monash-hub/pull/18) Give the translation pass the cores, and take the sharding back out / 让翻译任务使用多核并移除不合适的分片方案。
- [#17](https://github.com/Waldo0926/monash-hub/pull/17) Let the units pass be split across several processes / 支持把课程翻译任务分配到多个进程。
- [#16](https://github.com/Waldo0926/monash-hub/pull/16) Full Chinese on the guide pages, with the codes left alone / 完整翻译指南页面，同时保持课程代码等标识不变。

### 2026-08-23

- [#15](https://github.com/Waldo0926/monash-hub/pull/15) Make switching to English actually show English / 修复切换到英文后仍显示中文内容的问题。
- [#14](https://github.com/Waldo0926/monash-hub/pull/14) Stop showing students the CMS's own comments / 过滤 CMS 内部注释，避免向学生展示维护信息。
- [#13](https://github.com/Waldo0926/monash-hub/pull/13) Say census date the way the reviewed translations already say it / 统一 census date 的人工审核中文译法。
- [#12](https://github.com/Waldo0926/monash-hub/pull/12) Translate the content, with the terms that matter taken off the machine / 在关键术语保护机制下翻译官方内容。
- [#11](https://github.com/Waldo0926/monash-hub/pull/11) Machine-translate official content under a protected glossary / 尝试在术语保护下机器翻译官方内容；此 PR 已关闭且未合并，由 #12 取代。
- [#10](https://github.com/Waldo0926/monash-hub/pull/10) Chinese content, readable guide pages, and an email that always arrives / 加入中文内容和结构化指南页，并修复注册邮件静默不发送的问题。
- [#9](https://github.com/Waldo0926/monash-hub/pull/9) Stop the home page and footer leaving half the width empty / 重排首页和页脚，消除大面积空白并完善社区空状态。
- [#8](https://github.com/Waldo0926/monash-hub/pull/8) Stop `deploy.sh` sourcing `.env` as a shell script / 避免部署脚本把 Compose `.env` 当作 Shell 脚本执行。
- [#7](https://github.com/Waldo0926/monash-hub/pull/7) Verified accounts, answer notifications, and four interface languages / 新增邮箱验证与密码恢复、回答通知、四语言界面及并发计数修复。
- [#6](https://github.com/Waldo0926/monash-hub/pull/6) Crawl every 2026 unit, not just the twenty fixtures / 将 Handbook 抓取从 20 个测试课程扩展到全部 2026 课程。
- [#5](https://github.com/Waldo0926/monash-hub/pull/5) Key API fetches by path so the SSR payload reaches the client / 统一 SSR 与浏览器的 API 缓存键，修复 hydration 丢失数据。
- [#4](https://github.com/Waldo0926/monash-hub/pull/4) Render “last checked” in UTC so the server and browser agree / 使用 UTC 渲染最后检查日期，避免服务端与浏览器 hydration 不一致。
- [#3](https://github.com/Waldo0926/monash-hub/pull/3) Resolve the search answer during SSR so hydration keeps the results / 在 SSR 阶段获取搜索答案，避免 hydration 后结果消失。
- [#2](https://github.com/Waldo0926/monash-hub/pull/2) Correct what the first production deploy exposed / 修复首次生产部署暴露的 nginx、证书、sitemap 和部署文档问题。
- [#1](https://github.com/Waldo0926/monash-hub/pull/1) Resolve the frontend lockfile so `npm ci` can install it / 修复前端 lockfile，使 CI 和 Docker 构建可以正常执行 `npm ci`。

### Foundation / 初始版本

- `81173a4` Stage 0 foundation: Handbook parser, official knowledge seed, zero-AI QA, and community / 建立 Handbook 解析器、官方知识种子、零 AI 问答和学生社区的项目基础。
