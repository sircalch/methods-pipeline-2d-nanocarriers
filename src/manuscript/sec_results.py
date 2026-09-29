"""sec_results.py - the eight failure modes, each with its evidence. Numbers are read from
data/audit_evidence.json, data/carrier_audit.csv and the audit tables; nothing is typed by hand."""
from pathlib import Path

import pandas as pd
from rdkit import Chem

import docx_kit as k

BASE = Path(__file__).resolve().parents[2]
P = BASE.parent
FIG = BASE / "figures"


def f1(x):
    return f"{x:.1f}".replace("-", "−")


def f2(x):
    return "0.00" if abs(x) < 0.005 else f"{x:.2f}".replace("-", "−")


def identity_examples():
    rows = []
    for s, f in (("TNBC", "tnbc"), ("GBM", "gbm"), ("Tau", "tau")):
        a = pd.read_csv(P / "_auditoria_estructuras_2026-09-22" / f"audit_{f}.csv")
        for r in a[a.verdict.str.contains("WRONG")].itertuples():
            m1, m2 = Chem.MolFromSmiles(r.ours_smiles), Chem.MolFromSmiles(r.pubchem_smiles)
            if m1 is not None and m2 is not None:
                rows.append((s, r.name, r.ours_formula, r.pubchem_formula, m1.GetNumHeavyAtoms(),
                             m2.GetNumHeavyAtoms()))
    df = pd.DataFrame(rows, columns=["study", "name", "ours", "real", "ha_ours", "ha_real"])
    df["d"] = (df.ha_real - df.ha_ours).abs()
    return df


def sub(formula):
    import re
    return re.sub(r"(\d+)", r"_{\1}", formula)


def census(txt):
    """'B-B 36; B-N 60; N-N 24' -> {'B-B': 36, ...}"""
    out = {}
    for part in txt.split(";"):
        part = part.strip()
        if part and part != "none":
            name, n = part.rsplit(" ", 1)
            out[name] = int(n)
    return out


def results(doc, ev, c):
    idt, rc, me, dk, fab, per, q = (ev[x] for x in ("identity", "reconstruction", "method", "docking",
                                                      "fabricated", "periodic", "qspr"))
    ca = pd.read_csv(BASE / "data" / "carrier_audit.csv").set_index(["system", "model"])
    ex = identity_examples()
    worst = ex.sort_values("d", ascending=False).iloc[0]
    same = ex[ex.ours == ex.real]
    k.heading(doc, "Results")

    # 1 identity
    k.heading(doc, "1. The molecule is not the one named", 2)
    k.para(doc,
           f"Of the {idt['total']['n']} drug structures in the four data sets, {idt['total']['wrong']} encoded a "
           f"different compound from the one named (Fig. 2a, Table S1): none of {idt['KRAS']['n']} in the KRAS study, but "
           f"{idt['TNBC']['wrong']} of {idt['TNBC']['n']} for TNBC, {idt['GBM']['wrong']} of {idt['GBM']['n']} "
           f"for glioblastoma and {idt['Tau']['wrong']} of {idt['Tau']['n']} for tau. Some errors changed the "
           f"molecule beyond recognition: {worst['name'].lower()} in the "
           f"{ {'GBM': 'glioblastoma', 'TNBC': 'TNBC', 'Tau': 'tau'}[worst.study]} set was stored as "
           f"{sub(worst.ours)} ({worst.ha_ours} heavy atoms) instead of {sub(worst.real)} ({worst.ha_real}). "
           f"Others were invisible to a formula check: {len(same)} structures had the correct formula and the "
           "wrong connectivity, among them doxorubicin and epirubicin, and were found only through the InChIKey. "
           "Every descriptor, docking score and adsorption energy computed from these structures belonged to "
           "another molecule. This failure mode is well known in cheminformatics" + c("fourches2010", "williams2011") +
           "; it went unnoticed here because the SMILES strings had never been checked against a chemical "
           "database, and no later step of the workflow depends on the name of a compound.",
           indent=True)

    # 2 carrier validity
    k.heading(doc, "2. The carrier is not the material", 2)
    tb, gb, kb = ca.loc[("TNBC", "before")], ca.loc[("GBM", "before")], ca.loc[("KRAS", "before")]
    tbc, kbc, gbc = census(tb.bonds), census(kb.forbidden_bonds), census(gb.forbidden_bonds)
    k.para(doc,
           "Three of the four carrier models were not the materials they were named after (Fig. 2b, Table S2). The "
           f"B_{{36}}N_{{36}} cage of the TNBC study had the right formula but {tbc['B-B']} B–B and {tbc['N-N']} "
           f"N–N bonds and only {tbc['B-N']} B–N bonds, whereas in a boron nitride cage every bond joins boron to "
           "nitrogen" + c("strout2000") + f". Worse, {int(tb.overlapping_pairs)} of those B–N pairs were atoms "
           f"placed almost on top of each other, as close as {f2(tb.min_distance_A)} Å. The graphitic carbon nitride model of the KRAS study, "
           f"{sub(kb.formula)}, had the wrong stoichiometry for heptazine-based g-C_{{3}}N_{{4}}" + c("kroke2002") +
           f" and {kbc['C-C']} C–C bonds. The MXene of the glioblastoma study, {sub(gb.formula)}, did not have "
           f"the Ti_{{3}}C_{{2}}O_{{2}} composition and contained {gbc['C-C']} C–C bonds. The rebuilt models — a heptazine pore "
           f"flake ({sub(ca.loc[('KRAS', 'after')].formula)}), a cage with 108 B–N bonds, and a periodic "
           "Ti_{3}C_{2}O_{2} slab — contain no forbidden bond. A bond census of this kind takes seconds and would "
           "have rejected all three models before any adsorption was computed.", indent=True)
    k.figure(doc, FIG / "Fig2.png", 2,
             "Identity of the drugs and validity of the carriers before the rebuild. (a) Drug structures that "
             "match PubChem and structures that encode a different compound, per study; hatched, same formula "
             "but different connectivity. (b) Bonds that the ideal material cannot contain, in the carrier "
             "models before and after the rebuild; formulas below each study. (c) The three invalid carrier models, "
             "drawn with the bond criterion of the audit; bonds that the material cannot contain in amber. In the "
             "B_{36}N_{36} model, pairs of boron and nitrogen atoms sit almost on top of each other")

    # 3 reconstruction
    k.heading(doc, "3. The carrier changes during the calculation", 2)
    t = rc["tau_old"]
    k.para(doc,
           "A carrier can be chemically valid and still not survive the adsorption calculation. The β_{12} "
           "borophene flake of the tau study (B_{40}H_{15}) was a true minimum with no imaginary frequencies, "
           f"but in {t['n_below_min']} of {t['n']} complexes the carrier fragment ended "
           f"below that minimum, by up to {f1(-t['min_kcal'])} kcal mol^{{−1}} (Fig. 3a, Table S3): the free flake "
           "contracted toward a compact boron cluster, and the computed binding energies contained the energy "
           f"of that reconstruction. The classification of the drugs was affected as well: on the free flake "
           f"{t['chem_old']} of {t['n']} drugs appeared to chemisorb (Fig. 3b), and the version of the study "
           "deposited before the audit" + c("zenodo_tau") + f" had reported {rc['tau_v1_reported']['chem']} of "
           f"{rc['tau_v1_reported']['n']} ligands as chemisorbed on the same flake. Borophene exists only on a "
           "supporting metal" + c("feng2016", "mannix2015") +
           ", which keeps it planar; a flat β_{12} sheet with its boron atoms restrained to the lattice does not "
           f"reconstruct (carrier energy in the complexes {f1(rc['tau_new_dcar_kcal'][0])} to "
           f"{f1(rc['tau_new_dcar_kcal'][1])} kcal mol^{{−1}} above its reference), and on it only "
           f"{t['chem_new']} of {t['n_new']} drugs chemisorb. The rebuilt B_{{36}}N_{{36}} cage passes the same "
           f"test ({f1(rc['tnbc_cage_dcar_kcal'][0])} to {f1(rc['tnbc_cage_dcar_kcal'][1])} kcal mol^{{−1}}).",
           indent=True)
    kb2 = rc["kras_bp"]
    k.para(doc,
           "The same test applies to doped carriers. In a scan of boron/phosphorus co-doping sites in "
           f"g-C_{{3}}N_{{4}}, {kb2['n_rejected_lower']} of {kb2['n_configs']} configurations were lower in energy "
           f"than the substitutional one finally used, by up to {f1(kb2['lowest_rejected_below_accepted_kcal'])} "
           "kcal mol^{−1}, but none of them was the doped material: in " + f"{kb2['n_P_fourcoord']}" + " of them "
           "phosphorus had become four-coordinate, and in the other " + f"{kb2['n_NN_bond']}" + " the lattice had "
           "formed an N–N bond. Ranking by energy alone would have selected a structure that is no longer the doped "
           "material; the bond census of the carrier has to accompany the energy.", indent=True)
    k.figure(doc, FIG / "Fig3.png", 3,
             "Carrier reconstruction during adsorption. (a) Energy of the carrier fragment frozen at its geometry "
             "in each complex, relative to the relaxed carrier; negative values (shaded) mean that the carrier "
             "reached a structure below its own minimum. (b) Number of tau drugs classified as chemisorbed on "
             "the free flake and on the supported sheet. (c) Galantamine, the extreme case: the free B_{40}H_{15} flake "
             "relaxed alone, the same flake in the relaxed complex, which has collapsed into a three-dimensional "
             "cluster, and the supported β_{12} sheet in the relaxed complex (GFN2-xTB, side views)")

    # 4 method
    k.heading(doc, "4. The method cannot describe the carrier", 2)
    k.para(doc,
           "For the MXene, the problem was the method rather than the model. GFN2-xTB places the energy minimum "
           f"of periodic Ti_{{3}}C_{{2}}O_{{2}} at a = {f2(me['gfn2_min_a'])} Å, "
           f"{100 * (me['a_ref'] - me['gfn2_min_a']) / me['a_ref']:.0f}% below the PBE-D3 lattice constant of the "
           f"material ({f2(me['a_ref'])} Å, computed here for the primitive cell with the settings of the case study), with a jump of {f1(me['gfn2_max_jump_eV'])} eV per "
           f"formula unit between neighbouring points; GFN1-xTB failed to converge at {me['gfn1_failed']} of "
           f"{me['gfn1_n']} lattice constants and gave unphysical energies at {me['gfn1_unphysical']} more "
           f"(Fig. 4a). Finite flakes fared no better: {me['flake_neutral_converged']} of "
           f"{me['flake_neutral_attempts']} calculations on neutral flakes converged (Fig. 4b). Both methods "
           "were parametrized mainly on molecular data" + c("grimme2017", "bannwarth2019") + ", and a metallic "
           "transition-metal carbide lies outside that domain. A lattice scan of the bare carrier, which costs "
           "minutes, is enough to see it; the glioblastoma study was therefore moved to periodic density "
           "functional theory.", indent=True)
    k.figure(doc, FIG / "Fig4.png", 4,
             "Tight-binding methods applied to Ti_{3}C_{2}O_{2}. (a) Energy of a periodic 4×4 slab against the "
             "in-plane lattice constant with GFN2-xTB and GFN1-xTB; crosses, failed or unphysical SCF; dotted "
             "line, PBE-D3 lattice constant computed for the primitive cell. (b) Calculations on finite flakes attempted and "
             "converged, for neutral and charged flakes")

    # 5 docking
    k.heading(doc, "5. The docking control fails, or tests the wrong thing", 2)
    ctl = {s: [d["rmsd_A"] for d in dk[s]] for s in ("KRAS", "TNBC", "Tau", "GBM")}
    old = [d["rmsd_A"] for d in dk["GBM_4ZAU_before"]]
    modes = pd.DataFrame(dk["GBM_modes"])
    bx = modes[modes.control.str.startswith("self")].sort_values("rmsd_A").iloc[0]
    span = modes.groupby("control").vina_kcal_mol.agg(lambda v: v.max() - v.min()).max()
    k.para(doc,
           "Two of the four docking protocols reproduced the experimental ligand pose from both its crystal "
           f"conformation and from SMILES: KRAS-G12D ({f2(ctl['KRAS'][0])} and {f2(ctl['KRAS'][1])} Å) and PARP1 "
           f"({f2(ctl['TNBC'][0])} and {f2(ctl['TNBC'][1])} Å) (Fig. 5a, Table S4). The other two did not, and each "
           "failure carried information. The tau study had first docked into a fibril structure without any "
           "ligand, with a box centred on previously docked poses, so that the protocol could not fail; in a "
           "cryo-EM structure with a bound tracer" + c("merz2023") + ", the tracer is not reproduced in the "
           f"ligand-free fibril ({f1(ctl['Tau'][0])} and {f1(ctl['Tau'][1])} Å) and only partly when the stacked "
           f"neighbouring copies are kept ({f2(ctl['Tau'][2])} and {f2(ctl['Tau'][3])} Å). The glioblastoma study "
           f"had first validated against a covalent inhibitor, which a non-covalent program is not designed to place "
           f"({f1(old[0])} and {f1(old[1])} Å). With the non-covalent erlotinib complex" + c("stamos2002") +
           f", the top-ranked pose still failed ({f1(ctl['GBM'][0])} and {f1(ctl['GBM'][1])} Å), yet the "
           f"crystal-like pose was present as mode {int(bx['mode'])} ({f2(bx.rmsd_A)} Å), and all nine modes lay "
           f"within {f2(span)} kcal mol^{{−1}} (Fig. 5b): the search found the pose, and the score could not "
           "rank it. Inspecting every mode, not only the first, distinguishes these cases" +
           c("warren2006", "bender2021") + ".", indent=True)
    k.figure(doc, FIG / "Fig5.png", 5,
             "Redocking controls. (a) RMSD of the top-ranked pose to the experimental pose for each control and "
             "target; crystal, ligand redocked from its experimental conformation; SMILES, ligand rebuilt through "
             "the production protocol; empty and stack, tau fibril without ligands or with the neighbouring "
             "tracer copies. (b) RMSD of every Vina mode for erlotinib in EGFR")

    # 6 fabricated
    k.heading(doc, "6. Data that were never computed", 2)
    k.para(doc,
           f"The KRAS study reported a virtual screen of {fab['n_rows']} candidate molecules. The file contains no "
           "structure: no SMILES, InChI or InChIKey, only a compound identifier, a parent scaffold and descriptor "
           f"values. The script that produced it generated those values by adding random numbers to the descriptors "
           f"of a few parent scaffolds ({fab['n_scaffolds']} of them appear in the final table), and a "
           "'predicted' binding energy was then computed from the random descriptors. "
           "Such a table can pass every statistical test, because it is internally consistent by construction. "
           "The only check that exposes it is provenance: each row must lead to an input structure and to an "
           "output file of the program that computed its value.", indent=True)

    # 7 periodic images
    k.heading(doc, "7. The drug meets itself", 2)
    img, ln = per["image_distance_A"], per["drug_length_A"]
    ok = {k_: v for k_, v in img.items() if k_ != "Procarbazine"}
    k.para(doc,
           f"In periodic calculations the drug interacts with its own images. In the {f1(per['cell_A'])} Å cell of "
           f"the MXene slab, procarbazine, {f1(ln['Procarbazine'])} Å long, overlapped its image "
           f"({f2(img['Procarbazine'])} Å between atoms) and "
           "was removed from the calculation; the other drugs were rotated where necessary so that their "
           f"closest image contact was {f2(min(ok.values()))}–{f2(max(ok.values()))} Å. The check is a distance "
           "calculation on the starting geometry.", indent=True)

    # 8 statistics
    k.heading(doc, "8. Statistics that look like a result", 2)
    v1, v2 = q["KRAS_v1_reproduced"], q["KRAS:dE_int"]
    k.para(doc,
           "The QSPR model of the KRAS study illustrates why none of the checks above can be left to the "
           "statistics. With the same code, the same four descriptors and the same "
           f"{v1['n']} drugs, nested cross-validation gives *Q*^{{2}}_{{CV}} = {f2(v1['Q2_CV'])} with a "
           f"Y-randomization *p* of {v1['p_perm']:.3f} on adsorption energies computed on the invalid carrier, "
           f"and {f2(v2['Q2_CV'])} (*p* = {v2['p_perm']:.2f}) on energies computed on the valid one (Fig. 6a, "
           "b). The first model is leak-free and significant, and it describes a material that does not exist. "
           "Across the rebuilt studies, no descriptor model predicts its target usefully: the TNBC models give *Q*^{2}_{CV} = "
           f"{f2(q['TNBC:delta_Eint_SP_kcal_mol']['Q2_CV'])} for the interaction energy and "
           f"{f2(q['TNBC:vina_4UND_kcal_mol']['Q2_CV'])} for the docking score, and the only positive values, "
           f"{f2(q['Tau:dE_int']['Q2_CV'])} for tau and {f2(q['GBM:vina']['Q2_CV'])} for the glioblastoma docking "
           "score, are carried by the formal charge of four cationic dyes and by molecular size, respectively "
           "(Fig. 6c, Table S5). These negative results are the honest outcome of the screens.", indent=True)
    k.figure(doc, FIG / "Fig6.png", 6,
             "The same QSPR protocol on data from an invalid and from a valid carrier. (a, b) Out-of-fold "
             "predictions of nested 5×5 cross-validation for the KRAS drugs, with adsorption energies computed "
             "on the invalid C_{21}N_{21}H_{6} carrier and interaction energies on the valid C_{18}N_{27}H_{9} "
             "carrier. (c) *Q*^{2}_{CV} of the rebuilt models of the four studies and of the model on the invalid "
             "carrier, with Y-randomization *p* values")
