"""
build_si.py - Supporting Information (Word, converted to PDF for submission) of the
audit paper. Every row comes from data/ (written by src/gather_audit_evidence.py
and src/audit_carriers.py).

usage: python src/manuscript/build_si.py
writes manuscript/submission/Supporting_Information_Audit_JCBC.docx
"""
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import docx_kit as k  # noqa: E402
from build_manuscript import AFFIL, AUTHOR, EMAIL, TITLE  # noqa: E402

BASE = HERE.parents[1]
DATA = BASE / "data"
OUT = BASE / "manuscript" / "submission"
STUDY = {"KRAS": "KRAS", "TNBC": "TNBC", "GBM": "Glioblastoma", "Tau": "Tau"}


def num(x, nd=1):
    return "–" if pd.isna(x) else f"{x:.{nd}f}".replace("-", "−")


def formula(f):
    """C21N21H6 -> C_{21}N_{21}H_{6} (docx_kit subscript markup)."""
    import re
    return re.sub(r"(\d+)", r"_{\1}", str(f)) if isinstance(f, str) and f not in ("NOT_FOUND", "ERR") else str(f)


def main():
    ev = json.loads((DATA / "audit_evidence.json").read_text())
    doc = k.new_document()
    k.para(doc, "**Supporting Information**", align="left", size=15, space_after=4)
    k.para(doc, TITLE, align="left", size=11, space_after=4)
    k.para(doc, AUTHOR, align="left", size=10, space_after=2)
    k.para(doc, AFFIL, align="left", size=10, space_after=2)
    k.para(doc, f"E-mail: {EMAIL}", align="left", size=10, space_after=10)
    k.para(doc, "Contents: Table S1, identity of the 128 drug structures; Table S2, bond census of the carrier "
                "models; Table S3, carrier energy in each tau complex before and after the rebuild; Table S4, "
                "redocking controls of the four studies; Table S5, QSPR models before and after the rebuild.",
           align="left", size=10, space_after=12)

    a = pd.read_csv(DATA / "si_identity_audit.csv")
    rows = [[STUDY[r.study], r.name, formula(r.ours_formula), formula(r.pubchem_formula),
             "wrong" if r.verdict.startswith("WRONG") else r.verdict.replace("OK", "correct")]
            for r in a.itertuples()]
    idt = ev["identity"]
    k.table(doc, ("S1", f"Identity of the {idt['total']['n']} drug structures used before the rebuild. The stored "
                        "structure was compared with the PubChem record of the named compound by InChIKey after "
                        "removal of salts and counter-ions. Six lookups that failed during the audit were "
                        "resolved afterwards against the PubChem records of the rebuilt libraries "
                        "(audit_resolved_lookups.csv)."),
            ["Study", "Compound", "Stored formula", "PubChem formula", "Verdict"], rows, align="lllll", font=7)

    c = pd.read_csv(DATA / "carrier_audit.csv")
    rows = [[STUDY[r.system], r.model, r.material, formula(r.formula), str(r.n_atoms), r.bonds.replace("-", "–"),
             r.forbidden_bonds.replace("-", "–"), f"{r.min_distance_A:.2f}", str(r.overlapping_pairs)]
            for r in c.itertuples()]
    k.table(doc, ("S2", "Bond census of the carrier models before and after the rebuild (bond when the distance is "
                        "below 1.15 times the sum of the covalent radii). B···B distances across the diagonal "
                        "of the four-membered rings of the BN cage (about 1.86 Å) are listed separately and "
                        "are not bonds. *d*_{min}, closest atom pair (Å); overlapping, pairs closer than 0.6 times the sum "
                        "of the covalent radii."),
            ["Study", "Model", "Material", "Formula", "Atoms", "Bonds", "Forbidden bonds", "*d*_{min}",
             "Overlapping"], rows, align="llllcllcc", font=7)

    t = pd.read_csv(DATA / "si_tau_carrier_energy.csv")
    rows = [[r.name, num(r.dEcar_old_kcal), r.adsorption_mode_old, num(r.dEcar_new_kcal), r.adsorption_mode_new]
            for r in t.itertuples()]
    k.table(doc, ("S3", "Energy of the borophene carrier at its geometry in each tau complex relative to the relaxed "
                        "isolated carrier (Δ*E*_{car}, kcal mol^{−1}, GFN2-xTB), and the adsorption regime, for the "
                        "unconstrained B_{40}H_{15} flake (before) and the supported β_{12} sheet B_{44}H_{16} "
                        "(after). A negative Δ*E*_{car} means that the carrier found a lower-energy structure "
                        "during adsorption."),
            ["Drug", "Δ*E*_{car}, before", "Regime, before", "Δ*E*_{car}, after", "Regime, after"], rows,
            align="lclcl", font=7.5)

    dk = pd.read_csv(DATA / "si_docking_controls.csv")
    rows = [[STUDY.get(r.study, r.study.replace("GBM", "Glioblastoma")), r.control, num(r.rmsd_top_A, 2)]
            for r in dk.itertuples()]
    k.table(doc, ("S4", "Redocking controls: heavy-atom RMSD (Å) of the top-ranked pose to the crystal pose, "
                        "symmetry-aware and without re-alignment. The glioblastoma rows before the rebuild are the "
                        "controls of the earlier EGFR structure (PDB 4ZAU, osimertinib); every mode of the "
                        "rebuilt glioblastoma controls is listed in the supporting information of that study."),
            ["Study", "Control", "RMSD (Å)"], rows, align="llc", font=7.5)

    q = ev["qspr"]
    lab = {"KRAS_v1_reproduced": ("KRAS, before rebuild", "Δ*E*_{ads}, invalid C_{21}N_{21}H_{6} carrier"),
           "KRAS:dE_int": ("KRAS", "Δ*E*_{int}, pristine g-C_{3}N_{4}"),
           "TNBC:vina_4UND_kcal_mol": ("TNBC", "Vina score, PARP1"),
           "TNBC:delta_Eint_SP_kcal_mol": ("TNBC", "Δ*E*_{int}, B_{36}N_{36} cage"),
           "Tau:dE_int": ("Tau", "Δ*E*_{int}, supported β_{12} sheet"),
           "GBM:vina": ("Glioblastoma", "Vina score, EGFR")}
    rows = [[lab[key][0], lab[key][1], str(q[key]["n"]), f"{q[key]['Q2_CV']:.2f}".replace("-", "−"),
             f"{q[key]['p_perm']:.3f}"] for key in lab]
    k.table(doc, ("S5", "Ridge QSPR models under nested 5×5 cross-validation, before and after the rebuild. *p*, "
                        "fraction of 1,000 permuted targets with *Q*^{2}_{CV} at least as high, computed as "
                        "(1 + count)/1001."),
            ["Study", "Target", "*n*", "*Q*^{2}_{CV}", "*p*"], rows, align="llccc", font=8)

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "Supporting_Information_Audit_JCBC.docx"
    doc.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
