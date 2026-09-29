# Verification of the audit paper (2026-09-28)

Most numbers come from the four case-study repositories. Each of those was verified
independently; see `results/verification/VERIFICATION_REPORT.md` in each repository.
The checks specific to this paper:

| What | How | Result |
|---|---|---|
| Identity counts (55 of 128) | audit tables plus the six lookups resolved later (audit_resolved_lookups.csv) | 55/128. KRAS 0/33 and TNBC 24/33 confirmed against PubChem |
| B/P scan rejections | bonding re-analysed from the 19 relaxed geometries | 17 with four-coordinate P, 2 with an N–N bond (text corrected) |
| Tau pre-audit claim | read from the pre-audit SI (Zenodo deposit) | "12 of the 29 ligands" chemisorbed (now cited) |
| Virtual screen of 350 rows | archived script generate_master_kras_dataset.py | descriptors = scaffold value + np.random.uniform(...) (claim confirmed) |
| Tight-binding lattice scan (GBM) | full rerun with tblite (micromamba env 'tb') | 28/28 points, same status, \|ΔE\| ≤ 7e-8 eV/f.u. |
| Finite-flake tests (GBM) | convergence read from the 23 raw xtb outputs | table = raw in 23/23; 1 of 18 neutral attempts converged |
| References | Crossref (full author lists); relevance read sentence by sentence | refs 1–5 of the introduction did not support "proposed as drug carriers" (they were synthesis/structure papers) and were replaced by carrier papers: Pourmadadi 2023, Huang 2018, Li & Zhao 2023, Gholami 2023 |

## Resolved (2026-09-29): lattice constant of Ti3C2O2
- "a = 3.03 Å" was attributed to Khazaei et al. (2013), and so was "Ti3C2O2 is metallic",
  in this paper and in the GBM paper. That paper could not be accessed to confirm either
  claim for Ti3C2O2 (it mainly covers M2X MXenes).
- Both claims now rest on our own calculation, with the settings of the GBM slab
  (PBE-D3, SSSP 1.3, 50/400 Ry, MV 0.01 Ry). A vc-relax of the primitive cell at 12×12×1
  converged in 9 BFGS steps to a = 3.022 Å, with −0.15 kbar residual. A tetrahedron DOS at
  24×24×1 gives 1.03 states/eV per formula unit at E_F, so the material is metallic.
  Files: GBM `calculations/gbm_dft/lattice_primitive/`, collected by
  `src/quantum/collect_primitive.py` into `results/quantum/ti3c2o2_primitive_pbe_d3.json`.
- Khazaei 2013 has been removed from both papers. Fig. 4a and result 4 now use the
  computed 3.02 Å (GFN2 minimum 2.70 Å, still 11% below). The GBM slab keeps
  a = 3.03 Å, which is 0.3% above the optimum; this is stated in its Methods and Table S5.
