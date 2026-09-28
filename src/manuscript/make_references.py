"""
make_references.py - builds src/manuscript/references.py (ACS style, as required
by J. Chem. Inf. Model.) from Crossref metadata for a fixed list of DOIs.
Every entry is therefore taken from the registry, not typed by hand; entries
without a DOI (software, OECD guidance) are listed explicitly at the end.

usage: python src/manuscript/make_references.py
"""
import re
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
H = {"User-Agent": "refcheck/1.0 (mailto:andres.monreal@ues.mx)"}

DOIS = {
    # audit / validation literature
    "fourches2010": "10.1021/ci100176x", "fourches2016": "10.1021/acs.jcim.6b00129",
    "williams2011": "10.1016/j.drudis.2011.07.007", "kapoor2023": "10.1016/j.patter.2023.100804",
    "warren2006": "10.1021/jm050362n", "tropsha2010": "10.1002/minf.201000061",
    "cherkasov2014": "10.1021/jm4004285", "bender2021": "10.1038/s41596-021-00597-z",
    "sieg2019": "10.1021/acs.jcim.8b00712", "rucker2007": "10.1021/ci700157b",
    "gramatica2007": "10.1002/qsar.200610151",
    # methods used in the case studies
    "bannwarth2019": "10.1021/acs.jctc.8b01176", "grimme2017": "10.1021/acs.jctc.7b00118",
    "trott2010": "10.1002/jcc.21334", "eberhardt2021": "10.1021/acs.jcim.1c00203",
    "kim2021": "10.1093/nar/gkaa971", "giannozzi2017": "10.1088/1361-648X/aa8f79",
    "perdew1996": "10.1103/PhysRevLett.77.3865", "grimme2010": "10.1063/1.3382344",
    # carriers and targets
    "naguib2011": "10.1002/adma.201102306", "khazaei2013": "10.1002/adfm.201202502",
    "feng2016": "10.1038/nchem.2491", "mannix2015": "10.1126/science.aad1080",
    "kroke2002": "10.1039/b111062b", "strout2000": "10.1021/jp994129a",
    "pourmadadi2023": "10.1016/j.jddst.2022.104001", "huang2018_mxene": "10.1039/c7cs00838d",
    "gholami2023": "10.1016/j.poly.2023.116295", "li2023_borophene": "10.1007/s00894-023-05724-z",
    "merz2023": "10.1038/s41467-023-38537-y", "stamos2002": "10.1074/jbc.M207135200",
}
NO_DOI = {
    "oecd2007": "OECD. Guidance Document on the Validation of (Quantitative) Structure-Activity Relationship "
                "[(Q)SAR] Models; OECD Series on Testing and Assessment, No. 69; OECD Publishing: Paris, 2007.",
    "pedregosa2011": "Pedregosa, F.; Varoquaux, G.; Gramfort, A.; Michel, V.; Thirion, B.; Grisel, O.; Blondel, M.; "
                     "Prettenhofer, P.; Weiss, R.; Dubourg, V.; Vanderplas, J.; Passos, A.; Cournapeau, D.; Brucher, M.; "
                     "Perrot, M.; Duchesnay, E. Scikit-learn: Machine Learning in Python. "
                     "J. Mach. Learn. Res. 2011, 12, 2825–2830.",
    'zenodo_kras': 'Monreal Hernández, A. Atomistic Modeling and QSPR-Guided Screening of 2D Graphitic Carbon Nitride Nanocarriers for KRAS-G12D Inhibitor Loading and Target Engagement, version 2.0.0. Zenodo, 2026. https://doi.org/10.5281/zenodo.22700431',
    'zenodo_tnbc': 'Monreal Hernández, A. Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Loading on 2D Nanomaterials, version 2.0.0. Zenodo, 2026. https://doi.org/10.5281/zenodo.22700597',
    'zenodo_gbm': 'Monreal Hernández, A. Explainable AI and Quantum Chemical Exploration of 2D Titanium Carbide MXene (Ti3C2Tx) Nanocarriers for Glioblastoma Therapeutics, version 2.0.0. Zenodo, 2026. https://doi.org/10.5281/zenodo.22700227',
    'zenodo_tau': "Monreal Hernández, A. Machine Learning-Driven Nano-QSAR and Quantum Chemical Design of Functionalized 2D Borophene Nanocarriers for Alzheimer's Tau-Targeted Therapeutics, version 2.0.1. Zenodo, 2026. https://doi.org/10.5281/zenodo.22700723",
    'zenodo_methods_v1': "Monreal Hernández, A. Don't Fool Yourself When Screening 2D-Nanomaterial Drug Carriers: A Reproducible GFN2-xTB + Docking + Leak-Free QSAR Pipeline, Four Disease Case Studies, and a Cautionary Tale, version 1.0.1. Zenodo, 2026. https://doi.org/10.5281/zenodo.22760388",
    # Zenodo deposits of the pre-audit versions (DataCite DOIs, not in Crossref)
    "rdkit": "RDKit: Open-Source Cheminformatics, version 2024.03. https://www.rdkit.org "
             "(accessed 2026-09-26).",
}


# ACS (CASSI) journal abbreviations where Crossref gives the full or a non-ACS form
JOURNAL = {"J Mol Model": "J. Mol. Model.", "Journal of Drug Delivery Science and Technology": "J. Drug Delivery Sci. Technol.", "Polyhedron": "Polyhedron", "Molecular Informatics": "Mol. Inf.", "Nat Protoc": "Nat. Protoc.",
           "Journal of Chemical Theory and Computation": "J. Chem. Theory Comput.", "J Comput Chem": "J. Comput. Chem.",
           "Nucleic Acids Research": "Nucleic Acids Res.", "The Journal of Chemical Physics": "J. Chem. Phys.",
           "Advanced Materials": "Adv. Mater.", "Adv Funct Materials": "Adv. Funct. Mater.", "Nature Chem": "Nat. Chem.",
           "Nat Commun": "Nat. Commun.", "Journal of Biological Chemistry": "J. Biol. Chem."}
# titles that Crossref stores with an appended footnote or split formulas
TITLE = {"giannozzi2017": "Advanced capabilities for materials modelling with Quantum ESPRESSO",
         "kroke2002": "Tri-s-triazine derivatives. Part I. From trichloro-tri-s-triazine to graphitic C3N4 structures",
         "strout2000": "Structure and Stability of Boron Nitrides: Isomers of B12N12",
         "naguib2011": "Two-Dimensional Nanocrystals Produced by Exfoliation of Ti3AlC2"}


def initials(given):
    parts = [p for p in re.split(r"[\s]+", given or "") if p]
    out = []
    for p in parts:
        out.append("-".join(q[0] + "." for q in p.split("-") if q))
    return " ".join(out)


def acs(m, key=None):
    au = [f"{a.get('family', '')}, {initials(a.get('given', ''))}".strip(", ") for a in m.get("author", [])
          if a.get("family")]
    # J. Comput. Biophys. Chem.: full author lists, never 'et al.'
    auth = "; ".join(au[:-1]) + ("; " if len(au) > 1 else "") + au[-1] if au else ""
    auth = auth.replace("; et al.", "; et al.")
    title = TITLE.get(key) or re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m["title"][0])).strip().rstrip(".")
    jour = (m.get("short-container-title") or m.get("container-title") or [""])[0]
    jour = JOURNAL.get(jour, jour)
    year = (m.get("published-print") or m.get("issued"))["date-parts"][0][0]
    vol = m.get("volume", "")
    pages = (m.get("page") or m.get("article-number") or "").replace("-", "–")
    return f"{auth} {title}. *{jour}* **{year}**, *{vol}*, {pages}. https://doi.org/{m['DOI']}"


def main():
    refs = {}
    for k, d in DOIS.items():
        m = None
        for _ in range(5):
            try:
                m = requests.get("https://api.crossref.org/works/" + d, headers=H, timeout=30).json()["message"]
                break
            except Exception:
                time.sleep(4)
        if m is None:
            raise SystemExit(f"Crossref lookup failed for {k} ({d})")
        refs[k] = acs(m, k)
        time.sleep(0.8)
    refs.update(NO_DOI)
    lines = ['"""references.py - ACS-style references, generated by make_references.py from Crossref."""', "",
             "REFS = {"]
    lines += [f"    {k!r}: {v!r}," for k, v in refs.items()]
    lines.append("}")
    (HERE / "references.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for k, v in refs.items():
        print(k, "->", v[:150])


if __name__ == "__main__":
    main()
