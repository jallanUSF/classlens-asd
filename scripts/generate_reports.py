"""
Generate polished PDF reports for all students using Gemma 4.

Pipeline: Raw Material Forge output → Gemma 4 polishes → Markdown → HTML → PDF

Usage:
    python scripts/generate_reports.py                  # All students
    python scripts/generate_reports.py --student maya_2026  # Single student
    python scripts/generate_reports.py --mock           # Use MockGemmaClient
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fpdf import FPDF
import markdown
import re

# ── Gemma 4 polishing prompt ──────────────────────────────
POLISH_SYSTEM = """You are a professional document formatter for special education.
Given raw output from an IEP analysis system, rewrite it as a polished, professional
document in clean Markdown. Requirements:
- Use proper headings (##, ###), bullet points, and tables where appropriate
- Keep all data accurate — do not invent numbers or change facts
- Use warm, professional tone appropriate for the document type
- For parent letters: keep jargon-free and encouraging
- For admin reports: use formal IEP language
- For tracking sheets: create a clear table layout
- For lesson plans: organize into clear sections
- Include the student name, date, and document title prominently
- Output ONLY the polished Markdown — no commentary or explanation"""

POLISH_USER = """Polish this {doc_type} for student {student_name} (Grade {grade}, ASD Level {asd_level}).
Today's date: {date}

Raw content:
{content}"""

# ── PDF styling (ASD-friendly: calm colors, clear fonts) ──
PDF_CSS = """
@page {
    size: letter;
    margin: 1in;
    @bottom-center {
        content: "ClassLens ASD — Confidential Student Record";
        font-size: 8pt;
        color: #999;
    }
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 8pt;
        color: #999;
    }
}
body {
    font-family: 'Segoe UI', Calibri, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #2C3E50;
}
h1 {
    color: #5B8FB9;
    border-bottom: 2px solid #5B8FB9;
    padding-bottom: 8px;
    font-size: 20pt;
}
h2 {
    color: #34495E;
    border-bottom: 1px solid #E0E0E0;
    padding-bottom: 4px;
    font-size: 15pt;
}
h3 {
    color: #5B8FB9;
    font-size: 13pt;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
}
th, td {
    border: 1px solid #D5D5D5;
    padding: 8px 12px;
    text-align: left;
}
th {
    background-color: #5B8FB9;
    color: white;
    font-weight: 600;
}
tr:nth-child(even) {
    background-color: #F8F9FA;
}
blockquote {
    border-left: 4px solid #5B8FB9;
    margin: 12px 0;
    padding: 8px 16px;
    background: #F0F4F8;
    font-style: italic;
}
.header-bar {
    background: #5B8FB9;
    color: white;
    padding: 16px 24px;
    margin: -16px -16px 24px -16px;
    border-radius: 4px;
}
.header-bar h1 {
    color: white;
    border: none;
    margin: 0;
    padding: 0;
}
.meta {
    color: #777;
    font-size: 9pt;
    margin-bottom: 16px;
}
"""

# ── Document types to generate ────────────────────────────
DOCUMENT_TYPES = [
    {
        "key": "lesson_plan",
        "label": "Lesson Plan",
        "method": "generate_lesson_plan",
        "args": lambda sid: {"student_id": sid, "goal_id": "G1"},
    },
    {
        "key": "social_story",
        "label": "Social Story",
        "method": "generate_social_story",
        "args": lambda sid: {
            "student_id": sid,
            "scenario": "greeting peers at school arrival",
            "skill": "responding to peer greetings",
        },
    },
    {
        "key": "parent_communication",
        "label": "Parent Communication",
        "method": "generate_parent_comm",
        "args": lambda sid: {"student_id": sid, "goal_id": "G1"},
    },
    {
        "key": "admin_report",
        "label": "Administrative Progress Report",
        "method": "generate_admin_report",
        "args": lambda sid: {"student_id": sid},
    },
    {
        "key": "tracking_sheet",
        "label": "Data Tracking Sheet",
        "method": "generate_tracking_sheet",
        "args": lambda sid: {"student_id": sid, "goal_id": "G1"},
    },
    {
        "key": "visual_schedule",
        "label": "Visual Schedule",
        "method": "generate_visual_schedule",
        "args": lambda sid: {"student_id": sid, "routine": "morning_arrival"},
    },
    {
        "key": "first_then_board",
        "label": "First-Then Board",
        "method": "generate_first_then",
        "args": lambda sid: {"student_id": sid, "goal_id": "G1"},
    },
]


def get_client(use_mock=False):
    """Get GemmaClient or MockGemmaClient."""
    if use_mock:
        from tests.mock_api_responses import MockGemmaClient
        return MockGemmaClient()
    from core.gemma_client import GemmaClient
    return GemmaClient()


def raw_to_text(result):
    """Convert forge result (dict or str) to text for polishing."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        if "text" in result:
            return result["text"]
        return json.dumps(result, indent=2, ensure_ascii=False)
    return str(result)


def polish_with_gemma(client, raw_content, doc_type, student_profile, date_str):
    """Use Gemma 4 to polish raw output into professional markdown."""
    prompt = POLISH_USER.format(
        doc_type=doc_type,
        student_name=student_profile["name"],
        grade=student_profile["grade"],
        asd_level=student_profile["asd_level"],
        date=date_str,
        content=raw_content,
    )
    polished = client.generate(prompt=prompt, system=POLISH_SYSTEM)
    return polished


class ReportPDF(FPDF):
    """ClassLens ASD branded PDF."""

    def __init__(self, student_name, doc_title, date_str):
        super().__init__()
        self.student_name = student_name
        self.doc_title = doc_title
        self.date_str = date_str
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(91, 143, 185)  # #5B8FB9
        self.cell(0, 6, "ClassLens ASD", align="L")
        self.set_text_color(153, 153, 153)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 6, f"{self.student_name} | {self.date_str}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(91, 143, 185)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(153, 153, 153)
        self.cell(0, 10, "Confidential Student Record - ClassLens ASD", align="L")
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="R")


def _sanitize(text):
    """Replace unicode chars that latin-1 can't handle."""
    replacements = {
        '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '-', '\u2026': '...',
        '\u2192': '->', '\u2190': '<-', '\u2794': '->', '\u25cf': '*',
        '\u2605': '*', '\u2713': 'v', '\u2717': 'x', '\u00a0': ' ',
        '\U0001f3af': '[TARGET]', '\U0001f6e0': '[TOOLS]',
        '\U0001f4e6': '[MATERIALS]', '\U0001f9e9': '[PUZZLE]',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove any remaining emoji/non-latin-1 chars
    text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text


def _strip_md(text):
    """Remove markdown formatting for plain text rendering."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # italic
    text = re.sub(r'`(.+?)`', r'\1', text)  # code
    return _sanitize(text)


def markdown_to_pdf(md_text, output_path, student_name="Student", doc_title="Report", date_str=""):
    """Convert markdown text to a styled PDF using fpdf2."""
    LEFT = 10  # left margin
    W = 190    # usable width (210 - 10 left - 10 right)

    pdf = ReportPDF(student_name, doc_title, date_str)
    pdf.alias_nb_pages()
    pdf.add_page()

    for line in md_text.split("\n"):
        stripped = line.strip()

        if not stripped:
            pdf.ln(3)
            continue

        # Horizontal rule
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(LEFT, pdf.get_y(), LEFT + W, pdf.get_y())
            pdf.ln(4)
            continue

        # Sanitize unicode for latin-1 PDF encoding
        stripped = _sanitize(stripped)

        # Always reset x to left margin before rendering
        pdf.set_x(LEFT)

        # Headings
        if stripped.startswith("# "):
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(91, 143, 185)
            pdf.multi_cell(W, 9, _strip_md(stripped[2:]))
            pdf.set_draw_color(91, 143, 185)
            pdf.line(LEFT, pdf.get_y(), LEFT + W, pdf.get_y())
            pdf.ln(4)
        elif stripped.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(52, 73, 94)
            pdf.multi_cell(W, 8, _strip_md(stripped[3:]))
            pdf.set_draw_color(224, 224, 224)
            pdf.line(LEFT, pdf.get_y(), LEFT + W, pdf.get_y())
            pdf.ln(3)
        elif stripped.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(91, 143, 185)
            pdf.multi_cell(W, 7, _strip_md(stripped[4:]))
            pdf.ln(2)
        # Bullet points
        elif stripped.startswith("- ") or stripped.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(44, 62, 80)
            bullet_text = _strip_md(stripped[2:])
            pdf.set_x(LEFT + 4)
            pdf.cell(4, 6, "-")
            pdf.multi_cell(W - 8, 6, bullet_text)
        # Numbered lists
        elif re.match(r'^\d+\.', stripped):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(44, 62, 80)
            pdf.set_x(LEFT + 4)
            pdf.multi_cell(W - 4, 6, _strip_md(stripped))
        # Table rows
        elif stripped.startswith("|"):
            pdf.set_x(LEFT)
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not cells:
                continue
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue  # skip separator row
            is_header = any("**" in c for c in cells)
            if is_header:
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_fill_color(91, 143, 185)
                pdf.set_text_color(255, 255, 255)
            else:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(44, 62, 80)
                pdf.set_fill_color(248, 249, 250)
            col_w = W / max(len(cells), 1)
            for cell in cells:
                cell_text = _strip_md(cell)
                # Truncate based on actual column width at font size 8
                max_chars = int(col_w / 1.8)
                if len(cell_text) > max_chars:
                    cell_text = cell_text[:max_chars - 1] + ".."
                pdf.cell(col_w, 7, cell_text, border=1, fill=True)
            pdf.ln()
        # Blockquote
        elif stripped.startswith(">"):
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(91, 143, 185)
            pdf.set_x(LEFT + 6)
            pdf.multi_cell(W - 6, 6, _strip_md(stripped[1:].strip()))
            pdf.set_text_color(44, 62, 80)
        # Regular paragraph
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(44, 62, 80)
            pdf.multi_cell(W, 6, _strip_md(stripped))

    pdf.output(str(output_path))


def generate_student_reports(client, student_id, forge, output_base, date_str):
    """Generate all 7 polished PDF reports for a student."""
    # Load student profile
    profile_path = Path("data/students") / f"{student_id}.json"
    with open(profile_path) as f:
        profile = json.load(f)

    student_name = profile["name"]
    folder_name = f"{student_name}_{date_str}"
    output_dir = output_base / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Generating reports for {student_name} (Grade {profile['grade']})")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}")

    for doc in DOCUMENT_TYPES:
        print(f"\n  [{doc['key']}] {doc['label']}...")

        # Step 1: Generate raw output from Material Forge
        method = getattr(forge, doc["method"])
        args = doc["args"](student_id)
        try:
            raw_result = method(**args)
        except Exception as e:
            print(f"    ERROR generating: {e}")
            continue

        raw_text = raw_to_text(raw_result)

        # Step 2: Polish with Gemma 4
        print(f"    Polishing with Gemma 4...")
        try:
            polished_md = polish_with_gemma(
                client, raw_text, doc["label"], profile, date_str
            )
        except Exception as e:
            print(f"    ERROR polishing: {e}")
            polished_md = f"# {doc['label']}: {student_name}\n\n{raw_text}"

        # Step 3: Save markdown
        md_path = output_dir / f"{doc['key']}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(polished_md)

        # Step 4: Convert to PDF
        pdf_path = output_dir / f"{doc['key']}.pdf"
        try:
            markdown_to_pdf(
                polished_md, pdf_path,
                student_name=student_name,
                doc_title=doc["label"],
                date_str=date_str.replace("_", " "),
            )
            print(f"    -> {pdf_path.name}")
        except Exception as e:
            print(f"    PDF ERROR: {e}")
            print(f"    -> {md_path.name} (markdown only)")

    print(f"\n  Done: {output_dir}")
    return output_dir


def main():
    parser = argparse.ArgumentParser(description="Generate polished PDF reports")
    parser.add_argument("--student", help="Single student ID (e.g., maya_2026)")
    parser.add_argument("--mock", action="store_true", help="Use MockGemmaClient")
    args = parser.parse_args()

    # Setup
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_base = Path("outputs")
    output_base.mkdir(exist_ok=True)

    client = get_client(use_mock=args.mock)
    print(f"Using: {'MockGemmaClient' if args.mock else f'Gemma 4 ({client.model})'}")

    from agents.material_forge import MaterialForge
    forge = MaterialForge(client, data_dir="data")

    # Get student list
    if args.student:
        student_ids = [args.student]
    else:
        students_dir = Path("data/students")
        student_ids = sorted(
            p.stem for p in students_dir.glob("*.json")
        )

    print(f"Students: {', '.join(student_ids)}")
    print(f"Date: {date_str}")

    # Generate for each student
    for sid in student_ids:
        generate_student_reports(client, sid, forge, output_base, date_str)

    print(f"\n{'='*60}")
    print(f"  All reports complete!")
    print(f"  Output directory: {output_base}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
