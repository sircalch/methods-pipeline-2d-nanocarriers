# methods-pipeline-2d-nanocarriers

**Auditing Computational Screens of Two-Dimensional Drug Carriers: Eight Failure
Modes Found by Rebuilding Four Case Studies, and a Checklist to Catch Them**

Version 2 of this repository (target: *Journal of Computational Biophysics
and Chemistry*, World Scientific). It replaces version 1, a Beilstein Perspective whose conclusions
rested on results that the September 2026 rebuild of the four case studies showed
to be wrong. Version 1 remains available on Zenodo
([10.5281/zenodo.22760388](https://doi.org/10.5281/zenodo.22760388)); what changed
is listed in `OUTLINE_v2.md` and stated in the paper.

The four case studies, each rebuilt from raw inputs:

- [`kras-pancreatic-gC3N4-ai`](https://github.com/sircalch/kras-pancreatic-gc3n4-ai) — KRAS-G12D, graphitic carbon nitride
- [`nano-qsar-ai-therapeutics`](https://github.com/sircalch/nano-qsar-ai-therapeutics) — PARP1 (TNBC), B₃₆N₃₆ cage
- [`mxene-glioblastoma-qsar-ai`](https://github.com/sircalch/mxene-glioblastoma-qsar-ai) — EGFR (glioblastoma), Ti₃C₂O₂ MXene
- [`borophene-alzheimer-tau-ai`](https://github.com/sircalch/borophene-alzheimer-tau-ai) — tau filaments, β₁₂ borophene

## Contents

- `src/audit_carriers.py` — formula and bond census of every carrier model → `data/carrier_audit.csv`
- `src/gather_audit_evidence.py` — extracts every number of the paper from the four
  repositories and the archive of the pre-rebuild files → `data/audit_evidence.json`
  and the Supporting Information tables `data/si_*.csv`
- `data/v1_reproduction/` — reproduction of the version-1 KRAS QSPR model
- `src/figures/make_figures.py` — Figures 1–6 and the table-of-contents graphic (`figures/`)
- `src/manuscript/` — manuscript, Supporting Information and cover letter builders
  (`src/make_jcbc_package.py` assembles and checks the upload package)
  (`build_manuscript.py`, `build_si.py`, `build_cover_letter.py`; references from
  Crossref via `make_references.py`) → `manuscript/submission/`

## Reproducing

```bash
python src/audit_carriers.py
python src/gather_audit_evidence.py
python src/figures/make_figures.py
python src/manuscript/build_manuscript.py
python src/manuscript/build_si.py
python src/manuscript/build_cover_letter.py
```

The evidence scripts read the four case-study repositories and the archive of the
pre-rebuild files, which must sit in the same parent folders as on the author's
machine (see the paths at the top of `src/gather_audit_evidence.py`). Some figures
(Figures 3, 4 and 6) also read result files of the case-study repositories directly; the
manuscript, Supporting Information and cover letter need only the files in `data/`
and `figures/`.

## Status

Draft complete; not yet submitted. The DFT adsorption results of the glioblastoma
case study are still being computed.

MIT licence.
