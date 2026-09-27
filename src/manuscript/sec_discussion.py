"""sec_discussion.py - discussion, the checklist (Table 2), limitations and conclusions."""
import docx_kit as k

CHECKLIST = [
    ("Compound identity", "Retrieve every structure from a database by name or identifier; compare InChIKeys, "
                          "not formulas", "1"),
    ("Carrier composition and bonding", "Formula and bond census of the carrier; no bond that the material "
                                         "cannot contain", "2"),
    ("Carrier stability", "Energy of the carrier at its geometry in each complex never below the relaxed carrier; "
                          "bond census repeated in every complex; dopant sites checked for reconstruction", "3"),
    ("Method applicability", "Test the method on the bare carrier (lattice constant, SCF convergence) before any "
                             "adsorption", "4"),
    ("Docking controls", "Redock the experimental ligand from its conformation and from SMILES; box from the "
                         "experimental ligand; RMSD of every mode, not only the first", "5"),
    ("Provenance", "Every table row traceable to an input structure and an output file", "6"),
    ("Periodic images", "Drug–image distance of every starting geometry", "7"),
    ("Statistics last", "Nested cross-validation and Y-randomization only after checks 1–7; report negative "
                        "results", "8"),
]


def discussion(doc, ev, c):
    idt = ev["identity"]
    k.heading(doc, "Discussion")
    k.para(doc,
           "The eight failure modes fall into two groups. Five of them — the identity of the drugs, the "
           "composition and bonding of the carrier, its stability during the calculation, the applicability of "
           "the method and the periodic images — concern whether the system being computed is the system being "
           "described. The other three concern evidence: whether the docking protocol has been shown to work "
           "for the target, whether every number has a source, and whether a statistical result reflects the "
           "chemistry or the data. None of the eight is detected by the validation that screening studies "
           "usually report, because that validation is internal to the data set. A cross-validated, "
           "Y-randomized model built on the wrong molecules or on an impossible carrier is still "
           "cross-validated and Y-randomized. In the four studies examined here, every failure mode was found "
           "by a check that is cheaper than the calculation it protects.", indent=True)
    k.para(doc,
           "The checks are collected in Table 2, in the order in which they can be applied. Most take seconds "
           "or minutes: a database query, a bond census, a comparison of two energies, a distance. The most "
           "expensive, the redocking controls and the method test on the bare carrier, take hours, which is "
           "still less than the screen itself. Two points deserve emphasis. First, the stability check needs no "
           "extra calculation, because the energy of the carrier fragment at the complex geometry is already "
           "computed for the interaction energy; it only has to be compared with the relaxed carrier. Second, "
           "the docking control should be read mode by mode: a protocol that finds the experimental pose but "
           "ranks it sixth has a scoring problem, not a search problem, and its scores should be reported as "
           "an exploratory ranking.", indent=True)
    k.table(doc, (2, "Checklist for computational screens of drug carriers. Each item corresponds to one "
                     "failure mode in the Results."),
            ["Check", "What to do", "Failure mode"], [[a, b, n] for a, b, n in CHECKLIST], align="llc", font=8.5)
    k.para(doc,
           "The audit also changed what the four studies report. With valid structures and carriers, the "
           "screens describe physisorption on the undoped carriers and chemisorption where the carrier offers a "
           "reactive site (the phosphorus of B/P-doped carbon nitride, the boron of the nitride cage), docking "
           "scores that are a ranking of fit rather than affinities, and descriptor models that do not predict "
           "adsorption energies usefully. These are modest results, and they are the ones the calculations support.", indent=True)
    k.heading(doc, "Limitations", 2)
    k.para(doc,
           "The audit covers four studies by one author, so the frequencies reported here — for instance, "
           f"{idt['total']['wrong']} of {idt['total']['n']} wrong structures — describe these data sets and not "
           "the literature. The checks were chosen because they caught real errors; they are not exhaustive, "
           "and other failure modes, such as the neglect of solvent or of conformational sampling, are not "
           "addressed. The rebuilt studies still rest on gas-phase GFN2-xTB energies for three of the carriers.",
           indent=True)


def conclusions(doc, ev, c):
    q = ev["qspr"]
    k.heading(doc, "Conclusions")
    k.para(doc,
           "Rebuilding four computational screens of drug carriers from raw inputs exposed eight failure modes, "
           "none of which statistical validation can detect: wrong molecules, impossible carriers, carriers "
           "that reconstruct, methods outside their domain, docking controls that fail or cannot fail, data "
           "that were never computed, drugs overlapping their periodic images, and statistics that reflect "
           "these errors. The clearest illustration is a leak-free QSPR model that is significant on energies "
           f"from an invalid carrier (*Q*^{{2}}_{{CV}} = {q['KRAS_v1_reproduced']['Q2_CV']:.2f}) and has no "
           f"predictive power on energies from a valid one ({q['KRAS:dE_int']['Q2_CV']:.2f}). Each failure mode "
           "is caught by a check that costs less than the calculation it protects, and the checks are simple "
           "enough to be applied routinely before any model is fitted.", indent=True)
