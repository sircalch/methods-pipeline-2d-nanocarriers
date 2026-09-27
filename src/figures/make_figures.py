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
REN = FIG / "_renders"


def audit_findings():
    """Name of each check and its result in the audit, from the evidence file."""
    idt, rc, me, q = EV["identity"], EV["reconstruction"]["tau_old"], EV["method"], EV["qspr"]
    nbad = sum(1 for c in EV["carriers"] if c["model"] == "before" and c["forbidden_bonds"] != "none")
    fail = [s for s in STUDIES if any(c["rmsd_A"] > 2.0 for c in EV["docking"][s])]
    img = EV["periodic"]["image_distance_A"]
    worst = min(img, key=img.get)
    v1, v2 = q["KRAS_v1_reproduced"]["Q2_CV"], q["KRAS:dE_int"]["Q2_CV"]
    return {1: ("InChIKey\nvs PubChem", f"{idt['total']['wrong']} of {idt['total']['n']} wrong"),
            2: ("bond census,\nstoichiometry", f"{nbad} of 4 invalid"),
            3: ("E(carrier) ≥\nits minimum", f"{rc['n_below_min']} of {rc['n']} below"),
            4: ("test on the\nbare carrier", f"xTB: {me['gfn2_min_a']:.2f} vs {me['a_ref']:.2f} Å"),
            5: ("redock, RMSD\nof every mode", f"{len(fail)} of 4 targets fail"),
            6: ("row → structure\n+ output file", f"{EV['fabricated']['n_rows']} unbacked rows"),
            7: ("drug–image\ndistance", f"{worst.lower()} {img[worst]:.2f} Å"),
            8: ("fit only after\nchecks 1–7", f"$Q^2_{{CV}}$ {v1:.2f} → {v2:.2f}".replace("-", "−"))}


def _thumb_table(ax):
    """Schematic result table: every row must point to a structure and an output file."""
    from matplotlib.patches import Rectangle
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.set_axis_off(); ax.set_aspect("equal")
    ax.add_patch(Rectangle((0.5, 0.5), 9, 7, fc="white", ec=S.INK, lw=0.6))
    ax.add_patch(Rectangle((0.5, 6.3), 9, 1.2, fc=S.FAINT, ec=S.INK, lw=0.6))
    for y in (1.65, 2.8, 3.95, 5.1):
        ax.plot([0.5, 9.5], [y + 1.15, y + 1.15], color=S.FAINT, lw=0.5)
    for x in (3.5, 6.5):
        ax.plot([x, x], [0.5, 7.5], color=S.FAINT, lw=0.5)
    for k, y in enumerate((5.65, 4.5, 3.35, 2.2, 1.05)):
        ax.text(2.0, y, ["mol_01", "mol_02", "mol_03", "mol_04", "…"][k], fontsize=4.2, ha="center",
                va="center", color=S.INK)
        ax.text(5.0, y, "✓" if k < 3 else "?", fontsize=5, ha="center", va="center",
                color=S.ADS if k < 3 else S.CHEM, fontweight="bold", fontfamily="DejaVu Sans")
        ax.text(8.0, y, "✓" if k < 2 else "?", fontsize=5, ha="center", va="center",
                color=S.ADS if k < 2 else S.CHEM, fontweight="bold", fontfamily="DejaVu Sans")
    for x, t in ((2.0, "row"), (5.0, "struct."), (8.0, "output")):
        ax.text(x, 6.9, t, fontsize=4.2, ha="center", va="center", fontweight="bold", color=S.INK)


def _thumb_parity(ax):
    o = pd.read_csv(P / "kras-pancreatic-gC3N4-ai" / "results" / "qspr" / "dEint_pristine_oof.csv")
    y = o.filter(regex="^(y|obs|dE|delta)", axis=1).iloc[:, 0] if "y" not in o else o["y"]
    yh = o.filter(regex="pred", axis=1).iloc[:, 0]
    lo, hi = min(y.min(), yh.min()), max(y.max(), yh.max())
    ax.plot([lo, hi], [lo, hi], color=S.MUTED, lw=0.6, ls=(0, (3, 2)))
    ax.scatter(y, yh, s=5, color=S.DOCK, edgecolor="white", lw=0.2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("computed", fontsize=4.8, labelpad=1); ax.set_ylabel("predicted", fontsize=4.8, labelpad=1)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_aspect("equal", adjustable="datalim")


def fig1():
    """Screening workflow, the eight checks and what each one found in the audit.
    Laid out in inches so that circles stay round and text fits its box."""
    import matplotlib.image as mpimg
    from matplotlib.patches import FancyBboxPatch
    stages = [("Drug structures", [1], REN / "mrtx1133_2d.png"),
              ("Carrier model", [2], REN / "cage_B36N36.png"),
              ("Method", [4], REN / "slab_side.png"),
              ("Adsorption", [3, 7], REN / "mrtx_pristine_side.png"),
              ("Docking", [5], REN / "kras_pocket.png"),
              ("Result tables", [6], "table"),
              ("QSPR model", [8], "parity")]
    fnd = audit_findings()
    W = S.DOUBLE
    n, pad, gap = len(stages), 0.03, 0.075
    w = (W - 2 * pad - gap * (n - 1)) / n                     # card width (in)
    title_h, img_h, link_h, chip_h, chip_gap = 0.2, 0.78, 0.13, 0.46, 0.05
    card_h = title_h + img_h
    H = 0.03 + card_h + link_h + 2 * chip_h + chip_gap + 0.03
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_axis_off()

    def inset(x, y, wi, hi):
        return fig.add_axes([x / W, y / H, wi / W, hi / H])

    ctop = H - 0.03
    cbot = ctop - card_h
    for i, (title, cks, img) in enumerate(stages):
        x = pad + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, cbot), w, card_h, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc="white", ec="#c3cad4", lw=0.7))
        ax.add_patch(FancyBboxPatch((x, ctop - title_h), w, title_h, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc="#eef1f5", ec="#c3cad4", lw=0.7))
        ax.text(x + w / 2, ctop - title_h / 2, title, ha="center", va="center", fontsize=6.6,
                fontweight="bold", color=S.INK)
        bx, by, bw, bh = x + 0.04, cbot + 0.04, w - 0.08, img_h - 0.08
        if img == "table":
            _thumb_table(inset(bx + 0.02, by + 0.06, bw - 0.04, bh - 0.12))
        elif img == "parity":
            _thumb_parity(inset(bx + 0.17, by + 0.14, bw - 0.21, bh - 0.16))
        else:
            im = mpimg.imread(img)
            ar = im.shape[1] / im.shape[0]
            iw, ih = (bw, bw / ar) if bw / ar <= bh else (bh * ar, bh)
            iax = inset(bx + (bw - iw) / 2, by + (bh - ih) / 2, iw, ih)
            iax.imshow(im, interpolation="lanczos"); iax.set_axis_off()
        if i < n - 1:
            yA = cbot + img_h / 2
            ax.annotate("", xy=(x + w + gap - 0.008, yA), xytext=(x + w + 0.008, yA),
                        arrowprops=dict(arrowstyle="-|>", color=S.MUTED, lw=0.8, mutation_scale=6))
        for j, num in enumerate(cks):
            y1 = cbot - link_h - j * (chip_h + chip_gap)
            y0 = y1 - chip_h
            ax.plot([x + w / 2, x + w / 2], [y1 + (link_h if j == 0 else chip_gap), y1], color=BEFORE, lw=0.7)
            ax.add_patch(FancyBboxPatch((x, y0), w, chip_h, boxstyle="round,pad=0,rounding_size=0.04",
                                        fc="#fdf2f3", ec=BEFORE, lw=0.6))
            ax.scatter([x + 0.1], [y1 - 0.11], s=62, color=BEFORE, zorder=3, linewidths=0)
            ax.text(x + 0.1, y1 - 0.112, str(num), ha="center", va="center", color="white", fontsize=6.2,
                    fontweight="bold", zorder=4)
            name, found = fnd[num]
            ax.text(x + 0.19, y1 - 0.11, name, ha="left", va="center", fontsize=5.6, color=S.INK,
                    linespacing=1.12)
            ax.text(x + w / 2, y0 + 0.095, found, ha="center", va="center", fontsize=5.9, color=BEFORE,
                    fontweight="bold")
    xr = pad + 4 * (w + gap)
    ax.text(xr, cbot - link_h - chip_h - chip_gap - 0.08,
            "Red: what each check found in the audit of the four case studies\n"
            "(1, 2, 5: all four studies; 3: tau; 4, 7: MXene; 6, 8: KRAS)",
            ha="left", va="top", fontsize=5.6, color=S.MUTED, linespacing=1.3)
    S.save(fig, FIG, "Fig1")


# ------------------------------------------------------------------ Fig. 2
def fig2():
    """Compound identity and carrier validity before the rebuild."""
    idt = EV["identity"]
    ca = pd.read_csv(BASE / "data" / "carrier_audit.csv")
    fig = plt.figure(figsize=(S.DOUBLE, 118 * S.MM))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 0.78], hspace=0.62, top=0.95, bottom=0.03)
    top = gs[0].subgridspec(1, 2, wspace=0.55)
    axs = [fig.add_subplot(top[0]), fig.add_subplot(top[1])]
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
    # c: the three invalid carriers, drawn with the audit's own bonds
    import matplotlib.image as mpimg
    from matplotlib.lines import Line2D
    bot = gs[1].subgridspec(1, 3, wspace=0.08)
    cax = []
    for k, (s_, png) in enumerate((("KRAS", "old_KRAS"), ("TNBC", "old_TNBC"), ("GBM", "old_GBM"))):
        r = ca[(ca.system == s_) & (ca.model == "before")].iloc[0]
        a = fig.add_subplot(bot[k])
        a.imshow(mpimg.imread(FIG / "_renders" / f"{png}.png"), interpolation="lanczos")
        a.set_axis_off()
        parts = [x.split() for x in r.forbidden_bonds.split(";")]
        fb = " and ".join(f"{n_} {b.replace('-', '–')}" for b, n_ in parts) + " bonds"
        extra = f"; {int(r.overlapping_pairs)} overlapping atom pairs" if r.overlapping_pairs else ""
        a.set_title(f"{LABEL[s_].split(' / ')[0]}: {sub(r.formula)}", fontsize=6.8, loc="center", pad=2)
        a.text(0.5, -0.03, f"{fb}{extra}", transform=a.transAxes, ha="center", va="top", fontsize=6,
               color=S.INK)
        cax.append(a)
    fig.canvas.draw()
    p0 = cax[0].get_position()
    fig.text(axs[0].get_position().x0 - 0.045, p0.y1 + 0.035, "c", fontsize=9, fontweight="bold", va="bottom")
    fig.legend(handles=[Line2D([], [], color="#faa80d", lw=2.2, label="bond the material cannot contain")],
               loc="lower right", bbox_to_anchor=(0.99, p0.y1 + 0.02), frameon=False, fontsize=6)
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
    fig = plt.figure(figsize=(S.DOUBLE, 118 * S.MM))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 0.72], hspace=0.42, top=0.95, bottom=0.04)
    top = gs[0].subgridspec(1, 2, width_ratios=[1.6, 1], wspace=0.4)
    axs = [fig.add_subplot(top[0]), fig.add_subplot(top[1])]
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
    # c: galantamine, the extreme case, on the free flake and on the supported sheet
    import matplotlib.image as mpimg
    g = pd.read_csv(BASE / "data" / "si_tau_carrier_energy.csv").set_index("name").loc["Galantamine"]
    bot = gs[1].subgridspec(1, 3, wspace=0.06)
    panels = [("tau_old_flake", "free B$_{40}$H$_{15}$ flake, relaxed alone", "reference energy", S.INK),
              ("tau_old_galantamine", "the same flake under galantamine",
               f"{abs(g.dEcar_old_kcal):.1f} kcal mol$^{{-1}}$ below the reference", BEFORE),
              ("tau_new_galantamine", "supported β$_{12}$ sheet under galantamine",
               f"{g.dEcar_new_kcal:.1f} kcal mol$^{{-1}}$ above its own minimum", AFTER)]
    cax = []
    for k, (png, title, sub_, col) in enumerate(panels):
        a = fig.add_subplot(bot[k])
        a.imshow(mpimg.imread(FIG / "_renders" / f"{png}.png"), interpolation="lanczos")
        a.set_axis_off()
        a.set_title(title, fontsize=6.4, loc="center", pad=2)
        a.text(0.5, -0.02, sub_, transform=a.transAxes, ha="center", va="top", fontsize=6.2, color=col,
               fontweight="bold")
        cax.append(a)
    fig.canvas.draw()
    fig.text(axs[0].get_position().x0 - 0.045, cax[0].get_position().y1 + 0.035, "c", fontsize=9,
             fontweight="bold", va="bottom")
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
        K.stat_box(ax, [f"$Q^2_{{CV}}$ = {q[key]['Q2_CV']:.2f}".replace("-", "−"), f"$p$ = {q[key]['p_perm']:.3f}"],
                   loc="upper left")
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


def toc():
    """Table-of-contents graphic, exactly 3.25 × 1.75 in (ACS requirement)."""
    idt, rc, me, q = EV["identity"], EV["reconstruction"]["tau_old"], EV["method"], EV["qspr"]
    nbad = sum(1 for c in EV["carriers"] if c["model"] == "before" and c["forbidden_bonds"] != "none")
    fig = plt.figure(figsize=(3.25, 1.75))
    fig.text(0.03, 0.93, "Rebuilding four carrier screens from raw inputs", fontsize=7.2, weight="bold",
             color=S.INK, va="top")
    items = [(f"{idt['total']['wrong']}/{idt['total']['n']}", "drug structures were\nanother compound"),
             (f"{nbad}/4", "carrier models had\nimpossible bonds"),
             (f"{rc['chem_old']}→{rc['chem_new']}", "'chemisorbers' once the\ncarrier stopped collapsing"),
             (f"{me['gfn2_min_a']:.2f} Å", "xTB lattice of the MXene\n(reference 3.03 Å)")]
    for i, (big, small) in enumerate(items):
        y = 0.75 - i * 0.19
        fig.text(0.03, y, big, fontsize=8.5, weight="bold", color=S.CHEM, va="top")
        fig.text(0.215, y + 0.005, small, fontsize=5.4, color=S.INK, va="top", linespacing=1.05)
    ax = fig.add_axes([0.66, 0.2, 0.31, 0.56])
    v = [q["KRAS_v1_reproduced"]["Q2_CV"], q["KRAS:dE_int"]["Q2_CV"]]
    ax.bar([0, 1], v, color=[S.CHEM, S.ADS], width=0.62)
    ax.axhline(0, color=S.INK, lw=0.6)
    for x, val, p in zip([0, 1], v, [q["KRAS_v1_reproduced"]["p_perm"], q["KRAS:dE_int"]["p_perm"]]):
        ax.text(x, val + (0.05 if val > 0 else -0.05), f"{val:.2f}".replace("-", "−"), ha="center",
                va="bottom" if val > 0 else "top", fontsize=6, weight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["invalid\ncarrier", "valid\ncarrier"], fontsize=5.4)
    ax.set_ylim(-0.55, 0.8)
    ax.set_yticks([-0.5, 0, 0.5])
    ax.tick_params(labelsize=5.2, length=2)
    ax.set_title("QSPR $Q^2_{CV}$, leak-free", fontsize=5.8, loc="center", weight="normal", pad=3)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.text(0.5, 0.02, "8 failure modes · 8 checks that cost less than the calculation", fontsize=5.6,
             ha="center", color=S.MUTED)
    FIG.mkdir(exist_ok=True)
    for ext, kw in (("pdf", {}), ("png", {"dpi": 600}), ("tif", {"dpi": 600,
                                                                 "pil_kwargs": {"compression": "tiff_lzw"}})):
        with plt.rc_context({"savefig.bbox": "standard"}):       # keep the exact page size
            fig.savefig(FIG / f"TOC.{ext}", **kw)
    plt.close(fig)


FIGS = {"1": fig1, "2": fig2, "3": fig3, "4": fig4, "5": fig5, "6": fig6, "toc": toc}

if __name__ == "__main__":
    S.apply()
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
        print(f"Fig{key} done")
