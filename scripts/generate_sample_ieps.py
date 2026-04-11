#!/usr/bin/env python3
"""
Generate SYNTHETIC sample IEP PDFs for testing the /api/documents/upload endpoint.

These are NOT real IEPs. They use fictional school/district names and exist
only to exercise the document upload + extraction path during manual QA.
Each page is clearly marked 'SAMPLE - NOT A REAL IEP'.

Students covered: Amara, Marcus (using only their public profile data from
data/students/).
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
STUDENTS_DIR = ROOT / "data" / "students"
OUT_DIR = ROOT / "data" / "sample_iep"

DISTRICT = "Anytown USA Unified School District"
SCHOOL = "Lincoln Elementary Special Education Program"
SAMPLE_BANNER = "SAMPLE - NOT A REAL IEP"


def _watermark(canvas, doc):
    """Draw a subtle SAMPLE banner at the top of every page."""
    canvas.saveState()
    canvas.setFillColor(colors.red)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawCentredString(LETTER[0] / 2, LETTER[1] - 30, SAMPLE_BANNER)
    canvas.setFillColor(colors.grey)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(LETTER[0] / 2, 20,
                             f"Page {doc.page} - Synthetic test content for ClassLens ASD QA - {SAMPLE_BANNER}")
    canvas.restoreState()


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="DistrictHeader", fontName="Helvetica-Bold",
                              fontSize=14, alignment=1, spaceAfter=4))
    styles.add(ParagraphStyle(name="SchoolHeader", fontName="Helvetica",
                              fontSize=11, alignment=1, spaceAfter=12, textColor=colors.grey))
    styles.add(ParagraphStyle(name="SectionHeader", fontName="Helvetica-Bold",
                              fontSize=12, spaceBefore=10, spaceAfter=6,
                              textColor=colors.HexColor("#2C5282")))
    styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=10,
                              leading=13, spaceAfter=6))
    styles.add(ParagraphStyle(name="Goal", fontName="Helvetica", fontSize=10,
                              leading=13, leftIndent=12, spaceAfter=4))
    return styles


def _load_student(student_id: str) -> dict:
    with open(STUDENTS_DIR / f"{student_id}.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _build_iep(student_id: str, out_path: Path) -> None:
    profile = _load_student(student_id)
    styles = _styles()
    story = []

    # Page 1 header
    story.append(Paragraph(DISTRICT, styles["DistrictHeader"]))
    story.append(Paragraph(SCHOOL, styles["SchoolHeader"]))
    story.append(Paragraph("Individualized Education Program (IEP)", styles["SectionHeader"]))

    # Student info table
    info_data = [
        ["Student Name:", profile["name"]],
        ["Grade:", "Kindergarten" if profile["grade"] == 0 else f"Grade {profile['grade']}"],
        ["Age:", str(profile["age"])],
        ["Primary Eligibility:", f"Autism Spectrum Disorder (Level {profile['asd_level']})"],
        ["IEP Date:", "October 15, 2025"],
        ["Annual Review:", "October 15, 2026"],
        ["Case Manager:", "M. Rodriguez, M.Ed., Special Education"],
    ]
    tbl = Table(info_data, colWidths=[1.8 * inch, 4.2 * inch])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    # Present levels
    story.append(Paragraph("Present Levels of Academic Achievement and Functional Performance",
                           styles["SectionHeader"]))
    present_levels = (
        f"{profile['name']} is a {profile['age']}-year-old student receiving special education "
        f"services under the eligibility of Autism Spectrum Disorder. Communication profile: "
        f"{profile['communication_level']}. Preferred interests include "
        f"{', '.join(profile['interests'][:2])}, which are used as instructional anchors and "
        f"reinforcers across goal areas. Sensory profile indicates seeking "
        f"{', '.join(profile['sensory_profile']['seeks'][:2])} and avoiding "
        f"{', '.join(profile['sensory_profile']['avoids'][:2])}. Effective calming strategies "
        f"in the school setting include {', '.join(profile['sensory_profile']['calming_strategies'][:2])}."
    )
    story.append(Paragraph(present_levels, styles["Body"]))

    # Accommodations
    story.append(Paragraph("Accommodations and Supports", styles["SectionHeader"]))
    accommodations = [
        "Visual schedule posted at student desk, updated daily before arrival",
        "Access to sensory regulation tools at all times (see sensory profile)",
        "Advance warning (2-5 minutes) before transitions between activities",
        "Reduced-distraction testing environment for formal assessments",
        "Preferred-interest-based reinforcers on a variable schedule",
        "Small-group instruction for goal-aligned skill development",
    ]
    for a in accommodations:
        story.append(Paragraph(f"- {a}", styles["Goal"]))

    story.append(PageBreak())

    # Page 2: Goals + service minutes
    story.append(Paragraph(DISTRICT, styles["DistrictHeader"]))
    story.append(Paragraph(SCHOOL, styles["SchoolHeader"]))
    story.append(Paragraph(f"Annual Goals - {profile['name']}", styles["SectionHeader"]))

    for goal in profile["iep_goals"]:
        story.append(Paragraph(
            f"<b>Goal {goal['goal_id']}</b> ({goal['domain'].replace('_', ' ').title()})",
            styles["Body"],
        ))
        story.append(Paragraph(goal["description"], styles["Goal"]))
        baseline = goal.get("baseline", {})
        story.append(Paragraph(
            f"Baseline: {baseline.get('value', 'n/a')} (as of {baseline.get('date', 'n/a')}) "
            f"&nbsp;|&nbsp; Target: {goal.get('target', 'n/a')} "
            f"&nbsp;|&nbsp; Measurement: {goal.get('measurement_method', 'n/a')}",
            styles["Goal"],
        ))
        story.append(Spacer(1, 6))

    # Service minutes table
    story.append(Paragraph("Service Minutes (Weekly)", styles["SectionHeader"]))
    service_rows = [
        ["Service", "Setting", "Minutes/Week", "Provider"],
        ["Specialized Academic Instruction", "Small group", "600", "Special Ed Teacher"],
        ["Speech/Language Therapy", "Individual + group", "120", "SLP"],
        ["Occupational Therapy", "Individual", "60", "OT"],
        ["Behavior Support (consult)", "Classroom", "30", "BCBA (consult)"],
    ]
    stbl = Table(service_rows, colWidths=[2.4 * inch, 1.5 * inch, 1.1 * inch, 1.5 * inch])
    stbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(stbl)

    story.append(Spacer(1, 18))
    story.append(Paragraph(
        "<i>This is synthetic test content generated for ClassLens ASD QA. "
        "It is not a legal IEP document and must not be used in any real educational setting.</i>",
        styles["Body"],
    ))

    doc = SimpleDocTemplate(
        str(out_path), pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.9 * inch, bottomMargin=0.75 * inch,
        title=f"{profile['name']} IEP (SAMPLE)",
        author="ClassLens ASD QA Content Generator",
    )
    doc.build(story, onFirstPage=_watermark, onLaterPages=_watermark)
    print(f"Created {out_path}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _build_iep("amara_2026", OUT_DIR / "amara_iep_2025.pdf")
    _build_iep("marcus_2026", OUT_DIR / "marcus_iep_2025.pdf")


if __name__ == "__main__":
    main()
