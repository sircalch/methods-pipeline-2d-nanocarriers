Don't Fool Yourself When Screening 2D-Nanomaterial Drug Carriers: A
Reproducible GFN2-xTB + Docking + Leak-Free QSAR Pipeline, Four Disease Case
Studies, and a Cautionary Tale
=============================================================================

This record holds the 4 manuscript figures and the cross-system summary
dataset for the Perspective article above, submitted to the Beilstein Journal
of Nanotechnology.

The complete, fully reproducible pipeline (figure generators, cross-repo data
aggregation script, and the manuscript generator itself) is archived on
GitHub at the matching release:

  https://github.com/sircalch/methods-pipeline-2d-nanocarriers/releases/tag/v1.0.0

Files in this record
---------------------
- Figure_1_Pipeline_Schematic.png -- the nine-step reproducible screening
  pipeline described in the manuscript.
- Figure_2_Cross_System_Energy_Regimes.png -- interaction-energy regimes
  across the four disease/carrier systems (real, per-system GFN2-xTB data).
- Figure_3_Delta_rho_Four_Panels.png -- real charge-density-difference
  renders, one per system's strongest-adsorbing complex.
- Figure_4_Tau_Before_After.png -- the Tau/borophene cautionary tale: the
  original unrelaxed drug placement vs. the corrected relaxed chemisorbed
  pose, plus the real 29-compound before/after energy distribution.
- cross_system_summary.csv -- the real headline numbers (n, energy range,
  regime, Q2_CV) pulled from each of the four sibling case-study repositories.

This Perspective synthesizes results already deposited for each of the four
underlying case studies; no new primary computation is reported here beyond
the cross-system comparison itself. Each system's own complete code, curated
dataset, and computational outputs are archived at its own repository and
Zenodo deposit:

- KRAS-G12D / g-C3N4:        10.5281/zenodo.22187819
- Glioblastoma / MXene:      10.5281/zenodo.22187857
- Alzheimer's Tau / borophene: 10.5281/zenodo.22187834
- TNBC / B36N36:             10.5281/zenodo.22187873

Not included by design: the submitted manuscript file and the cover letter
(internal editorial correspondence) are not made public here; the full text
is available from the corresponding author on reasonable request or upon
publication.
