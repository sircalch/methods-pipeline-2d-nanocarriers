"""
prepare_methods_submission_package.py
Packages the Beilstein J. Nanotechnology Perspective manuscript into an
official submission-ready folder and ZIP archive.
"""

import os
import shutil
import zipfile

from docx import Document
from docx.shared import Inches, Pt, RGBColor

import generate_methods_manuscript


def create_cover_letter(sub_dir):
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(1.0)
        s.left_margin = s.right_margin = Inches(1.0)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(33, 33, 33)

    p_h = doc.add_paragraph()
    p_h.paragraph_format.space_after = Pt(14)
    p_h.add_run(
        "Andrés Monreal Hernández, Ph.D.\n"
        "Universidad Estatal de Sonora\n"
        "Hermosillo, Sonora, Mexico\n"
        "Email: andres.monreal@ues.mx | ORCID: 0009-0009-1207-8597\n"
        "Date: September 13, 2026\n"
    ).font.bold = True

    p_ed = doc.add_paragraph()
    p_ed.paragraph_format.space_after = Pt(12)
    p_ed.add_run(
        "To: The Editor-in-Chief\n"
        "Beilstein Journal of Nanotechnology\n"
        "Beilstein-Institut, Frankfurt am Main, Germany\n"
    )

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    p_sub.add_run("Subject: Submission of a Perspective Article").font.bold = True

    doc.add_paragraph("Dear Editor-in-Chief,")
    doc.add_paragraph(
        "On behalf of my co-authors (Sara Lizbeth Franco Amaya, Carlos Ivanhoe Martínez Osorio, and myself), "
        "I am pleased to submit our manuscript for consideration as a Perspective article:"
    )
    p_t = doc.add_paragraph()
    p_t.paragraph_format.left_indent = Inches(0.4)
    p_t.paragraph_format.space_after = Pt(10)
    r_t = p_t.add_run(
        "“Don't Fool Yourself When Screening 2D-Nanomaterial Drug Carriers: A Reproducible GFN2-xTB + "
        "Docking + Leak-Free QSAR Pipeline, Four Disease Case Studies, and a Cautionary Tale”"
    )
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(13, 71, 161)

    doc.add_paragraph(
        "This Perspective distills a methodological lesson from four independent computational drug-carrier "
        "screens we have carried out for unrelated disease systems (KRAS-G12D/pancreatic cancer on graphitic "
        "carbon nitride; glioblastoma on Ti3C2Tx MXene; triple-negative breast cancer on a B36N36 nanocage; "
        "Alzheimer's Tau on β12 borophene). We describe a single reproducible pipeline — relaxed-geometry "
        "GFN2-xTB adsorption modeling, AutoDock Vina docking with an explicit pose-recovery check, and a "
        "leak-free nested cross-validated QSPR surrogate — and show, with a genuine before/after result from "
        "our own Tau/borophene work, what an unrelaxed single-point adsorption geometry can hide: our first "
        "pass at that system reported an inert-looking physisorption energy for a surface that, once the "
        "complex was actually geometry-optimized, turned out to chemisorb 12 of 29 screened ligands through a "
        "new covalent bond. We believe this fits the journal's Perspective format directly — a constructive, "
        "critical discussion of a recurring methodological pitfall in a field of active interest to your "
        "readership, illustrated with a concrete, corrected, and fully reproducible worked example rather than "
        "a purely abstract argument."
    )
    doc.add_paragraph(
        "Every quantitative claim in the manuscript is drawn from the four underlying case studies, each "
        "independently archived with open code and data at its own Zenodo deposit (DOIs 10.5281/zenodo.22187819, "
        "22187857, 22187834, and 22187873)."
    )
    doc.add_paragraph(
        "All authors have approved the manuscript and confirm no competing interests."
    )
    p_sign = doc.add_paragraph()
    p_sign.paragraph_format.space_before = Pt(14)
    p_sign.add_run(
        "Sincerely,\n\n"
        "Andrés Monreal Hernández, Ph.D. (Corresponding Author)\n"
        "Universidad Estatal de Sonora, Mexico\n"
        "Email: andres.monreal@ues.mx"
    )

    out_docx = os.path.join(sub_dir, "01_Cover_Letter_Beilstein_Perspective.docx")
    doc.save(out_docx)
    print(f"Generated Methods Paper Cover Letter: {out_docx}")


def build_submission_bundle():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub_dir = os.path.join(base_dir, "manuscript", "submission_ready")
    os.makedirs(sub_dir, exist_ok=True)

    create_cover_letter(sub_dir)

    generate_methods_manuscript.generate_methods_manuscript()
    src_ms = os.path.join(base_dir, "manuscript",
                           "Beilstein_Perspective_Methods_Pipeline_Monreal_Hernandez_et_al.docx")
    dst_ms = os.path.join(sub_dir, "02_Manuscript_Methods_Pipeline_Monreal_Hernandez_et_al.docx")
    shutil.copyfile(src_ms, dst_ms)

    zip_path = os.path.join(base_dir, "methods-pipeline-2d-nanocarriers-SUBMISSION-DRAFT.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for root, dirs, files in os.walk(sub_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, sub_dir)
                zip_f.write(file_path, os.path.join("submission_ready", rel_path))

    print(f"\n=======================================================")
    print(f">>> METHODS PAPER DRAFT PACKAGE GENERATED ({os.path.getsize(zip_path)} bytes) <<<")
    print(f" -> {zip_path}")
    print(f" NOTE: this is a DRAFT package -- all 4 figures are now built and embedded,")
    print(f" but this has NOT been reviewed the way the other 4 papers' final")
    print(f" submission packages were. Do not submit without a full review pass.")
    print(f"=======================================================")


if __name__ == "__main__":
    build_submission_bundle()
