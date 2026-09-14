"""
generate_methods_manuscript.py
================================
Builds the Beilstein Journal of Nanotechnology "Perspective" manuscript for
the methods paper that ties together the four sibling nano-QSAR case studies
(KRAS/g-C3N4, GBM/MXene, TNBC/B36N36, Tau/borophene).

Venue decided 2026-09-13: Beilstein J. Nanotechnol., Perspective article.
Diamond Open Access (no APC for author or reader), Q2, and the "Perspective"
article type ("constructive critical discussion... insights on the impact or
future of a field") is a direct fit for this paper's argument. See
[[feedback_prioritize_q3_no_apc_journals]].

Status: text is complete for Sections 1-6 + back matter. Figure 2 (the real,
already-built cross-system energy-regime plot) is embedded. Figures 1
(pipeline schematic), 3 (four Delta_rho panels), and 4 (Tau before/after) are
NOT yet built -- referenced in the text but not embedded, with an explicit
[FIGURE N - PENDING] marker rather than a fabricated placeholder image.
"""

import csv
import os

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

import _backmatter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures")
DATA_CSV = os.path.join(BASE, "data", "cross_system_summary.csv")


def load_cross_system_table():
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        r.font.name = "Arial"
        r.font.bold = True
        if level == 1:
            r.font.size = Pt(14)
            r.font.color.rgb = RGBColor(13, 71, 161)
        elif level == 2:
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(21, 101, 192)
        else:
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(33, 33, 33)
    return h


def add_image_if_exists(doc, img_path, caption_text, width=Inches(6.2)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        run = p_img.add_run()
        run.add_picture(img_path, width=width)
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_after = Pt(12)
        p_cap.paragraph_format.line_spacing = 1.15
        r_num = p_cap.add_run(caption_text.split(":")[0] + ": ")
        r_num.font.bold = True
        r_num.font.size = Pt(9.5)
        r_num.font.color.rgb = RGBColor(21, 101, 192)
        r_desc = p_cap.add_run(":".join(caption_text.split(":")[1:]))
        r_desc.font.size = Pt(9.5)
        r_desc.font.italic = True
    else:
        p = doc.add_paragraph()
        r = p.add_run(f"[{caption_text.split(':')[0]} — PENDING: not yet generated]")
        r.font.italic = True
        r.font.color.rgb = RGBColor(176, 42, 42)


def add_pending_figure_note(doc, label, caption):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run(f"[{label} — PENDING: {caption}]")
    r.font.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(176, 42, 42)


REFERENCES = [
    {"citation": "Bannwarth, C.; Ehlert, S.; Grimme, S. GFN2-xTB—An Accurate and Broadly Parametrized Self-Consistent Tight-Binding Quantum Chemical Method with Multipole Electrostatics and Density-Dependent Dispersion Contributions. Journal of Chemical Theory and Computation 2019, 15 (3), 1652-1671.", "doi": "10.1021/acs.jctc.8b01176"},
    {"citation": "Grimme, S.; Bannwarth, C.; Shushkov, P. A Robust and Accurate Tight-Binding Quantum Chemical Method for Structures, Vibrational Frequencies, and Noncovalent Interactions of Large Molecular Systems Parameterized for All spd-Block Elements (Z = 1-86). Journal of Chemical Theory and Computation 2017, 13 (5), 1989-2009.", "doi": "10.1021/acs.jctc.7b00118"},
    {"citation": "Caldeweyher, E.; Ehlert, S.; Hansen, A.; Neugebauer, H.; Spicher, S.; Bannwarth, C.; Grimme, S. A generally applicable atomic-charge dependent London dispersion correction. The Journal of Chemical Physics 2019, 150 (15), 154122.", "doi": "10.1063/1.5090222"},
    {"citation": "Grimme, S.; Antony, J.; Ehrlich, S.; Krieg, H. A consistent and accurate ab initio parametrization of density functional dispersion correction (DFT-D) for the 94 elements H-Pu. The Journal of Chemical Physics 2010, 132 (15), 154104.", "doi": "10.1063/1.3382344"},
    {"citation": "Trott, O.; Olson, A. J. AutoDock Vina: Improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. Journal of Computational Chemistry 2010, 31 (2), 455-461.", "doi": "10.1002/jcc.21334"},
    {"citation": "Eberhardt, J.; Santos-Martins, D.; Tillack, A. F.; Forli, S. AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings. Journal of Chemical Information and Modeling 2021, 61 (8), 3891-3898.", "doi": "10.1021/acs.jcim.1c00203"},
    {"citation": "Landrum, G. RDKit: Open-Source Cheminformatics Software; GitHub: 2021.", "doi": "10.5281/zenodo.5086055"},
    {"citation": "Geerlings, P.; De Proft, F.; Langenaeker, W. Conceptual Density Functional Theory. Chemical Reviews 2003, 103 (5), 1793-1874.", "doi": "10.1021/cr990029p"},
    {"citation": "Varoquaux, G.; Buitinck, L.; Louppe, G.; Grisel, O.; Pedregosa, F.; Mueller, A. Scikit-learn. GetMobile: Mobile Computing and Communications 2015, 19 (1), 29-33.", "doi": "10.1145/2786984.2786995"},
    {"citation": "Rücker, C.; Rücker, G.; Meringer, M. y-Randomization and Its Variants in QSPR/QSAR. Journal of Chemical Information and Modeling 2007, 47 (6), 2345-2357.", "doi": "10.1021/ci700157b"},
    {"citation": "Tropsha, A. Best Practices for QSAR Model Development, Validation, and Exploitation. Molecular Informatics 2010, 29 (6-7), 476-488.", "doi": "10.1002/minf.201000061"},
    {"citation": "Gramatica, P. Principles of QSAR models validation: internal and external. QSAR & Combinatorial Science 2007, 26 (5), 694-701.", "doi": "10.1002/qsar.200610151"},
    {"citation": "OECD. Guidance Document on the Validation of (Quantitative) Structure-Activity Relationship [(Q)SAR] Models; OECD Environment Health and Safety Publications, Series on Testing and Assessment No. 69; OECD: Paris, 2007.", "doi": ""},
    {"citation": "Cherkasov, A.; Muratov, E. N.; Fourches, D.; Varnek, A.; Baskin, I. I.; Cronin, M.; Dearden, J.; Gramatica, P.; Martin, Y. C.; Todeschini, R.; et al. QSAR Modeling: Where Have You Been? Where Are You Going To? Journal of Medicinal Chemistry 2014, 57 (12), 4977-5010.", "doi": "10.1021/jm4004285"},
    {"citation": "Lu, T.; Chen, F. Multiwfn: A multifunctional wavefunction analyzer. Journal of Computational Chemistry 2012, 33 (5), 580-592.", "doi": "10.1002/jcc.22885"},
    {"citation": "Pettersen, E. F.; Goddard, T. D.; Huang, C. C.; Meng, E. C.; Couch, G. S.; Croll, T. I.; Morris, J. H.; Ferrin, T. E. UCSF ChimeraX: Structure visualization for researchers, educators, and developers. Protein Science 2021, 30 (1), 70-82.", "doi": "10.1002/pro.3943"},
    {"citation": "Ong, W. J.; Tan, L. L.; Ng, Y. H.; Yong, S. T.; Chai, S. P. Graphitic Carbon Nitride (g-C3N4)-Based Photocatalysts for Artificial Photosynthesis and Environmental Remediation: Are We a Step Closer To Achieving Sustainability? Chemical Reviews 2016, 116 (12), 7159-7329.", "doi": "10.1021/acs.chemrev.6b00075"},
    {"citation": "Naguib, M.; Mochalin, V. N.; Barsoum, M. W.; Gogotsi, Y. 25th Anniversary Article: MXenes: A New Family of Two-Dimensional Materials. Advanced Materials 2014, 26 (7), 992-1005.", "doi": "10.1002/adma.201304138"},
    {"citation": "Golberg, D.; Bando, Y.; Huang, Y.; Terao, T.; Mitome, M.; Tang, C.; Zhi, C. Boron Nitride Nanotubes and Nanosheets. ACS Nano 2010, 4 (6), 2979-2993.", "doi": "10.1021/nn1006495"},
    {"citation": "Mannix, A. J.; Zhou, X. F.; Kiraly, B.; Wood, J. D.; Alducin, D.; Myers, B. D.; Liu, X.; Fisher, B. L.; Santiago, U.; Guest, J. R.; et al. Synthesis of borophenes: Anisotropic, two-dimensional boron polymorphs. Science 2015, 350 (6267), 1513-1516.", "doi": "10.1126/science.aad1080"},
    {"citation": "Zhang, Z.; Penev, E. S.; Yakobson, B. I. Two-dimensional boron: structures, properties and applications. Chemical Society Reviews 2017, 46 (22), 6746-6763.", "doi": "10.1039/c7cs00261k"},
    {"citation": "Monreal Hernández, A.; Franco Amaya, S. L.; Martínez Osorio, C. I. Quantum-Validated QSPR and Molecular Screening of KRAS-G12D Inhibitors across Graphitic Carbon Nitride Interaction Space [Data set]. Zenodo. 2026.", "doi": "10.5281/zenodo.22187819"},
    {"citation": "Monreal Hernández, A.; Franco Amaya, S. L.; Martínez Osorio, C. I. Explainable AI and Quantum Chemical Exploration of 2D Titanium Carbide MXene Nanosheets for Glioblastoma Therapeutics [Data set]. Zenodo. 2026.", "doi": "10.5281/zenodo.22187857"},
    {"citation": "Monreal Hernández, A.; Franco Amaya, S. L.; Martínez Osorio, C. I. Machine Learning-Driven Nano-QSAR and Quantum Chemical Design of Functionalized 2D Borophene Nanosheets for Targeted Disaggregation of Pathological Tau Fibrils [Data set]. Zenodo. 2026.", "doi": "10.5281/zenodo.22187834"},
    {"citation": "Monreal Hernández, A.; Franco Amaya, S. L.; Martínez Osorio, C. I. Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages [Data set]. Zenodo. 2026.", "doi": "10.5281/zenodo.22187873"},
]


def generate_methods_manuscript():
    rows = {r["system"]: r for r in load_cross_system_table()}
    doc = Document()

    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(1.0)
        s.left_margin = s.right_margin = Inches(1.0)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(33, 33, 33)

    # ---- Title / Authors ----
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(10)
    p_title.paragraph_format.line_spacing = 1.15
    r_title = p_title.add_run(
        "Don't Fool Yourself When Screening 2D-Nanomaterial Drug Carriers: A "
        "Reproducible GFN2-xTB + Docking + Leak-Free QSAR Pipeline, Four Disease "
        "Case Studies, and a Cautionary Tale"
    )
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(16.5)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(13, 71, 161)

    p_authors = doc.add_paragraph()
    p_authors.paragraph_format.space_after = Pt(4)
    r_auth = p_authors.add_run(
        "Andrés Monreal Hernández1,*, Sara Lizbeth Franco Amaya2, and Carlos Ivanhoe Martínez Osorio3"
    )
    r_auth.font.bold = True
    r_auth.font.size = Pt(11.0)

    p_aff = doc.add_paragraph()
    p_aff.paragraph_format.space_after = Pt(12)
    p_aff.paragraph_format.line_spacing = 1.10
    r_aff = p_aff.add_run(
        "1 Universidad Estatal de Sonora, Ley Federal del Trabajo S/N, Col. Apolo, C.P. 83100, Hermosillo, Sonora, Mexico.\n"
        "2 Doctorado en Nanotecnología, Universidad de Sonora, Hermosillo, Sonora, Mexico.\n"
        "3 Doctorado en Ciencia de Materiales, Universidad de Sonora, Hermosillo, Sonora, Mexico.\n"
        "*Corresponding Author: andres.monreal@ues.mx | ORCID: 0009-0009-1207-8597"
    )
    r_aff.font.size = Pt(9.5)
    r_aff.font.italic = True
    r_aff.font.color.rgb = RGBColor(80, 80, 80)

    # ---- Abstract ----
    add_heading_styled(doc, "Abstract", level=1)
    doc.add_paragraph(
        "Computational screening of two-dimensional (2D) nanomaterials as drug-delivery scaffolds is cheap "
        "enough to run for any disease target — a GFN2-xTB adsorption calculation and an AutoDock Vina docking "
        "run together take hours on a workstation — which has produced a large and fast-growing literature. "
        "Much of it, however, rests on protocols that quietly break: regression targets fabricated from "
        "empirical descriptor formulas rather than measured or computed energies, cross-validation schemes that "
        "leak test-set information into preprocessing, and adsorption geometries built by placing a drug above "
        "a sheet without ever relaxing the resulting complex. We built a single reproducible pipeline — GFN2-xTB "
        "geometry optimization, docking against the disease target's experimental structure, and a leak-free "
        "nested cross-validated QSPR surrogate with Y-scrambling — and applied it, unchanged, to four unrelated "
        "disease systems: KRAS-G12D/pancreatic cancer on graphitic carbon nitride, glioblastoma on Ti3C2Tx "
        "MXene, triple-negative breast cancer on a B36N36 nanocage, and Alzheimer's Tau on β12 borophene. Under "
        "this protocol, one carrier, MXene, shows only modest, non-predictive physisorption (Q²_CV ≈ 0.10), an "
        "honest but unglamorous result. Two others, the B36N36 nanocage and β12 borophene, turn out to be more "
        "complex than a single physisorption picture suggests. Each hides a small chemisorbing subpopulation — "
        "5 of 33 TNBC-directed drugs, 12 of 29 Tau-directed drugs — behind a larger, non-predictive physisorbing "
        "majority. The field's common practice of a single, unrelaxed point calculation would have hidden that "
        "distinction entirely in both cases, and did, in our own first pass at the borophene system: we reported "
        "an inert-looking physisorption energy for what is actually a chemically reactive surface for a third "
        "of its ligands. The fourth carrier, boron/phosphorus-doped graphitic carbon nitride, is the exception "
        "in the opposite sense: instead of a hidden chemisorption story, it is a hidden predictive-model story. "
        "Despite comparably modest interaction energies and no detected chemisorption, its adsorption-energy "
        "QSPR is genuinely predictive (Q²_CV = 0.51-0.58) — evidence that the leak-free protocol itself is not "
        "simply too conservative to detect a real signal when one is present. We use the borophene case, "
        "corrected, as a worked example of what a relaxed-geometry, leak-free screen changes, and distill the "
        "broader lesson into a short checklist for computational drug-carrier screening."
    )
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_after = Pt(14)
    r_kwt = p_kw.add_run("Keywords: ")
    r_kwt.font.bold = True
    p_kw.add_run(
        "2D Nanomaterials; Drug Delivery; QSAR/QSPR Validation; GFN2-xTB; Molecular Docking; "
        "Reproducibility; Data Leakage."
    )

    # ---- 1. Introduction ----
    add_heading_styled(doc, "1. Introduction — The Problem", level=1)
    doc.add_paragraph(
        "Two-dimensional nanomaterials — graphitic carbon nitride (g-C3N4) [17], MXenes [18], boron nitride "
        "nanostructures [19], and borophene [20,21] among them — are widely proposed as drug-delivery scaffolds, and the "
        "computational screening literature evaluating them is large and growing quickly. The appeal is "
        "obvious: a GFN2-xTB adsorption calculation and an AutoDock Vina docking run together take hours, not "
        "months, so a single group can screen dozens of candidate drugs against a candidate carrier before any "
        "wet-lab work begins. That speed is also the risk. We have found, in the course of building four such "
        "screens for unrelated disease systems, that a small number of protocol failures recur often enough to "
        "be worth naming explicitly, because each one is easy to introduce without noticing and each one can "
        "silently invert the paper's conclusion."
    )
    for i, item in enumerate([
        ("Fabricated regression targets.", "A ΔG_bind or ΔE_ads reported as if it were a "
         "quantum-mechanical result is sometimes, on inspection, an empirical linear formula over RDKit "
         "descriptors — internally consistent, but not a physical energy."),
        ("Data leakage.", "Feature scaling or feature selection fit on the whole dataset before "
         "cross-validation inflates the reported Q² in a way that does not reproduce on genuinely new "
         "compounds; the effect can be large enough to turn a non-predictive model into an apparently "
         "excellent one, a failure mode long flagged in the QSAR best-practices literature [11,12,14]."),
        ("Unrelaxed adsorption geometries.", "A drug is “placed” some fixed distance above the "
         "carrier and a single-point energy is reported as the adsorption energy, with the complex never "
         "geometry-optimized. If the placement protocol references the wrong point on a buckled or finite "
         "cluster, the drug can end up several Ångström away from the surface it is nominally adsorbing "
         "onto."),
        ("Un-run benchmarks.", "A “DFT validation” table is presented with no accompanying output "
         "files, and the numbers cannot be independently reproduced from the stated method."),
        ("Cohort and bibliography drift.", "The descriptor set, the docking cohort, and the reference list "
         "circulate between related studies from the same group, occasionally picking up a mismatch — a "
         "different protein target, a different compound count — that a careful re-derivation would have "
         "caught."),
    ], start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(6)
        r_num = p.add_run(f"{i}. {item[0]} ")
        r_num.font.bold = True
        p.add_run(item[1])
    doc.add_paragraph(
        "None of these failures require bad faith; each is a plausible shortcut under time pressure, and each "
        "is exactly the kind of thing that peer review, without access to the underlying code and raw outputs, "
        "cannot reliably catch. This Perspective describes one pipeline that avoids all five, applied without "
        "modification to four disease systems that share no biology, no carrier chemistry, and no descriptor "
        "set — and documents, in the fourth case, exactly what broke when we did not yet have this discipline "
        "in place."
    )

    # ---- 2. The pipeline ----
    add_heading_styled(doc, "2. The Reproducible Screening Pipeline", level=1)
    doc.add_paragraph(
        "For every (drug, 2D-carrier) pair evaluated in this work, the following nine-step protocol is applied "
        "without case-by-case exceptions. The pipeline, not any single result, is the paper's central "
        "contribution."
    )
    pipeline_steps = [
        ("Structures.", "The drug is built from its SMILES string (RDKit [7] ETKDG conformer generation + MMFF "
         "minimization) and then geometry-optimized with GFN2-xTB (xtb, including its D4 dispersion "
         "correction) [1-4]. The 2D carrier is modeled as an explicit, "
         "hydrogen-terminated finite cluster and separately optimized the same way."),
        ("Adsorption geometry.", "The drug is placed 3.2 Å above the local sheet surface directly beneath "
         "it — never above the global z-extremum of a buckled or edge-terminated finite cluster, a distinction "
         "that matters more than it sounds (§4) — in four in-plane orientations (0°, 90°, "
         "180°, 270°), and every resulting complex is geometry-optimized, not merely evaluated at a "
         "single point. The lowest-energy converged pose whose closest heavy-atom contact falls between 1.25 "
         "and 4.0 Å is retained."),
        ("Two interaction-energy conventions, reported separately.", "ΔE_int,SP = E(complex) − "
         "E(carrier) − E(drug), with both fragments frozen at the complex geometry, isolates the "
         "electronic interaction; ΔE_ads, with both fragments relaxed to their isolated-molecule minima, "
         "additionally captures the conformational strain paid on binding. A closest contact below 1.9 Å "
         "is classified as chemisorption (a new covalent bond has formed); anything looser is physisorption."),
        ("Charge-density difference.", "For the strongest-adsorbing complex in each system, GFN2-xTB electron "
         "densities of the complex, the isolated carrier, and the isolated drug are evaluated on one shared "
         "grid (Multiwfn [15]) and combined into Δρ = ρ(complex) − ρ(carrier) − "
         "ρ(drug); the resulting isosurface is rendered in ChimeraX [16] to visualize the electronic "
         "reorganization on binding directly, rather than inferring it from energetics alone."),
        ("Docking.", "AutoDock Vina [5,6] is run against the disease target's experimental structure (a PDB entry "
         "chosen for resolution and relevance to the binding site of interest), with the docking protocol's "
         "own pose-recovery fidelity established by redocking the native co-crystallized ligand. Where that "
         "redocking does not reproduce the native pose within a few tenths of an Ångström, the docking "
         "scores are reported explicitly as a relative ranking of surface or cleft affinity, never as a "
         "quantitative binding free energy."),
        ("Descriptors.", "Conceptual-DFT global reactivity indices [8] — chemical hardness η, softness S, "
         "electronegativity χ, chemical potential μ, and electrophilicity ω — are read directly "
         "from the same GFN2-xTB frontier-orbital output used for the adsorption calculation; none is "
         "estimated from an empirical formula fit to the descriptor set itself."),
        ("Surrogate model.", "A StandardScaler + RidgeCV regression (scikit-learn [9]) is trained inside a nested 5×5 "
         "cross-validation: an outer 5-fold split produces out-of-fold predictions for every compound, while "
         "the scaler and the ridge regularization strength are fit exclusively on each outer-training split via "
         "an inner 5-fold search, so no test-fold information leaks into preprocessing or hyperparameter "
         "selection. Predictive performance is reported as the pooled out-of-fold Q²_CV, together with a "
         "1000-permutation Y-scrambling test [10] and its empirical p-value."),
        ("Applicability domain.", "Compliance with OECD Principle 3 [11-13] is assessed via Williams hat-matrix "
         "leverage, flagging compounds whose descriptor vector falls outside the model's training-data "
         "envelope."),
        ("Reproducibility.", "For each disease system, a single script (run_entire_<system>_study.py) "
         "regenerates every number and figure in the corresponding manuscript directly from the raw drug and "
         "carrier inputs, and the complete code, curated dataset, and computational outputs are archived on "
         "Zenodo alongside the public GitHub repository."),
    ]
    for i, item in enumerate(pipeline_steps, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(6)
        r_num = p.add_run(f"{i}. {item[0]} ")
        r_num.font.bold = True
        p.add_run(item[1])
    add_image_if_exists(
        doc, os.path.join(FIG_DIR, "fig1_pipeline_schematic.png"),
        "Figure 1: The nine-step reproducible screening pipeline described in this section, applied "
        "identically to all four disease/carrier systems."
    )

    # ---- 3. Four case studies ----
    add_heading_styled(doc, "3. Four Case Studies", level=1)
    doc.add_paragraph(
        "The pipeline above was applied, without modification to a single step, to four disease systems that "
        "share no target biology, no carrier chemistry, and no descriptor set: oncogenic KRAS-G12D in "
        "pancreatic ductal adenocarcinoma screened against boron/phosphorus-doped graphitic carbon nitride; "
        "glioblastoma against Ti3C2Tx MXene; triple-negative breast cancer against a B36N36 boron nitride "
        "nanocage; and Alzheimer's Tau paired-helical-filament aggregation against β12 borophene. Table 1 "
        "summarizes the outcome."
    )

    tbl = doc.add_table(rows=1, cols=6)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = "Light Grid Accent 1"
    hdr = tbl.rows[0].cells
    headers = ["System", "Carrier", "n", "ΔE_int,SP range (kcal/mol)", "Regime", "Physisorption QSPR Q²_CV"]
    for cell, text in zip(hdr, headers):
        cell.text = text
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(9)

    # cross_system_summary.csv's "n" column is now consistently defined (fixed
    # 2026-09-13 in gather_cross_system_summary.py) as the total number of
    # complexes successfully modelled at the GFN2-xTB level for that system --
    # trust it directly rather than hardcoding, so a future data refresh can't
    # silently drift out of sync with this table again.
    table_rows = [
        ("KRAS-G12D / PDAC", "g-C3N4 (B,P-doped)", rows["KRAS"]["n"],
         f"{float(rows['KRAS']['eint_lo']):.1f} … {float(rows['KRAS']['eint_hi']):.1f}",
         "physisorption, doping-tuned", "0.51–0.55 (per-carrier models)"),
        ("Glioblastoma", "Ti3C2O2 MXene", rows["GBM"]["n"],
         f"{float(rows['GBM']['eint_lo']):.1f} … {float(rows['GBM']['eint_hi']):.1f}",
         "physisorption", f"{float(rows['GBM']['q2']):.2f}"),
        ("Triple-negative breast", "B36N36 nanocage", rows["TNBC"]["n"],
         f"{float(rows['TNBC']['eint_lo']):.1f} … {float(rows['TNBC']['eint_hi']):.1f}",
         "mixed: 5 chemisorb / 25 physisorb", "≈0.00 (n=25 physisorbers)"),
        ("Alzheimer's Tau", "β12 borophene", rows["Tau"]["n"],
         f"{float(rows['Tau']['eint_lo']):.1f} … {float(rows['Tau']['eint_hi']):.1f}",
         "mixed: 12 chemisorb / 17 physisorb", f"{float(rows['Tau']['q2']):.2f} (n=17 physisorbers)"),
    ]
    for row_data in table_rows:
        cells = tbl.add_row().cells
        for cell, text in zip(cells, row_data):
            cell.text = str(text)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
    p_tbl_cap = doc.add_paragraph()
    p_tbl_cap.paragraph_format.space_before = Pt(6)
    p_tbl_cap.paragraph_format.space_after = Pt(12)
    r_tbl_num = p_tbl_cap.add_run("Table 1: ")
    r_tbl_num.font.bold = True
    r_tbl_num.font.size = Pt(9.5)
    p_tbl_cap.add_run(
        "Cross-system summary of the four disease/carrier pairs screened with the identical pipeline. n is the "
        "number of drug-carrier complexes successfully modelled at the GFN2-xTB level for that system; "
        "Q²_CV values are pooled out-of-fold coefficients of determination from the leak-free nested surrogate "
        "described in §2. Full per-system detail, docking statistics, and Y-scrambling controls are archived "
        "with each system's own dataset and code [22-25]."
    ).font.size = Pt(9.5)

    add_image_if_exists(
        doc, os.path.join(FIG_DIR, "fig2_cross_system_energy_regimes.png"),
        "Figure 2: Interaction-energy regimes across the four disease/carrier systems. Each horizontal bar spans "
        "the real, per-system minimum-to-maximum GFN2-xTB interaction energy across all successfully modelled "
        "complexes (n labelled per system); the shaded band marks the covalent/chemisorption range. The x-axis "
        "covers a wide span to accommodate the TNBC and Tau chemisorbing subpopulations alongside the narrower "
        "physisorption-only bands of KRAS and MXene."
    )
    add_image_if_exists(
        doc, os.path.join(FIG_DIR, "fig3_drho_four_panels.png"),
        "Figure 3: Charge-density difference (Δρ = ρ_complex − ρ_carrier − ρ_drug) at the "
        "strongest-adsorbing complex per system, real GFN2-xTB densities in every panel. Yellow/blue "
        "lobes mark electron accumulation/depletion on complex formation."
    )

    doc.add_paragraph(
        "MXene is the cleanest case of the more common story: no bare, pristine carrier gives a descriptor-based "
        "QSPR model of the adsorption energy that predicts meaningfully better than the training-set mean "
        "(Q²_CV ≈ 0.10). This is not a failure of the modelling: it is the honest signal that, for a "
        "physisorption-dominated interaction with these four descriptors, the adsorption energy is not well "
        "predicted by molecular weight, molar refractivity, and frontier-orbital indices alone. Reporting a "
        "high Q² under these conditions would itself be a red flag for leakage. The scientific value of the "
        "screen, in this case, is the mechanistic picture the pipeline still delivers honestly — the "
        "interaction-energy regime and the charge-redistribution pattern — not a predictive surrogate model."
    )
    doc.add_paragraph(
        "TNBC and Tau complicate this picture in the same qualitative way, at different scale. Neither carrier "
        "is purely physisorptive once every complex is actually geometry-optimized and its closest contact "
        "checked. Five of the 33 TNBC-directed drugs — SN-38, epirubicin, topotecan, lapatinib, and rucaparib — "
        "chemisorb onto the B36N36 nanocage through a new covalent B-O or B-N bond (1.37-1.72 Å, "
        "ΔE_int,SP = -43 to -186 kcal/mol). That is exactly the same qualitative pattern that dominates the "
        "borophene/Tau system at larger scale (12 of 29 ligands, §4): a reactive minority hidden inside an "
        "otherwise unremarkable physisorption-dominated cohort. The descriptor-based QSPR remains non-predictive "
        "for the physisorbing majority in both cases (TNBC: Q²_CV ≈ 0.00, n=25; Tau: Q²_CV = 0.06, n=17), so "
        "here too the chemisorption/physisorption split itself, not a regression model, is the finding worth "
        "reporting. That the same qualitative pattern shows up independently in two chemically unrelated "
        "carrier/ligand systems is, if anything, a reason to check for it by default, rather than to assume a "
        "screened 2D carrier is purely physisorptive without verifying the relaxed contact distance."
    )
    doc.add_paragraph(
        "KRAS-G12D on boron/phosphorus-doped g-C3N4 is the instructive exception, in the opposite sense from "
        "TNBC and Tau: instead of a hidden chemisorption story, it is a hidden predictive-model story. Its "
        "interaction energies sit in the same modest range as MXene, and we did not detect chemisorption for "
        "this carrier, yet the identical StandardScaler + RidgeCV surrogate reaches Q²_CV = 0.51-0.58 across the "
        "pristine and doped carriers — a genuinely predictive model by the same 1000-permutation Y-scrambling "
        "standard applied to every other system here. We read this less as a claim that g-C3N4 is somehow "
        "special and more as a control on the pipeline itself: the same leak-free nested cross-validation that "
        "returns Q²_CV ≈ 0 for MXene and the TNBC/Tau physisorbing majorities is demonstrably capable of "
        "returning a high, permutation-validated Q² when the underlying descriptor-property relationship "
        "actually supports one. A validation scheme that always reports near-zero performance regardless of the "
        "input would be as suspect as one that always reports an excellent fit."
    )
    doc.add_paragraph(
        "Of the two chemisorbing systems, β12 borophene against the Tau paired-helical-filament cohort is the "
        "more dramatic case (a larger reactive fraction, and the one we ourselves first got wrong), and is the "
        "subject of the next section."
    )

    # ---- 4. The cautionary tale ----
    add_heading_styled(doc, "4. The Cautionary Tale — Tau / Borophene", level=1)
    doc.add_paragraph(
        "Our own first pass at the Tau/borophene system made exactly the unrelaxed-geometry error named as "
        "failure mode 3 in §1, and is instructive precisely because it was not an obviously bad calculation — "
        "the numbers were internally consistent, the code ran end to end, and the result looked like a "
        "plausible, unremarkable physisorption screen."
    )
    doc.add_paragraph(
        "The original protocol placed each drug 3.2 Å above the z-maximum atom of the finite, buckled "
        "B40H15 borophene cluster — a natural-looking reference point for “above the sheet.” For a "
        "buckled, edge-hydrogen-terminated finite cluster, however, the global z-maximum is frequently an edge "
        "hydrogen rather than a point on the flat interior facet the drug is meant to adsorb onto. The result "
        "was a family of complexes in which the drug sat 5-6 Å from the sheet it should have been "
        "interacting with — never geometry-optimized, evaluated only at a single point — reported as "
        "“dispersion-dominated physisorption” at −0.9 to −13.8 kcal/mol, with the compound "
        "tideglusib (whose SMILES string had also been silently truncated during curation) flagged as the "
        "strongest binder."
    )
    doc.add_paragraph(
        "Re-running the identical pipeline described in §2 — referencing the placement offset to the local "
        "surface height directly beneath the drug, and geometry-optimizing every resulting complex — changes "
        "the conclusion completely. Twelve of the 29 screened ligands chemisorb, forming a new covalent B–C or "
        "B–O bond at a closest contact of 1.36-1.69 Å (ΔE_int,SP = −81 to −233 kcal/mol): "
        "the π-rich polyphenols (curcumin, luteolin, apigenin, fisetin, baicalein), the azo and "
        "phenothiazine dyes, rosmarinic acid, and FDDNP. The remaining 17 physisorb at 2.6-3.7 Å "
        "(−8 to −44 kcal/mol). Pristine β12 borophene is, for this chemotype, a chemically "
        "reactive surface rather than an inert, reversible carrier — the opposite conclusion from the "
        "unrelaxed protocol, and one with direct consequences for any downstream drug-loading claim: covalent "
        "modification of a nucleophile-bearing therapeutic on the carrier surface is not a reversible loading "
        "event."
    )
    add_image_if_exists(
        doc, os.path.join(FIG_DIR, "fig4_tau_before_after.png"),
        "Figure 4: The Tau/borophene before/after comparison for curcumin, the strongest-adsorbing ligand. "
        "(a) The original unrelaxed placement, drug 5-6 Å from the sheet. (b) The corrected, relaxed, "
        "chemisorbed pose (1.41 Å B-C contact). (c) The real 29-compound ΔE_int,SP distribution before "
        "versus after — not simulated data."
    )
    doc.add_paragraph(
        "We state the lessons from this case as four explicit rules, offered not as an indictment of any prior "
        "work but as a checklist we now apply to every new system before trusting a single number from it:"
    )
    for i, rule in enumerate([
        "Always geometry-optimize the complex. A single-point energy on a placed, un-relaxed geometry is not "
        "an adsorption energy, and cannot be labelled as one.",
        "Reference the placement offset to the local surface height directly beneath the adsorbate, never to a "
        "global z-extremum of a finite, buckled, or edge-terminated cluster.",
        "Check the closest heavy-atom contact after optimization, and classify chemisorption versus "
        "physisorption explicitly and by that measured contact — not by assumption from the starting geometry.",
        "Verify every curated drug structure against its molecular formula before committing compute to a "
        "batch of complexes; a truncated SMILES string can survive an entire pipeline undetected if nothing "
        "checks atom counts against the source identifier.",
    ], start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(4)
        r_num = p.add_run(f"{i}. ")
        r_num.font.bold = True
        p.add_run(rule)

    # ---- 5. Catalogue of failure modes ----
    add_heading_styled(doc, "5. Catalogue of Failure Modes Found and Fixed Across the Four Projects", level=1)
    doc.add_paragraph(
        "Beyond the Tau geometry error, the process of building and auditing all four case studies to a "
        "single, consistent standard surfaced a further set of concrete, fixable defects — none unique to a "
        "single system, and each worth naming so that other groups can check their own pipelines for the same "
        "pattern:"
    )
    for item in [
        "A fabricated “ΔG_bind” or “ΔE_ads” target computed from an empirical linear "
        "formula over RDKit descriptors, printed as if it were a quantum-mechanical result, in all four early "
        "drafts — replaced in every case with the real GFN2-xTB single-point or relaxed interaction energy.",
        "A StandardScaler fitted on the entire dataset before cross-validation in the earliest KRAS surrogate "
        "model, silently leaking test-fold statistics into training — replaced with a scikit-learn Pipeline "
        "fit exclusively inside each outer-training fold of a nested cross-validation.",
        "Hardcoded post-hoc test statistics (a Kruskal-Wallis or Dunn p-value typed directly into the "
        "manuscript text rather than computed from the deposited data) — replaced with values computed inline "
        "from the master results table at manuscript-generation time.",
        "A bibliography imported wholesale from a sibling project (the KRAS draft briefly carried the TNBC "
        "reference list) — replaced with a per-project, individually verified reference list.",
        "A fallback of np.random.uniform() standing in for an undefined applicability-domain leverage value "
        "when the real calculation failed silently — replaced with an explicit exception, so a broken "
        "leverage calculation fails loudly instead of being reported as data.",
        "A “multi-level DFT benchmark” table with no corresponding ORCA output files anywhere in the "
        "repository — removed rather than retained with an unverifiable citation.",
        "Schematic “3D structural context” figures that were, on inspection, text boxes styled to "
        "resemble a rendered structure — replaced with real ChimeraX or PyMOL renders of the actual computed "
        "geometries.",
        "A docking cohort, a descriptor/QSPR cohort, and a reference-list compound count that had quietly "
        "drifted apart across three separate script revisions — unified into a single master table that every "
        "downstream figure and statistic is computed from directly.",
    ]:
        p = doc.add_paragraph(item)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(6)

    # ---- 6. Conclusion ----
    add_heading_styled(doc, "6. Conclusion", level=1)
    doc.add_paragraph(
        "A rigorous computational screen of a 2D-nanomaterial drug carrier is genuinely cheap — a GFN2-xTB "
        "adsorption calculation and an AutoDock Vina docking run together take hours on an ordinary "
        "workstation — but only under three conditions: the adsorption geometry must be relaxed, not placed "
        "and left at a single point; the regression target must be a real computed or measured quantity, never "
        "an empirical formula dressed up as one; and the cross-validation must be leak-free, with all "
        "preprocessing and hyperparameter selection confined to the training folds. Under those conditions, the "
        "honest outcome across our four disease systems is mixed in an informative way. MXene gives a modest, "
        "non-predictive physisorption energy (Q²_CV ≈ 0.10) — the unglamorous majority case. KRAS/g-C3N4 gives "
        "an equally modest interaction energy but a genuinely predictive QSPR (Q²_CV = 0.51-0.58), a useful "
        "internal control showing the near-zero results elsewhere are not simply an artefact of an overly "
        "conservative validation scheme. TNBC and Tau both turn out to hide a chemisorbing minority (5 of 33 "
        "and 12 of 29 ligands, respectively) inside an otherwise non-predictive physisorbing majority — the "
        "same qualitative pattern at two different scales, in two chemically unrelated systems, which the "
        "field's common unrelaxed, single-point protocol would have hidden entirely in both cases, and did, for "
        "a time, in ours. We offer the pipeline, the four case studies, and the "
        "corrected Tau result as a concrete, reproducible reference point for what changes when this discipline "
        "is applied, and as a short checklist for anyone building the next such screen."
    )

    # ---- Data Availability ----
    add_heading_styled(doc, "Data Availability", level=1)
    doc.add_paragraph(
        "This Perspective synthesizes results already deposited for each of the four underlying case studies; "
        "no new primary computation is reported here. Each system's complete code, curated dataset, GFN2-xTB "
        "and AutoDock Vina outputs, and figure/manuscript generators are archived at its own public GitHub "
        "repository and Zenodo deposit [22-25]; this paper's own cross-system summary table and Figure 2 "
        "generator are archived alongside the manuscript source in the methods-pipeline-2d-nanocarriers "
        "repository."
    )

    # ---- Back matter (Beilstein order) ----
    add_heading_styled(doc, "Conflict of Interest", level=1)
    doc.add_paragraph("The authors declare no competing financial or non-financial interest.")

    add_heading_styled(doc, "Funding", level=1)
    doc.add_paragraph(
        "This work was supported by Universidad Estatal de Sonora and the Doctorado en Nanotecnología, "
        "Universidad de Sonora. No external grant funding was received."
    )

    add_heading_styled(doc, "Acknowledgements", level=1)
    doc.add_paragraph(
        "The authors thank the computational resources of Universidad Estatal de Sonora and Universidad de "
        "Sonora."
    )

    add_heading_styled(doc, "Author Contributions", level=1)
    doc.add_paragraph(
        "Andrés Monreal Hernández: conceptualization, methodology, software, formal analysis, investigation, "
        "data curation, visualization, writing – original draft. Sara Lizbeth Franco Amaya: validation, "
        "writing – review and editing. Carlos Ivanhoe Martínez Osorio: supervision, writing – review and "
        "editing. All authors read and approved the final manuscript."
    )

    add_heading_styled(doc, "ORCID iDs", level=1)
    doc.add_paragraph("Andrés Monreal Hernández – https://orcid.org/0009-0009-1207-8597")

    # ---- References ----
    add_heading_styled(doc, "References", level=1)
    for idx, ref in enumerate(REFERENCES, 1):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.space_after = Pt(3)
        r_num = p_ref.add_run(f"{idx}. ")
        r_num.font.bold = True
        p_ref.add_run(ref["citation"] + " ")
        if ref.get("doi"):
            r_doi = p_ref.add_run(f"doi:{ref['doi']}")
            r_doi.font.italic = True
            r_doi.font.size = Pt(9.0)
            r_doi.font.color.rgb = RGBColor(13, 71, 161)

    out_dir = os.path.join(BASE, "manuscript")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Beilstein_Perspective_Methods_Pipeline_Monreal_Hernandez_et_al.docx")
    doc.save(out_path)
    print(f"[SUCCESS] Generated methods manuscript: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_methods_manuscript()
