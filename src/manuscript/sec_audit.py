"""sec_audit.py - how the audit was carried out (the paper's Methods)."""
from pathlib import Path

import docx_kit as k

BASE_FIG = Path(__file__).resolve().parents[2] / "figures"


def audit_methods(doc, ev, c):
    k.heading(doc, "Methods")
    k.heading(doc, "The four case studies", 2)
    k.para(doc,
           "Each study paired a disease target with a cohort of drugs and a carrier model (Table 1). Before the "
           "audit, each existed as a code repository, a data set and a manuscript; the supporting files of all "
           "four, and a methods description built on them, had been deposited on Zenodo" +
           c("zenodo_kras", "zenodo_tnbc", "zenodo_gbm", "zenodo_tau", "zenodo_methods_v1") + ". Those "
           "records are the pre-audit state that this paper corrects. The audit rebuilt every "
           "study from its raw inputs (drug names, Protein Data Bank structures, carrier lattices) with scripts "
           "that regenerate every number and figure. Files from before the rebuild were moved to an archive and "
           "never deleted, so that each failure mode can be shown with the original files.", indent=True)

    k.heading(doc, "Checks", 2)
    k.para(doc,
           "Eight checks were applied, each at the step of the workflow that it protects (Figure 1). They are "
           "described below in the order of the failure modes they address.", indent=True)
    k.figure(doc, BASE_FIG / "Fig1.png", 1,
             "Workflow of a computational carrier screen and the eight checks of the audit, each attached to "
             "the step it protects; the numbers correspond to the failure modes in the Results and to the "
             "checklist in Table 2")
    k.para(doc,
           "*Compound identity.* The SMILES string of every drug was compared with the PubChem" + c("kim2021") +
           " record retrieved by name, through the InChIKey. A structure was counted as wrong when its "
           "molecular formula or its connectivity (first InChIKey block) differed from PubChem; differences only "
           "in stereochemistry, salt form or charge state were accepted.", indent=True)
    k.para(doc,
           "*Carrier validity.* For each carrier model the formula and a census of bonds were computed, a bond "
           "being any atom pair closer than 1.15 times the sum of the covalent radii. Bonds that the ideal "
           "material cannot contain were counted: C–C and N–N in heptazine carbon nitride, B–B and N–N in boron "
           "nitride, and C–C, C–O and O–O in Ti_{3}C_{2}O_{2}. In boron nitride cages the transannular "
           "B···B contact across a four-membered B_{2}N_{2} ring (about 1.86 Å) falls inside the bond criterion; "
           "such pairs, recognized because they share two nitrogen neighbours, were counted separately and not "
           "as bonds.", indent=True)
    k.para(doc,
           "*Carrier stability.* A carrier model is only useful if it keeps its structure during the adsorption "
           "calculation. For every complex, the energy of the carrier fragment frozen at its geometry in the "
           "complex was compared with the energy of the isolated relaxed carrier. Distortion away from the "
           "relaxed minimum raises that energy; a value below the relaxed reference means that the carrier has moved to a different, "
           "lower-energy structure. The bond census of the carrier was also repeated in every complex.",
           indent=True)
    k.para(doc,
           "*Method applicability.* Before adsorption was computed on the metallic MXene, the tight-binding "
           "methods were tested on the material alone: the energy of a periodic Ti_{3}C_{2}O_{2} slab was "
           "scanned against the in-plane lattice constant with GFN2-xTB" + c("bannwarth2019") + " and "
           "GFN1-xTB" + c("grimme2017") + ", and finite flakes were computed in several charge and spin states "
           "and electronic temperatures.", indent=True)
    k.para(doc,
           "*Docking controls.* In each target the crystallographic or cryo-EM ligand was redocked from its "
           "experimental conformation and, rebuilt from SMILES, through the same protocol used for the cohort. "
           "The heavy-atom root-mean-square deviation (RMSD) to the experimental pose was computed with RDKit," +
           c("rdkit") + " symmetry-aware and without re-alignment, for the top-ranked pose and, where it "
           "failed, for every output mode. The placement of the docking box was also checked.", indent=True)
    k.para(doc,
           "*Provenance.* Every row of every table was traced back to an input structure and an output file of "
           "the program that produced it.", indent=True)
    k.para(doc,
           "*Periodic images.* In the periodic calculations, the shortest distance between each drug and its "
           "own in-plane images was computed for the starting geometry of every complex.", indent=True)
    k.para(doc,
           "*QSPR.* The rebuilt studies share one QSPR implementation: a ridge-regression pipeline "
           "(scikit-learn" + c("pedregosa2011") + ") with standardization inside the pipeline, nested five-fold "
           "cross-validation (five inner folds for the penalty), 1,000 Y-randomizations of the whole nested "
           "procedure" + c("rucker2007") + ", and a leverage applicability domain" +
           c("oecd2007", "tropsha2010") + ". To separate the effect of the data from that of the protocol, the "
           "same code was also applied to the adsorption energies of the pre-rebuild KRAS study.", indent=True)

    k.heading(doc, "Software and data", 2)
    k.para(doc,
           "The rebuilt studies used xtb 6.7.1 and tblite (GFN2-xTB, GFN1-xTB), AutoDock Vina 1.2.7" +
           c("eberhardt2021") + " with Meeko and PDBFixer, RDKit, scikit-learn and, for the MXene, Quantum "
           "ESPRESSO 7.5" + c("giannozzi2017") + " with the PBE functional" + c("perdew1996") + " and D3 "
           "dispersion" + c("grimme2010") + ". The scripts that extract the evidence for this paper from the four "
           "repositories and from the archive of the pre-rebuild files are part of its own repository.",
           indent=True)
