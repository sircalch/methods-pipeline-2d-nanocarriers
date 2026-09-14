"""Collect the headline numbers of the four disease case studies into one table
+ a cross-system comparison figure for the methods paper."""
import os, json, glob
import numpy as np
import pandas as pd

ROOT = r"C:\Users\Andre\Proyectos doctorado"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, os.path.join(HERE, "src"))
import _pubstyle
_pubstyle.apply()
import matplotlib.pyplot as plt


def q2_ridge(df, feat, tgt):
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.metrics import r2_score
    d = df.dropna(subset=feat + [tgt])
    X, y = d[feat].values, d[tgt].values
    a = np.array([.001, .01, .1, .3, 1, 3, 10, 30, 100, 300, 1000])
    p = Pipeline([("s", StandardScaler()),
                  ("r", RidgeCV(alphas=a, cv=KFold(5, shuffle=True, random_state=42)))])
    yp = cross_val_predict(p, X, y, cv=KFold(5, shuffle=True, random_state=42))
    return len(y), float(r2_score(y, yp))


def main():
    rows = []

    # --- GBM ---
    g = pd.read_csv(os.path.join(ROOT, "nano-qsar-ai-papers", "mxene-glioblastoma-qsar-ai",
                    "data", "processed", "dataset_drug_mxene_pristine.csv"))
    n, q2 = q2_ridge(g, ["MolWt", "MolMR", "E_HOMO_eV", "Omega_eV"], "delta_Eint_SP_kcal_mol")
    e = g["delta_Eint_SP_kcal_mol"]
    rows.append(dict(system="GBM", carrier="Ti$_3$C$_2$O$_2$ MXene", n=n,
                     eint_lo=e.min(), eint_hi=e.max(), regime="physisorption",
                     q2=q2, dq_hero=None))

    # --- Tau ---
    t = pd.read_csv(os.path.join(ROOT, "borophene-alzheimer-tau-ai",
                    "data", "processed", "dataset_tau_borophene_pristine.csv"))
    tp = t[t.adsorption_mode == "physisorption"]
    n_qspr, q2 = q2_ridge(tp, ["MolWt", "MolMR", "E_HOMO_eV", "Omega_eV"], "delta_Eint_SP_kcal_mol")
    e = t["delta_Eint_SP_kcal_mol"]
    nchem = int((t.adsorption_mode == "chemisorption").sum())
    # NOTE: n reported here is the TOTAL complexes successfully modelled at the
    # GFN2-xTB level (all 29: chemisorbers + physisorbers) -- NOT n_qspr (17),
    # which is only the physisorption subset the QSPR surrogate is fit on. Using
    # n_qspr here previously caused Figure 2 to disagree with Table 1's n=29.
    rows.append(dict(system="Tau", carrier=r"$\beta$-12 borophene", n=len(t),
                     eint_lo=e.min(), eint_hi=e.max(),
                     regime=f"mixed: {nchem} chemisorb / {len(tp)} physisorb",
                     q2=q2, dq_hero=None))

    # --- TNBC ---
    for c in glob.glob(os.path.join(ROOT, "nano-qsar-ai-papers", "nano-qsar-ai-therapeutics",
                       "data", "processed", "*b*n*pristine*.csv")):
        tn = pd.read_csv(c)
        col = [x for x in tn.columns if "eint" in x.lower()]
        if col:
            e = tn[col[0]]
            # NOTE: len(tn) (33) counts the full curated cohort including the 3
            # square-planar Pt(II) agents that could NOT be modelled at the
            # GFN2-xTB level (no force field for Pt); e.dropna() correctly
            # excludes them (30), which previously disagreed with Table 1's n=30.
            nchem_tn = int((tn.adsorption_mode == "chemisorption").sum()) if "adsorption_mode" in tn.columns else None
            regime_tn = (f"mixed: {nchem_tn} chemisorb / {int(e.dropna().shape[0]) - nchem_tn} physisorb"
                         if nchem_tn else "weak physisorption")
            rows.append(dict(system="TNBC", carrier="B$_{36}$N$_{36}$ nanocage",
                             n=int(e.dropna().shape[0]), eint_lo=e.min(), eint_hi=e.max(),
                             regime=regime_tn, q2=None, dq_hero=None))
            break

    # --- KRAS (adsorption in a separate results CSV) ---
    for c in glob.glob(os.path.join(ROOT, "nano-qsar-ai-papers", "kras-pancreatic-gC3N4-ai",
                       "results", "quantum", "*adsorption*.csv")):
        k = pd.read_csv(c)
        e = k["Delta_E_ads_kcal_mol"]
        # n=38 = the full set of compounds successfully evaluated at the GFN2-xTB
        # adsorption level (the 33-compound curated docking/QSPR cohort PLUS the
        # 5 prospective screening leads confirmed by quantum calculation) -- this
        # is the correct "modelled at GFN2-xTB level" count for Table 1, not the
        # narrower 33-compound docking cohort alone.
        rows.append(dict(system="KRAS", carrier="g-C$_3$N$_4$ (B,P-doped)",
                         n=k["drug_name"].nunique(), eint_lo=e.min(), eint_hi=e.max(),
                         regime="physisorption (doping-tuned)", q2=None, dq_hero=0.15))
        break

    df = pd.DataFrame(rows).set_index("system").loc[["KRAS", "GBM", "TNBC", "Tau"]]
    df.to_csv(os.path.join(HERE, "data", "cross_system_summary.csv"))
    print(df.to_string())

    # comparison figure: interaction-energy span per system
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    y = np.arange(len(df))[::-1]
    for yi, (name, r) in zip(y, df.iterrows()):
        ax.plot([r.eint_lo, r.eint_hi], [yi, yi], lw=6, solid_capstyle="round",
                color=_pubstyle.OKABE_ITO[list(df.index).index(name) % len(_pubstyle.OKABE_ITO)])
        ax.text(r.eint_hi + 4, yi, f"  n={r.n}", va="center", fontsize=8, color=_pubstyle.MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{s}\n{df.loc[s,'carrier']}" for s in df.index], fontsize=8)
    ax.set_xlabel("GFN2-xTB interaction energy span (kcal mol$^{-1}$)")
    ax.axvspan(-260, -70, color="0.92", zorder=0)
    ax.text(-165, len(df) - 0.35, "covalent / chemisorption", ha="center", fontsize=7.5, color=_pubstyle.MUTED)
    ax.set_title("Interaction-energy regimes across the four 2D-carrier case studies",
                 fontsize=10, fontweight="bold")
    _pubstyle.save(fig, os.path.join(HERE, "figures", "fig2_cross_system_energy_regimes.png"), also_pdf=True)
    print("wrote figures/fig2_cross_system_energy_regimes.png")


if __name__ == "__main__":
    main()
