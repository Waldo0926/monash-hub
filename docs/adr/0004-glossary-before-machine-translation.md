# 0004. Machine translation on the box, behind a glossary

Status: Accepted (written down 2026-10, for a decision made earlier)

## Context

The site is read mostly by Chinese-speaking students and also offers
Japanese and Korean. Handbook fields and official guide text have to be
translated: several thousand units and several hundred pages, refreshed as
Monash changes them. Paid translation APIs price that out of a student
project. Argos Translate (OPUS-MT on CTranslate2) runs locally for free and
is wrong exactly where the site cannot afford it: it renders *census date* as
人口普查日期, *unit* as 单位, *Exercise* as 锻炼.

## Decision

Every string goes through: agreed value? → protect the terms → translate →
put the terms back. `app/knowledge/glossary.py` holds the agreed terms and
the closed-list values (campuses, teaching periods, assessment types). A
closed-list value never reaches the model. A term inside a sentence is
swapped for a letter placeholder, which the model leaves alone, and restored
afterwards.

Human and machine translations sit side by side in `content_translations`
with a `provenance` column; the human one wins on read and the page says
which it is showing. Student posts are never translated.

## Consequences

- Free and unlimited, which is what makes the whole catalogue possible.
- The glossary is the quality lever. Most translation bugs are fixed by
  adding a term, and the fix applies to every page on the next run.
- A human translation can take over from a machine one without deleting
  anything, so the two never fight.
- Japanese and Korean are a lower bar than Chinese by decision: machine
  output behind the same glossary, with no routine human review.

## Revisit when

A free or very cheap model does noticeably better on the measured sample in
`docs/ARCHITECTURE.md`, or human translators join. The pipeline shape stays
either way; only the engine behind the glossary changes.
