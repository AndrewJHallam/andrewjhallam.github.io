#!/usr/bin/env python3
"""Rebuild the public CV using ReportLab and the website publication catalogue.

Run from the website directory: python3 make_public_cv.py
Dependency: pip install reportlab
All personal content below is intentionally suitable for public distribution.
The original private CV is not required.
"""

from pathlib import Path
from html import escape
import json
import re

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak,
)

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "andrew-hallam-cv.pdf"
PAGE_W, PAGE_H = A4
MARGIN_X = 49
CONTENT_W = PAGE_W - 2 * MARGIN_X
INK = colors.HexColor("#26372f")
SAGE = colors.HexColor("#526b5a")
RUST = colors.HexColor("#955a43")
MUTED = colors.HexColor("#5c655f")
RULE = colors.HexColor("#d6ddd4")

FONT_DIR = Path(reportlab.__file__).parent / "fonts"
for name, filename in [
    ("Vera", "Vera.ttf"), ("Vera-Bold", "VeraBd.ttf"),
    ("Vera-Italic", "VeraIt.ttf"), ("Vera-BoldItalic", "VeraBI.ttf"),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily(
    "Vera", normal="Vera", bold="Vera-Bold", italic="Vera-Italic",
    boldItalic="Vera-BoldItalic",
)


def style(name, **kwargs):
    values = dict(
        fontName="Vera", fontSize=9.1, leading=13.1, textColor=INK,
        spaceAfter=5, allowWidows=0, allowOrphans=0,
    )
    values.update(kwargs)
    return ParagraphStyle(name, **values)


STYLES = {
    "name": style("Name", fontName="Times-Roman", fontSize=32, leading=35,
                  spaceAfter=8),
    "role": style("Role", fontName="Vera-Bold", fontSize=10.2,
                  leading=15, textColor=SAGE, spaceAfter=3),
    "contact": style("Contact", fontSize=8.4, leading=12.2,
                     textColor=MUTED, spaceAfter=3),
    "section": style("Section", fontName="Vera-Bold", fontSize=10,
                     leading=14, textColor=RUST, spaceBefore=15, spaceAfter=8,
                     keepWithNext=True),
    "title": style("Title", fontName="Times-Roman", fontSize=23,
                   leading=28, spaceAfter=6, keepWithNext=True),
    "subtitle": style("Subtitle", fontSize=8.5, leading=12.2,
                      textColor=MUTED, spaceAfter=15, keepWithNext=True),
    "body": style("Body"),
    "small": style("Small", fontSize=8.5, leading=12),
    "entry": style("Entry", fontSize=9.1, leading=13.2, spaceAfter=2,
                   keepWithNext=True),
    "meta": style("Meta", fontSize=8.3, leading=11.8, textColor=MUTED,
                  spaceAfter=8),
    "bullet": style("Bullet", fontSize=9, leading=13, leftIndent=10,
                    firstLineIndent=-10, spaceAfter=4),
    "pubtitle": style("PublicationTitle", fontName="Vera-Bold", fontSize=9.1,
                      leading=12.9, spaceAfter=3, keepWithNext=True),
    "pubauthors": style("PublicationAuthors", fontSize=8.3, leading=11.9,
                        spaceAfter=2, keepWithNext=True),
    "pubvenue": style("PublicationVenue", fontSize=8.3, leading=11.9,
                      textColor=MUTED, spaceAfter=11),
    "presentation": style("Presentation", fontSize=8.6, leading=12.5,
                          spaceAfter=7),
    "year": style("Year", fontName="Vera-Bold", fontSize=8.6, leading=12.5,
                  textColor=SAGE, spaceAfter=7),
}


def clean(text):
    return (str(text).replace("\u2013", "-").replace("\u2014", "-")
            .replace("\u2011", "-").replace("\u2010", "-"))


def p(text, kind="body"):
    return Paragraph(clean(text), STYLES[kind])


def section(text):
    return p(text.upper(), "section")


def bullet(text):
    return p("•  " + text, "bullet")


def link(url, label):
    return '<link href="{}" color="#526b5a">{}</link>'.format(
        escape(url, quote=True), escape(clean(label)),
    )


def page_header(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.7)
    canvas.line(MARGIN_X, 38, PAGE_W - MARGIN_X, 38)
    canvas.setFont("Vera", 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 24, "Andrew Hallam | Curriculum vitae")
    canvas.drawRightString(PAGE_W - MARGIN_X, 24, str(doc.page))
    if doc.page > 1:
        canvas.setFont("Vera-Bold", 7.4)
        canvas.setFillColor(SAGE)
        canvas.drawString(MARGIN_X, PAGE_H - 32, "ANDREW HALLAM")
        canvas.setFont("Vera", 7.4)
        canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 32, "CURRICULUM VITAE")
        canvas.setStrokeColor(RULE)
        canvas.line(MARGIN_X, PAGE_H - 42, PAGE_W - MARGIN_X, PAGE_H - 42)
    canvas.restoreState()


def entry(title, detail=None):
    result = [p(title, "entry")]
    if detail:
        result.append(p(detail, "meta"))
    return result


def publication_list():
    data = json.loads((ROOT / "publications.json").read_text())
    if isinstance(data, dict):
        data = data.get("publications", data.get("items", []))
    return sorted(data, key=lambda item: -int(item["year"]))


def publication(item, number):
    authors = escape(item["authors"])
    authors = authors.replace("Andrew Hallam", "<b>Andrew Hallam</b>")
    authors = authors.replace("A. Hallam", "<b>A. Hallam</b>")
    venue = escape(item["venue"])
    if item.get("status") == "preprint":
        venue += " (preprint)"
    venue += " · " + str(item["year"])
    url = item.get("url") or item.get("arxiv")
    if url:
        label = "arXiv" if "arxiv.org" in url else "Publication"
        venue += " · " + link(url, label)
    if item.get("arxiv") and item.get("arxiv") != url:
        venue += " · " + link(item["arxiv"], "arXiv")
    return KeepTogether([
        p(f'{number:02d}  {escape(item["title"])}', "pubtitle"),
        p(authors, "pubauthors"), p(venue, "pubvenue"),
    ])


def presentation_rows(items):
    rows = []
    for year, title, venue in items:
        rows.append([p(year, "year"), p(f'<b>{escape(title)}</b><br/>{escape(venue)}', "presentation")])
    table = Table(rows, colWidths=[42, CONTENT_W - 42], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def build():
    story = [
        p("Andrew Hallam", "name"),
        p("Quantum Fellow · EPCC, University of Edinburgh", "role"),
        p(link("mailto:andrew.hallam@epcc.ed.ac.uk", "andrew.hallam@epcc.ed.ac.uk")
          + " &nbsp; · &nbsp; " + link("mailto:ahallam3@ed.ac.uk", "ahallam3@ed.ac.uk"), "contact"),
        p(link("https://scholar.google.co.uk/citations?user=1GuZeDkAAAAJ&hl=en", "Google Scholar")
          + " &nbsp; · &nbsp; " + link("https://github.com/AndrewJHallam", "GitHub: AndrewJHallam")
          + " &nbsp; · &nbsp; " + link("https://www.linkedin.com/in/andrew-hallam-185717383/", "LinkedIn"), "contact"),
        section("Research interests"),
        p("Quantum many-body physics, tensor networks and quantum information. Research includes out-of-equilibrium dynamics, quantum thermalisation and many-body scars; nonstabilizerness and quantum criticality; and spin-chain models of black-hole physics."),
        section("Appointments"),
        *entry("<b>Quantum Fellow</b>, EPCC, University of Edinburgh", "Current appointment"),
        *entry("<b>Postdoctoral Fellow</b>, University of Leeds", "From 2020; previous appointment"),
        *entry("<b>Postdoctoral Fellow</b>, Ghent University", "2018-2020"),
        section("Education"),
        *entry("<b>PhD in Physics</b>, University College London", "2015-2018 · Supervisor: Andrew Green"),
        *entry("<b>MRes in Delivering Quantum Technologies</b>, University College London", "2014-2015 · Distinction"),
        *entry("<b>MSci in Physics</b>, University College London", "2010-2014 · First class honours"),
        section("Teaching and supervision"),
        bullet("Taught parts of <b>PHYS3003: Advanced Techniques in Theoretical Physics</b> and <b>PHYS5017M: Quantum Many-Body Physics</b> at the University of Leeds."),
        bullet("Supervised several year-long Master's projects at Ghent University and the University of Leeds; co-supervised several PhD students at Leeds."),
        section("Award and technical experience"),
        bullet("<b>Mentorship Award for the Engineering and Physical Sciences</b>, University of Leeds, 2025."),
        bullet("Significant programming experience in <b>Python, Julia and C++</b>; experience with <b>MATLAB and TensorFlow</b>."),
        PageBreak(),
        p("Research experience", "title"),
        p("Projects undertaken during postdoctoral and postgraduate research.", "subtitle"),
        section("University of Leeds · Postdoctoral research"),
        p("Supervisors: Jiannis Pachos and Zlatko Papić", "meta"),
        bullet("Used the entanglement spectrum of quantum ground states and the interaction distance to study one-dimensional interacting fermionic models."),
        bullet("Built effective models of electrons on curved spacetime using one-dimensional spin chains."),
        bullet("Studied non-equilibrium dynamics of systems that do not relax to thermal equilibrium, including quantum many-body scars and many-body localisation."),
        section("Ghent University · Postdoctoral research"),
        p("Supervisor: Jutho Haegeman", "meta"),
        bullet("Constructed a path integral summing over matrix product states in the continuum and at finite temperatures."),
        bullet("Investigated the structure of the multiscale entanglement renormalization ansatz using matrix-product operator techniques."),
        section("University College London · PhD"),
        p("<b>Tensor network descriptions of quantum entanglement in path integrals, thermalisation and machine learning.</b>", "entry"),
        p("Supervisor: Andrew Green", "meta"),
        bullet("Developed a method for simulating and compressing neural networks using tensor networks based on the multiscale entanglement renormalization ansatz."),
        bullet("Explored fluctuations around the saddle point of a path integral constructed over matrix product states."),
        bullet("Used a semiclassical description of quantum time evolution to study the relationship between classical chaos and quantum thermalisation."),
        bullet("Combined tensor networks and the truncated spectrum approach to study a two-dimensional system created by suddenly coupling one-dimensional systems."),
        section("University College London · MRes and MSci"),
        p("<b>MRes: Tensor network descriptions of out-of-equilibrium quantum systems.</b> Supervisors: Andrew Green and Andrew James. Studied short-time behaviour after a two-dimensional quantum quench, using matrix product states in a cylindrical geometry."),
        p("<b>MSci: Entanglement of Trapped Ions via Measurement.</b> Supervisor: Dan Browne. Examined how common experimental imperfections affect the entanglement of atoms inside an optical cavity."),
        section("Academic service and outreach"),
        bullet("Organised the internal quantum theory seminar at Leeds and the Leeds-Loughborough-Nottingham non-equilibrium seminar: invited and hosted speakers, recorded talks, and maintained the website and YouTube channel."),
        bullet("Helped organise UCL Physics and Astronomy's postgraduate conference <b>QCumber</b> in 2015 and 2016, and the <b>24th Symposium on Quantum Matter and High-Energy Physics</b> in 2022; arranged speakers, transport and accommodation."),
        bullet("Helped deliver a hands-on quantum computing workshop for Year 12 and 13 pupils through Leeds' <b>Reach for Excellence</b> widening participation programme."),
        PageBreak(),
    ]

    pubs = publication_list()
    recent = [item for item in pubs if int(item["year"]) >= 2025]
    earlier = [item for item in pubs if int(item["year"]) < 2025]
    story.extend([p("Publications and preprints", "title"),
                  p("2025-2026 · Links lead to the published article and/or arXiv record.", "subtitle")])
    for number, item in enumerate(recent, 1):
        story.append(publication(item, number))
    story.extend([PageBreak(), p("Publications and preprints", "title"),
                  p("Earlier work · Publications are listed in reverse chronological order.", "subtitle")])
    for number, item in enumerate(earlier, len(recent) + 1):
        story.append(publication(item, number))
    story.extend([PageBreak(), p("Presentations", "title"),
                  p("Talks and posters at seminars, meetings and conferences.", "subtitle"),
                  section("Talks")])
    talks = [
        ("2026", "Understanding magic in critical many-body systems", "12th Northern Quantum Meeting, Google · 20 April"),
        ("2026", "Understanding magic in critical many-body systems", "Tensor Network weekly seminar, Google · 6 April"),
        ("2026", "Understanding magic in critical many-body systems", "University of Manchester · 1 April"),
        ("2025", "Connecting many-body magic with quantum criticality with infinite matrix-product states", "Many-Body Quantum Magic (MBQM-2025), iQuS Seattle · 18-29 August"),
        ("2024", "Non-stabilizerness in kinetically-constrained Rydberg atom arrays", "Bridging the physics and mathematics of quantum many-body chaos · 24-28 June"),
        ("2023", "Quantum many-body physics", "White Rose Quantum Information and Technologies lectures · 13 December"),
        ("2023", "Embedding semiclassical periodic orbits into chaotic many-body Hamiltonians", "IQTN workshop: Tensor networks for quantum many-body dynamics · 26-28 June"),
        ("2022", "Tuning between continuous time crystals and many-body scars in long-range XYZ spin chains", "CMD29 · 21-26 August"),
        ("2021", "Emergence of Gaussianity in the thermodynamic limit of interacting fermions", "Quantum, Atomic, and Molecular Physics (QuAMP 2021), online · 31 August-3 September"),
        ("2019", "The Lyapunov spectrum of quantum thermalisation", "University of Freiburg · 2 July; Belgian Quantum Physics Initiative, Brussels · 2 May"),
        ("2019", "Feynman path integrals over matrix product states", "Entanglement in Strongly Correlated Systems, Benasque · 24 February-9 March"),
        ("2016", "Tensor networks and out-of-equilibrium dynamics in two dimensions", "QCumber, Cumberland Lodge · 16-18 June"),
    ]
    posters = [
        ("2024", "Embedding semiclassical periodic orbits into chaotic many-body Hamiltonians", "IQTN 4th Plenary Meeting, Glasgow · 24-26 January"),
        ("2021", "Interaction distance of the extended XYZ model", "Condensed Matter and Quantum Materials (CMQM 2021), online · 21-23 June"),
        ("2018", "Compact Neural Networks based on the Multiscale Entanglement Renormalization Ansatz", "British Machine Vision Conference, Northumbria University · 3-6 September"),
        ("2017", "The Lyapunov spectrum of thermalising quantum systems", "Frontiers in Condensed Matter Physics, Bristol · 11-12 January; Tensor17 School, Ghent · 6-10 November"),
        ("2017", "Quantum quenches in two spatial dimensions", "Theory of Condensed Matter Group Annual Meeting, Warwick · 6 June; Frontiers in Condensed Matter Physics, Bristol · 9-10 January"),
    ]
    story.extend([presentation_rows(talks), section("Posters"), presentation_rows(posters)])

    doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=MARGIN_X,
                          rightMargin=MARGIN_X, topMargin=58, bottomMargin=53,
                          title="Andrew Hallam - Curriculum vitae",
                          author="Andrew Hallam", subject="Academic curriculum vitae")
    frame = Frame(MARGIN_X, 51, CONTENT_W, PAGE_H - 107, leftPadding=0,
                  bottomPadding=0, rightPadding=0, topPadding=0)
    doc.addPageTemplates([PageTemplate(id="CV", frames=frame, onPage=page_header)])
    doc.build(story)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    build()
