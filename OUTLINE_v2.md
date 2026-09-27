# Methods paper, version 2 — outline (2026-09-26)

Replaces OUTLINE.md. Version 1 (Zenodo v1.0.1, 2026-09-14) rests on results that the
2026-09 rebuild of the four case studies showed to be wrong; see "What changed" below.
Every number in the paper must come from a file in the four repos or in data/ here.

## Working title
Auditing computational screens of 2D-nanomaterial drug carriers: eight failure modes
found by rebuilding four case studies, and a checklist to catch them

## Core message
A screen of drug–carrier pairs can be internally consistent, leak-free and well
validated statistically, and still be wrong, because the errors sit upstream of the
statistics: in what the molecules are, what the carrier is, whether the method can
describe it, and whether the controls pass. Rebuilding four published-style screens
from raw inputs exposed eight such failure modes. The paper documents each one with
its evidence and the check that catches it.

## Failure modes and evidence (source file)

| # | Failure mode | Evidence | Check |
|---|---|---|---|
| 1 | Wrong molecule for the name | 55 of 128 SMILES encoded a different compound (KRAS 0/33, TNBC 24/33, GBM 17/33, Tau 14/29) — `_auditoria_estructuras_2026-09-22/` | InChIKey against PubChem |
| 2 | Chemically invalid carrier | old B36N36 with 36 B–B, 24 N–N and 60 B–N bonds; old g-C3N4 C21N21H6 and MXene Ti12C7O14 each with 4 C–C bonds — `data/carrier_audit.csv` | stoichiometry + forbidden-bond census |
| 3 | Carrier reconstructs during adsorption | unconstrained B40H15 borophene: carrier energy in the complex up to 110 kcal/mol below its "minimum"; B/P g-C3N4: lower-energy dopant sites are P reconstructions, not substitution | E(carrier@complex) ≥ E(carrier, relaxed); bond census of the carrier in every complex |
| 4 | Method outside its domain | GFN2-xTB puts the Ti3C2O2 lattice at 2.70 Å (3.03 Å), 31 eV/f.u. jump; GFN1 fails; finite flake: 1/18 neutral SCF | lattice scan / SCF test before any adsorption |
| 5 | Docking control not passed or not meaningful | Tau: box centred on docked poses (circular), ligand-free fibril 6.7/6.3 Å; GBM: covalent osimertinib 8.6 Å, erlotinib correct pose only as mode 6; TNBC/KRAS pass (0.51/1.27, 0.51/1.25 Å) | redock from crystal and from SMILES; RMSD of every mode |
| 6 | Data that were never computed | KRAS "350-compound virtual library" = descriptor vectors without structures | every table row traceable to an input structure and an output file |
| 7 | Periodic-image artefacts | procarbazine overlaps its image (0.56 Å) in the 12.1 Å MXene cell | drug–image distance of each start geometry |
| 8 | Statistics that look like a result | QSPR after rebuild: KRAS Q² −0.32, TNBC −0.08/−0.08, Tau 0.23 (charge only), GBM docking 0.17; v1 reported KRAS 0.51–0.58 | nested CV + Y-scrambling on the rebuilt data; report negative results |

## Sections
1. Introduction — screening literature; why validation statistics are not enough.
2. The four case studies in one paragraph each (target, carrier, cohort size).
3. The audit: how it was done (rebuild from raw inputs with scripts, archive, never delete).
4. Failure modes 1–8, one subsection each: what happened, the evidence, the effect on the
   conclusions, the check. Figure per group of modes.
5. What the rebuilt studies show (short): regime counts, energies, QSPR, docking —
   as outcomes, not as selling points.
6. Checklist (table) — the paper's main deliverable.
7. Limitations — GFN2-xTB/gas phase, finite carriers, rigid docking; audit by one author.

## Figures (planned)
1. Audit workflow and the eight checks along the pipeline.
2. Identity and carrier validity: wrong-structure counts per study; before/after carriers
   with forbidden bonds highlighted.
3. Carrier reconstruction (Tau): carrier energy in each complex, before/after; B/P scan.
4. Method applicability: xTB lattice scans (from GBM Fig. 4b data).
5. Docking controls: RMSD vs mode for the four targets.
6. QSPR before/after rebuild.

## What changed from version 1 (to state openly in the paper and on Zenodo)
- KRAS "predictive QSPR" (Q² 0.51–0.58) → −0.32 on the rebuilt data.
- TNBC 5 chemisorbed / 25 physisorbed on an invalid cage → 12 / 18 on a valid cage.
- Tau "hidden chemisorption, 12 of 29" → mostly carrier collapse; 3 of 28 on the stable sheet.
- GBM MXene physisorption from an invalid Ti12C7O14 cluster → xTB inapplicable; PBE-D3.

## Open decisions (user)
- Authorship: v1 listed three authors; the rebuilt case studies are single-author.
- Venue: Beilstein J. Nanotechnol. (Perspective) or J. Chem. Inf. Model.
