"""sec_introduction.py - Introduction of the audit paper. Numbers from data/audit_evidence.json."""
import docx_kit as k


def introduction(doc, ev, c):
    idt, q = ev["identity"], ev["qspr"]
    v1, v2 = q["KRAS_v1_reproduced"], q["KRAS:dE_int"]
    k.heading(doc, "Introduction")
    k.para(doc,
           "Two-dimensional materials and nanoclusters such as graphitic carbon nitride, MXenes, borophene and "
           "boron nitride cages are frequently proposed as carriers for drugs" +
           c("kroke2002", "naguib2011", "mannix2015", "feng2016", "strout2000") + ". A computational screen of "
           "such a carrier is inexpensive: the drug and the carrier are optimized with a semiempirical method such "
           "as GFN2-xTB," + c("bannwarth2019") + " the drug is docked into its biological target with AutoDock "
           "Vina," + c("trott2010", "eberhardt2021") + " and a quantitative structure–property relationship "
           "(QSPR) model is fitted to the computed energies. For a few dozen drugs the whole workflow runs in "
           "days on a workstation, and the statistical side of it is well codified: nested cross-validation, "
           "Y-randomization and an applicability domain are standard" +
           c("oecd2007", "tropsha2010", "gramatica2007", "rucker2007", "cherkasov2014") + ", and the ways in "
           "which information leaks from test to training data are well documented" + c("kapoor2023") + ".",
           indent=True)
    k.para(doc,
           "Statistical validation, however, can only test the numbers it is given. It cannot tell whether a "
           "SMILES string encodes the molecule named in the table, whether a carrier model is a chemically "
           "possible structure, whether it stays intact during the calculation, or whether the quantum-chemical "
           "method is valid for the material at all. Errors of this kind are known in cheminformatics, where "
           "structure curation has been shown to change the outcome of QSAR studies" +
           c("fourches2010", "fourches2016", "williams2011") + ", and in docking, where the ability of a program "
           "to reproduce known poses has to be demonstrated for each target" + c("warren2006", "bender2021") +
           " and data sets can carry hidden biases" + c("sieg2019") + ". For carrier screens, which add a "
           "materials model and an adsorption calculation to the usual chain, they have received less attention.",
           indent=True)
    k.para(doc,
           "Here we report an audit of four such screens, carried out by the author on the author's own earlier "
           "work. Each "
           "study combined a disease target, a cohort of about 30 drugs and a two-dimensional carrier: KRAS-G12D "
           "with graphitic carbon nitride, triple-negative breast cancer (PARP1) with a B_{36}N_{36} cage, "
           "glioblastoma (EGFR) with a Ti_{3}C_{2}O_{2} MXene, and Alzheimer's disease (tau paired helical "
           "filaments) with β_{12} borophene. All four had been written up for publication, with QSPR models "
           "validated by the protocol described above. Rebuilding each one from raw inputs with scripts revealed eight "
           "distinct failure modes, from the identity of the molecules "
           f"({idt['total']['wrong']} of {idt['total']['n']} structures encoded a different compound) to the "
           "validity of the carrier models and of the methods applied to them. The most instructive case is "
           "the QSPR model of the KRAS study: the same leak-free nested cross-validation, with the same four "
           f"descriptors and the same {v1['n']} drugs, gives *Q*^{{2}}_{{CV}} = {v1['Q2_CV']:.2f} "
           f"(Y-randomization *p* = {v1['p_perm']:.3f}) on adsorption energies computed on a chemically invalid "
           f"carrier and {v2['Q2_CV']:.2f} (*p* = {v2['p_perm']:.2f}) on energies computed on a valid one. The "
           "validation was correct; the data were not.", indent=True)
    k.para(doc,
           "The paper documents each failure mode with the evidence from the four studies and the check that "
           "catches it, and collects the checks into a list that can be applied before any statistics are "
           "computed. All scripts, the files from before and after the rebuild, and the code that extracts every "
           "number quoted here are openly available.", indent=True)
