"""
build_manuscript.py - J. Comput. Biophys. Chem. manuscript (Word) of the audit paper. Every
number comes from data/audit_evidence.json, data/carrier_audit.csv or the audit tables.

usage: python src/manuscript/build_manuscript.py
writes manuscript/submission/Manuscript_Audit_JCBC.docx
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import functools

import docx_kit as k  # noqa: E402

k.figure = functools.partial(k.figure, label="Fig.", end=".")      # J. Comput. Biophys. Chem.: "Fig. N."
from references import REFS  # noqa: E402
from sec_audit import audit_methods  # noqa: E402
from sec_discussion import conclusions, discussion  # noqa: E402
from sec_introduction import introduction  # noqa: E402
from sec_results import results  # noqa: E402

BASE = HERE.parents[1]
OUT = BASE / "manuscript" / "submission"
FIG = BASE / "figures"

AUTHOR = "Andrés Monreal Hernández"
AFFIL = "Universidad Estatal de Sonora, Ley Federal del Trabajo S/N, Col. Apolo, 83100 Hermosillo, Sonora, Mexico"
EMAIL = "andres.monreal@ues.mx"
ORCID = "0009-0009-1207-8597"
REPO = "https://github.com/sircalch/methods-pipeline-2d-nanocarriers"
RUNNING_TITLE = "Auditing 2D drug-carrier screens"      # <= 45 letters and spaces
KEYWORDS = ["structure curation", "molecular docking", "tight binding", "nested cross-validation",
            "reproducibility"]                         # 3-5, none repeating a title word
TITLE = ("Auditing Computational Screens of Two-Dimensional Drug Carriers: Eight Failure Modes Found by "
         "Rebuilding Four Case Studies, and a Checklist to Catch Them")


class Cites:
    """ACS style: superscript numbers in order of first citation."""

    def __init__(self):
        self.order = []

    def __call__(self, *keys):
        nums = []
        for key in keys:
            if key not in REFS:
                raise KeyError(key)
            if key not in self.order:
                self.order.append(key)
            nums.append(self.order.index(key) + 1)
        nums = sorted(set(nums))
        spans, start = [], nums[0]
        for a, b in zip(nums, nums[1:] + [None]):
            if b != a + 1:
                spans.append(f"{start}" if start == a else f"{start}–{a}" if a - start > 1 else f"{start},{a}")
                start = b
        return "^{" + ",".join(spans) + "}"

    def list(self):
        return [REFS[k_] for k_ in self.order]


def front(doc):
    k.para(doc, f"**{TITLE}**", align="left", size=15, space_after=12)
    k.para(doc, f"{AUTHOR}^{{*}}", align="left", space_after=2)
    k.para(doc, AFFIL, align="left", size=10, space_after=2)
    k.para(doc, f"^{{*}}E-mail: {EMAIL}. ORCID: {ORCID}", align="left", size=10, space_after=4)
    k.para(doc, f"Running title: {RUNNING_TITLE}", align="left", size=10, space_after=14)


def abstract(doc, ev):
    idt, q, rc = ev["identity"], ev["qspr"], ev["reconstruction"]["tau_old"]
    k.heading(doc, "Abstract")
    k.para(doc,
           "Computational screens of two-dimensional materials as drug carriers combine semiempirical adsorption "
           "energies, docking and quantitative structure–property relationship (QSPR) models, and they are "
           "usually validated with cross-validation and Y-randomization. We rebuilt four such screens from raw "
           "inputs — KRAS-G12D with graphitic carbon nitride, PARP1 with a B_{36}N_{36} cage, EGFR with a "
           "Ti_{3}C_{2}O_{2} MXene and tau filaments with β_{12} borophene — and found eight failure modes that "
           f"this validation cannot detect. Of {idt['total']['n']} drug structures, {idt['total']['wrong']} "
           "encoded a different compound; three of the four carrier models contained bonds the material cannot "
           "have; a borophene flake reconstructed during adsorption, and on it "
           f"{rc['chem_old']} of {rc['n']} drugs appeared to chemisorb, against {rc['chem_new']} on a stable "
           "sheet; GFN2-xTB and GFN1-xTB could not describe the metallic MXene; two docking protocols failed or "
           "could not fail their controls; a virtual screen contained no structures; a drug overlapped its "
           "periodic image; and a leak-free QSPR model that was significant on energies from an invalid carrier "
           f"(*Q*^{{2}}_{{CV}} = {q['KRAS_v1_reproduced']['Q2_CV']:.2f}, *p* = "
           f"{q['KRAS_v1_reproduced']['p_perm']:.3f}) had no predictive power on energies from a valid one "
           "(" + f"{q['KRAS:dE_int']['Q2_CV']:.2f}".replace("-", "−") + "). Each failure mode is caught by a check that costs less than the "
           "calculation it protects. We describe the evidence for each and collect the checks into a list to "
           "apply before any model is fitted.")
    k.para(doc, "**Keywords:** " + "; ".join(KEYWORDS), align="left")


def case_table(doc):
    rows = [["KRAS-G12D (pancreatic cancer)", "7RPZ", "g-C_{3}N_{4} pore flake, pristine and B/P-doped", "33",
             "GFN2-xTB"],
            ["PARP1 (triple-negative breast cancer)", "4UND", "B_{36}N_{36} cage", "30", "GFN2-xTB"],
            ["EGFR (glioblastoma)", "1M17", "Ti_{3}C_{2}O_{2} MXene, periodic slab", "33", "PBE-D3"],
            ["Tau paired helical filaments (Alzheimer's disease)", "8FUG", "β_{12} borophene, supported sheet",
             "28", "GFN2-xTB"]]
    k.table(doc, ("I", "The four case studies after the rebuild."),
            ["Target (disease)", "PDB", "Carrier model", "Drugs", "Adsorption method"], rows, align="llllc",
            font=8.5, note="Drugs, number in the rebuilt cohort (organic compounds with a structure that could "
                           "be docked and adsorbed). For the MXene, adsorption of the alkylating agents is "
                           "computed with periodic DFT (PBE-D3), because the tight-binding methods fail for it.")


def declarations(doc):
    k.heading(doc, "Supporting Information")
    k.para(doc, "The Supporting Information contains the identity of "
                "the 128 drug structures (Table S1), bond census of the carrier models (Table S2), carrier "
                "energy in each tau complex before and after the rebuild (Table S3), redocking controls of the "
                "four studies (Table S4) and the QSPR models before and after the rebuild (Table S5) (PDF).")
    k.heading(doc, "Data and Software Availability")
    k.para(doc, "The scripts that extract every number and figure of this paper from the four case-study "
                f"repositories and from the archive of the pre-rebuild files are available at {REPO} under the MIT "
                "licence, together with the extracted evidence (audit_evidence.json, carrier_audit.csv).")
    k.heading(doc, "Conflict of Interest")
    k.para(doc, "The author declares no competing interests.")
    k.heading(doc, "Use of AI Tools")
    k.placeholder(doc, "[AUTHOR TO COMPLETE BEFORE SUBMISSION: statement on the use of AI tools, as required by "
                       "the journal.]")


def references(doc, refs):
    k.heading(doc, "References", 1)
    from docx.shared import Mm, Pt
    for i, r in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Mm(8)
        p.paragraph_format.first_line_indent = Mm(-8)
        p.paragraph_format.space_after = Pt(3)
        k.rich(p, f"({i}) {r}", size=10)


def main():
    ev = json.loads((BASE / "data" / "audit_evidence.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    c = Cites()
    doc = k.new_document()
    front(doc)
    abstract(doc, ev)
    introduction(doc, ev, c)
    audit_methods(doc, ev, c)
    case_table(doc)
    results(doc, ev, c)
    discussion(doc, ev, c)
    conclusions(doc, ev, c)
    declarations(doc)
    references(doc, c.list())
    out = OUT / "Manuscript_Audit_JCBC.docx"
    doc.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
