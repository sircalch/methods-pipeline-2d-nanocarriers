# methods-pipeline-2d-nanocarriers

Methods / perspective paper (option **2c**) that ties together the four sibling
nano-QSAR case studies:

- `kras-pancreatic-gC3N4-ai` — MRTX1133 on B,P-doped g-C₃N₄ (PDAC)
- `mxene-glioblastoma-qsar-ai` — kinase inhibitors on Ti₃C₂O₂ MXene (GBM)
- `nano-qsar-ai-therapeutics` — PARP inhibitors on B₃₆N₃₆ nanocage (TNBC)
- `borophene-alzheimer-tau-ai` — Tau ligands on β-12 borophene (AD)

**Thesis:** a rigorous screen of a 2D drug carrier is cheap (GFN2-xTB + Vina,
hours) but only if the adsorption geometry is *relaxed*, the regression target is
*real*, and the cross-validation is *leak-free*. Under those conditions the four
carriers here give modest physisorption and no predictive QSPR — except β-12
borophene, which chemisorbs 12/29 Tau ligands, a result the common unrelaxed
single-point protocol hides completely.

## Status: scaffold

- `OUTLINE.md` — full section-by-section outline with the argument sketched.
- `src/gather_cross_system_summary.py` → `data/cross_system_summary.csv`,
  `figures/fig2_cross_system_energy_regimes.png`.
- Manuscript text not yet written — waiting on venue/framing decision.

## To do

1. Pick venue (Beilstein Perspective / JCIM methods / Digital Discovery).
2. Write the manuscript (`src/generate_methods_manuscript.py`, reuse
   `src/_pubstyle.py` + `src/_backmatter.py`).
3. Figure 1 (pipeline schematic), Figure 3 (4 Δρ panels), Figure 4 (Tau
   before/after).
4. Reference list.
