# Phase 1 — Immediate Income Playbook (Weeks 1–2)

Goal: first cash inside 14 days via productized services + bug bounties, while
logging recurring pain points that justify the ChemParse product.

> The lists below are **starting templates + where to look**, not live scraped
> posts — fill the tables by spending 30 min/day in the listed venues. Each
> table has the exact search to run.

---

## 1. Demand identification & outreach

### Where to look (run these searches)
| Venue | Search / filter |
|---|---|
| Biostars.org | "parse" , "convert", "pipeline help", filter Unanswered |
| r/bioinformatics | flair *Technical*; sort New; keywords parse/convert/GTF/BAM |
| r/comp_chem | "Gaussian output", "extract energy", "parse log" |
| SEQanswers | Bioinformatics subforum, "custom script" |
| Matter Modeling SE | tag `software`, `output-parsing` |
| GitHub | `is:issue is:open label:"help wanted" gaussian OR cclib OR rna-seq` |
| Twitter/Bluesky | "anyone know how to parse", academic accounts |

### Categorize each post into one of these buckets
Track in a sheet: `link | venue | bucket | proposed price | outreach sent | reply`.

| Bucket | Typical ask | Price band |
|---|---|---|
| **A. QM output → structured data** | Gaussian/ORCA/CP2K `.log` → JSON/CSV (energy, geometry, freqs) | $150–250 |
| **B. Format conversion** | BAM↔SAM, GTF↔GFF3, XYZ↔PDB, batch reformatting | $150–200 |
| **C. Pipeline build** | RNA-seq / scRNA-seq / phylogenomics one-off pipeline | $300–400 |
| **D. Data cleaning / scripting** | Merge tables, dedupe, plot, automate a manual step | $150–300 |

> **The 3 recurring needs that justify the product** are expected to be
> Bucket A (QM parsing — ChemParse core), Bucket B (conversion — easy product
> add-on), and Bucket D (batch automation — upsell). Confirm by counting how
> many real posts land in each bucket during week 1.

### Outreach templates

**Forum reply (public, value-first):**
> Hi — I parse comp-chem/bioinformatics outputs like this for researchers.
> For your case (Gaussian `.log` → JSON with final energy, optimized geometry,
> SCF convergence, and frequencies) I can turn it around in ~24h. Happy to do
> the first small file free so you can check the output format, then it's a flat
> $X for the batch. Want me to send a sample?

**Cold DM (shorter, 1 ask):**
> Saw your post about [specific problem]. I build these parsers/scripts fast.
> I can deliver [exact deliverable] by [day] for a flat $X — code + clean
> JSON/CSV, no subscription. Want a free sample on one of your files first?

**Follow-up (48h, no reply):**
> Quick bump — still happy to run one of your files free so you can see the
> output. No obligation.

### Conversion math
$1000 ≈ **4–6 jobs** at $150–400. Aim for 20–30 outreach touches → ~15% reply →
~5 closes. Front-load free samples; they convert.

---

## 2. Bug bounty & micro-contract sourcing

### Where to look (run these)
| Platform | How to filter |
|---|---|
| Algora.io | Sort by bounty $ desc; languages Python/TS; `good first issue` |
| Console.algora.io org boards | Watch active orgs paying weekly |
| IssueHunt | Funded issues; filter Python/JS |
| Opire / BountyHub | New GitHub-issue bounties, Stripe payout |
| GitHub search | `is:issue is:open label:bounty` and `label:"💎 Bounty"` |

### Target table (fill with live links — these are the *shapes* to hunt for)
| # | Task shape | Skill fit | Est. effort | Pay band |
|---|---|---|---|---|
| 1 | Fix parsing/edge-case bug in a Python sci lib (cclib/ASE/biopython) | comp-bio + py | 2–4h | $100–300 |
| 2 | Add a small feature/CLI flag to an OSS data tool | full-stack | 3–6h | $150–400 |
| 3 | Frontend bug in a React/TS dashboard | full-stack | 2–5h | $100–250 |
| 4 | Performance optimization (vectorize / cache) | ML/systems | 4–8h | $200–500 |
| 5 | Write tests / type hints to close a "help wanted" issue | py | 1–3h | $50–150 |

### Selection rules
- Prefer issues where a maintainer has **already commented a $ amount** or the
  bounty is escrowed (Algora/IssueHunt) — avoid unfunded "would be nice".
- Confirm scope in one comment before starting: *"Picking this up, plan is X,
  ETA Y — confirm the bounty is still open?"*
- Bias to your wheelhouse (Python sci-stack, React) for speed-to-cash.

---

## 3. Service delivery playbook — Gaussian `.log` → structured data

Concrete walkthrough for a Bucket A job (this is literally the ChemParse core,
so every paid job also hardens the product).

1. **Intake** — get the file + confirm exactly which fields they need
   (final energy? all geometry steps or just optimized? frequencies? thermo?).
2. **Parse** — run it through `parser/` here:
   ```bash
   python3 -c "from parser import parse_gaussian, json; \
     import json; print(json.dumps(parse_gaussian('THEIR.log'), indent=2))"
   ```
   cclib does the heavy lift; the regex fallback covers odd variants.
3. **Validate** — sanity-check energy magnitude, atom count vs. their molecule,
   frequency count = 3N−6 (non-linear) / 3N−5 (linear). Catch truncated runs
   (`metadata.normal_termination == false`).
4. **Package deliverable**:
   - `result.json` (full structured output)
   - `geometry.csv` (flat table for spreadsheets)
   - the small parse script so they can re-run on future files (this is the
     upsell to the monthly/self-host tier).
5. **Deliver + invoice** — Stripe Payment Link or invoice; ask for a testimonial
   and whether they have more files (recurring revenue).

**Edge cases to quote extra for:** multi-job files (opt+freq+TD), ONIOM/QM-MM,
non-Gaussian formats (ORCA/CP2K — route to the sibling parsers), >100 files
(batch = monthly tier pitch).
