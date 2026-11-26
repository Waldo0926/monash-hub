# Course elective references and browsing

C3702 Part A lists FIT5125 explicitly and describes another 18 points from
approved electives. Its approved-list link is in `Special_notes_to_students`,
which the previous parser discarded. Requirement rich-text links were also
flattened away across courses and areas of study.

The parser now retains references, including special notes, in separate JSON
fields on courses, areas and containers. Labels remain source text. Browsing
hints are derived from original English requirements, independent of the
selected translation. The UI uses the existing paginated unit search, scoped
to the selected Handbook year, campus and any levels stated in the rule. These
results are potential units to investigate, not an approved list. They never
enter curriculum items, graduation checks or planner credit totals.

## After the tested PR is merged and deployed

The migration alone cannot reconstruct discarded references. Refresh every
stored active degree and area for every loaded year, then audit the result:

```bash
docker compose -p monash-hub run --rm crawler \
  python -m crawler.handbook.refresh_course_references

docker compose -p monash-hub run --rm crawler \
  python -m crawler.handbook.audit_courses
```

The repair fetches sequentially with a three-second minimum interval and does
not discover or retire courses. Failed fetches keep the last good record and
cause a nonzero exit. The audit reports unresolved structures and records not
reparsed, plus every elective pool. A deploy does not block on upstream fetches.

Verify C3702 Part A in English and Chinese at Malaysia and another campus:
FIT5125 stays in the explicit list; the separate browser shows matching units,
search, pagination, empty/loading/error states; source references include the
approved elective list. Repeat with C2001 free electives, nested alternatives,
an area of study, and course links inside double-degree structures.
