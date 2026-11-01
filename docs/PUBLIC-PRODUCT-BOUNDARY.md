# Public product scope and paid-service boundary

Monash Hub is a free, independent site for published Monash information and student tools. It is **not** a frontend for the maintainer's paid education-consulting services.

## Not part of Monash Hub

- **Exchange Tracker** — a separate paid client-service system. No private tracker API, data feed, internal logic, client identities, paid features or approval records are to be integrated or copied.
- **Exchange Course Matcher** — also a separate paid service. Do not ship an equivalent free course-matching, credit-equivalence scoring, recommendation, or approval-record management feature as part of Monash Hub.
- No background synchronization, public search, source examples or blog posts should expose private client records or commercial workflows.

Monash Hub may show **officially published general Monash Abroad policy and dates**, with original source links, without connecting to either paid product or making any course-equivalence assertions.

## Included public student functions

- Handbook year-by-year unit facts, differences and source references
- Study-plan prerequisite and offering checks, with explicit uncertainty
- Public Malaysia tuition tables and *user-controlled* fee/discount/living-cost scenarios
- Official academic dates and optional local calendar exports
- Non-authoritative graduation preparation checklists
- Community tools and transparent, privacy-conscious improvements to their usability

Only Monash can confirm enrolment, transfer credit, scholarship awards and graduation eligibility. Do not infer admissions status from a fee entry; **unknown** is different from open or closed.

## Content and privacy standards

- Chinese UI strings follow [Chinese copy guidelines](CHINESE-COPY-STYLE.md) where available; labels and buttons need no final punctuation.
- Never silently modify official quotation or policy text for stylistic reasons.
- Keep individual planning data in the browser by default. A deliberate plan check may send the minimum necessary entries to an API; do not persist that material in server analytics or logs.
- State when a source was checked and distinguish a missing response from a verified negative finding.
