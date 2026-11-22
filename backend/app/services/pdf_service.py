"""
TruthGuard Publication-Quality PDF Report Generation Service
Generates comprehensive evidence-grounded hallucination audit reports via ReportLab.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch

from backend.app.models import VerificationJob


class PDFReportService:
    @staticmethod
    def generate_verification_report(job: VerificationJob) -> io.BytesIO:
        """Generates an official TruthGuard PDF verification certificate & audit report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1C1917'),
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#78716C'),
            fontName='Helvetica'
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#1C1917'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#292524'),
            fontName='Helvetica'
        )

        code_style = ParagraphStyle(
            'ReportCode',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#44403C'),
            fontName='Courier',
            backColor=colors.HexColor('#FAF8F5')
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("TruthGuard™ Proof Desk Report", title_style))
        story.append(Paragraph(f"Evidence-Grounded Hallucination Audit & Calibration • Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#D5D1C6'), spaceAfter=14))

        # 2. Executive Summary Metrics Table
        rel_color = colors.HexColor('#16A34A') if job.reliability_score >= 0.7 else (colors.HexColor('#EA580C') if job.reliability_score >= 0.4 else colors.HexColor('#DC2626'))
        
        summary_data = [
            [
                Paragraph("<b>Analysis Title</b>", body_style),
                Paragraph(job.title, body_style),
                Paragraph("<b>Reliability Score R(a)</b>", body_style),
                Paragraph(f"<b><font color='{rel_color}'>{job.reliability_score * 100:.1f}%</font></b>", body_style)
            ],
            [
                Paragraph("<b>Total Atomic Claims</b>", body_style),
                Paragraph(str(job.total_claims), body_style),
                Paragraph("<b>Supported Claims (S)</b>", body_style),
                Paragraph(f"<font color='#16A34A'><b>{job.supported_count}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Contradicted Claims (C)</b>", body_style),
                Paragraph(f"<font color='#DC2626'><b>{job.contradicted_count}</b></font>", body_style),
                Paragraph("<b>Unverified Claims (NEI)</b>", body_style),
                Paragraph(f"<font color='#CA8A04'><b>{job.nei_count}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Mean Claim Rho (ρ̄)</b>", body_style),
                Paragraph(f"{job.mean_rho * 100:.1f}%", body_style),
                Paragraph("<b>Strongest Contradiction (P_C^max)</b>", body_style),
                Paragraph(f"{job.max_p_c * 100:.1f}%", body_style)
            ]
        ]

        t_summary = Table(summary_data, colWidths=[1.7 * inch, 2.0 * inch, 1.8 * inch, 1.5 * inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAF8F5')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E5DC')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E5DC')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 14))

        # 3. Original Answer vs Corrected Answer Comparison
        story.append(Paragraph("Answer Comparison (Original vs Grounded Correction)", section_heading))
        comp_data = [
            [
                Paragraph("<b>Original Answer</b>", body_style),
                Paragraph("<b>M5 Grounded Revision (Verified-Then-Accepted)</b>", body_style)
            ],
            [
                Paragraph(job.original_text, body_style),
                Paragraph(job.corrected_text or job.original_text, body_style)
            ]
        ]
        t_comp = Table(comp_data, colWidths=[3.5 * inch, 3.5 * inch])
        t_comp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F3ED')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D5D1C6')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E5DC')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_comp)
        story.append(Spacer(1, 14))

        # 4. Atomic Claims Breakdown Table
        story.append(Paragraph("Atomic Claim-Level Audit & Evidence Grounding", section_heading))
        
        claims_table_data = [
            [
                Paragraph("<b>#</b>", body_style),
                Paragraph("<b>Claim Text</b>", body_style),
                Paragraph("<b>Verdict</b>", body_style),
                Paragraph("<b>Reliability (ρ)</b>", body_style),
                Paragraph("<b>Best Grounded Evidence</b>", body_style)
            ]
        ]

        for claim in job.claims:
            v_color = '#16A34A' if claim.predicted_label == 'SUPPORTED' else ('#DC2626' if claim.predicted_label == 'CONTRADICTED' else '#CA8A04')
            claims_table_data.append([
                Paragraph(str(claim.claim_number), body_style),
                Paragraph(claim.claim_text, body_style),
                Paragraph(f"<font color='{v_color}'><b>{claim.predicted_label}</b></font>", body_style),
                Paragraph(f"{claim.reliability * 100:.0f}%", body_style),
                Paragraph(claim.best_evidence or claim.rationale or "No evidence retrieved", body_style)
            ])

        t_claims = Table(claims_table_data, colWidths=[0.3 * inch, 2.5 * inch, 1.1 * inch, 0.9 * inch, 2.2 * inch])
        t_claims.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F3ED')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D5D1C6')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E5DC')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_claims)
        story.append(Spacer(1, 16))

        # 5. Limitations & Academic Footnote
        story.append(Paragraph("Important Epistemic Limitations & Policy", section_heading))
        story.append(Paragraph(
            "TruthGuard applies a calibrated 3-way epistemic split. Claims classified as NOT-ENOUGH-INFO (NEI) indicate that retrieved sources lacked conclusive entailment or contradiction, not that the statement is false. All grounded corrections undergo a strict verify-then-accept re-evaluation prior to inclusion.",
            subtitle_style
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer
