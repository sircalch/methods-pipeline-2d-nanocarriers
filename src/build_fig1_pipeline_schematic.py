"""
build_fig1_pipeline_schematic.py
==================================
Figure 1: the nine-step pipeline schematic described in Section 2 of the
manuscript. Purely conceptual/illustrative (boxes and arrows) -- no
simulated or fabricated data is drawn as if it were a result.

Layout: a true boustrophedon (snake) flow, 3 rows x 3 columns. Steps are
grouped into three conceptual phases, each with its own colour, so the
reader sees both the local step-by-step order and the larger structure of
the pipeline at a glance.
"""
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _pubstyle

_pubstyle.apply()
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Three conceptual phases, one colour each (Okabe-Ito, colour-blind safe).
PHASE_A = _pubstyle.ACCENT  # quantum-chemical setup
PHASE_B = _pubstyle.GOOD    # structure- and interaction-derived analysis
PHASE_C = _pubstyle.WARN    # surrogate modelling & validation

STEPS = [
    ("1. Structures", "SMILES → RDKit + MMFF\nGFN2-xTB optimize\n(drug & carrier)", PHASE_A),
    ("2. Adsorption\ngeometry", "Place 3.2 Å above LOCAL\nsurface, 4 orientations,\noptimize every complex", PHASE_A),
    ("3. Interaction\nenergies", "ΔE_int,SP (frozen) &\nΔE_ads (relaxed);\ncontact <1.9 Å = chemisorb", PHASE_A),
    ("4. Δρ map", "GFN2-xTB densities\n(Multiwfn) → isosurface\n(ChimeraX)", PHASE_B),
    ("5. Docking", "AutoDock Vina vs. disease\ntarget; pose-recovery\nchecked by redocking", PHASE_B),
    ("6. Descriptors", "Conceptual-DFT indices\n(η, S, χ, μ, ω)\nfrom the same xtb output", PHASE_B),
    ("7. Surrogate\nmodel", "StandardScaler+RidgeCV\ninside nested 5×5 CV;\n1000× Y-scrambling", PHASE_C),
    ("8. Applicability\ndomain", "OECD Principle 3;\nWilliams hat-matrix\nleverage", PHASE_C),
    ("9. Reproducibility", "run_entire_<system>\n_study.py; code + data\non GitHub & Zenodo", PHASE_C),
]

PHASE_LABELS = [
    (0, "Quantum-chemical setup"),
    (3, "Structure & interaction analysis"),
    (6, "Surrogate modelling & validation"),
]


def rounded_box(ax, xy, w, h, title, body, color):
    box = FancyBboxPatch(
        xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.07",
        linewidth=1.8, edgecolor=color, facecolor="white", zorder=3,
    )
    ax.add_patch(box)
    # subtle tinted header strip so each box reads as one card, not floating text
    header_h = h * 0.30
    header = FancyBboxPatch(
        (xy[0], xy[1] + h - header_h), w, header_h,
        boxstyle="round,pad=0.02,rounding_size=0.07",
        linewidth=0, facecolor=color, alpha=0.12, zorder=2,
    )
    ax.add_patch(header)
    cx = xy[0] + w / 2
    ax.text(cx, xy[1] + h - header_h / 2, title, ha="center", va="center",
            fontsize=9.2, fontweight="bold", color=color, zorder=4)
    ax.text(cx, xy[1] + (h - header_h) / 2, body, ha="center", va="center",
            fontsize=7.4, color=_pubstyle.INK, zorder=4, linespacing=1.5)


def main():
    ncols, nrows = 3, 3
    fig, ax = plt.subplots(figsize=(9.0, 7.4))
    ax.set_xlim(0, ncols)
    ax.set_ylim(-0.05, nrows + 0.28)
    ax.axis("off")
    ax.set_aspect("equal")

    box_w, box_h = 0.90, 0.82
    gap_x, gap_y = 0.10, 0.30

    # True boustrophedon layout: even rows go L->R, odd rows go R->L, so
    # column position always matches the step's place in the reading order.
    positions = []
    for row in range(nrows):
        row_reversed = (row % 2 == 1)
        col_order = range(ncols - 1, -1, -1) if row_reversed else range(ncols)
        for col in col_order:
            x = col * (box_w + gap_x) + 0.05
            y = (nrows - 1 - row) * (box_h + gap_y) + 0.10
            positions.append((x, y))

    for (title, body, color), (x, y) in zip(STEPS, positions):
        rounded_box(ax, (x, y), box_w, box_h, title, body, color)

    cx = [p[0] + box_w / 2 for p in positions]
    cy = [p[1] + box_h / 2 for p in positions]
    right = [p[0] + box_w for p in positions]
    left = [p[0] for p in positions]
    top = [p[1] + box_h for p in positions]
    bottom = [p[1] for p in positions]

    def straight_arrow(p_from, p_to, color=_pubstyle.MUTED):
        a = FancyArrowPatch(p_from, p_to, arrowstyle="-|>", mutation_scale=18,
                             linewidth=1.8, color=color, zorder=1,
                             shrinkA=2, shrinkB=2)
        ax.add_patch(a)

    def down_arrow(i_from, i_to, color=_pubstyle.MUTED):
        """Vertical connector between the last box of one row and the
        first box of the next (both already aligned on the same column
        thanks to the boustrophedon layout)."""
        straight_arrow((cx[i_from], bottom[i_from] - 0.02), (cx[i_to], top[i_to] + 0.02), color)

    # Row 0 (indices 0,1,2): 1 -> 2 -> 3, left to right
    straight_arrow((right[0], cy[0]), (left[1], cy[1]), PHASE_A)
    straight_arrow((right[1], cy[1]), (left[2], cy[2]), PHASE_A)
    down_arrow(2, 3, PHASE_B)
    # Row 1 (indices 3,4,5): 4 -> 5 -> 6, right to left (box order already reversed)
    straight_arrow((left[3], cy[3]), (right[4], cy[4]), PHASE_B)
    straight_arrow((left[4], cy[4]), (right[5], cy[5]), PHASE_B)
    down_arrow(5, 6, PHASE_C)
    # Row 2 (indices 6,7,8): 7 -> 8 -> 9, left to right
    straight_arrow((right[6], cy[6]), (left[7], cy[7]), PHASE_C)
    straight_arrow((right[7], cy[7]), (left[8], cy[8]), PHASE_C)

    # Phase group labels, centred over the first row occupied by each phase.
    row_of = {0: 0, 3: 1, 6: 2}
    for start_idx, label in PHASE_LABELS:
        row = row_of[start_idx]
        y = (nrows - 1 - row) * (box_h + gap_y) + 0.10 + box_h + 0.075
        color = STEPS[start_idx][2]
        ax.text(ncols / 2, y, label, ha="center", va="bottom",
                fontsize=9.5, fontweight="bold", color=color, style="italic")

    fig.suptitle("The nine-step reproducible screening pipeline (§2)",
                  fontsize=13, fontweight="bold", color=_pubstyle.INK, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.94])

    out_path = os.path.join(BASE, "figures", "fig1_pipeline_schematic.png")
    _pubstyle.save(fig, out_path, also_pdf=True)
    print(f"[SUCCESS] {out_path}")


if __name__ == "__main__":
    main()
