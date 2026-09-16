# methods-pipeline-2d-nanocarriers

**Don't Fool Yourself When Screening 2D-Nanomaterial Drug Carriers: A Reproducible
GFN2-xTB + Docking + Leak-Free QSAR Pipeline, Four Disease Case Studies, and a
Cautionary Tale**

Perspective article (target: *Beilstein Journal of Nanotechnology*, Perspective
format — Q2, Diamond Open Access) that distills a methodological lesson from
four independent nano-QSAR case studies built with the same reproducible
pipeline:

- [`kras-pancreatic-gC3N4-ai`](https://github.com/sircalch/kras-pancreatic-gc3n4-ai) — MRTX1133 on B,P-doped g-C₃N₄ (PDAC)
- [`mxene-glioblastoma-qsar-ai`](https://github.com/sircalch/mxene-glioblastoma-qsar-ai) — kinase inhibitors on Ti₃C₂O₂ MXene (GBM)
- [`nano-qsar-ai-therapeutics`](https://github.com/sircalch/nano-qsar-ai-therapeutics) — PARP inhibitors on B₃₆N₃₆ nanocage (TNBC)
- [`borophene-alzheimer-tau-ai`](https://github.com/sircalch/borophene-alzheimer-tau-ai) — Tau ligands on β-12 borophene (AD)

## Thesis

A rigorous computational screen of a 2D-nanomaterial drug carrier is genuinely
cheap (GFN2-xTB + AutoDock Vina, hours on a workstation) — but only if the
adsorption geometry is *relaxed*, the regression target is a *real* computed
quantity, and the cross-validation is *leak-free*. Applying one unmodified
pipeline to four chemically unrelated disease/carrier systems gives an
informative, mixed picture:

- **MXene (GBM)** — modest, honestly non-predictive physisorption (Q²_CV ≈ 0.10).
- **KRAS-G12D / g-C3N4** — comparably modest interaction energies, but a
  genuinely predictive QSPR (Q²_CV = 0.51–0.55): a control showing the
  leak-free protocol isn't simply too conservative to find real signal.
- **TNBC / B36N36 and Tau / β12 borophene** — both hide a small chemisorbing
  minority (5 of 33; 12 of 29 ligands) inside an otherwise non-predictive
  physisorbing majority, a distinction the field's common single-point,
  unrelaxed protocol would hide entirely — and did, in our own first pass at
  the borophene system.

The corrected Tau/borophene result is used as a worked before/after example,
and the recurring failure modes found (and fixed) across all four sibling
projects are distilled into a short checklist.

## Repository contents

- `manuscript/Beilstein_Perspective_Methods_Pipeline_Monreal_Hernandez_et_al.docx` — full manuscript (~4,200 words, 4 figures, 25 references, all cited inline).
- `manuscript/submission_ready/` — cover letter + submission copy.
- `src/generate_methods_manuscript.py` — regenerates the manuscript from source.
- `src/build_fig1_pipeline_schematic.py`, `build_fig3_drho_panels.py`, `build_fig4_tau_before_after.py` — figure generators (Figs. 1, 3, 4).
- `src/gather_cross_system_summary.py` — pulls the real headline numbers from all 4 sibling repos into `data/cross_system_summary.csv` and Figure 2.
- `figures/fig4_assets/` — the real ChimeraX renders and structures behind Figure 4's Tau before/after panel.
- `OUTLINE.md` — the original section-by-section argument sketch this was written from.

## Reproducing

```bash
python src/gather_cross_system_summary.py      # cross-system table + Figure 2
python src/build_fig1_pipeline_schematic.py    # Figure 1
python src/build_fig3_drho_panels.py           # Figure 3
python src/build_fig4_tau_before_after.py      # Figure 4
python src/generate_methods_manuscript.py      # full manuscript .docx
```

Each of the four sibling repos must be cloned as a sibling directory (i.e.
under the same parent folder) for the cross-repo figure/data scripts to find
their inputs.

## Status

Manuscript complete and reviewed (data/logic consistency pass + a separate
prose-quality pass). Believed submission-ready pending the corresponding
author's final read. Not yet submitted.

Figures + cross-system dataset archived on Zenodo:
[10.5281/zenodo.22760388](https://doi.org/10.5281/zenodo.22760388).
