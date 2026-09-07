# Methods paper — outline (option 2c)

**Working title:** *Don't fool yourself when screening 2D-nanomaterial drug
carriers: a reproducible GFN2-xTB + docking + leak-free QSAR pipeline, with four
disease case studies and a cautionary tale.*

**Format / venue candidates:** Beilstein J. Nanotechnol. (Full Research Paper or
Perspective); *J. Chem. Inf. Model.* (methods); *Digital Discovery*; *Molecular
Systems Design & Engineering*. Decide before drafting the full text.

**Status:** scaffold only. Data + figures for all four systems already exist in
the four sibling repos. This paper needs writing, not computation.

---

## 1. Introduction — the problem

- 2D nanomaterials (g-C₃N₄, MXenes, borophene, BN nanostructures) are widely
  proposed as drug-delivery scaffolds; the computational screening literature is
  large and growing.
- Recurrent methodological failures make many of those screens unreliable:
  1. **Fabricated regression targets** — a "ΔG_bind" or "ΔE_ads" that is an
     empirical linear formula over RDKit descriptors, printed as if it were a
     QM result.
  2. **Data leakage** — feature scaling / selection fitted on the whole set
     before cross-validation, inflating Q².
  3. **Unrelaxed adsorption geometries** — a single point on a drug "placed"
     above the sheet, never optimised.
  4. **Un-run benchmarks** — a "DFT validation" table with no output files.
  5. **Cohort / bibliography drift** — descriptor set, docking cohort and
     reference list from three different studies.
- We built one pipeline that avoids all five, applied it to four disease systems,
  and document what broke when we did not.

## 2. The pipeline (Methods = the paper's core)

For each (drug, 2D-carrier) pair:

1. **Structures** — drug from SMILES (RDKit ETKDG + MMFF) → GFN2-xTB opt;
   carrier as an explicit H-terminated cluster, GFN2-xTB opt.
2. **Adsorption** — place the drug 3.2 Å above the *local* sheet surface (not
   z_max of an edge atom — see §4), 4 in-plane orientations, **optimise every
   complex**, keep the lowest-energy pose with a heavy-atom contact of
   1.25–4.0 Å. Report
   - ΔE_int,SP = E(AB) − E(A) − E(B), fragments frozen at the complex geometry;
   - ΔE_ads with relaxed fragments;
   - regime label: contact < 1.9 Å ⇒ chemisorption (covalent B–X / metal–X).
3. **Charge-density difference** — GFN2-xTB densities of complex/carrier/drug on
   one grid (Multiwfn) → Δρ isosurface (ChimeraX).
4. **Docking** — AutoDock Vina against the disease target's experimental
   structure; reported as a *relative* surface/cleft ranking, not ΔG.
5. **Descriptors** — conceptual-DFT global indices (η, S, χ, μ, ω) read from the
   same xTB output; no empirical estimation.
6. **Surrogate model** — StandardScaler + RidgeCV inside a **leak-free nested
   5×5 CV**; 1000-permutation Y-scrambling; reported Q²_CV with its p-value.
7. **Applicability domain** — OECD Principles 1–5, Williams hat-matrix leverage.
8. **Figures** — one shared house style (`_pubstyle`), PyMOL for
   protein–ligand / complexes, ChimeraX for Δρ.
9. **Reproducibility** — `run_entire_<system>_study.py` regenerates every number
   and figure from raw inputs; code + Zenodo.

**Figure 1** — pipeline schematic.

## 3. Four case studies (one short subsection each)

| System | Carrier | Hero drug | ΔE (kcal/mol) | Regime | Physisorption QSPR Q²_CV |
|---|---|---|---|---|---|
| KRAS-G12D / PDAC | g-C₃N₄ (B,P-doped) | MRTX1133 | −5.0 … −39.9 | physisorption, doping-tuned; ΔQ +0.15 e | (separate 33-cpd model, weak) |
| Glioblastoma | Ti₃C₂O₂ MXene | Larotrectinib | −0.9 … −15.5 | physisorption | 0.10 |
| Triple-neg. breast | B₃₆N₃₆ nanocage | Olaparib | −16.4 … +0.1 | weak physisorption | negative |
| Alzheimer Tau | β-12 borophene | curcumin | **−8 … −233** | **mixed: 12 chemisorb / 17 physisorb** | 0.06 |

**Figure 2** — interaction-energy regimes across the four systems (built).
**Figure 3** — the four Δρ panels side by side.

Common finding: **none of the four bare carriers gives a predictive
descriptor-based QSPR of the adsorption energy** (Q²_CV ≤ 0.1). The value of the
screen is the *mechanistic* picture (regime, Δρ, doping effect), not a model.

## 4. The cautionary tale — Tau / borophene

- Original dataset: `delta_Eint_SP` = a GFN2-xTB **single point** on a geometry
  where the drug was offset 3.2 Å from **z_max of the buckled B40H15 flake** —
  i.e. 3.2 Å above an edge H, leaving the drug 5–6 Å from the sheet it should
  sit on. Never optimised. Result: −0.9 to −13.8 kcal/mol, read as
  "dispersion-dominated physisorption," with Tideglusib (whose SMILES was also
  truncated) as the "strongest binder."
- After relaxation: 12/29 ligands **chemisorb** (covalent B–C/B–O, −81 to
  −233 kcal/mol); the rest physisorb at −8 to −44. Pristine β-12 borophene is a
  reactive surface, not a reversible carrier, for π-rich phenols and dyes.
- **Figure 4** — Tau before/after: the old unrelaxed placement vs the relaxed
  chemisorbed pose, with the two ΔE distributions.
- Lessons, stated as rules:
  1. Always optimise the complex; a single point on a placed geometry is not an
     adsorption energy.
  2. Reference the offset to the local surface height under the adsorbate, never
     to a global z-extremum of a finite, buckled cluster.
  3. Check the closest contact after optimisation; classify chemi/physisorption
     explicitly.
  4. Verify every drug structure against its formula before running 30 jobs.

## 5. Catalogue of failure modes fixed across the four projects

(from the project history — condense the scAMH scopeNotes)

- fabricated `Target_DeltaG_bind` empirical formula (all 4) → real xTB endpoint
- `StandardScaler` fitted pre-CV (KRAS) → Pipeline inside nested CV
- hardcoded post-hoc statistics (Dunn p) → computed
- wrong bibliography imported (KRAS used TNBC's) → per-project verified lists
- `np.random.uniform` fallback for leverages → `raise`
- "Multilevel DFT benchmark" tables with no ORCA output → removed
- schematic "3D" figures that were text cards → real renders
- docking cohort ≠ descriptor cohort ≠ reference list → single master table

## 6. Conclusion

A rigorous screen of a 2D drug carrier is cheap (GFN2-xTB + Vina, hours on a
workstation) but only if the geometry is relaxed, the target is real, and the CV
is leak-free. Under those conditions the honest outcome for all four systems here
is modest — physisorption in the −10 to −40 kcal/mol range, no predictive QSPR —
except where the surface is reactive enough to chemisorb, which the unrelaxed
protocol hides entirely.

---

## Assets already available

- `data/cross_system_summary.csv`, `figures/fig2_cross_system_energy_regimes.png` (built)
- Δρ panels: `<each repo>/results/quantum/drho/*_deltarho_render.png`
- Tau recompute: `borophene-alzheimer-tau-ai/calculations/tau_recompute/results.csv`
- All 4 `run_entire_*_study.py`, all 4 manuscripts, `BEILSTEIN_FORMAT_CHECKLIST.md`
