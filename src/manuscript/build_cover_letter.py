"""build_cover_letter.py - cover letter for J. Comput. Biophys. Chem. (Word). Numbers
from data/audit_evidence.json."""
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import docx_kit as k  # noqa: E402
from build_manuscript import AFFIL, AUTHOR, EMAIL, ORCID, TITLE  # noqa: E402

BASE = HERE.parents[1]
OUT = BASE / "manuscript" / "submission"


def main():
    ev = json.loads((BASE / "data" / "audit_evidence.json").read_text())
    idt, rc, q = ev["identity"], ev["reconstruction"]["tau_old"], ev["qspr"]
    doc = k.new_document()
    for t in (AUTHOR, AFFIL, EMAIL, "", date.today().strftime("%d %B %Y"), "",
              "The Editor-in-Chief", "Journal of Computational Biophysics and Chemistry", ""):
        k.para(doc, t, align="left", space_after=0)
    k.para(doc, "Dear Editor,", align="left")
    k.para(doc, f"I submit the manuscript \"{TITLE}\" for consideration as a Research article in the Journal of "
                "Computational Biophysics and Chemistry.")
    k.para(doc,
           "Screens of two-dimensional materials as drug carriers are usually judged by the statistics of the "
           "models fitted at their end. The manuscript reports what I found when I rebuilt four of my own "
           "screens of this kind from raw inputs, with scripts: eight failure modes that cross-validation and "
           f"Y-randomization cannot detect. {idt['total']['wrong']} of {idt['total']['n']} drug structures "
           "encoded a different compound, three of the four carrier models contained bonds the material cannot "
           f"have, and a borophene carrier reconstructed during adsorption, on which {rc['chem_old']} of {rc['n']} "
           f"drugs appeared to chemisorb against {rc['chem_new']} on a stable sheet. Most directly relevant to the journal, a QSPR model that was leak-free and "
           f"significant (*Q*^{{2}}_{{CV}} = {q['KRAS_v1_reproduced']['Q2_CV']:.2f}, *p* = "
           f"{q['KRAS_v1_reproduced']['p_perm']:.3f}) described a carrier that does not exist, and had no "
           "predictive power once the carrier was corrected. For each failure mode the paper gives the evidence "
           "and a check that costs less than the calculation it protects, and it collects the checks into a "
           "list to apply before any model is fitted.")
    k.para(doc,
           "Earlier versions of the four case studies and a methods description based on them were deposited "
           "on Zenodo before the audit; the manuscript states what changed. The rebuilt case studies are being "
           "prepared for submission to the Journal of Molecular Modeling as separate papers; this manuscript "
           "does not report their results beyond what is needed to document the failure modes. The scripts "
           "that extract every number and figure are openly available. The manuscript has not been published "
           "and is not under consideration elsewhere. The author declares no competing interests.")
    k.para(doc, "Sincerely,", align="left", space_after=0)
    k.para(doc, f"{AUTHOR} (ORCID {ORCID})", align="left")
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "Cover_Letter_JCBC.docx"
    doc.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
