# Malaysia admissions evidence

Reviewed against primary sources on **2026-11-03**. This adds independent
current programme notices; it does not certify individual eligibility or a
future intake's opening status. Related issues: #264 and #262 remain open for
their broader requirements.

## Reviewed sources

| Source | Result of review |
| --- | --- |
| [Undergraduate fees](https://www.monash.edu.my/study/undergraduate/fees) | Published 2027 fee table; annual amounts must remain separate from admissions. The previously malformed pharmacy amount is now well formed upstream; no guessing is needed when it is refreshed. |
| [Postgraduate fees](https://www.monash.edu.my/study/postgraduate-and-research/fees) | Published 2027 table mixes annual and full-course bases. Missing rows do not establish discontinuation. |
| [October intake](https://www.monash.edu.my/study/apply/intake-periods/october-intake) | 2027 named course list and general deadlines reconfirmed. Listing does not prove applications are open now. |
| [February intake](https://www.monash.edu.my/study/apply/intake-periods/february-intake) | 2027 general and special-category dates reconfirmed; general dates are not programme availability. |
| [Intake periods](https://www.monash.edu.my/study/apply/intake-periods) | July 2027 dates reconfirmed. A future counselling deadline does not override the course page's current closure notice. |
| [Psychology](https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-psychology) | Programme page exists, has 2027 fees and links Handbook code M2018; no explicit current application-open sentence was verified. |
| [Psychology and Business](https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-psychology-and-business) | Programme page exists, has 2027 fees and links M2015. It must not inherit the honours programme's identity or another programme's application status. |
| [Professional Counselling](https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-of-professional-counselling) | Current page explicitly says applications are closed. Its Handbook link names D6006; an unavailable Handbook target is not itself evidence of discontinuation. |

## Runtime behavior

`app/knowledge/admissions.py` reads indexed `OfficialPage` rows and their matching
`OfficialPageVersion` fetched titles. The bounded
programme-link catalogue now includes **61 unique programme destinations**: the 52 distinct published fee-table destinations,
one corrected independently reviewed Business/Computer Science destination,
and eight individual Engineering destinations linked by its directory. The existing counselling
notice remains separate from the fee catalogue. New destinations use the
existing dynamic refresh tier; no automatic link following is introduced. No request-time
network access, binary mirroring, model-generated decisions or private data is
introduced. Unreviewed programmes remain unverified.

Programme identity is matched by a reviewed catalogue destination (or the published
fee-cell link when no reviewed mapping exists), plus the current version’s fetched
programme title, retaining school-specific destinations for repeated titles
such as PhD and MPhil. School-scoped catalogue lookup supports older indexed
pages; legacy whole-row links are accepted only for single-title rows with an
exact complete row label and one unambiguous destination. Multi-degree covers
never inherit a notice from an ambiguous group link. Handbook course codes are
read only from a unique explicit Handbook course link; unknown codes stay null.
The three earlier manually reviewed identities also require fetched-title proof. Only complete, explicit application
sentences scoped to that title can yield open/closed/suspended. Buttons, generic
application deadlines, negated/qualified notices and unrelated titles cannot.
Opposing explicit notices are marked conflict for review. Missing, failed,
login-only, future-dated or older-than-30-day sources yield unverified, retaining
provenance and the earlier observed state separately. Thirty days is this UI's
freshness policy, not an official admissions rule.

The cleaner preserves each table link's section, row, column and anchor text,
including merged-cell positioning, while retaining the older Policy Bank link
index and plain-text grid. This lets the tuition parser retain programme URLs
without assigning an unrelated link or another school's notice.

Fee rows and course detail responses carry separate `admissions` evidence with
source URL, last check, expiry and source hash. The fee API also reports linked/current/explicit-notice coverage; the UI labels
these separately. `programme_page_verified` means a fresh matching source is
indexed, not that the programme is accepting applicants. Course detail cannot
inherit a Malaysia notice when the selected Handbook record has no verified
Malaysia campus. The fee table can filter current
notice status without conflating it with the selected intake list. A current
notice always leaves future `intake_status` unverified. The old timeless closed
claim in the missing-fee note is removed: runtime evidence must support it.

The year comparison now marks missing/null source fields as unavailable. It
reports differences only among known values, lists insufficient fields
separately, and no longer says the entire Handbook is unchanged when fields
are missing. Explicit empty lists remain distinct from missing arrays.

## Rollout boundary

No production refresh or service restart was performed. Until the normal
reviewed deployment and indexed seed refresh, missing programme rows correctly
show unverified. Use the existing targeted harvest/refresh path for the bounded catalogue
slugs; do not trigger an unbounded crawl or new scheduler. Direct requests from
the current development machine returned 403 on 2026-11-03. No bypass or
production source refresh was attempted. Registered, fetched, fresh and
explicitly verified notices must be counted separately. No schema
migration is needed; rollback is the previous application release, with indexed
HTML/text records left intact.


## #264 acceptance still requiring production evidence

- The linked destinations are not a claim that all 61 pages have been fetched.
  New sources must complete the normal reviewed harvest and freshness checks.
- The current official fee indexes identify 2027 fees; annual/full-course units
  remain separate. The public indexed copy inspected during development was
  last checked on 2026-11-02, so it cannot prove today's updated prices.
- Current/future intake status remains unverified without an explicit scoped
  source. A 2028 Software Engineering closure is not a 2027 closure.
- A missing fee, missing programme source or failed Handbook URL never proves
  that a course has been discontinued or is not offered on the campus.
- Exact-year eligibility, full-source reconciliation and live affected-flow
  evidence must be reviewed before closing #264. This PR alone does not close it.


## 2026-11-04 identity correction

Programme identity must use the fetched title from `OfficialPageVersion` whose page ID and content hash match the current page. `OfficialPage.title` is a curated search label and can be overwritten during seed registration; it cannot independently verify programme identity. Missing or mismatching version titles remain unverified, including the earlier curated programmes. Titles are read in one batched query, without a migration, backfill or request-time source fetch.

The Business/Computer Science double degree has its own reviewed programme URL, distinct from the Business/Digital Media double degree. Where the fee-table anchor disagrees with the school-scoped reviewed catalogue, admissions uses the reviewed destination and exposes `fee_link_conflict`; the original fee link is retained and the UI warns in both languages. Neither the catalogue nor a valid page establishes a current or future application opening.

Reviewed programme: https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-bachelor-computer-science

These are source-code corrections awaiting review and deployment. Previously reported coverage based on curated labels must not be treated as independent-source proof. No manual production refresh or service restart was performed.


## 2026-11-08 — selected-intake applicability

The fees API accepts bounded `year`, `intake` and `campus=Malaysia` selection and returns the selection with independent fee-publication and selected-intake evidence. An intake state needs a complete notice naming the exact programme, year, intake and (for absence) Malaysia campus, plus the existing fresh fetched-title identity proof. Undated notices, generic deadlines, future cessation, missing fees and qualified/negated sentences do not transfer to that selection. Conflicting explicit statements stay conflicting. Unknown states never imply discontinuation.

Fee publication retains its own source year, basis, hash and check date. A different/unknown fee year, unreadable basis/amount, failed refresh or stale source remains unverified for the selection while retaining the archived amounts. Browser filters keep current notices separate from selected-intake states and retain year/intake choices in the URL. The dated October list and general deadline references were rechecked on 2026-11-08 and expire to unverified after 30 days; they never prove open applications.

See [the bounded source reconciliation](ADMISSIONS-RECONCILIATION-2026-11-08.md): 68 valid HTML sources, 62/63 programme-title matches, one qualification mismatch for manual review, no guessed Handbook codes. This is read-only source review, not a production refresh. Deployment, normal index refresh and affected-flow production acceptance remain required before closing #264.
