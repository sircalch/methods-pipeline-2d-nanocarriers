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

## Open
- a = 3.03 Å for Ti3C2O2 is attributed to Khazaei et al. (2013), both here and in the GBM
  paper. That paper could not be accessed to confirm that it reports this value for
  Ti3C2O2 (it mainly covers M2X MXenes). Open sources give 3.038 Å (PBE) for Ti3C2O2 and
  about 3.05 Å for Ti3C2Tx (XRD). Before submission: confirm it in the paper or cite a
  source that states the value.
