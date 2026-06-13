# ChemParse

Turn computational-chemistry output files (Gaussian, LAMMPS, CP2K) into clean
JSON/CSV. Built as the compounding product behind a summer
freelance-services + bug-bounty income plan.

**Who this is for:** *you* (the builder) earn the money; the *customers /
target users* are the researchers drowning in unparsed comp-chem & bioinformatics
output. Every surface below is framed for them.

```
chemparse/
├── docs/      phase1-services-and-bounties.md  ← outreach + bounty + delivery playbook
│              phase4-roadmap.md                ← product roadmap + service automation
│              phase4-bounty-proposal.md        ← $5k Obsidian-importer technical proposal
│              phase5-advanced-ai.md            ← LLM fine-tune + data-curation + branding
├── landing/   index.html                       ← single-file Tailwind landing (Cloudflare Pages ready)
├── backend/   parser/ + converters/ + app.py   ← parsers, GTF→GFF3, FastAPI endpoints
└── frontend/  Vite + React                     ← drag-drop UI, JSON viewer, 3D viewer, Stripe gate
```

## What's done
- **Parser core** — `parse_gaussian(filepath) -> dict` (final energy, optimized
  geometry, SCF convergence, frequencies). cclib primary, regex fallback (zero
  heavy deps). **LAMMPS** (thermo/geometry/forces/cell) and **CP2K**
  (energy/cell/geometry/forces) parsers fully implemented as siblings sharing one
  interface + auto-detecting registry.
- **Converters** — `gtf_to_gff3` (attribute reformat + ID/Parent derivation).
- **API** (FastAPI, CORS open):
  - `POST /parse` — auto-detect format → structured JSON; `POST /parse.csv`
  - `POST /convert/gtf-to-gff3` — free single-file conversion
  - `POST /batch-parse` — premium: `.zip` in → parallel parse → `.zip` of JSON
- **Frontend** — Vite/React: drag-drop, loading state, collapsible JSON viewer,
  **interactive 3D geometry viewer (3Dmol.js)**, CSV/JSON download gated behind a
  Stripe Payment Link (stateless `?paid=1` unlock).
- **Landing** — self-contained `landing/index.html`: hero, supported formats,
  3 pricing tiers (placeholder $X/$Y/$Z), email capture POST. Mobile-responsive.
- **Strategy** — `docs/` covers Phases 1, 4, 5 (services, bounties, roadmap,
  $5k bounty proposal, LLM fine-tuning, data curation, branding).
- **Tests** — 13 pytest tests pass (Gaussian, LAMMPS, CP2K, GTF→GFF3).

## Run it

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload          # http://localhost:8000  (POST /parse)
pytest                            # 13 passing
```

**Frontend**
```bash
cd frontend
cp .env.example .env              # set VITE_API_BASE + VITE_STRIPE_LINK
npm install && npm run dev        # http://localhost:5173
```

**Landing** — open `landing/index.html`, or `wrangler pages deploy landing`.

## Stripe wiring (Phase 3)
1. Create a Stripe **Payment Link** for each tier.
2. Set its success URL to your app with `?paid=1` (e.g. `https://chemparse.app/?paid=1`).
3. Drop the link into `frontend/.env` (`VITE_STRIPE_LINK`) and the landing
   page's `data-stripe` anchors.
The unlock is intentionally stateless (URL param) — no accounts, no DB. Harden
later with a webhook + signed token if abuse appears.

## Where to extend
- Add ORCA/Q-Chem parsers as new siblings + register in `registry.py`.
- More converters (`vcf-to-tsv`, `tsv-to-gtf`) — same `converters/` interface.
- Thermochemistry add-on (ZPE/H/G from Gaussian freqs); batch CSV summary.
- See `docs/phase4-roadmap.md` for the prioritized feature list.
