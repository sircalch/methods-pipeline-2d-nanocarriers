"""
build_fig4_tau_before_after.py
================================
Figure 4: the Tau/borophene before/after cautionary tale. Top row: real
ChimeraX renders of the Curcumin/B40H15 complex at (a) the original unrelaxed
placement (drug offset from the cluster's global z-max, never optimized) and
(b) the relaxed, chemisorbed pose from the corrected pipeline. Bottom panel:
the real 29-compound Delta_E_int,SP distribution before vs after, from the
actual pre-fix (git history) and post-fix datasets -- not simulated.
"""
import csv
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _pubstyle

_pubstyle.apply()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE, "figures", "fig4_assets")
OLD_RENDER = os.path.join(ASSETS_DIR, "old_complex.png")
NEW_RENDER = os.path.join(ASSETS_DIR, "new_complex.png")
OLD_CSV = os.path.join(ASSETS_DIR, "tau_old_dataset.csv")
NEW_CSV = os.path.join(
    os.path.dirname(os.path.dirname(BASE)),
    "borophene-alzheimer-tau-ai", "data", "processed", "dataset_tau_borophene_pristine.csv"
)


def autocrop(img, margin=0.04):
    bbox = img.split()[-1].getbbox() if img.mode == "RGBA" else None
    if bbox is None:
        return img
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    mx, my = int(w * margin), int(h * margin)
    x0, y0 = max(0, x0 - mx), max(0, y0 - my)
    x1, y1 = min(img.width, x1 + mx), min(img.height, y1 + my)
    return img.crop((x0, y0, x1, y1))


def load_col(path, col):
    with open(path, newline="", encoding="utf-8") as f:
        return [float(r[col]) for r in csv.DictReader(f)]


def main():
    for p in (OLD_RENDER, NEW_RENDER, OLD_CSV, NEW_CSV):
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing required real asset: {p}")

    old_vals = load_col(OLD_CSV, "delta_Eint_SP_kcal_mol")
    new_vals = load_col(NEW_CSV, "delta_Eint_SP_kcal_mol")

    fig = plt.figure(figsize=(7.2, 7.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.85, 1.0], hspace=0.12, wspace=0.06)

    ax_old = fig.add_subplot(gs[0, 0])
    ax_new = fig.add_subplot(gs[0, 1])
    ax_dist = fig.add_subplot(gs[1, :])

    for ax, path, letter, title, sub in [
        (ax_old, OLD_RENDER, "a", "Original: unrelaxed placement", "drug 5-6 Å from the sheet, single point only"),
        (ax_new, NEW_RENDER, "b", "Corrected: relaxed complex", "chemisorbed, 1.41 Å B-C contact"),
    ]:
        im = autocrop(Image.open(path).convert("RGBA"))
        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(title, fontsize=9.5, fontweight="bold", color=_pubstyle.INK, pad=4)
        ax.text(0.5, -0.02, sub, transform=ax.transAxes, ha="center", va="top",
                fontsize=7.8, color=_pubstyle.MUTED, style="italic")
        _pubstyle.panel_label(ax, letter, dx=0.02, dy=1.0, size=12)

    rng = np.random.default_rng(0)
    for i, (vals, label, color, xpos) in enumerate([
        (old_vals, "Original\n(unrelaxed)", _pubstyle.WARN, 0),
        (new_vals, "Corrected\n(relaxed)", _pubstyle.ACCENT, 1),
    ]):
        jitter = rng.uniform(-0.13, 0.13, size=len(vals))
        ax_dist.scatter(np.full(len(vals), xpos) + jitter, vals, s=22, color=color,
                         alpha=0.75, edgecolor="white", linewidth=0.5, zorder=3)
        ax_dist.scatter([xpos], [np.median(vals)], marker="_", s=900, color=_pubstyle.INK,
                         linewidth=2.2, zorder=4)

    ax_dist.axhline(0, color=_pubstyle.GRID, linewidth=1.0, zorder=1)
    ax_dist.set_xticks([0, 1])
    ax_dist.set_xticklabels(["Original\n(unrelaxed)", "Corrected\n(relaxed)"], fontsize=9)
    ax_dist.set_ylabel("ΔE_int,SP (kcal/mol)")
    ax_dist.set_title(
        "(c) Real 29-compound ΔE_int,SP distribution, before vs. after (median: black bar)",
        fontsize=9.5, fontweight="bold", color=_pubstyle.INK, pad=8, loc="left"
    )
    _pubstyle.finish(ax_dist)
    ax_dist.text(
        0.02, 0.03,
        "3 anomalous positive outliers in the original set (phenothiazine dyes; excluded from the manuscript\n"
        "as SCF/geometry artifacts) are shown here for full transparency, not omitted.",
        transform=ax_dist.transAxes, fontsize=7.2, color=_pubstyle.MUTED, style="italic", va="bottom"
    )

    fig.suptitle("Tau / β12 borophene: what geometry relaxation changes", fontsize=11.5,
                  fontweight="bold", color=_pubstyle.INK, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = os.path.join(BASE, "figures", "fig4_tau_before_after.png")
    _pubstyle.save(fig, out_path, also_pdf=True)
    print(f"[SUCCESS] {out_path}")


if __name__ == "__main__":
    main()
