"""
make_figures.py - figures of the audit paper (ACS double-column width), drawn
from data/audit_evidence.json, data/carrier_audit.csv and the result files of
the four case-study repositories.

usage: python src/figures/make_figures.py [fig ...]      (default: all)
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import figkit as K  # noqa: E402
import style as S  # noqa: E402

BASE = HERE.parents[1]
ROOT = BASE.parents[1]
P = ROOT / "nano-qsar-ai-papers"
FIG = BASE / "figures"
EV = json.loads((BASE / "data" / "audit_evidence.json").read_text())
STUDIES = ["KRAS", "TNBC", "GBM", "Tau"]
LABEL = {"KRAS": "KRAS / g-C$_3$N$_4$", "TNBC": "TNBC / B$_{36}$N$_{36}$", "GBM": "GBM / Ti$_3$C$_2$O$_2$",
         "Tau": "Tau / β$_{12}$ borophene"}
BEFORE, AFTER = S.CHEM, S.ADS


def sub(formula):
    """C21N21H6 -> C$_{21}$N$_{21}$H$_{6}$"""
    import re
    return re.sub(r"(\d+)", r"$_{\1}$", formula)


def letters(fig, axs, dy=0.02):
    fig.canvas.draw()
    top = max(ax.get_position().y1 for ax in axs)
    for ax, l in zip(axs, "abcdef"):
        fig.text(ax.get_position().x0 - 0.045, top + dy, l, fontsize=9, fontweight="bold", va="bottom")


# ------------------------------------------------------------------ Fig. 1
def fig1():
    """Screening workflow and where each of the eight checks applies."""
    from matplotlib.patches import FancyBboxPatch
    stages = [("Drug\nstructures", [1]), ("Carrier\nmodel", [2]), ("Method\n(xTB / DFT)", [4]),
              ("Adsorption\ncomplexes", [3, 7]), ("Docking", [5]), ("Result\ntables", [6]), ("QSPR\nmodel", [8])]
    checks = {1: "InChIKey vs\nPubChem", 2: "bond census,\nstoichiometry", 3: "carrier energy\n≥ its minimum",
              4: "test on the\nbare carrier", 5: "redock, every\nmode", 6: "row → input\n+ output file",
              7: "drug–image\ndistance", 8: "only after\nchecks 1–7"}
    fig = plt.figure(figsize=(S.DOUBLE, 48 * S.MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(8, 50)
    ax.set_axis_off()
    n = len(stages)
    w, gap = 11.2, (100 - 2 - n * 11.2) / (n - 1)
    for i, (name, ck) in enumerate(stages):
        x = 1 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 30), w, 12, boxstyle="round,pad=0.3,rounding_size=1.2",
                                    fc=S.PANEL_BG, ec=S.INK, lw=0.8))
        ax.text(x + w / 2, 36, name, ha="center", va="center", fontsize=7, fontweight="bold")
        if i < n - 1:
            ax.annotate("", xy=(x + w + gap - 0.3, 36), xytext=(x + w + 0.5, 36),
                        arrowprops=dict(arrowstyle="-|>", color=S.MUTED, lw=0.8))
        for j, num in enumerate(ck):
            cx = x + w / 2 + (j - (len(ck) - 1) / 2) * 9.5
            ax.plot([cx, cx], [29.5, 22.5], color=BEFORE, lw=0.7)
            ax.scatter(cx, 20.5, s=150, color=BEFORE, zorder=3)
            ax.text(cx, 20.5, str(num), ha="center", va="center", color="white", fontsize=7, fontweight="bold",
                    zorder=4)
            ax.text(cx, 16.5, checks[num], ha="center", va="top", fontsize=5.8, color=S.INK, linespacing=1.15)
    ax.text(1, 47, "Screening workflow", fontsize=7, color=S.MUTED)
    S.save(fig, FIG, "Fig1")


# ------------------------------------------------------------------ Fig. 2
def fig2():
    """Compound identity and carrier validity before the rebuild."""
    idt = EV["identity"]
    ca = pd.read_csv(BASE / "data" / "carrier_audit.csv")
    fig, axs = plt.subplots(1, 2, figsize=(S.DOUBLE, 62 * S.MM), gridspec_kw=dict(wspace=0.55))
    ax = axs[0]
    y = np.arange(len(STUDIES))[::-1]
    for yi, s in zip(y, STUDIES):
        n, w, same = idt[s]["n"], idt[s]["wrong"], idt[s]["same_formula_wrong_connectivity"]
        ax.barh(yi, n - w, color=AFTER, height=0.6)
        ax.barh(yi, w - same, left=n - w, color=BEFORE, height=0.6)
        ax.barh(yi, same, left=n - same, color=BEFORE, alpha=0.45, height=0.6, hatch="////", edgecolor="white", lw=0)
        ax.text(n + 0.6, yi, f"{w}/{n}", va="center", fontsize=6.5)
    ax.set_yticks(y)
    ax.set_yticklabels([LABEL[s] for s in STUDIES], fontsize=6.5)
    ax.set_xlabel("Compounds")
    ax.set_xlim(0, 38)
    K.light_grid(ax, "x")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=AFTER, label="matches PubChem"), Patch(color=BEFORE, label="different compound"),
                       Patch(facecolor=BEFORE, alpha=0.45, hatch="////", edgecolor="white",
                             label="same formula, other connectivity")],
              loc="upper center", bbox_to_anchor=(0.45, -0.22), ncol=2, frameon=False, fontsize=6)
    ax = axs[1]
    rows = []
    for s in STUDIES:
        for when in ("before", "after"):
            r = ca[(ca.system == s) & (ca.model == when)].iloc[0]
            fb = 0 if r.forbidden_bonds == "none" else sum(int(x.split()[-1]) for x in r.forbidden_bonds.split(";"))
            rows.append((s, when, fb, r.formula))
    x = np.arange(len(STUDIES))
    w = 0.36
    for k, when, col in ((0, "before", BEFORE), (1, "after", AFTER)):
        vals = [r[2] for r in rows if r[1] == when]
        ax.bar(x + (k - 0.5) * w, vals, w, color=col, label="before rebuild" if when == "before" else "rebuilt")
        for xi, v in zip(x, vals):
            ax.text(xi + (k - 0.5) * w, v + 0.8, str(v), ha="center", fontsize=6.3)
    forms = {(r[0], r[1]): r[3] for r in rows}
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\n{sub(forms[(s, 'before')])}\n→ {sub(forms[(s, 'after')])}" for s in STUDIES], fontsize=5.8)
    ax.set_ylabel("Bonds forbidden in the material")
    ax.set_ylim(0, 66)
    ax.legend(frameon=False, fontsize=6, loc="upper right")
    K.light_grid(ax, "y")
    letters(fig, axs)
    S.save(fig, FIG, "Fig2")


# ------------------------------------------------------------------ Fig. 3
def fig3():
    """Carrier reconstruction during adsorption."""
    tau = ROOT / "borophene-alzheimer-tau-ai"
    old = pd.read_csv(tau / "results" / "quantum" / "adsorption_results_B40H15_collapsing_2026-09-24.csv")
    e_old = json.loads((tau / "data" / "processed" / "carrier_B40H15_collapsing_2026-09-24.json").read_text())["E_Eh"]
    new = pd.read_csv(tau / "results" / "quantum" / "adsorption_results.csv")
    e_new = json.loads((tau / "data" / "processed" / "carrier.json").read_text())["E_Eh"]
    tn = P / "nano-qsar-ai-therapeutics"
    e_cage = json.loads((tn / "calculations" / "tnbc" / "B36N36_energy.json").read_text())["E_Eh"]
    cage = [(json.loads(f.read_text())["E_carrier_frozen_Eh"] - e_cage) * 627.509
            for f in (tn / "calculations" / "tnbc_recompute").glob("*/result.json")
            if json.loads(f.read_text()).get("status") == "OK"]
    sets = [("Tau, free B$_{40}$H$_{15}$ flake\n(before)", (old.E_carrier_frozen_Eh - e_old) * 627.509, BEFORE),
            ("Tau, supported β$_{12}$ sheet\n(rebuilt)", (new.E_carrier_frozen_Eh - e_new) * 627.509, AFTER),
            ("TNBC, B$_{36}$N$_{36}$ cage\n(rebuilt)", np.array(cage), AFTER)]
    fig, axs = plt.subplots(1, 2, figsize=(S.DOUBLE, 64 * S.MM), gridspec_kw=dict(width_ratios=[1.6, 1], wspace=0.4))
    ax = axs[0]
    rng = np.random.default_rng(0)
    for i, (lab, v, col) in enumerate(sets):
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=14, color=col, edgecolor="white", lw=0.3, zorder=3)
    ax.axhspan(-130, 0, color=BEFORE, alpha=0.06, lw=0, zorder=0)
    ax.axhline(0, color=S.INK, lw=0.8)
    ax.text(2.45, -4, "below the carrier's\nown minimum", fontsize=6, color=BEFORE, va="top", ha="right")
    ax.set_xticks(range(3))
    ax.set_xticklabels([s[0] for s in sets], fontsize=6.2)
    ax.set_ylabel("$E$(carrier in complex) − $E$(relaxed carrier)\n(kcal mol$^{-1}$)")
    ax.set_xlim(-0.5, 2.5)
    K.light_grid(ax, "y")
    ax = axs[1]
    r = EV["reconstruction"]["tau_old"]
    vals = [r["chem_old"], r["chem_new"]]
    ax.bar([0, 1], vals, color=[BEFORE, AFTER], width=0.6)
    for xi, v, n in zip([0, 1], vals, [r["n"], r["n_new"]]):
        ax.text(xi, v + 0.4, f"{v} of {n}", ha="center", fontsize=6.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["free flake", "supported\nsheet"], fontsize=6.5)
    ax.set_ylabel("Tau drugs classed as chemisorbed")
    ax.set_ylim(0, 21)
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    K.light_grid(ax, "y")
    letters(fig, axs)
    S.save(fig, FIG, "Fig3")


# ------------------------------------------------------------------ Fig. 4
def fig4():
    """Method applicability: tight binding on the metallic MXene."""
    g = P / "mxene-glioblastoma-qsar-ai"
    sc = pd.read_csv(g / "results" / "quantum" / "xtb_lattice_scan.csv")
    ft = pd.read_csv(g / "results" / "quantum" / "mxene_flake_scf_tests.csv")
    ft = ft[~ft.structure.str.contains("discarded")]
    fig, axs = plt.subplots(1, 2, figsize=(S.DOUBLE, 62 * S.MM), gridspec_kw=dict(width_ratios=[1.5, 1], wspace=0.4))
    ax = axs[0]
    for meth, col, mk in (("GFN2-xTB", S.DOCK, "o"), ("GFN1-xTB", S.ADS, "s")):
        x = sc[sc.method == meth]
        ok = x.E_eV_per_fu.notna() & (x.E_eV_per_fu > -600)
        e = x.E_eV_per_fu[ok]
        ax.plot(x.a_A[ok], e - e.min(), marker=mk, ms=3.5, lw=1, color=col, label=meth)
        bad = x[~ok]
        ax.scatter(bad.a_A, np.full(len(bad), -2.2), marker="x", color=col, s=16, lw=0.8)
    ax.axvline(3.03, color=S.INK, lw=0.8, ls=(0, (1, 2)))
    ax.text(3.035, 33, "experiment/DFT\na = 3.03 Å", fontsize=6, va="top")
    ax.set_xlabel("In-plane lattice constant of Ti$_3$C$_2$O$_2$ (Å)")
    ax.set_ylabel("E − E$_{min}$ (eV per formula unit)")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=S.DOCK, marker="o", ms=3.5, label="GFN2-xTB"),
                       Line2D([], [], color=S.ADS, marker="s", ms=3.5, label="GFN1-xTB"),
                       Line2D([], [], color=S.INK, marker="x", ls="", label="SCF failed or unphysical")],
              frameon=False, fontsize=6, loc="upper center", bbox_to_anchor=(0.4, 1.0))
    K.light_grid(ax)
    ax = axs[1]
    grp = ft.assign(state=np.where(ft.charge == 0, "neutral", "charged")).groupby("state").scf_converged
    labels = ["neutral", "charged"]
    conv = [int(grp.sum()[k]) for k in labels]
    tot = [int(grp.size()[k]) for k in labels]
    ax.bar([0, 1], tot, color=S.FAINT, width=0.6, label="attempted")
    ax.bar([0, 1], conv, color=S.DOCK, width=0.6, label="SCF converged")
    for xi, c_, t_ in zip([0, 1], conv, tot):
        ax.text(xi, t_ + 0.4, f"{c_}/{t_}", ha="center", fontsize=6.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["neutral\nflake", "charged\nflake"], fontsize=6.5)
    ax.set_ylabel("Finite-flake xtb runs")
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(frameon=False, fontsize=6, loc="upper right")
    K.light_grid(ax, "y")
    letters(fig, axs)
    S.save(fig, FIG, "Fig4")


# ------------------------------------------------------------------ Fig. 5
def fig5():
    """Docking controls in the four targets."""
    dk = EV["docking"]
    names = {"self-redock, crystal conformation": "crystal conf.", "production protocol, from SMILES": "from SMILES",
             "ligand-free fibril: self-redock, crystal conformation": "crystal conf., empty fibril",
             "ligand-free fibril: production protocol, from SMILES": "from SMILES, empty fibril",
             "tracer stack present: self-redock, crystal conformation": "crystal conf., tracer stack",
             "tracer stack present: production protocol, from SMILES": "from SMILES, tracer stack"}
    target = {"KRAS": "KRAS-G12D\n7RPZ", "TNBC": "PARP1\n4UND", "Tau": "PHF\n8FUG", "GBM": "EGFR\n1M17"}
    fig, axs = plt.subplots(1, 2, figsize=(S.DOUBLE, 80 * S.MM), gridspec_kw=dict(width_ratios=[1.5, 1], wspace=0.35))
    fig.subplots_adjust(bottom=0.38)
    ax = axs[0]
    short = {"crystal conf.": "crystal", "from SMILES": "SMILES", "crystal conf., empty fibril": "crystal, empty",
             "from SMILES, empty fibril": "SMILES, empty", "crystal conf., tracer stack": "crystal, stack",
             "from SMILES, tracer stack": "SMILES, stack"}
    pos, plabs, groups, xi = [], [], [], 0
    for s in ("KRAS", "TNBC", "Tau", "GBM"):
        start = xi
        for c_ in dk[s]:
            r = c_["rmsd_A"]
            ax.bar(xi, r, color=AFTER if r <= 2 else BEFORE, width=0.7)
            pos.append(xi)
            plabs.append(short[names.get(c_["control"], c_["control"])])
            xi += 1
        groups.append(((start + xi - 1) / 2, target[s]))
        xi += 0.8
    ax.axhline(2.0, color=S.INK, lw=0.7, ls=(0, (4, 3)))
    ax.text(xi - 0.9, 2.15, "2 Å", fontsize=6, ha="right")
    ax.set_xticks(pos)
    ax.set_xticklabels(plabs, rotation=90, fontsize=5.6)
    for gx, gl in groups:
        ax.text(gx, -0.42, gl, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=6.3)
    ax.set_ylabel("RMSD of the top-ranked pose (Å)")
    ax.set_ylim(0, 9)
    K.light_grid(ax, "y")
    ax = axs[1]
    md = pd.DataFrame(dk["GBM_modes"])
    for c_, col, mk in (("self-redock, crystal conformation", S.DOCK, "o"),
                        ("production protocol, from SMILES", S.ADS, "s")):
        x = md[md.control == c_]
        ax.scatter(x["mode"], x.rmsd_A, color=col, marker=mk, s=16, edgecolor="white", lw=0.3, zorder=3,
                   label=names[c_])
    ax.axhline(2.0, color=S.INK, lw=0.7, ls=(0, (4, 3)))
    ax.set_xlabel("Vina mode (rank by score)")
    ax.set_ylabel("RMSD to crystal pose (Å)")
    ax.set_xticks(range(1, 10))
    ax.set_title("EGFR (1M17): every mode", fontsize=6.5, loc="left")
    ax.legend(frameon=False, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2)
    K.light_grid(ax)
    letters(fig, axs)
    S.save(fig, FIG, "Fig5")


# ------------------------------------------------------------------ Fig. 6
def fig6():
    """Same QSPR protocol, data from an invalid and from a valid carrier."""
    v1 = pd.read_csv(BASE / "data" / "v1_reproduction" / "kras_v1_oof.csv")
    v2 = pd.read_csv(P / "kras-pancreatic-gC3N4-ai" / "results" / "qspr" / "dEint_pristine_oof.csv")
    q = EV["qspr"]
    fig, axs = plt.subplots(1, 3, figsize=(S.DOUBLE, 62 * S.MM), gridspec_kw=dict(wspace=0.75, width_ratios=[1, 1, 0.9]))
    for ax, df, col, key, ttl in ((axs[0], v1, BEFORE, "KRAS_v1_reproduced", "invalid C$_{21}$N$_{21}$H$_6$ carrier"),
                                  (axs[1], v2, AFTER, "KRAS:dE_int", "valid C$_{18}$N$_{27}$H$_9$ carrier")):
        y = df[df.columns[df.columns.get_loc("oof_pred") - 1]] if "y" not in df else df["y"]
        K.parity(ax, y.values, df.oof_pred.values, col, stats_lines=None, xlabel="GFN2-xTB energy")
        K.stat_box(ax, [f"$Q^2_{{CV}}$ = {q[key]['Q2_CV']:.2f}", f"$p$ = {q[key]['p_perm']:.3f}"], loc="upper left")
        ax.set_title(ttl, fontsize=6.5, loc="left")
    ax = axs[2]
    items = [("KRAS, invalid carrier", q["KRAS_v1_reproduced"], BEFORE),
             ("KRAS, valid carrier", q["KRAS:dE_int"], AFTER),
             ("TNBC, Δ$E_{int}$", q["TNBC:delta_Eint_SP_kcal_mol"], AFTER),
             ("TNBC, docking", q["TNBC:vina_4UND_kcal_mol"], AFTER),
             ("Tau, Δ$E_{int}$", q["Tau:dE_int"], AFTER),
             ("GBM, docking", q["GBM:vina"], AFTER)]
    yy = np.arange(len(items))[::-1]
    for yi, (lab, d, col) in zip(yy, items):
        ax.hlines(yi, 0, d["Q2_CV"], color=S.FAINT, lw=1)
        ax.scatter(d["Q2_CV"], yi, color=col, s=22, zorder=3)
        ax.text(0.72, yi, f"p = {d['p_perm']:.3f}", fontsize=5.8, va="center", color=S.MUTED)
    ax.axvline(0, color=S.INK, lw=0.7)
    ax.set_yticks(yy)
    ax.set_yticklabels([i[0] for i in items], fontsize=6)
    ax.set_xlim(-0.45, 0.95)
    ax.set_xlabel("$Q^2_{CV}$ (nested 5×5 CV)")
    K.light_grid(ax, "x")
    letters(fig, axs)
    S.save(fig, FIG, "Fig6")


FIGS = {"1": fig1, "2": fig2, "3": fig3, "4": fig4, "5": fig5, "6": fig6}

if __name__ == "__main__":
    S.apply()
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
        print(f"Fig{key} done")
