# Architecture decision records

Short notes on the decisions that shape the project and would be expensive to
reverse. Each one says what the situation was, what was decided, what it
costs, and what would make us revisit it. `docs/ARCHITECTURE.md` describes how
the system is built today; these records say why it is built that way.

A record is never edited to say something different later. When a decision
changes, a new record supersedes the old one and both stay.

| Record | Decision | Status |
| --- | --- | --- |
| [0001](0001-modular-monolith.md) | One FastAPI app, one PostgreSQL, one Nuxt server | Accepted |
| [0002](0002-search-in-postgresql.md) | Search in PostgreSQL, not a search engine | Accepted |
| [0003](0003-zero-ai-answers.md) | Direct answers from templates, no language model | Accepted |
| [0004](0004-glossary-before-machine-translation.md) | Machine translation on the box, behind a glossary | Accepted |
| [0005](0005-accounts-without-identity.md) | Accounts are a nickname and a verified email | Accepted |

## Writing one

Copy the shape of an existing record: Context, Decision, Consequences, and
when to revisit. Number it next in sequence, add it to the table, and open it
in the same PR as the change it explains. Plain words; a reader a year from
now should not need the conversation that led to it.
