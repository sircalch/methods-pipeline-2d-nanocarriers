"""
build_fig1_pipeline_schematic.py
==================================
Figure 1: the nine-step pipeline schematic described in Section 2 of the
manuscript. Purely conceptual/illustrative (boxes and arrows) -- no
simulated or fabricated data is drawn as if it were a result.
"""
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path
import matplotlib.patches as mpatches

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _pubstyle

_pubstyle.apply()
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STEPS = [
    ("1. Structures", "SMILES → RDKit + MMFF\nGFN2-xTB optimize\n(drug & carrier)", _pubstyle.ACCENT),
    ("2. Adsorption\ngeometry", "Place 3.2 Å above LOCAL\nsurface, 4 orientations,\noptimize every complex", _pubstyle.ACCENT),
    ("3. Interaction\nenergies", "ΔE_int,SP (frozen) &\nΔE_ads (relaxed);\ncontact <1.9 Å = chemisorb", _pubstyle.WARN),
    ("4. Δρ map", "GFN2-xTB densities\n(Multiwfn) → isosurface\n(ChimeraX)", _pubstyle.GOOD),
    ("5. Docking", "AutoDock Vina vs. disease\ntarget; pose-recovery\nchecked by redocking", _pubstyle.ACCENT),
    ("6. Descriptors", "Conceptual-DFT indices\n(η, S, χ, μ, ω)\nfrom the same xtb output", _pubstyle.GOOD),
    ("7. Surrogate\nmodel", "StandardScaler+RidgeCV\ninside nested 5×5 CV;\n1000× Y-scrambling", _pubstyle.WARN),
    ("8. Applicability\ndomain", "OECD Principle 3;\nWilliams hat-matrix\nleverage", _pubstyle.MUTED),
    ("9. Reproducibility", "run_entire_<system>\n_study.py; code + data\non GitHub & Zenodo", _pubstyle.INK),
]


def rounded_box(ax, xy, w, h, title, body, color):
    box = FancyBboxPatch(
        xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.4, edgecolor=color, facecolor="white", zorder=2,
    )
    ax.add_patch(box)
    cx, cy = xy[0] + w / 2, xy[1] + h / 2
    ax.text(cx, xy[1] + h - 0.10, title, ha="center", va="top",
            fontsize=8.6, fontweight="bold", color=color, zorder=3)
    ax.text(cx, xy[1] + h * 0.42, body, ha="center", va="center",
            fontsize=7.0, color=_pubstyle.INK, zorder=3, linespacing=1.4)


def main():
    ncols = 3
    nrows = 3
    fig, ax = plt.subplots(figsize=(8.0, 6.6))
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    ax.axis("off")

    box_w, box_h = 0.92, 0.86
    gap_x, gap_y = 0.08, 0.10

    positions = []
    for row in range(nrows):
        for col in range(ncols):
            x = col * (box_w + gap_x) + 0.04
            y = (nrows - 1 - row) * (box_h + gap_y) + 0.08
            positions.append((x, y))

    for (title, body, color), (x, y) in zip(STEPS, positions):
        rounded_box(ax, (x, y), box_w, box_h, title, body, color)

    # Arrows: snake path 1->2->3 (row0 L-to-R), 3->4 (down), 4->5->6 (row1 R-to-L), 6->7 (down), 7->8->9 (row2 L-to-R)
    def arrow(p_from, p_to):
        a = FancyArrowPatch(p_from, p_to, arrowstyle="-|>", mutation_scale=16,
                             linewidth=1.6, color=_pubstyle.MUTED, zorder=1,
                             connectionstyle="arc3,rad=0.0")
        ax.add_patch(a)

    def elbow_arrow(p0, mid_y, p2):
        """Manual two-segment down-then-across connector, arrowhead only at the end."""
        ax.plot([p0[0], p0[0]], [p0[1], mid_y], color=_pubstyle.MUTED, linewidth=1.6, zorder=1, solid_capstyle="round")
        ax.plot([p0[0], p2[0]], [mid_y, mid_y], color=_pubstyle.MUTED, linewidth=1.6, zorder=1, solid_capstyle="round")
        a = FancyArrowPatch((p2[0], mid_y), p2, arrowstyle="-|>", mutation_scale=16,
                             linewidth=1.6, color=_pubstyle.MUTED, zorder=1)
        ax.add_patch(a)

    cx = [p[0] + box_w / 2 for p in positions]
    cy = [p[1] + box_h / 2 for p in positions]
    right = [p[0] + box_w for p in positions]
    left = [p[0] for p in positions]
    top = [p[1] + box_h for p in positions]
    bottom = [p[1] for p in positions]

    # row 0: 0->1->2
    arrow((right[0], cy[0]), (left[1], cy[1]))
    arrow((right[1], cy[1]), (left[2], cy[2]))
    # down 2->3 (elbow: drop from box 3's right edge, then left into box 4's top)
    mid_y_1 = (bottom[2] + top[3]) / 2
    elbow_arrow((right[2] + gap_x / 2, bottom[2]), mid_y_1, (cx[3], top[3]))
    # row 1 (indices 3,4,5) right-to-left: 3->4->5
    arrow((left[3], cy[3]), (right[4], cy[4]))
    arrow((left[4], cy[4]), (right[5], cy[5]))
    # down 5->6 (elbow: drop from box 6's right edge, then left into box 7's top)
    mid_y_2 = (bottom[5] + top[6]) / 2
    elbow_arrow((right[5] + gap_x / 2, bottom[5]), mid_y_2, (cx[6], top[6]))
    # row 2: 6->7->8
    arrow((right[6], cy[6]), (left[7], cy[7]))
    arrow((right[7], cy[7]), (left[8], cy[8]))

    fig.suptitle("The nine-step reproducible screening pipeline (§2)",
                  fontsize=11.5, fontweight="bold", color=_pubstyle.INK, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    out_path = os.path.join(BASE, "figures", "fig1_pipeline_schematic.png")
    _pubstyle.save(fig, out_path, also_pdf=True)
    print(f"[SUCCESS] {out_path}")


if __name__ == "__main__":
    main()
