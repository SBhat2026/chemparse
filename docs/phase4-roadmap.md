# Phase 4 — ChemParse Roadmap & Service Automation

## What shipped this phase (in this repo)
| Item | Status | Where |
|---|---|---|
| LAMMPS parser (thermo, geometry, forces, cell) | ✅ done + tests | `backend/parser/lammps.py` |
| CP2K parser (energy, cell, geometry, forces) | ✅ done + tests | `backend/parser/cp2k.py` |
| GTF→GFF3 conversion micro-service | ✅ done + tests | `converters/`, `POST /convert/gtf-to-gff3` |
| Batch parse (.zip→.zip, parallel) | ✅ done | `POST /batch-parse` |
| Interactive 3D geometry viewer | ✅ done | `frontend/src/MolViewer.jsx` (3Dmol.js) |

## Service automation: the 3 recurring needs → product surfaces
The 3 buckets validated in Phase 1 each map to a now-built surface, so paid
manual jobs and the self-serve product reinforce each other:

| Recurring need (from Phase 1) | Manual service | Productized surface |
|---|---|---|
| QM output → structured data | per-file parse jobs | `POST /parse`, `/parse.csv` |
| Format conversion | GTF/VCF/TSV reformats | `POST /convert/gtf-to-gff3` (+ siblings) |
| Batch automation | "run this on 200 files" | `POST /batch-parse` (premium) |

**Tiering:** single file = free/preview; batch + full download = paid (Stripe).
Conversion mirrors this: single convert free, batch convert gated.

## Next features (prioritized by value × effort)
1. **More converters** — `vcf-to-tsv`, `tsv-to-gtf` (both showed up in demand
   searches). Same `converters/` interface (text in → text out); add endpoint +
   tests per format. *(Low effort, direct demand.)*
2. **More parsers** — ORCA, Q-Chem, ASE-readable formats. Drop in as siblings,
   register in `registry.py`. cclib already covers several — wrap + normalize.
3. **Thermochemistry add-on** — from Gaussian freqs, compute ZPE / enthalpy /
   Gibbs (GoodVibes-style). High willingness-to-pay; pure post-processing on
   already-parsed data.
4. **Batch CSV summary** — one row per file (energy, n_atoms, converged?) across
   a `.zip`; the spreadsheet researchers actually want. Builds on `/batch-parse`.
5. **Async jobs** — for big batches, move to a queue + job-id polling so requests
   don't hold a connection. *(Only when batch sizes force it.)*

## Interactive visualization — plan (partially shipped)
- **Shipped:** browser-native 3D via **3Dmol.js** (`MolViewer.jsx`) — builds an
  XYZ from the parsed geometry, renders stick+sphere, drag/zoom. No server load,
  no Python in the hot path. This is the right call for web (vs. `nglview`/
  `py3Dmol`, which are Jupyter-oriented and need a kernel).
- **Next:** (a) animate optimization trajectory (multi-frame XYZ from each
  geometry step — already parseable from Gaussian orientation blocks);
  (b) overlay force vectors for MD/CP2K; (c) server-side static PNG render
  (headless) for share links / OG images.
- **When a kernel exists** (e.g. a notebook tier), `py3Dmol` reuses the same XYZ
  builder — keep geometry as the single interchange format.
