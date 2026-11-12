# Handbook unit comparison: evidence and limits

Related: #262. Updated 2026-11-03; implementation is a PR until reviewed and deployed.

## Existing behavior and fixes

The unit comparison already supports explicit year pairs, nested prerequisites/corequisites/prohibitions, campuses/periods, assessment weights, nullable exam flags, source links and check dates. Missing years are not inferred to mean discontinued units. AND/OR reordering retains equivalent rules without flattening nesting.

Two additional defects are fixed:

1. Changing a selector after a comparison used to relabel the completed result without reloading its data. Results now retain their requested code and years, mark edited inputs as pending, prevent overlapping submissions and reject an API snapshot whose code/year differs from the request.
2. The API always serializes missing relationship collections as `[]`; the UI therefore could not prove that an old empty record came from an explicit empty source. Collection comparison now needs nonempty rendered data or explicit source coverage before calling empty lists unchanged, added or removed. Legacy records remain unknown until the normal parser refresh supplies evidence.

The parser stores boolean collection-source proof in the normalized UnitVersion JSON, never raw HTML. Coverage metadata is excluded from semantic content hashing. An unchanged-content refresh may enrich only this metadata on the matching version; it does not rewrite child records, invalidate translations or emit a policy-change event. No schema migration or production backfill is part of this PR.

## Acceptance checklist

- Explicit years and API identity checks; no silent fallback for missing editions.
- Added/removed/changed/unchanged/unavailable distinguish absent data from explicit empty source collections.
- English/Chinese wording, original Handbook links and check dates retained.
- Synthetic parser, persistence/API and desktop/phone regression coverage added.
- A unit edition does not replace degree rules for the student's commencement year. The comparison links to the existing course map, which selects degree rules from the plan start year separately from each unit's teaching year.
- This unit page does not compare degree/AOS requirements that it does not model. No eligibility, credit mapping or AI policy interpretation is added.

## Rollout boundary

Ruff, typecheck, unit tests and build run locally. PostgreSQL-specific API/persistence and the full disposable browser stack run in CI; skipped local tests are not passes. Production deployment, naturally refreshed coverage metadata and live affected-flow checks remain necessary before closing #262. Existing old snapshots fail closed, without a forced recrawl, data deletion or new scheduler.


## 2026-11-08 — commencement-year context

The course map now requests degree rules for the exact commencement year, never the nearest loaded year. Missing, failed or mismatching degree/year/source records remain unverified, clear the progress structure, and do not imply discontinuation. Unit teaching-year fallback remains separate. Late degree responses cannot replace the current selection.

The comparison accepts optional degree and commencement-year context, retains that context with the completed unit snapshots, and preserves it in shareable query parameters. It displays the exact degree edition's structure when available, links its complete record and original Handbook, and shows check dates. Editing inputs marks the completed result pending instead of relabeling old requirements. Missing structure is unknown, not an empty requirement set. This remains unit-year comparison with independent commencement-degree context, not a whole-degree/AOS equivalence or credit-mapping engine.

Read-only public API checks on 2026-11-08 confirmed FIT2102 records for 2026 and 2027 (all three collection coverage flags present), C2001 for 2025 (five root curriculum containers), and an explicit 404 for C2001 in 2024. The new UI must not substitute 2025 for that missing 2024 edition. The production build at review time was dbc3a33; new-UI production acceptance remains pending until reviewed deployment. No production data was modified.

### Source metadata observed

| Request | HTTP | Returned year | Original source | Last checked |
| --- | --- | --- | --- | --- |
| `/v1/units/FIT2102?year=2026&locale=en` | 200 | 2026 | https://handbook.monash.edu/2026/units/FIT2102 | 2026-09-27T06:26:18.220815+00:00 |
| `/v1/units/FIT2102?year=2027&locale=en` | 200 | 2027 | https://handbook.monash.edu/2027/units/FIT2102 | 2026-11-07T20:47:31.396496+00:00 |
| `/v1/courses/C2001?year=2025&locale=en` | 200 | 2025 | https://handbook.monash.edu/2025/courses/C2001 | 2026-10-02T09:34:05.835223+00:00 |
| `/v1/courses/C2001?year=2024&locale=en` | 404 | Unavailable | Unavailable | Unknown |

### 中文说明

学位要求按精确入学年份读取，不再用邻近版本代替。跨年课程对照可以附带学位代码和入学年份，显示独立的学位来源、原文结构摘要和核对日期；修改输入不会改写已有结果的年份标签。缺失、失败或身份不符继续显示未核实，不推断停办或符合毕业要求。课程教学年份与学位入学年份不是同一个概念。完整学位/AOS 对照及学分认定不在这个课程对照页面的范围内。

新增合成测试覆盖缺失入学版本、错误年份/代码/来源、编辑后的结果标签、手机布局；生产新界面的受影响流程仍待合并部署后验收，暂不关闭 #262。
