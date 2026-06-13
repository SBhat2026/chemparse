# Phase 5 — Advanced AI/ML Offerings & Positioning

Higher-ceiling work to graduate from $1k/mo services into $5k+ engagements.
Templates to adapt per client — not generic boilerplate.

---

## 1. LLM Fine-Tuning — Project Proposal

**Domain chosen:** *structured data extraction from chemistry patents/papers*
(method → product, conditions, yield) into JSON. High ROI, clean eval, and it
feeds straight back into ChemParse's "literature → structured data" story.

**Problem statement.** Client's chemists hand-extract reaction details from PDFs;
slow, inconsistent, unscalable. General LLMs hallucinate conditions and miss
table/SI context. They need a model that reliably emits a fixed JSON schema from
messy patent text.

**Proposed solution.**
- **Approach:** parameter-efficient fine-tune (**QLoRA**, 4-bit) — fits one
  consumer/A100 GPU, cheap to iterate, easy to ship as an adapter.
- **Base model:** an open ~7–8B instruct model (e.g. Llama-3.1-8B or Mistral-7B)
  for cost/latency; reserve a larger model only if eval demands it.
- **Data:** 800–1,500 (text → target-JSON) pairs. Bootstrap with a strong
  teacher model for draft labels, then **human-correct** (this is where the
  domain expertise — and the data-curation upsell below — pays off). Hold out a
  gold eval set the client signs off on.
- **Schema-constrained decoding** at inference (grammar/JSON-mode) so output is
  always valid JSON.

**Deliverables.** Fine-tuned LoRA adapter + merged weights; inference script +
minimal API; eval report (field-level precision/recall/exact-match vs. gold);
data pipeline + labeling guidelines; deployment note (vLLM/TGI, or a serverless
GPU endpoint).

**Pricing & timeline.** $6,000–$9,000 fixed, **3 weeks**: wk1 schema + data +
pipeline; wk2 train/iterate; wk3 eval, hardening, handoff. Milestone billing
(40% / 30% / 30%).

**Ethical considerations.** Patent text licensing/usage rights confirmed up
front; no PII; document train/eval provenance. Report failure modes (rare
reagents, multi-step reactions) and ship a confidence flag so low-certainty
extractions get human review, not silent errors. Adapter ships to client only —
no cross-client data leakage.

---

## 2. Scientific Data Curation — Service Offering

**Service description.** Turn messy, unstructured scientific data into clean,
ML-ready datasets: reaction/condition tables, assay/experimental results,
molecular structures (SMILES/InChI normalization), genomic/sequence annotations,
and labeled text spans from literature.

**Methodology.** Semi-automated, human-in-the-loop:
1. Ingest + profile (schema, dupes, missingness).
2. Auto-normalize with scripts (units, identifiers, dedupe; RDKit canonical
   SMILES; resolve names→structures).
3. Pre-label with heuristics/LLM, then **human QC** against a written guideline.
4. Double-review a sample for inter-annotator agreement; report quality metrics.

**Tool stack.** Label Studio (annotation UI), `pandas` (wrangling), `rdkit`
(chem normalization/validation), `biopython`/`pysam` (sequence), custom Python
validators, the ChemParse parsers for any comp-chem outputs in the mix.

**Pricing model.** $60–$120/hr depending on domain depth, or project-based
(e.g. $1,500 for a 5k-row curated + validated dataset with a quality report).
Bundle "curation + fine-tune" (§1) as a premium combined engagement.

---

## 3. Personal Branding & Thought Leadership (AI for Science)

**Content (ship 1 every 1–2 weeks; each doubles as SEO + lead-gen):**
- "Parsing Gaussian Output with Python: A Practical Guide" — links to ChemParse;
  ranks for the exact pain you're selling against.
- "GTF vs GFF3, and a 30-line converter that actually preserves Parent IDs."
- "Fine-tuning an 8B model to extract reactions from patents — what worked."
- "From manual parsing to a product: building ChemParse in public."

**Open source (credibility + inbound):**
- Contribute fixes/parsers upstream to `cclib`, `pymatgen`, `biopython` — the
  same libraries you depend on; PRs are public proof of skill.
- Open-source the ChemParse parser core (keep the hosted batch/UI paid). OSS core
  drives top-of-funnel; the convenience layer monetizes.

**Networking.** Be genuinely useful where the demand already lives — answer on
Biostars / r/bioinformatics / r/comp_chem / Matter Modeling SE (the same venues
from Phase 1), link your guide only when it directly helps. Post build logs on
Twitter/Bluesky + LinkedIn. Lurk ISMB / comp-chem virtual sessions for warm
intros to labs that need exactly this work.

**Flywheel:** answer pain → publish the guide → guide sells the product →
product work generates more guides → reputation lowers CAC on the next service
client.
