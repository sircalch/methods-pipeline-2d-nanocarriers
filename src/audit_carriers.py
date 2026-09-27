"""
audit_carriers.py - chemical validity of the carrier models used before and
after the 2026-09 rebuild of the four case studies: formula, bond census and
bonds that the ideal material cannot contain.

A bond is any pair closer than 1.15 x the sum of covalent radii (Ti-Ti metal
contacts excluded). "Forbidden" bonds per material:
  g-C3N4 (heptazine)      C-C, N-N
  h-BN / BN cage          B-B, N-N
  Ti3C2O2 MXene           C-C, C-O, O-O
  borophene (H-capped)    none (only stability is tested, elsewhere)

writes data/carrier_audit.csv
"""
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]                   # Proyectos doctorado
ARCH = ROOT / "_archivo" / "nano-qsar-limpieza-2026-09-22"
P = ROOT / "nano-qsar-ai-papers"
COV = {"H": 0.31, "B": 0.84, "C": 0.76, "N": 0.71, "O": 0.66, "P": 1.07, "Ti": 1.60}
FORBIDDEN = {"g-C3N4": {"C-C", "N-N"}, "BN cage": {"B-B", "N-N"}, "Ti3C2O2": {"C-C", "C-O", "O-O"},
             "borophene": set()}

CARRIERS = [
    ("KRAS", "before", "g-C3N4", ARCH / "kras" / "invalid_C21N21H6_carrier" / "gC3N4_pristine.xyz"),
    ("KRAS", "after", "g-C3N4", P / "kras-pancreatic-gC3N4-ai" / "data" / "quantum" / "structures" / "gC3N4_pristine.xyz"),
    ("TNBC", "before", "BN cage", ARCH / "tnbc" / "calculations" / "tnbc" / "B36N36_pristine.xyz"),
    ("TNBC", "after", "BN cage", P / "nano-qsar-ai-therapeutics" / "calculations" / "tnbc" / "B36N36_optimized.xyz"),
    ("GBM", "before", "Ti3C2O2", P / "mxene-glioblastoma-qsar-ai" / "calculations" / "gbm" / "Ti12C7O14_optimized.xyz"),
    ("GBM", "after", "Ti3C2O2", P / "mxene-glioblastoma-qsar-ai" / "calculations" / "gbm_dft" / "slab_start.xyz"),
    ("Tau", "before", "borophene", ROOT / "borophene-alzheimer-tau-ai" / "calculations" / "tau" / "beta12_B40H15_doublet_optimized.xyz"),
    ("Tau", "after", "borophene", ROOT / "borophene-alzheimer-tau-ai" / "calculations" / "tau" / "beta12_flat" / "u0.xtbopt.xyz"),
]


def read_xyz(f):
    L = Path(f).read_text().splitlines()
    n = int(L[0].split()[0])
    el = [x.split()[0] for x in L[2:2 + n]]
    xyz = np.array([[float(v) for v in x.split()[1:4]] for x in L[2:2 + n]])
    return el, xyz


def census(el, xyz):
    """Bond counts. A B...B or N...N pair that shares two neighbours of the other
    element is the transannular contact across a four-membered B2N2 ring (about
    1.86 A in BN cages), not a bond; it is counted separately."""
    pairs = [(i, j) for i, j in combinations(range(len(el)), 2)
             if not (el[i] == el[j] == "Ti")
             and np.linalg.norm(xyz[i] - xyz[j]) < 1.15 * (COV[el[i]] + COV[el[j]])]
    nb = {i: set() for i in range(len(el))}
    for i, j in pairs:
        nb[i].add(j)
        nb[j].add(i)
    c = Counter()
    for i, j in pairs:
        a, b = sorted((el[i], el[j]))
        if a == b and a in ("B", "N"):
            other = {k for k in nb[i] & nb[j] if el[k] != a}
            if len(other) >= 2:
                c[f"{a}...{b} 4-ring diagonal"] += 1
                continue
        c[f"{a}-{b}"] += 1
    return c


def main():
    rows = []
    for system, when, material, f in CARRIERS:
        if not Path(f).exists():
            rows.append({"system": system, "model": when, "file": str(f), "status": "missing"})
            continue
        el, xyz = read_xyz(f)
        cnt = Counter(el)
        formula = "".join(f"{e}{cnt[e]}" for e in ("Ti", "C", "B", "N", "O", "P", "H") if cnt[e])
        c = census(el, xyz)
        bad = {k: v for k, v in c.items() if k in FORBIDDEN[material]}
        rows.append({"system": system, "model": when, "material": material, "formula": formula,
                     "n_atoms": len(el), "bonds": "; ".join(f"{k} {v}" for k, v in sorted(c.items())),
                     "forbidden_bonds": "; ".join(f"{k} {v}" for k, v in sorted(bad.items())) or "none",
                     "file": str(Path(f).relative_to(ROOT)).replace("\\", "/")})
    df = pd.DataFrame(rows)
    out = HERE / "data" / "carrier_audit.csv"
    df.to_csv(out, index=False)
    print(df.drop(columns=["file"]).to_string())


if __name__ == "__main__":
    main()
