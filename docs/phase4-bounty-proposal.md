# Phase 4 — High-Value Bounty Proposal

Two $5k bounties were surfaced in research. Pick by skill leverage:

| Bounty | Ref | Fit | Risk |
|---|---|---|---|
| **Obsidian Importer — Notion API importer w/ Databases→Bases** ($5,000) | obsidianmd/obsidian-importer #421 | **Full-stack / TS — strong** | Medium; well-scoped |
| Tenstorrent tt-metal matmul / numerics ($1.5k–5k) | tenstorrent/tt-metal `bounty` label | Systems/ML — steep ramp | High; HW-specific |

**Recommendation: Obsidian Importer.** Pure TypeScript, no exotic hardware,
scope is a concrete data-transform pipeline — squarely in the full-stack lane and
realistically closeable solo in ~2 weeks. Below is the proposal for it.

---

## Obsidian Notion-API Importer (Databases → Bases) — $5,000

### Problem
The current importer ingests Notion's *HTML/Markdown export ZIP*. Users want a
**live Notion API** importer that also converts Notion **Databases** into
Obsidian **Bases** (the new native DB feature), preserving relations, properties,
images, and attachments as Obsidian-flavored Markdown.

### Approach
1. **Auth + fetch** — Notion internal-integration token; page through
   `/v1/search`, `/v1/databases/{id}/query`, `/v1/blocks/{id}/children`
   (recursive) with rate-limit backoff (Notion caps ~3 req/s).
2. **Normalize** — build an in-memory graph of pages/databases/blocks; resolve
   relation + rollup properties to stable local IDs before writing (two-pass so
   forward references resolve).
3. **Map to Obsidian**
   - Blocks → Obsidian-flavored Markdown (callouts, toggles→`<details>`, code,
     equations, embeds). Reuse the existing block→MD converter where possible.
   - **Database → Base**: emit a `.base` file (YAML view def) + one note per row;
     Notion properties → Base properties (select/multi-select/date/number/
     checkbox/relation). Relations become `[[wikilinks]]`.
   - Images/files: download from the signed S3 URLs (expire ~1h — fetch eagerly),
     write to the vault attachment folder, rewrite links.
4. **Idempotency + report** — slugify titles, dedupe collisions, emit an import
   report (counts, skipped, errors) like the other importers.
5. **Tests** — fixture Notion API JSON → assert vault tree, Base schema, link
   integrity. Mock the HTTP layer.

### Timeline (≈2 weeks, ~40–50h)
| Days | Milestone |
|---|---|
| 1–2 | Auth, paginated fetch, raw-JSON snapshot tests |
| 3–5 | Block → Markdown coverage + attachments |
| 6–8 | Database → Base mapping + relations |
| 9–10 | Idempotency, import report, edge cases |
| 11–12 | Tests, docs, PR + maintainer review loop |

### Challenges / mitigations
- **Signed URL expiry** → download during the walk, never defer.
- **Rate limits** → queue + exponential backoff; resumable from JSON snapshot.
- **Base format churn** (new feature) → isolate the emitter behind one module so
  a schema change is a one-file fix.
- **Property-type coverage** → start with the common 8 types, log unsupported.

### Draft engagement comment (post on the issue before coding)
> Hi — I'd like to take this on. Plan: paginate the Notion API
> (search → db query → block children, recursive) into an intermediate graph,
> then a two-pass writer that emits Obsidian-flavored Markdown for pages and a
> `.base` + per-row notes for databases (select/date/number/relation→wikilinks).
> Attachments downloaded eagerly to dodge signed-URL expiry; import report at the
> end matching the existing importers. I'll mock the HTTP layer for fixture
> tests. Targeting ~2 weeks. Is the bounty still open and is `.base` emission the
> desired target for databases (vs. a plain Markdown table)? Happy to share a
> design note before I start.
