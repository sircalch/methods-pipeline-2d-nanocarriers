"""
gather_audit_evidence.py - collects, from the four rebuilt case-study repositories
and the archive of the pre-rebuild files, every number the audit paper quotes for
the eight failure modes. Nothing is typed by hand.

writes data/audit_evidence.json
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
P = ROOT / "nano-qsar-ai-papers"
ARCH = ROOT / "_archivo" / "nano-qsar-limpieza-2026-09-22"
REPO = {"KRAS": P / "kras-pancreatic-gC3N4-ai", "TNBC": P / "nano-qsar-ai-therapeutics",
        "GBM": P / "mxene-glioblastoma-qsar-ai", "Tau": ROOT / "borophene-alzheimer-tau-ai"}
HARTREE = 627.509


def audit_table(s, f):
    """Structure audit of one study, with the lookups that failed on 2026-09-22
    resolved afterwards (audit_resolved_lookups.csv) applied."""
    d = P / "_auditoria_estructuras_2026-09-22"
    a = pd.read_csv(d / f"audit_{f}.csv")
    res = pd.read_csv(d / "audit_resolved_lookups.csv")
    for r in res[res.study == s].itertuples():
        a.loc[a.name == r.name, "verdict"] = r.verdict
    return a


def identity():
    out = {}
    for s, f in (("KRAS", "kras"), ("TNBC", "tnbc"), ("GBM", "gbm"), ("Tau", "tau")):
        a = audit_table(s, f)
        unchecked = int(a.verdict.str.startswith("CHECK").sum())
        assert unchecked == 0, (s, unchecked)
        wrong = a[a.verdict.str.contains("WRONG")]
        out[s] = {"n": len(a), "wrong": len(wrong), "same_formula_wrong_connectivity":
                  int((wrong.ours_formula == wrong.pubchem_formula).sum())}
    out["total"] = {"n": sum(v["n"] for v in out.values()), "wrong": sum(v["wrong"] for v in out.values())}
    return out


def carriers():
    df = pd.read_csv(HERE / "data" / "carrier_audit.csv")
    return df[["system", "model", "formula", "bonds", "forbidden_bonds"]].to_dict("records")


def reconstruction():
    tau = REPO["Tau"]
    old = pd.read_csv(tau / "results" / "quantum" / "adsorption_results_B40H15_collapsing_2026-09-24.csv")
    e_old = json.loads((tau / "data" / "processed" / "carrier_B40H15_collapsing_2026-09-24.json").read_text())["E_Eh"]
    d_old = (old.E_carrier_frozen_Eh - e_old) * HARTREE
    new = pd.read_csv(tau / "results" / "quantum" / "adsorption_results.csv")
    c = json.loads((tau / "data" / "processed" / "carrier.json").read_text())
    d_new = (new.E_carrier_frozen_Eh - c["E_Eh"]) * HARTREE
    tn = REPO["TNBC"]
    e_cage = json.loads((tn / "calculations" / "tnbc" / "B36N36_energy.json").read_text())["E_Eh"]
    d_cage = [(json.loads(f.read_text())["E_carrier_frozen_Eh"] - e_cage) * HARTREE
              for f in (tn / "calculations" / "tnbc_recompute").glob("*/result.json")
              if json.loads(f.read_text()).get("status") == "OK"]
    bp = pd.read_csv(REPO["KRAS"] / "results" / "quantum" / "bp_codoping_scan.csv")
    acc = bp[bp.accepted.astype(bool)]
    lower_rej = bp[(~bp.accepted.astype(bool)) & (bp.E_singlet_Eh < acc.E_singlet_Eh.min())]
    # what the pre-audit tau study reported on the same free B40H15 flake (its Supporting
    # Information, the file deposited on Zenodo before the audit)
    import re
    from docx import Document
    txt = " ".join(x.text for x in Document(ARCH / "tau" / "manuscript" /
                                           "Tau_Borophene_Supporting_Information.docx").paragraphs)
    mv1 = re.search(r"(\d+) of the (\d+) ligands fall in this regime", txt)
    return {"tau_v1_reported": {"chem": int(mv1.group(1)), "n": int(mv1.group(2))},
            "tau_old": {"n": len(d_old), "n_below_min": int((d_old < -1).sum()),
                        "min_kcal": float(d_old.min()), "chem_old": int((old.adsorption_mode == "chemisorption").sum()),
                        "chem_new": int((new.adsorption_mode == "chemisorption").sum()), "n_new": len(new)},
            "tau_new_dcar_kcal": [float(d_new.min()), float(d_new.max())],
            "tnbc_cage_dcar_kcal": [float(min(d_cage)), float(max(d_cage))],
            "kras_bp": {"n_configs": len(bp), "n_rejected_lower": len(lower_rej),
                        "lowest_rejected_below_accepted_kcal":
                            float((acc.E_singlet_Eh.min() - lower_rej.E_singlet_Eh.min()) * HARTREE)
                            if len(lower_rej) else 0.0}}


def method():
    g = REPO["GBM"]
    sc = pd.read_csv(g / "results" / "quantum" / "xtb_lattice_scan.csv")
    g2 = sc[sc.method == "GFN2-xTB"].dropna(subset=["E_eV_per_fu"]).sort_values("a_A")
    g1 = sc[sc.method == "GFN1-xTB"]
    ft = pd.read_csv(g / "results" / "quantum" / "mxene_flake_scf_tests.csv")
    neutral = ft[(ft.charge == 0) & ~ft.structure.str.contains("discarded")]
    return {"gfn2_min_a": float(g2.loc[g2.E_eV_per_fu.idxmin(), "a_A"]), "a_ref": 3.03,
            "gfn2_max_jump_eV": float(np.abs(np.diff(g2.E_eV_per_fu)).max()),
            "gfn1_failed": int(g1.E_eV_per_fu.isna().sum()), "gfn1_n": len(g1),
            "gfn1_unphysical": int((g1.E_eV_per_fu < -600).sum()),
            "flake_neutral_attempts": len(neutral), "flake_neutral_converged": int(neutral.scf_converged.sum())}


def docking():
    out = {}
    for s in ("KRAS", "TNBC", "Tau", "GBM"):
        f = REPO[s] / ("data/processed" if s == "TNBC" else "results/docking") / "redocking_validation.csv"
        rd = pd.read_csv(f)
        out[s] = [{"control": r.control, "rmsd_A": float(r.rmsd_heavy_atom_A)} for r in rd.itertuples()]
    md = pd.read_csv(REPO["GBM"] / "results" / "docking" / "redocking_all_modes.csv")
    out["GBM_modes"] = md.to_dict("records")
    old = pd.read_csv(ARCH / "gbm" / "docking_4ZAU_failed_controls" / "redocking_validation.csv")
    out["GBM_4ZAU_before"] = [{"control": r.control, "rmsd_A": float(r.rmsd_heavy_atom_A)} for r in old.itertuples()]
    return out


def fabricated():
    f = ARCH / "kras" / "results" / "virtual_screening" / "virtual_screening_500_cohort_ranked.csv"
    v = pd.read_csv(f)
    src = (ARCH / "kras" / "src" / "virtual_screening" / "screen_500_oncology_library.py").read_text()
    return {"n_rows": len(v), "has_structure_column": any(c.lower() in ("smiles", "inchi", "inchikey") for c in v.columns),
            "n_scaffolds": int(v.parent_scaffold.nunique()),
            "descriptors_from_random_numbers": bool(re.search(r"np\.random\.uniform", src)),
            "columns": list(v.columns)}


def periodic():
    import sys
    sys.path.insert(0, str(REPO["GBM"] / "src" / "quantum"))
    import qe_mxene_dft as Q
    _, _, cv = Q.cell()
    out = {}
    for d in [REPO["GBM"] / "calculations" / "gbm_dft" / "_dropped_procarbazine" / "cplx_Procarbazine"] + \
             sorted((REPO["GBM"] / "calculations" / "gbm_dft").glob("cplx_*")):
        t = (d / "pw.in").read_text()
        at = [l.split() for l in t.split("ATOMIC_POSITIONS angstrom\n")[1].split("K_POINTS")[0].strip().split("\n")]
        ns = json.loads((d / "meta.json").read_text())["n_slab"]
        x = np.array([[float(v) for v in a[1:4]] for a in at])[ns:]
        out[d.name.replace("cplx_", "")] = round(float(Q.image_distance(x, cv)), 2)
    from scipy.spatial.distance import pdist
    lengths = {}
    for n in out:
        el, xyz = Q.read_xyz(Q.STARTS / f"{n}.xyz")
        lengths[n] = round(float(pdist(xyz).max()), 1)
    return {"image_distance_A": out, "drug_length_A": lengths, "cell_A": round(float(np.linalg.norm(cv[0])), 2)}


def qspr():
    q = {"KRAS": ("results/qspr/dEint_pristine_summary.json",), "TNBC": ("results/qspr/vina_summary.json",
                                                                          "results/qspr/dEint_summary.json"),
         "Tau": ("results/qspr/dEint_summary.json",), "GBM": ("results/qspr/vina_summary.json",)}
    out = {}
    for s, files in q.items():
        for f in files:
            j = json.loads((REPO[s] / f).read_text())
            out[f"{s}:{j['target']}"] = {"n": j["n"], "Q2_CV": j["Q2_CV"], "p_perm": j["Y_scrambling"]["p"]}
    # the model behind the v1 claim (Fig. 8 of the old KRAS paper): same protocol, same four
    # descriptors, n = 33 - but the target came from the invalid C21N21H6 carrier
    old = json.loads((ARCH / "kras" / "data" / "figures_source_package" / "02_Figure8_QSPR_Validation" /
                      "qspr_model_summary.json").read_text())
    out["KRAS_v1"] = {k: old[k] for k in ("n_samples", "p_descriptors", "selected_descriptors", "cv_scheme",
                                          "Q2_CV", "fold_Q2", "Y_Scrambling_Empirical_P", "RMSE_kcal_mol")}
    # reproduce the v1 number with today's code on the v1 targets (invalid-carrier energies)
    import sys
    import tempfile
    sys.path.insert(0, str(REPO["KRAS"] / "src" / "ml_models"))
    import qspr_core
    m = pd.read_csv(ARCH / "kras" / "docking_untraceable" / "MASTER_COMPOUNDS_CURATED.csv")
    inv = pd.read_csv(ARCH / "kras" / "invalid_C21N21H6_carrier" / "adsorption_qm_results.csv")
    inv = inv[inv.carrier_name == "pristine"].set_index("drug_name").Delta_E_ads_kcal_mol
    df = m[["name", "MW", "PSA", "Polarizability_alpha", "Electrophilicity_omega"]].rename(
        columns={"Polarizability_alpha": "alpha", "Electrophilicity_omega": "omega"})
    df["y"] = df.name.map(inv)
    assert df.y.notna().all(), "v1 target missing for some drug"
    cache = HERE / "data" / "v1_reproduction" / "kras_v1_summary.json"
    if cache.exists():                    # 1,000 nested-CV permutations take minutes; reuse the saved run
        r = json.loads(cache.read_text())
    else:
        r = qspr_core.run(df.reset_index(drop=True), ["MW", "PSA", "alpha", "omega"], "y",
                          HERE / "data" / "v1_reproduction", "kras_v1")
    out["KRAS_v1_reproduced"] = {"n": r["n"], "Q2_CV": r["Q2_CV"], "p_perm": r["Y_scrambling"]["p"],
                                 "target": "Delta_E_ads on the invalid C21N21H6 carrier (v1)"}
    return out


def si_tables():
    """Per-row tables behind the Supporting Information, copied into data/ so that
    the SI can be rebuilt from this repository alone."""
    rows = []
    for s, f in (("KRAS", "kras"), ("TNBC", "tnbc"), ("GBM", "gbm"), ("Tau", "tau")):
        a = audit_table(s, f)
        a.insert(0, "study", s)
        rows.append(a[["study", "name", "ours_formula", "pubchem_formula", "skeleton_match", "verdict"]])
    pd.concat(rows).to_csv(HERE / "data" / "si_identity_audit.csv", index=False)

    tau = REPO["Tau"]
    e_old = json.loads((tau / "data" / "processed" / "carrier_B40H15_collapsing_2026-09-24.json").read_text())["E_Eh"]
    e_new = json.loads((tau / "data" / "processed" / "carrier.json").read_text())["E_Eh"]
    old = pd.read_csv(tau / "results" / "quantum" / "adsorption_results_B40H15_collapsing_2026-09-24.csv")
    new = pd.read_csv(tau / "results" / "quantum" / "adsorption_results.csv")
    t = old[["name", "E_carrier_frozen_Eh", "adsorption_mode"]].merge(
        new[["name", "E_carrier_frozen_Eh", "adsorption_mode"]], on="name", suffixes=("_old", "_new"))
    t["dEcar_old_kcal"] = ((t.E_carrier_frozen_Eh_old - e_old) * HARTREE).round(1)
    t["dEcar_new_kcal"] = ((t.E_carrier_frozen_Eh_new - e_new) * HARTREE).round(1)
    t[["name", "dEcar_old_kcal", "adsorption_mode_old", "dEcar_new_kcal", "adsorption_mode_new"]].to_csv(
        HERE / "data" / "si_tau_carrier_energy.csv", index=False)

    rows = []
    for s in ("KRAS", "TNBC", "Tau", "GBM"):
        f = REPO[s] / ("data/processed" if s == "TNBC" else "results/docking") / "redocking_validation.csv"
        for r in pd.read_csv(f).itertuples():
            rows.append({"study": s, "receptor": "", "control": r.control, "rmsd_top_A": r.rmsd_heavy_atom_A})
    for r in pd.read_csv(ARCH / "gbm" / "docking_4ZAU_failed_controls" / "redocking_validation.csv").itertuples():
        rows.append({"study": "GBM (before rebuild)", "receptor": "", "control": r.control,
                     "rmsd_top_A": r.rmsd_heavy_atom_A})
    pd.DataFrame(rows).to_csv(HERE / "data" / "si_docking_controls.csv", index=False)


def main():
    si_tables()
    ev = {"identity": identity(), "carriers": carriers(), "reconstruction": reconstruction(),
          "method": method(), "docking": docking(), "fabricated": fabricated(), "periodic": periodic(),
          "qspr": qspr()}
    out = HERE / "data" / "audit_evidence.json"
    out.write_text(json.dumps(ev, indent=2, default=float))
    print(json.dumps({k: v for k, v in ev.items() if k not in ("carriers", "docking")}, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
