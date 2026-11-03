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

`app/knowledge/admissions.py` reads indexed `OfficialPage` rows only. Three
reviewed programme URLs are added as dynamic curated HTML seeds. No request-time
network access, binary mirroring, model-generated decisions or private data is
introduced. Unreviewed programmes remain unverified.

Programme identity is exact-title/approved-URL matched and carries its reviewed
course code and Malaysia campus scope. Only complete, explicit application
sentences scoped to that title can yield open/closed/suspended. Buttons, generic
application deadlines, negated/qualified notices and unrelated titles cannot.
Opposing explicit notices are marked conflict for review. Missing, failed,
login-only, future-dated or older-than-30-day sources yield unverified, retaining
provenance and the earlier observed state separately. Thirty days is this UI's
freshness policy, not an official admissions rule.

Fee rows and course detail responses carry separate `admissions` evidence with
source URL, last check, expiry and source hash. The fee table can filter current
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
show unverified. Use the existing targeted harvest/refresh path for the three
new slugs; do not trigger an unbounded crawl or new scheduler. No schema
migration is needed; rollback is the previous application release, with indexed
HTML/text records left intact.
