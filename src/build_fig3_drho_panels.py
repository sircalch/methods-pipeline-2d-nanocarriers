"""
build_fig3_drho_panels.py
===========================
Figure 3: the four real charge-density-difference (Delta_rho) isosurface
renders, one per system's representative complex (the same complex highlighted
in that system's own charge-density analysis -- not necessarily the strongest
binder identified for that system), composed into a single 2x2 panel figure
with the shared _pubstyle house look. Each render is the REAL GFN2-xTB-density
image already built and used in that system's own manuscript -- nothing here
is re-rendered or fabricated, only composed.
"""
import os
import sys
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _pubstyle

_pubstyle.apply()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NANO_QSAR = os.path.dirname(BASE)  # .../nano-qsar-ai-papers
DOCTORADO = os.path.dirname(NANO_QSAR)  # .../Proyectos doctorado

PANELS = [
    ("a", "KRAS-G12D / g-C3N4",
     os.path.join(NANO_QSAR, "kras-pancreatic-gC3N4-ai", "results", "quantum", "drho", "kras_deltarho_render.png"),
     "MRTX1133, physisorption"),
    ("b", "Glioblastoma / Ti3C2O2 MXene",
     os.path.join(NANO_QSAR, "mxene-glioblastoma-qsar-ai", "results", "quantum", "drho", "gbm_deltarho_render.png"),
     "Larotrectinib, physisorption"),
    ("c", "TNBC / B36N36 nanocage",
     os.path.join(NANO_QSAR, "nano-qsar-ai-therapeutics", "results", "quantum", "drho", "tnbc_deltarho_render.png"),
     "Olaparib, physisorption"),
    ("d", "Alzheimer's Tau / β12 borophene",
     os.path.join(DOCTORADO, "borophene-alzheimer-tau-ai", "results", "quantum", "drho", "tau_deltarho_render.png"),
     "Curcumin, chemisorption"),
]


def main():
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.8))
    for (letter, title, path, sub), ax in zip(PANELS, axes.flat):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing real Delta_rho render: {path}")
        im = Image.open(path).convert("RGB")
        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(title, fontsize=9.5, fontweight="bold", color=_pubstyle.INK, pad=4)
        ax.text(0.5, -0.03, sub, transform=ax.transAxes, ha="center", va="top",
                fontsize=8, color=_pubstyle.MUTED, style="italic")
        _pubstyle.panel_label(ax, letter, dx=0.02, dy=1.0, size=12)

    fig.suptitle(
        "Charge-density difference (Δρ = ρ_complex − ρ_carrier − ρ_drug) for one representative "
        "complex per system, analyzed in each case study's own manuscript",
        fontsize=10.5, y=1.00
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = os.path.join(BASE, "figures", "fig3_drho_four_panels.png")
    _pubstyle.save(fig, out_path, also_pdf=True)
    print(f"[SUCCESS] {out_path}")


if __name__ == "__main__":
    main()
