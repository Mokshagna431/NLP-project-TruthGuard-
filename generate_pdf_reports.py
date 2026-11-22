"""
TruthGuard PDF Report Generator
Converts TruthGuard markdown reports into publication-quality PDF documents using ReportLab.
Generates:
1. TruthGuard_Development_Report.pdf (Full Engineering & Development Completion Report)
2. TruthGuard_Research_Paper.pdf (Academic & Technical Research Report)
3. TruthGuard_Complete_Master_Report.pdf (Omnibus Master Volume)
"""

import os
import re
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACT_DIR = r"C:\Users\mokim\.gemini\antigravity\brain\17f641a3-8f3c-4aa3-adaa-e72bc1a419a7"


class NumberedCanvas(canvas.Canvas):
    """Adds running headers and footers with page numbers: Page X of Y."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#78716C"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 756, "TruthGuard™ • AI Hallucination Detection & Grounded Verification Platform")
            self.drawRightString(576, 756, "Confidential / Research Release")
            self.setStrokeColor(colors.HexColor("#E7E5E4"))
            self.setLineWidth(0.5)
            self.line(36, 750, 576, 750)

        # Footer
        self.setStrokeColor(colors.HexColor("#E7E5E4"))
        self.setLineWidth(0.5)
        self.line(36, 45, 576, 45)

        self.drawString(36, 32, f"TruthGuard Production System • Generated {datetime.utcnow().strftime('%B %Y')}")
        self.drawRightString(576, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def clean_markdown_text(text: str) -> str:
    """Converts inline markdown formatting to ReportLab XML tags."""
    # 1. Escape HTML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    # 2. Convert markdown formatting AFTER escaping
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_(.*?)_(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#1E293B"><b>\1</b></font>', text)

    # 3. Handle KaTeX / Math symbols
    text = text.replace(r'\le', '≤').replace(r'\ge', '≥').replace(r'\to', '→').replace(r'\implies', '⟹')
    text = text.replace(r'\in', '∈').replace(r'\pm', '±').replace(r'\neq', '≠').replace(r'\equiv', '≡')
    text = text.replace(r'\mid', '|').replace(r'\theta', 'θ').replace(r'\sigma', 'σ')
    text = text.replace(r'\tau', 'τ').replace(r'\lambda', 'λ').replace(r'\rho', 'ρ')
    text = text.replace(r'\bar{\rho}', 'ρ̄').replace(r'\sum', 'Σ').replace(r'\cdot', '·')
    text = text.replace(r'\mathcal{C}', 'C').replace(r'\mathcal{D}', 'D').replace(r'\mathbb{I}', '1')
    text = text.replace(r'\text{softmax}', 'softmax').replace(r'\text{CrossEncoder}', 'CrossEncoder')
    text = text.replace(r'\text{rank}', 'rank').replace(r'\text{RRF}', 'RRF')
    text = text.replace(r'\text{argmax}', 'argmax').replace(r'\text{argmin}', 'argmin')
    text = text.replace(r'\text{NLL}', 'NLL').replace(r'\text', '').replace(r'\mathbf', '')
    text = text.replace(r'\frac', '').replace(r'\|', '|').replace(r'$$', '')
    text = re.sub(r'\\left|\\right', '', text)
    text = re.sub(r'\$(.*?)\$', r'<i>\1</i>', text)
    return text


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        'doc_title': ParagraphStyle(
            'DocTitle',
            parent=base['Heading1'],
            fontSize=21,
            leading=25,
            textColor=colors.HexColor('#0F172A'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ),
        'doc_subtitle': ParagraphStyle(
            'DocSubtitle',
            parent=base['Normal'],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#475569'),
            fontName='Helvetica',
            spaceAfter=14
        ),
        'h1': ParagraphStyle(
            'H1',
            parent=base['Heading1'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0F172A'),
            fontName='Helvetica-Bold',
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True
        ),
        'h2': ParagraphStyle(
            'H2',
            parent=base['Heading2'],
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        ),
        'h3': ParagraphStyle(
            'H3',
            parent=base['Heading3'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#334155'),
            fontName='Helvetica-Bold',
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True
        ),
        'body': ParagraphStyle(
            'Body',
            parent=base['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica',
            spaceAfter=6
        ),
        'bullet': ParagraphStyle(
            'Bullet',
            parent=base['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica',
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=3
        ),
        'quote': ParagraphStyle(
            'Quote',
            parent=base['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#334155'),
            fontName='Helvetica-Oblique',
            leftIndent=14,
            rightIndent=14,
            spaceBefore=4,
            spaceAfter=6
        ),
        'code': ParagraphStyle(
            'Code',
            parent=base['Normal'],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor('#0F172A'),
            fontName='Courier',
            leftIndent=8,
            spaceBefore=2,
            spaceAfter=2
        ),
        'table_cell': ParagraphStyle(
            'TableCell',
            parent=base['Normal'],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica'
        ),
        'table_header': ParagraphStyle(
            'TableHeader',
            parent=base['Normal'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#FFFFFF'),
            fontName='Helvetica-Bold'
        )
    }
    return styles


def parse_markdown_to_flowables(md_text: str, styles) -> list:
    """Parses markdown text into ReportLab Flowables."""
    flowables = []
    lines = md_text.splitlines()
    i = 0
    in_code_block = False
    code_lines = []

    in_table = False
    table_lines = []

    while i < len(lines):
        line = lines[i]

        # Handle Code Blocks
        if line.strip().startswith("```"):
            if in_code_block:
                # Close code block
                in_code_block = False
                code_text = "<br/>".join(
                    [cl.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;") for cl in code_lines]
                )
                code_table = Table(
                    [[Paragraph(code_text, styles['code'])]],
                    colWidths=[540]
                )
                code_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                flowables.append(Spacer(1, 4))
                flowables.append(code_table)
                flowables.append(Spacer(1, 6))
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Handle Markdown Tables
        if line.strip().startswith("|") and line.strip().endswith("|"):
            table_lines.append(line.strip())
            # Look ahead to see if table continues
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
                i += 1
                continue
            else:
                # End of table, process it
                if len(table_lines) >= 2:
                    # Filter out separator row e.g. |---|---|
                    filtered_rows = [r for r in table_lines if not re.match(r'^\|[\s\:\-]+(?:\|[\s\:\-]+)*\|$', r)]
                    parsed_rows = []
                    for row_idx, r in enumerate(filtered_rows):
                        cells = [c.strip() for c in r.strip('|').split('|')]
                        is_header = (row_idx == 0)
                        row_cells = []
                        for cell_text in cells:
                            cleaned = clean_markdown_text(cell_text)
                            style = styles['table_header'] if is_header else styles['table_cell']
                            row_cells.append(Paragraph(cleaned, style))
                        parsed_rows.append(row_cells)

                    if parsed_rows:
                        num_cols = len(parsed_rows[0])
                        # Calculate proportional col widths
                        total_width = 540
                        col_width = total_width / num_cols
                        t = Table(parsed_rows, colWidths=[col_width] * num_cols)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                            ('LEFTPADDING', (0, 0), (-1, -1), 5),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                        ]))
                        flowables.append(Spacer(1, 4))
                        flowables.append(t)
                        flowables.append(Spacer(1, 6))

                table_lines = []
                i += 1
                continue

        stripped = line.strip()

        # Empty lines
        if not stripped:
            i += 1
            continue

        # Display Math Blocks
        if stripped.startswith("$$"):
            math_lines = [stripped.strip("$")]
            if not stripped.endswith("$$") or stripped == "$$":
                i += 1
                while i < len(lines) and not lines[i].strip().endswith("$$"):
                    math_lines.append(lines[i].strip().strip("$"))
                    i += 1
                if i < len(lines):
                    math_lines.append(lines[i].strip().strip("$"))
            math_text = " ".join([clean_markdown_text(ml) for ml in math_lines if ml.strip()])
            math_table = Table(
                [[Paragraph(f"<font color='#0F172A'><b>Formula:</b> <i>{math_text}</i></font>", styles['quote'])]],
                colWidths=[540]
            )
            math_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            flowables.append(Spacer(1, 2))
            flowables.append(math_table)
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Horizontal Rule
        if re.match(r'^(\-{3,}|\_{3,}|\*{3,})$', stripped):
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#E2E8F0'), spaceAfter=8))
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            flowables.append(Paragraph(clean_markdown_text(stripped[2:]), styles['doc_title']))
            i += 1
            continue
        elif stripped.startswith("## "):
            flowables.append(Paragraph(clean_markdown_text(stripped[3:]), styles['h1']))
            i += 1
            continue
        elif stripped.startswith("### "):
            flowables.append(Paragraph(clean_markdown_text(stripped[4:]), styles['h2']))
            i += 1
            continue
        elif stripped.startswith("#### "):
            flowables.append(Paragraph(clean_markdown_text(stripped[5:]), styles['h3']))
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_text = clean_markdown_text(stripped.lstrip("> "))
            quote_table = Table(
                [[Paragraph(quote_text, styles['quote'])]],
                colWidths=[540]
            )
            quote_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('LINEBEFORE', (0, 0), (0, -1), 3.0, colors.HexColor('#2563EB')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            flowables.append(Spacer(1, 2))
            flowables.append(quote_table)
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Bullet lists (- or * or numbered 1.)
        bullet_match = re.match(r'^(\*|\-|\d+\.)\s+(.+)$', stripped)
        if bullet_match:
            b_sym = "•" if bullet_match.group(1) in ('*', '-') else bullet_match.group(1)
            b_content = bullet_match.group(2)
            bullet_html = f"<b>{b_sym}</b> {clean_markdown_text(b_content)}"
            flowables.append(Paragraph(bullet_html, styles['bullet']))
            i += 1
            continue

        # Standard Body paragraph
        flowables.append(Paragraph(clean_markdown_text(stripped), styles['body']))
        i += 1

    return flowables


def generate_pdf_from_markdown(md_path: str, output_pdf_path: str):
    """Compiles a single markdown report into an official numbered PDF."""
    if not os.path.exists(md_path):
        print(f"[Error] Source markdown not found: {md_path}")
        return False

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    styles = build_styles()
    flowables = parse_markdown_to_flowables(md_content, styles)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    doc.build(flowables, canvasmaker=NumberedCanvas)
    print(f"[Success] Generated PDF: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
    return True


def generate_all_reports():
    """Generates development report, academic research paper, and combined master PDF."""
    print("=========================================================")
    print("Generating Official TruthGuard Publication-Quality PDFs...")
    print("=========================================================")

    # 1. Development Completion Report
    dev_md = os.path.join(ARTIFACT_DIR, "TRUTHGUARD_DEVELOPMENT_COMPLETION_REPORT.md")
    dev_pdf_root = os.path.join(ROOT_DIR, "TruthGuard_Development_Report.pdf")
    dev_pdf_art = os.path.join(ARTIFACT_DIR, "TruthGuard_Development_Report.pdf")

    generate_pdf_from_markdown(dev_md, dev_pdf_root)
    generate_pdf_from_markdown(dev_md, dev_pdf_art)

    # 2. Academic Research & Systems Report
    res_md = os.path.join(ARTIFACT_DIR, "TRUTHGUARD_RESEARCH_SYSTEM_REPORT.md")
    res_pdf_root = os.path.join(ROOT_DIR, "TruthGuard_Research_Paper.pdf")
    res_pdf_art = os.path.join(ARTIFACT_DIR, "TruthGuard_Research_Paper.pdf")

    generate_pdf_from_markdown(res_md, res_pdf_root)
    generate_pdf_from_markdown(res_md, res_pdf_art)

    # 3. Master Omnibus Report (Combining both into a single volume)
    with open(dev_md, 'r', encoding='utf-8') as f1, open(res_md, 'r', encoding='utf-8') as f2:
        master_md = f1.read() + "\n\n---\n\n" + f2.read()

    master_pdf_root = os.path.join(ROOT_DIR, "TruthGuard_Master_Report.pdf")
    master_pdf_art = os.path.join(ARTIFACT_DIR, "TruthGuard_Master_Report.pdf")

    styles = build_styles()
    master_flowables = parse_markdown_to_flowables(master_md, styles)
    doc = SimpleDocTemplate(
        master_pdf_root,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    doc.build(master_flowables, canvasmaker=NumberedCanvas)
    print(f"[Success] Generated Master Omnibus: {master_pdf_root} ({os.path.getsize(master_pdf_root)} bytes)")

    # Copy to artifact dir
    import shutil
    shutil.copyfile(master_pdf_root, master_pdf_art)
    print(f"[Success] Copied Master Omnibus to artifact dir: {master_pdf_art}")

    print("\nAll PDF reports generated successfully!")


if __name__ == "__main__":
    generate_all_reports()
