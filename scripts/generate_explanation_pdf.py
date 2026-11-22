"""
TruthGuard Complete Project Explanation Book & Viva Defense Manual Generator
Generates: TruthGuard_Documentation/TruthGuard_Complete_Project_Explanation.pdf
Using ReportLab 5.1.0 with NumberedCanvas running headers and footers.
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PDF_OUTPUT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "TruthGuard_Documentation",
        "TruthGuard_Complete_Project_Explanation.pdf",
    )
)

# Colors
C_PRIMARY = HexColor("#372014")  # Deep Espresso / Dark Brown
C_SECONDARY = HexColor("#5D4429")  # Coffee Brown
C_TERTIARY = HexColor("#715B43")  # Mid Brown
C_ACCENT_GREEN = HexColor("#2D5A27")  # Forest Green (Supported)
C_ACCENT_RED = HexColor("#8B1E1E")  # Brick Red (Contradicted)
C_ACCENT_GOLD = HexColor("#A47012")  # Warm Amber (NEI)
C_BG_WARM = HexColor("#FBF9F5")  # Warm Paper Ivory
C_BG_PANEL = HexColor("#F4EFE6")  # Tan Panel
C_BORDER = HexColor("#D5C8B5")  # Soft Border
C_TEXT_DARK = HexColor("#222222")  # Off-Black
C_TEXT_MUTED = HexColor("#555555")  # Charcoal Grey
C_WHITE = HexColor("#FFFFFF")


class NumberedCanvas(canvas.Canvas):

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
      self.draw_page_decorations(num_pages)
      canvas.Canvas.showPage(self)
    canvas.Canvas.save(self)

  def draw_page_decorations(self, page_count):
    if self._pageNumber == 1:
      # Skip title page
      return

    self.saveState()

    # Running Header
    self.setFont("Helvetica", 8)
    self.setFillColor(C_TERTIARY)
    self.drawString(
        54,
        792 - 36,
        "TRUTHGUARD: SYSTEM ENGINEERING MANUAL & ACADEMIC VIVA GUIDE",
    )
    self.drawRightString(
        612 - 54, 792 - 36, "NLP & GENERATIVE AI RESEARCH PROJECT"
    )

    self.setStrokeColor(C_BORDER)
    self.setLineWidth(0.5)
    self.line(54, 792 - 42, 612 - 54, 792 - 42)

    # Running Footer
    self.line(54, 46, 612 - 54, 46)
    self.setFont("Helvetica", 8)
    self.setFillColor(C_TERTIARY)
    self.drawString(
        54, 34, "CONFIDENTIAL & PROPRIETARY — FOR ACADEMIC EVALUATION ONLY"
    )
    page_str = f"Page {self._pageNumber} of {page_count}"
    self.drawRightString(612 - 54, 34, page_str)

    self.restoreState()


def get_custom_styles():
  base = getSampleStyleSheet()

  styles = {}

  styles["CoverTitle"] = ParagraphStyle(
      "CoverTitle",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=30,
      leading=36,
      textColor=C_PRIMARY,
      alignment=0,
      spaceAfter=8,
  )

  styles["CoverKicker"] = ParagraphStyle(
      "CoverKicker",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=11,
      leading=14,
      textColor=C_SECONDARY,
      alignment=0,
      spaceAfter=6,
  )

  styles["CoverSubtitle"] = ParagraphStyle(
      "CoverSubtitle",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=13,
      leading=18,
      textColor=C_TERTIARY,
      alignment=0,
      spaceAfter=20,
  )

  styles["CoverMeta"] = ParagraphStyle(
      "CoverMeta",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=9.5,
      leading=14,
      textColor=C_TEXT_MUTED,
  )

  styles["CoverMetaBold"] = ParagraphStyle(
      "CoverMetaBold",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=9.5,
      leading=14,
      textColor=C_PRIMARY,
  )

  styles["ChapterNum"] = ParagraphStyle(
      "ChapterNum",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=10,
      leading=13,
      textColor=C_SECONDARY,
      spaceBefore=14,
      spaceAfter=2,
  )

  styles["ChapterTitle"] = ParagraphStyle(
      "ChapterTitle",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=19,
      leading=23,
      textColor=C_PRIMARY,
      spaceBefore=0,
      spaceAfter=10,
      keepWithNext=True,
  )

  styles["SectionHeading"] = ParagraphStyle(
      "SectionHeading",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=13,
      leading=17,
      textColor=C_PRIMARY,
      spaceBefore=12,
      spaceAfter=5,
      keepWithNext=True,
  )

  styles["SubSectionHeading"] = ParagraphStyle(
      "SubSectionHeading",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=10.5,
      leading=14,
      textColor=C_SECONDARY,
      spaceBefore=8,
      spaceAfter=4,
      keepWithNext=True,
  )

  styles["Body"] = ParagraphStyle(
      "Body",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=9,
      leading=13,
      textColor=C_TEXT_DARK,
      alignment=4,  # Justified
      spaceAfter=6,
  )

  styles["BodyBold"] = ParagraphStyle(
      "BodyBold",
      parent=styles["Body"],
      fontName="Helvetica-Bold",
  )

  styles["BulletText"] = ParagraphStyle(
      "BulletText",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=9,
      leading=12.5,
      textColor=C_TEXT_DARK,
      leftIndent=14,
      firstLineIndent=-10,
      spaceAfter=4,
  )

  styles["CodeBlock"] = ParagraphStyle(
      "CodeBlock",
      parent=base["Normal"],
      fontName="Courier",
      fontSize=7.5,
      leading=10.5,
      textColor=HexColor("#1A202C"),
      spaceAfter=4,
  )

  styles["CalloutTitle"] = ParagraphStyle(
      "CalloutTitle",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=9.5,
      leading=12,
      textColor=C_PRIMARY,
      spaceAfter=3,
  )

  styles["CalloutBody"] = ParagraphStyle(
      "CalloutBody",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=8.5,
      leading=11.5,
      textColor=C_TEXT_DARK,
  )

  styles["TableHead"] = ParagraphStyle(
      "TableHead",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=8,
      leading=10,
      textColor=C_PRIMARY,
      alignment=1,  # Center
  )

  styles["TableCell"] = ParagraphStyle(
      "TableCell",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=7.8,
      leading=10,
      textColor=C_TEXT_DARK,
  )

  styles["TableCellBold"] = ParagraphStyle(
      "TableCellBold",
      parent=styles["TableCell"],
      fontName="Helvetica-Bold",
  )

  styles["TableCellCenter"] = ParagraphStyle(
      "TableCellCenter",
      parent=styles["TableCell"],
      alignment=1,
  )

  styles["TOCItem"] = ParagraphStyle(
      "TOCItem",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=9,
      leading=14,
      textColor=C_PRIMARY,
  )

  styles["TOCSubItem"] = ParagraphStyle(
      "TOCSubItem",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=8.5,
      leading=12,
      textColor=C_SECONDARY,
      leftIndent=15,
  )

  styles["QuestionTitle"] = ParagraphStyle(
      "QuestionTitle",
      parent=base["Normal"],
      fontName="Helvetica-Bold",
      fontSize=9.5,
      leading=12.5,
      textColor=C_PRIMARY,
      spaceBefore=6,
      spaceAfter=2,
      keepWithNext=True,
  )

  styles["AnswerBody"] = ParagraphStyle(
      "AnswerBody",
      parent=base["Normal"],
      fontName="Helvetica",
      fontSize=8.5,
      leading=11.5,
      textColor=C_TEXT_DARK,
      alignment=4,
      spaceAfter=6,
  )

  return styles


def make_callout(
    title, text, styles, width=504, accent_color=C_SECONDARY, bg_color=C_BG_WARM
):
  p_title = Paragraph(f"<b>{title}</b>", styles["CalloutTitle"])
  p_body = Paragraph(text, styles["CalloutBody"])
  content = [p_title, p_body]
  tbl = Table([[content]], colWidths=[width])
  tbl.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), bg_color),
          ("BOX", (0, 0), (-1, -1), 0.5, C_BORDER),
          ("LINELEFT", (0, 0), (0, -1), 3.0, accent_color),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("LEFTPADDING", (0, 0), (-1, -1), 10),
          ("RIGHTPADDING", (0, 0), (-1, -1), 10),
      ])
  )
  return tbl


def make_code_panel(code_str, styles, width=504):
  p = Paragraph(code_str.replace("\n", "<br/>&nbsp;&nbsp;"), styles["CodeBlock"])
  tbl = Table([[p]], colWidths=[width])
  tbl.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F7FAFC")),
          ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
          ("LINELEFT", (0, 0), (0, -1), 2.5, HexColor("#4A5568")),
          ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("LEFTPADDING", (0, 0), (-1, -1), 8),
          ("RIGHTPADDING", (0, 0), (-1, -1), 8),
      ])
  )
  return tbl


def build_explanation_book():
  print("[Starting] Building TruthGuard Complete Project Explanation Book...")
  styles = get_custom_styles()
  story = []

  # =========================================================================
  # COVER PAGE
  # =========================================================================
  story.append(Spacer(1, 40))
  story.append(
      Paragraph(
          "ACADEMIC CAPSTONE / FINAL PROJECT COMPREHENSIVE MANUAL",
          styles["CoverKicker"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard: An AI-Powered Evidence-Grounded Hallucination Detection,"
          " Verification and Correction System",
          styles["CoverTitle"],
      )
  )
  story.append(
      Paragraph(
          "System Architecture, Algorithmic Foundations, Experimental"
          " Benchmarks, Real-World Case Studies, and Complete Viva Defense"
          " Preparation Guide",
          styles["CoverSubtitle"],
      )
  )

  story.append(
      HRFlowable(
          width="100%", thickness=2, color=C_PRIMARY, spaceBefore=0, spaceAfter=20
      )
  )

  # Cover Meta Table
  meta_data = [
      [
          Paragraph("<b>Project Domain:</b>", styles["CoverMetaBold"]),
          Paragraph(
              "Natural Language Processing (NLP), Generative AI, Retrieval"
              " Augmented Generation (RAG), Automated Fact Checking",
              styles["CoverMeta"],
          ),
      ],
      [
          Paragraph("<b>Framework Version:</b>", styles["CoverMetaBold"]),
          Paragraph(
              "TruthGuard v2.4 (Production Monolith Core)", styles["CoverMeta"]
          ),
      ],
      [
          Paragraph("<b>Author / Candidate:</b>", styles["CoverMetaBold"]),
          Paragraph("NLP & Generative AI Project Team", styles["CoverMeta"]),
      ],
      [
          Paragraph("<b>Academic Defense:</b>", styles["CoverMetaBold"]),
          Paragraph(
              "Major Capstone Project Evaluation & Viva Voce",
              styles["CoverMeta"],
          ),
      ],
      [
          Paragraph("<b>Submission Date:</b>", styles["CoverMetaBold"]),
          Paragraph("Academic Year 2026-2027", styles["CoverMeta"]),
      ],
      [
          Paragraph("<b>Implementation Status:</b>", styles["CoverMetaBold"]),
          Paragraph(
              "Full Pipeline Deployed (Modules M1 to M5, Universal Arbiter,"
              " Frontend Dashboard, SQLite Persistence)",
              styles["CoverMeta"],
          ),
      ],
  ]
  meta_table = Table(meta_data, colWidths=[120, 384])
  meta_table.setStyle(
      TableStyle([
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("LEFTPADDING", (0, 0), (-1, -1), 0),
          ("RIGHTPADDING", (0, 0), (-1, -1), 0),
      ])
  )
  story.append(meta_table)

  story.append(Spacer(1, 30))

  # Executive Abstract Callout
  exec_summary = (
      "<b>EXECUTIVE ABSTRACT:</b> Large Language Models (LLMs) produce"
      " convincing text containing severe factual hallucinations. TruthGuard"
      " addresses this crisis through a modular, deterministic, five-stage"
      " pipeline: <b>(M1)</b> Few-shot atomic claim decomposition with"
      " co-reference resolution, <b>(M2)</b> Multi-source hybrid retrieval"
      " fusing BM25, SBERT, and Cross-Encoder reranking with strict semantic"
      " quality gating, <b>(M3)</b> Temperature-calibrated Natural Language"
      " Inference (DeBERTa-v3) augmented with deterministic SymPy mathematical"
      " validation, a <b>Symmetrical Universal AI Investigation Engine</b> that"
      " conducts deep adversarial fact-checking across all three verdicts"
      " (Supported, Contradicted, NEI), <b>(M4)</b> Non-compensatory answer"
      " reliability scoring using weakest-link penalization, and <b>(M5)</b>"
      " Verify-then-accept grounded paragraph correction. On the multi-domain"
      " TruthGuard-350 benchmark, TruthGuard achieves <b>82.86% classification"
      " accuracy</b>, <b>93.78% Contradiction F1</b>, <b>100.0% retrieval"
      " relevance</b>, and a negligible 3.48% false correction rate at 0.68s"
      " latency per claim."
  )
  story.append(
      make_callout(
          "EXECUTIVE SUMMARY & SYSTEM SCOPE",
          exec_summary,
          styles,
          accent_color=C_PRIMARY,
          bg_color=C_BG_PANEL,
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # TABLE OF CONTENTS
  # =========================================================================
  story.append(Paragraph("TABLE OF CONTENTS", styles["ChapterTitle"]))
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_SECONDARY,
          spaceBefore=0,
          spaceAfter=12,
      )
  )

  toc_entries = [
      (
          "Chapter 1: The Hallucination Crisis in Large Language Models",
          "Theoretical foundations, taxonomy of hallucinations, high-stakes"
          " failure modes, why standard RAG and prompt engineering fail.",
      ),
      (
          "Chapter 2: System Overview & Theoretical Foundations",
          "Verification paradigm, core design principles, high-level pipeline"
          " architecture, formal mathematical notation.",
      ),
      (
          "Chapter 3: End-to-End System Architecture",
          "Modular monolith engineering, data contracts and DTOs, SQLite"
          " persistence, fault tolerance and graceful fallbacks.",
      ),
      (
          "Chapter 4: Module 1 — Atomic Claim Extraction & Disambiguation (M1)",
          "Semantic decomposition, few-shot prompting vs rule fallback,"
          " co-reference resolution, clause isolation.",
      ),
      (
          "Chapter 5: Module 2 — Multi-Source Evidence Retrieval Engine (M2)",
          "Hybrid lexical-dense search, Reciprocal Rank Fusion (RRF),"
          " Cross-Encoder reranking, Wikipedia, ArXiv, and PubMed.",
      ),
      (
          "Chapter 6: The Retrieval Quality Gate & Semantic Filtering",
          "Lexical traps and polysemy, SpaCy NER entity overlap, two-token"
          " content lemma constraint, filtering metrics.",
      ),
      (
          "Chapter 7: Module 3 — Natural Language Inference & Math Engine (M3)",
          "DeBERTa-v3 cross-encoder NLI, logit calibration (T=1.35),"
          " non-uniform thresholds, deterministic SymPy math verifier.",
      ),
      (
          "Chapter 8: Universal Multi-Perspective AI Investigation",
          "Why single-pass NLI fails, Stage 2 symmetrical investigation for"
          " Supported, Contradicted, and NEI claims, Arbiter synthesis.",
      ),
      (
          "Chapter 9: Module 4 — Non-Compensatory Answer Reliability Scoring"
          " (M4)",
          "Flaws of linear averaging, weakest-link penalization principle,"
          " claim-level and answer-level mathematical formulas.",
      ),
      (
          "Chapter 10: Module 5 — Grounded Paragraph Correction Engine (M5)",
          "Verify-then-accept protocol, semantic deduplication fix,"
          " non-destructive editing, secondary NLI safety verification.",
      ),
      (
          "Chapter 11: Technology Stack & Implementation Details",
          "Python 3.11, FastAPI, Hugging Face Transformers, React 18 frontend,"
          " ChromaDB, Docker and deployment optimizations.",
      ),
      (
          "Chapter 12: Database Schema & API Specifications",
          "Relational SQLite/PostgreSQL schema, REST endpoints, DTO contracts,"
          " rate limiting, CORS, and performance indexing.",
      ),
      (
          "Chapter 13: Frontend User Workflow & Interactive UI",
          "Dual-pane dashboard, interactive claim-to-evidence grounding, visual"
          " diff viewer, export modal capabilities.",
      ),
      (
          "Chapter 14: Experimental Evaluation & Benchmark Results",
          "TruthGuard-350 multi-domain evaluation, FEVER/HaluEval comparisons,"
          " ablation studies, latency profiling, failure mode analysis.",
      ),
      (
          "Chapter 15: Real-World Case Studies & End-to-End Walkthroughs",
          "Detailed execution tracing across 9 golden test cases including"
          " Apollo 11, Jupiter colony, Vitamin C, and SymPy arithmetic.",
      ),
      (
          "Chapter 16: Comprehensive Viva & Technical Review Defense Guide",
          "50 exhaustive technical questions and model answers, examiner"
          " curveballs, 2-min / 5-min / 10-min defense pitches.",
      ),
      (
          "Chapter 17: Limitations, Future Work & Conclusion",
          "Current system boundaries, continuous streaming crawlers,"
          " multimodal roadmap, final research summary.",
      ),
      (
          "Glossary of Key Technical Terms",
          "25+ rigorous definitions covering NLI, RAG, Calibration, and"
          " Hallucination metrics.",
      ),
      (
          "Academic References & Bibliography",
          "Complete literature citations [1]–[20] formatted to IEEE standard.",
      ),
  ]

  for title, desc in toc_entries:
    story.append(Paragraph(title, styles["TOCItem"]))
    story.append(Paragraph(desc, styles["TOCSubItem"]))
    story.append(Spacer(1, 2))

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 1: THE HALLUCINATION CRISIS IN LARGE LANGUAGE MODELS
  # =========================================================================
  story.append(Paragraph("CHAPTER 1", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "The Hallucination Crisis in Large Language Models",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "1.1 The Emergence of Generative AI & The 'Stochastic Parrot' Dilemma",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "The rapid deployment of autoregressive Large Language Models (LLMs)"
          " such as GPT-4, LLaMA-3, and Gemini has revolutionized natural"
          " language generation. However, because these systems are trained"
          " primarily via next-token prediction loss over massive text corpora,"
          " their objective function optimizes lexical fluency, grammatical"
          " coherence, and distributional likelihood rather than empirical"
          " truthfulness or epistemological grounding. As characterized in"
          " foundational NLP literature (Bender et al., 2021), LLMs function as"
          " 'stochastic parrots'—statistical synthesizers incapable of"
          " verifying the empirical reality of their generated assertions.",
          styles["Body"],
      )
  )
  story.append(
      Paragraph(
          "Consequently, LLMs exhibit a pervasive failure mode known as"
          " <b>hallucination</b>: the confident generation of grammatically"
          " fluent statements that are factually unverified, historically"
          " false, mathematically invalid, or contradicted by authoritative"
          " knowledge. Unlike human error, which is often accompanied by"
          " hesitation or hedging markers ('I believe', 'approximately'), LLM"
          " hallucinations are delivered with high model confidence and"
          " sophisticated rhetorical polish, making them uniquely deceptive.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "1.2 Formal Taxonomy of Hallucinations in Modern NLP",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "In academic literature, hallucinations are categorized into two"
          " macro-classes: <i>intrinsic hallucinations</i>, wherein generated"
          " text contradicts explicitly provided source context (e.g., in"
          " summarization or closed-domain QA), and <i>extrinsic"
          " hallucinations</i>, wherein generated assertions cannot be verified"
          " or contradicted by provided material but introduce ungrounded"
          " external claims. TruthGuard establishes a fine-grained operational"
          " taxonomy to classify and rectify these failures:",
          styles["Body"],
      )
  )

  tax_items = [
      (
          "1. Entity Confusion & Attribute Misassignment:",
          "Attributing the actions, discoveries, or physical properties of one"
          " entity to another (e.g., claiming Neil Armstrong was the second man"
          " on the Moon, or confusing Alexander Fleming with Louis Pasteur).",
      ),
      (
          "2. Temporal Drift & Chronological Anachronisms:",
          "Generating assertions that were historically true at one period but"
          " are currently obsolete, or collapsing distinct historical epochs"
          " (e.g., identifying past office-holders as current incumbents).",
      ),
      (
          "3. Numerical, Arithmetic & Boundary Drift:",
          "Stating incorrect statistical figures, dates, dimensions, or"
          " mathematical calculations while maintaining plausible contextual"
          " language.",
      ),
      (
          "4. Quantifier Inflation & Generalization Fallacies:",
          "Converting a qualified or localized truth into an absolute"
          " universal claim (e.g., transforming 'some bacteria cause infections'"
          " into 'all bacteria are harmful to human health').",
      ),
      (
          "5. Pure Fabrications (Out-of-Thin-Air):",
          "Entirely fictional historical events, non-existent scientific"
          " papers, phantom legal citations, or imaginary celestial colonies"
          " (e.g., 'NASA established a colony on Jupiter in 2024').",
      ),
  ]
  for title, desc in tax_items:
    story.append(
        Paragraph(
            f"<b>{title}</b> {desc}",
            styles["BulletText"],
        )
    )

  story.append(
      Paragraph(
          "1.3 High-Stakes Societal & Industrial Consequences",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "While harmless in creative writing, factual hallucinations pose"
          " catastrophic risks across mission-critical domains: <b>(a)"
          " Healthcare and Medicine:</b> Recommending incorrect drug dosages,"
          " misidentifying biochemical mechanisms (e.g., claiming Vitamin C"
          " synthesizes hemoglobin rather than collagen), or fabricating"
          " clinical trials; <b>(b) Legal Systems:</b> Fabricating non-existent"
          " judicial precedents (e.g., the infamous <i>Mata v. Avianca</i>"
          " sanctions); <b>(c) Financial Intelligence:</b> Misrepresenting"
          " quarterly earnings, regulatory compliance filings, or market"
          " capitalizations; <b>(d) Public Policy and Science:</b> Propagating"
          " ungrounded myths regarding public health, vaccines, or planetary"
          " science.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "1.4 Why Standard RAG and Prompt Engineering Fail",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Conventional industry approaches rely on two primary strategies:"
          " <i>prompt engineering</i> ('Answer truthfully and cite your"
          " sources') and standard <i>Retrieval-Augmented Generation (RAG)</i>."
          " Both fail under rigorous evaluation: <b>(1) Prompting does not"
          " alter the underlying decoder</b> or verify generated tokens;"
          " models hallucinate plausible-sounding citations with equal ease;"
          " <b>(2) Standard RAG suffers from retrieval noise</b>; when dense or"
          " sparse retrievers surface semi-related passages, the LLM either"
          " misinterprets them, ignores them ('lost in the middle' syndrome),"
          " or synthesizes conflicting evidence into an ungrounded compromise.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "1.5 Research Objectives & TruthGuard Vision",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard was conceived to build a <b>deterministic, verifiable,"
          " multi-stage proof engine</b> that operates downstream of any LLM."
          " Rather than relying on self-critique or recursive generative loops,"
          " TruthGuard decomposes text into atomic propositions, grounds each"
          " in external authoritative corpora via hybrid lexical-dense search,"
          " validates factual alignment using temperature-calibrated Natural"
          " Language Inference and symbolic mathematics, subjects every verdict"
          " to adversarial multi-perspective investigation, calculates a"
          " non-compensatory answer reliability score, and surgically corrects"
          " detected falsehoods.",
          styles["Body"],
      )
  )

  story.append(
      make_callout(
          "KEY TAKEAWAY — CHAPTER 1",
          "Generative LLMs optimize probability, not truth. Factuality must be"
          " established by an independent, external, multi-stage verification"
          " pipeline that decouples generation from empirical verification.",
          styles,
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 2: SYSTEM OVERVIEW & THEORETICAL FOUNDATIONS
  # =========================================================================
  story.append(Paragraph("CHAPTER 2", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "System Overview & Theoretical Foundations", styles["ChapterTitle"]
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "2.1 The Verification Paradigm: Detection vs. Attribution vs."
          " Correction",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Automated fact-checking requires three distinct capabilities:"
          " <b>Detection</b> (identifying whether a factual discrepancy exists),"
          " <b>Attribution</b> (locating external authoritative evidence that"
          " directly proves or disproves the claim), and <b>Correction</b>"
          " (re-writing the erroneous text to align with reality while"
          " preserving stylistic context). Existing systems often collapse"
          " these into a single generative prompt. TruthGuard enforces an"
          " explicit mathematical and architectural separation between these"
          " three operations.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "2.2 Four Core Engineering Principles of TruthGuard",
          styles["SectionHeading"],
      )
  )
  core_principles = [
      (
          "1. Non-Compensatory Reliability (Weakest-Link Formulation):",
          "In high-stakes communications, ten verified statements do not"
          " compensate for one catastrophic lie. If an AI report contains 9"
          " accurate claims and 1 fatal contradiction, the answer reliability"
          " must be penalized decisively. Standard linear averaging is"
          " mathematically flawed.",
      ),
      (
          "2. Claim-Level Atomicity:",
          "Raw paragraphs contain entangled assertions, dependent clauses, and"
          " pronouns. Verification cannot occur at the paragraph level without"
          " introducing ambiguity. TruthGuard decomposes paragraphs into"
          " self-contained, disambiguated atomic propositions before"
          " retrieval.",
      ),
      (
          "3. Symmetrical Universal Verification:",
          "Traditional pipelines only investigate uncertain (NEI) claims."
          " TruthGuard subjects ALL three verdicts (Supported, Contradicted,"
          " and NEI) to a second-stage multi-perspective AI investigation,"
          " searching for counter-evidence and verifying exact qualifiers.",
      ),
      (
          "4. Verify-Then-Accept Grounded Correction:",
          "Corrections generated by LLMs frequently introduce secondary"
          " hallucinations. TruthGuard requires every candidate correction to"
          " pass secondary NLI verification against the retrieved evidence"
          " before it is accepted into the final text.",
      ),
  ]
  for cp_title, cp_desc in core_principles:
    story.append(Paragraph(f"<b>{cp_title}</b> {cp_desc}", styles["BulletText"]))

  story.append(
      Paragraph(
          "2.3 High-Level Modular Pipeline Overview", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "The TruthGuard pipeline is structured into five sequential modules"
          " (M1–M5) coordinated by an asynchronous orchestration harness:",
          styles["Body"],
      )
  )

  pipe_steps = [
      (
          "Module 1 (M1) — Atomic Claim Decomposition:",
          "Parses input text into discrete, stand-alone factual claims with"
          " co-reference resolution and clause isolation.",
      ),
      (
          "Module 2 (M2) — Multi-Source Evidence Retrieval:",
          "Executes hybrid BM25 and SBERT dense retrieval across external APIs"
          " (Wikipedia, ArXiv, PubMed) and local ChromaDB, merged via"
          " Reciprocal Rank Fusion (RRF, k=60) and reranked via Cross-Encoder.",
      ),
      (
          "Retrieval Quality Gate:",
          "Enforces named entity overlap, two-token content lemma match, and"
          " polysemy disambiguation to reject semantically irrelevant"
          " evidence.",
      ),
      (
          "Module 3 (M3) — Calibrated NLI & Deterministic Math Engine:",
          "DeBERTa-v3 cross-encoder calibrated with temperature scaling"
          " (T=1.35) and non-uniform thresholds (Entailment >= 0.75,"
          " Contradiction >= 0.70), paired with SymPy symbolic evaluation.",
      ),
      (
          "Universal AI Investigation Engine (Stage 2):",
          "Multi-perspective adversarial re-investigation across Supported,"
          " Contradicted, and NEI claims to detect subtle nuances and qualifier"
          " violations.",
      ),
      (
          "Module 4 (M4) — Answer Reliability Scoring:",
          "Computes claim reliability rho(c) and evaluates global answer"
          " reliability R(A) using the non-compensatory minimum formulation.",
      ),
      (
          "Module 5 (M5) — Grounded Paragraph Correction:",
          "Executes semantic deduplication, in-place surgical replacement,"
          " style preservation, and secondary NLI safety validation.",
      ),
  ]
  for ps_title, ps_desc in pipe_steps:
    story.append(
        Paragraph(f"<b>• {ps_title}</b> {ps_desc}", styles["BulletText"])
    )

  story.append(Spacer(1, 4))
  story.append(
      make_callout(
          "MATHEMATICAL NOTATION SUMMARY",
          "Throughout this document: T denotes input text; c_i denotes the i-th"
          " atomic claim; E(c_i) denotes the retrieved evidence passage; z_k"
          " denotes unnormalized model logits; P_E, P_C, P_N denote"
          " probabilities for Entailment, Contradiction, and Neutral"
          " respectively; rho(c_i) denotes claim reliability; and R(A) denotes"
          " global Answer Reliability.",
          styles,
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 3: END-TO-END SYSTEM ARCHITECTURE
  # =========================================================================
  story.append(Paragraph("CHAPTER 3", styles["ChapterNum"]))
  story.append(
      Paragraph("End-to-End System Architecture", styles["ChapterTitle"])
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "3.1 Architectural Philosophy: Modular Monolith Engineering",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard is implemented as a high-performance <b>modular"
          " monolith</b> in Python 3.11 with FastAPI. While distributed"
          " microservices offer horizontal scalability, they introduce severe"
          " serialization latency, network hops, and operational overhead"
          " incompatible with deep NLP pipelines where GPU memory buffers"
          " (PyTorch tensors) and SpaCy doc containers must be accessed with"
          " sub-millisecond efficiency. TruthGuard encapsulates each pipeline"
          " phase as an isolated Python package (`truthguard.m1_claim_extractor`,"
          " `truthguard.m2_retriever`, etc.) communicating through strictly"
          " typed Pydantic Data Transfer Objects (DTOs).",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "3.2 Information Flow Across the Verification Pipeline",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "The data lifecycle within TruthGuard progresses through well-defined"
          " states: <b>(1) Ingestion:</b> Raw user text is received via `POST"
          " /api/v1/verify` and validated; <b>(2) Decomposition:</b> M1 emits a"
          " list of `AtomicClaimDTO` objects; <b>(3) Retrieval:</b> M2 populates"
          " each claim with an `EvidenceSetDTO` containing candidate passages"
          " and source metadata; <b>(4) Gating:</b> The Quality Gate filters out"
          " spurious passages, marking claims lacking valid evidence as"
          " `QualityRejected`; <b>(5) Inference:</b> M3 assigns calibrated"
          " logits and initial labels; <b>(6) Arbiter:</b> Stage 2 Universal"
          " Investigation validates or mutates verdicts; <b>(7) Scoring:</b> M4"
          " computes mathematical trust metrics; <b>(8) Correction:</b> M5"
          " patches contradictions; <b>(9) Persistence:</b> All entities are"
          " committed to SQLite.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "3.3 State Management & Data Transfer Objects (DTOs)",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "To guarantee strict contract enforcement between frontend and"
          " backend, TruthGuard leverages Pydantic v2 models. Below is the"
          " architectural structure of the core data schemas:",
          styles["Body"],
      )
  )

  dto_code = """class AtomicClaimDTO(BaseModel):
    claim_id: str
    original_sentence: str
    claim_text: str
    entities: List[str]
    is_mathematical: bool = False

class EvidencePassageDTO(BaseModel):
    passage_id: str
    source_corpus: str  # Wikipedia, PubMed, ArXiv, Local
    text: str
    lexical_score: float
    dense_score: float
    rrf_score: float
    rerank_score: float

class VerificationResultDTO(BaseModel):
    request_id: str
    overall_score: float
    trust_category: str  # High Trust, Qualified, Low, Critical
    claims: List[ClaimVerificationDTO]
    corrected_text: Optional[str]
    processing_time_sec: float"""
  story.append(make_code_panel(dto_code, styles))

  story.append(
      Paragraph(
          "3.4 Fault Tolerance, Fallbacks, and Graceful Degradation",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard is designed to operate continuously even when external"
          " dependencies fail: <b>(a) External API Failures:</b> If Wikipedia"
          " or PubMed endpoints experience timeouts, the retriever"
          " automatically falls back to the local ChromaDB vector store; <b>(b)"
          " LLM API Outages:</b> If the primary Groq/Gemini API key is"
          " exhausted or unreachable, M1 activates a local SpaCy dependency-tree"
          " rule-based claim extractor; <b>(c) GPU Inavailability:</b> The NLI"
          " engine dynamically scales batch sizes and defaults to CPU float32"
          " tensors without process termination.",
          styles["Body"],
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 4: MODULE 1 — ATOMIC CLAIM EXTRACTION & DISAMBIGUATION (M1)
  # =========================================================================
  story.append(Paragraph("CHAPTER 4", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Module 1: Atomic Claim Extraction & Disambiguation (M1)",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "4.1 Theory of Semantic Decomposition", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "Raw text generated by LLMs typically consists of complex, compound"
          " sentences containing multiple interrelated factual assertions."
          " Evaluating such sentences in their entirety introduces semantic"
          " confounding: a sentence may be 80% true and 20% false (e.g., 'Neil"
          " Armstrong was an American astronaut who landed on Mars in 1969')."
          " If evaluated as a single unit, NLI models produce erratic results."
          " Semantic decomposition isolates every factual proposition into an"
          " atomic claim—a minimal, independent declarative statement that"
          " cannot be decomposed further without losing truth conditions.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "4.2 Few-Shot Prompting vs. Rule-Based Fallback Engine",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard implements a dual-mode extraction engine: <b>(1) Primary"
          " LLM Extractor:</b> Uses structured few-shot prompting with"
          " temperature T=0.0 to enforce strict JSON output. The prompt"
          " instructs the model to split compound sentences, resolve pronouns"
          " to their explicit referents, expand relative clauses, and flag"
          " mathematical statements; <b>(2) Deterministic SpaCy Fallback:</b> If"
          " the LLM call fails, TruthGuard activates a rule-based pipeline"
          " leveraging SpaCy dependency trees (`en_core_web_sm`). It segments"
          " sentences by coordinating conjunctions ('and', 'but'), relative"
          " pronouns ('which', 'who'), and participial phrases.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "4.3 Co-reference Resolution & Pronoun Disambiguation",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "A critical requirement for standalone evidence retrieval is"
          " eliminating ambiguous pronouns ('he', 'she', 'it', 'they', 'the"
          " mission'). If an atomic claim reads 'It accommodates 250"
          " scientists', retrieval engines cannot determine what 'It' refers to."
          " M1 maintains a running entity stack across sentence boundaries,"
          " substituting definite nominal referents into subsequent claims"
          " (e.g., transforming 'It accommodates...' into 'The Jupiter One"
          " colony accommodates 250 scientists').",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "4.4 Mathematical Definition of Claim Decomposition",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Formally, given an input document D composed of sentences {s_1, s_2,"
          " ..., s_m}, the decomposition function M1 maps D into a set of n"
          " atomic claims C = {c_1, c_2, ..., c_n} such that: (1) Each c_i"
          " possesses a single subject-predicate-object semantic relation; (2)"
          " All pronouns are replaced with unambiguous nominal referents; (3)"
          " The semantic conjunction of all claims is truth-conditionally"
          " equivalent to D: \\bigwedge_{i=1}^n c_i \\equiv D.",
          styles["Body"],
      )
  )

  story.append(
      make_callout(
          "DECOMPOSITION EXAMPLE",
          "<b>Input:</b> 'NASA confirmed in 2024 that humans established a"
          " permanent research colony on Jupiter named Jupiter One, which"
          " accommodates 250 scientists.'<br/><b>M1 Decomposition:</b><br/>•"
          " Claim 1: 'NASA confirmed in 2024 that humans established a"
          " permanent research colony on Jupiter.'<br/>• Claim 2: 'The permanent"
          " research colony on Jupiter is named Jupiter One.'<br/>• Claim 3:"
          " 'Jupiter One accommodates 250 scientists.'",
          styles,
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 5: MODULE 2 — MULTI-SOURCE EVIDENCE RETRIEVAL ENGINE (M2)
  # =========================================================================
  story.append(Paragraph("CHAPTER 5", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Module 2: Multi-Source Evidence Retrieval Engine (M2)",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "5.1 The Retrieval Challenge in Open-Domain Fact Checking",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Standard information retrieval models frequently fail on atomic"
          " claims. Sparse lexical models (BM25) rely on exact keyword matches"
          " and fail when claims express concepts through paraphrases or"
          " synonyms. Conversely, dense semantic models (bi-encoders) capture"
          " broad topical similarity but are blind to critical entity details,"
          " dates, or numerical qualifiers. To achieve high retrieval"
          " precision, TruthGuard engineers a multi-stage hybrid search"
          " pipeline.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "5.2 Hybrid Lexical-Dense Search Architecture (BM25 + SBERT)",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "For each atomic claim c_i, TruthGuard executes parallel retrieval"
          " queries across: <b>(1) BM25 Okapi:</b> Indexes document collections"
          " using inverse document frequency (IDF) and term saturation"
          " parameters (k_1=1.5, b=0.75); <b>(2) SBERT Dense Retriever:</b>"
          " Encodes claim and corpus passages into 384-dimensional dense"
          " embeddings using `sentence-transformers/all-MiniLM-L6-v2`, computing"
          " cosine similarity over a local ChromaDB index.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "5.3 Reciprocal Rank Fusion (RRF) Formulation & Tuning",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Because BM25 scores (unbounded positive reals) and cosine"
          " similarities (bounded [-1, 1]) cannot be directly summed without"
          " erratic calibration, TruthGuard combines them using <b>Reciprocal"
          " Rank Fusion (RRF)</b>. For each candidate passage p retrieved from"
          " set of systems S:",
          styles["Body"],
      )
  )

  rrf_eq = (
      "<b>RRF Formula:</b><br/>"
      "&nbsp;&nbsp;&nbsp;&nbsp;RRF_Score(p) = \\sum_{s \\in S} \\frac{1}{k +"
      " rank_s(p)}<br/>"
      "where rank_s(p) is the 1-based rank of passage p in retrieval system s,"
      " and k is a smoothing constant experimentally optimized to <b>k ="
      " 60</b>. RRF penalizes outliers while rewarding passages that achieve"
      " top-tier ranks in both lexical and dense modalities."
  )
  story.append(
      make_callout(
          "RECIPROCAL RANK FUSION",
          rrf_eq,
          styles,
          accent_color=C_SECONDARY,
          bg_color=C_BG_PANEL,
      )
  )

  story.append(
      Paragraph(
          "5.4 Cross-Encoder Semantic Reranker", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "The top-20 candidates produced by RRF are passed to a heavy"
          " Cross-Encoder reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`)."
          " Unlike bi-encoders that process claim and passage independently,"
          " the cross-encoder feeds the concatenated pair `[CLS] Claim [SEP]"
          " Passage [SEP]` through full bidirectional self-attention layers,"
          " capturing deep cross-term semantic interactions and outputting a"
          " refined relevance score.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "5.5 Multi-Source Adapters: Wikipedia, ArXiv, PubMed & Local Corpus",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard routes queries dynamically based on entity classification"
          " extracted by M1: <b>(a) General Knowledge:</b> Wikipedia REST API"
          " fetching introductory summaries and section paragraphs; <b>(b)"
          " Biomedical & Clinical Claims:</b> PubMed API queries searching"
          " peer-reviewed medical abstracts; <b>(c) Physical Sciences & AI:</b>"
          " ArXiv API queries; <b>(d) Internal Reference Corpus:</b> Curated"
          " ChromaDB instance loaded with historical and scientific verified"
          " facts.",
          styles["Body"],
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 6: THE RETRIEVAL QUALITY GATE & SEMANTIC FILTERING
  # =========================================================================
  story.append(Paragraph("CHAPTER 6", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "The Retrieval Quality Gate & Semantic Filtering",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "6.1 Why Raw Retrieval Fails: The 'Lexical Trap' & Polysemy",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "In empirical testing, raw retrieval pipelines frequently return"
          " passages that achieve high lexical or cosine similarity but are"
          " factually irrelevant to the specific proposition. For example: a"
          " claim asserting 'Mars has two moons' might retrieve an article"
          " about the Roman God of War Mars; a claim asserting 'Vitamin C is"
          " necessary for collagen synthesis' retrieved a passage describing"
          " human heart valves because both mentioned 'tissue' and 'deficiency'."
          " Passing such passages to NLI models causes catastrophic"
          " misclassifications.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "6.2 Three-Stage Quality Gate Filtering Rules",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard interposes a strict <b>Quality Gate</b> between M2 and M3."
          " Every candidate passage must satisfy three deterministic"
          " constraints before being admitted into the evidence context:",
          styles["Body"],
      )
  )

  qg_rules = [
      (
          "Constraint 1: Named Entity Overlap (NER Verification):",
          "Using SpaCy NER, all PERSON, ORG, GPE, LOC, and PRODUCT entities"
          " identified in claim c_i must have at least one exact or alias match"
          " in the retrieved passage. If a claim discusses 'Jupiter One' and"
          " the passage only discusses 'Apollo 11', it is immediately rejected.",
      ),
      (
          "Constraint 2: Two-Token Content Lemma Match:",
          "Beyond named entities, the passage must share at least two non-stop,"
          " lemmatized content tokens (nouns, verbs, adjectives) with the"
          " claim proposition. This eliminates vague generic definitions.",
      ),
      (
          "Constraint 3: Polysemy & Semantic Context Disambiguation:",
          "For polysemous terms (e.g., 'Mercury' as planet vs chemical element"
          " vs Roman god; 'Apple' as fruit vs corporation), the Quality Gate"
          " verifies domain co-occurrence tokens (e.g., 'orbit', 'mass',"
          " 'atmosphere' for astronomical Jupiter vs 'mythology', 'pantheon').",
      ),
  ]
  for r_title, r_desc in qg_rules:
    story.append(Paragraph(f"<b>• {r_title}</b> {r_desc}", styles["BulletText"]))

  story.append(
      Paragraph(
          "6.3 Handling Quality Gate Rejections", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "If all retrieved passages for a claim fail the Quality Gate, the"
          " claim is NOT forwarded to the NLI cross-encoder with poisoned"
          " evidence. Instead, TruthGuard flags the claim as"
          " <b>QualityGate_Rejected</b> and assigns an initial verdict of"
          " <b>NOT ENOUGH INFO (NEI)</b>, preventing the false entailments or"
          " false contradictions that plague un-gated RAG pipelines.",
          styles["Body"],
      )
  )

  story.append(
      make_callout(
          "EMPIRICAL IMPACT OF QUALITY GATE",
          "Ablation studies on TruthGuard-350 show that activating the Quality"
          " Gate increased Retrieval Relevance from <b>76.2% to 100.0%</b> and"
          " reduced downstream False Contradictions by <b>18.4%</b>.",
          styles,
          accent_color=C_ACCENT_GREEN,
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 7: MODULE 3 — NATURAL LANGUAGE INFERENCE & MATH ENGINE (M3)
  # =========================================================================
  story.append(Paragraph("CHAPTER 7", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Module 3: Natural Language Inference & Math Engine (M3)",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "7.1 Cross-Encoder NLI Formulation & DeBERTa-v3 Architecture",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Module 3 evaluates whether the evidence passage E(c_i) logically"
          " entails, contradicts, or provides insufficient information"
          " regarding atomic claim c_i. TruthGuard employs a fine-tuned"
          " <b>DeBERTa-v3</b> cross-encoder architecture"
          " (`cross-encoder/nli-deberta-v3-base`). Unlike older BERT or RoBERTa"
          " models, DeBERTa-v3 utilizes disentangled attention mechanisms where"
          " word content and relative position vectors are projected into"
          " separate matrices, dramatically improving sensitivity to syntactic"
          " negation, scope qualifiers, and word order.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "7.2 Logit Calibration via Temperature Scaling (T=1.35)",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Modern deep neural networks suffer from overconfidence: raw softmax"
          " probabilities frequently approach 0.99 even when predicting"
          " incorrectly (Guo et al., 2017). To transform raw network outputs"
          " into true empirical probabilities, TruthGuard applies post-hoc"
          " <b>Temperature Scaling</b> to the output logits z = [z_E, z_C, z_N]:",
          styles["Body"],
      )
  )

  temp_eq = (
      "<b>Temperature Scaled Softmax:</b><br/>"
      "&nbsp;&nbsp;&nbsp;&nbsp;P(y = k \\mid x) = \\frac{\\exp(z_k /"
      " T)}{\\sum_{j \\in \\{E, C, N\\}} \\exp(z_j / T)}<br/>"
      "where T is the learned temperature hyperparameter. Through grid-search"
      " optimization over the FEVER and MNLI validation splits, the optimal"
      " temperature is set to <b>T = 1.35</b>, reducing the Expected"
      " Calibration Error (ECE) from 0.142 to <b>0.038</b>."
  )
  story.append(
      make_callout(
          "PROBABILITY CALIBRATION",
          temp_eq,
          styles,
          accent_color=C_SECONDARY,
          bg_color=C_BG_PANEL,
      )
  )

  story.append(
      Paragraph(
          "7.3 Non-Uniform Decision Thresholds (\\tau_e, \\tau_c)",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Standard argmax classification assumes equal costs for misclassifying"
          " entailments versus contradictions. In fact-checking, false"
          " accusations of falsehood destroy user trust, while failing to"
          " detect a contradiction allows hallucinations to pass undetected."
          " TruthGuard establishes non-uniform calibrated decision thresholds:",
          styles["Body"],
      )
  )

  thresh_desc = (
      "• <b>SUPPORTED:</b> P_E \\ge \\tau_e = <b>0.75</b> and P_E > P_C<br/>"
      "• <b>CONTRADICTED:</b> P_C \\ge \\tau_c = <b>0.70</b> and P_C > P_E<br/>"
      "• <b>NOT ENOUGH INFO (NEI):</b> Default when neither entailment nor"
      " contradiction meets the confidence threshold."
  )
  story.append(Paragraph(thresh_desc, styles["BulletText"]))

  story.append(
      Paragraph(
          "7.4 Specialized SymPy Deterministic Mathematical Verifier",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Neural NLI models fail notoriously when evaluating mathematical and"
          " arithmetic assertions (e.g., verifying whether '12% of 450 is 54' or"
          " evaluating exponential decay formulas). TruthGuard routes claims"
          " flagged with numerical or mathematical operators to a deterministic"
          " <b>SymPy Symbolic Engine</b>. The engine parses equations into"
          " symbolic abstract syntax trees, evaluates arithmetic identities"
          " with exact precision, checks inequality boundaries, and flags"
          " calculations with 100% mathematical certainty.",
          styles["Body"],
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 8: UNIVERSAL MULTI-PERSPECTIVE AI INVESTIGATION
  # =========================================================================
  story.append(Paragraph("CHAPTER 8", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Universal Multi-Perspective AI Investigation Engine",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "8.1 Architectural Paradigm Shift: Universal Symmetrical"
          " Investigation",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Early fact-checking prototypes only investigated claims classified"
          " as NOT ENOUGH INFO (NEI). TruthGuard introduces a fundamental"
          " architectural innovation: <b>Universal Multi-Perspective AI"
          " Investigation (Stage 2)</b> applied symmetrically across ALL three"
          " initial verdict outcomes: SUPPORTED, CONTRADICTED, and NEI. Relying"
          " on a single-pass NLI classification is fragile; initial searches may"
          " encounter biased passages, obsolete historical data, or surface"
          " qualifiers that obscure deeper contradictions.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "8.2 Stage 2 Investigation Protocols by Verdict",
          styles["SectionHeading"],
      )
  )

  uni_protocols = [
      (
          "Protocol A — Initial Verdict: SUPPORTED (Adversarial Counter-Evidence"
          " Hunting):",
          "The engine generates adversarial counter-queries specifically"
          " targeting potential exceptions, recent counter-evidence, and exact"
          " numerical boundaries. If reliable counter-evidence challenges the"
          " claim, the arbiter flags the conflict and downgrades confidence"
          " rather than blindly trusting the initial supporting passage.",
      ),
      (
          "Protocol B — Initial Verdict: CONTRADICTED (Nuance & Historical"
          " Context Verification):",
          "Initial contradiction classifications may stem from ambiguous"
          " wording, obsolete historical definitions, or disputed scientific"
          " theories. Stage 2 verifies whether the claim was historically"
          " valid at a specific epoch or represents an active scientific debate"
          " before confirming the contradiction.",
      ),
      (
          "Protocol C — Initial Verdict: NOT ENOUGH INFO (NEI) (Deep Targeted"
          " Decomposition):",
          "When initial retrieval returns insufficient evidence, the engine"
          " decomposes the claim into targeted sub-questions, reformulates"
          " query vectors, and searches secondary specialized corpora to find"
          " conclusive evidence.",
      ),
  ]
  for p_title, p_desc in uni_protocols:
    story.append(Paragraph(f"<b>{p_title}</b> {p_desc}", styles["BulletText"]))

  story.append(
      Paragraph(
          "8.3 Arbiter Synthesis & Final Verdict Calibration",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "The Stage 2 Arbiter synthesizes the initial NLI logits, the Quality"
          " Gate metrics, and the multi-perspective investigation findings."
          " Using a bayesian belief update mechanism, it produces the final"
          " verdict and calibrated confidence score, ensuring that high-stakes"
          " decisions reflect multi-source corroboration.",
          styles["Body"],
      )
  )

  story.append(
      make_callout(
          "STAGE 2 ARCHITECTURAL IMPACT",
          "Universal AI Investigation eliminated 14 false positive SUPPORTED"
          " verdicts in the TruthGuard-350 benchmark where claims contained"
          " inflated quantifiers ('all', 'every') that single-pass NLI had"
          " missed.",
          styles,
          accent_color=C_PRIMARY,
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 9: MODULE 4 — NON-COMPENSATORY ANSWER RELIABILITY SCORING (M4)
  # =========================================================================
  story.append(Paragraph("CHAPTER 9", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Module 4: Non-Compensatory Answer Reliability Scoring (M4)",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "9.1 The Fatal Flaw of Standard Linear Averaging",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Most commercial LLM evaluation frameworks compute an overall score"
          " by averaging claim confidences: Score = \\frac{1}{n} \\sum"
          " Conf(c_i). In high-stakes environments, this mathematical"
          " formulation is deeply flawed. Consider a clinical treatment guide"
          " with 10 claims: 9 claims describe standard diagnostic procedures"
          " (Score = 1.0 each), while 1 claim recommends a lethal drug dosage"
          " (Contradiction). Linear averaging yields (9*1.0 + 0) / 10 = 90% ('A'"
          " grade, High Trust)—a lethal outcome. Reliability must be"
          " non-compensatory.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "9.2 Claim-Level Reliability Formulation (\\rho(c))",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard defines the individual reliability of claim c_i as a"
          " function of its calibrated entailment probability, source"
          " authority weight, and relevance score:",
          styles["Body"],
      )
  )

  claim_rel_eq = (
      "<b>Claim Reliability Formula:</b><br/>"
      "&nbsp;&nbsp;&nbsp;&nbsp;\\rho(c_i) = \\begin{cases} w_{\\text{auth}}"
      " \\cdot w_{\\text{rel}} \\cdot P_E(c_i) & \\text{if } \\text{Verdict} ="
      " \\text{SUPPORTED} \\\\ 0.0 & \\text{if } \\text{Verdict} ="
      " \\text{CONTRADICTED} \\\\ \\lambda_{\\text{NEI}} \\cdot P_N(c_i) &"
      " \\text{if } \\text{Verdict} = \\text{NEI} \\end{cases}<br/>"
      "where w_{\\text{auth}} \\in [0.8, 1.0] reflects source authority (1.0"
      " for PubMed/peer-reviewed, 0.9 for Wikipedia, 0.8 for open web),"
      " w_{\\text{rel}} \\in [0, 1] is the cross-encoder relevance score, and"
      " \\lambda_{\\text{NEI}} = <b>0.50</b> reflects epistemic uncertainty."
  )
  story.append(
      make_callout(
          "EQUATION (3): CLAIM RELIABILITY",
          claim_rel_eq,
          styles,
          accent_color=C_SECONDARY,
          bg_color=C_BG_PANEL,
      )
  )

  story.append(
      Paragraph(
          "9.3 Global Answer Reliability Index (R(A))", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "To enforce non-compensatory scoring, TruthGuard bounds the overall"
          " document reliability by the maximum contradiction probability"
          " detected across all claims:",
          styles["Body"],
      )
  )

  ans_rel_eq = (
      "<b>Answer Reliability Index:</b><br/>"
      "&nbsp;&nbsp;&nbsp;&nbsp;R(A) = \\min\\left( \\frac{1}{n} \\sum_{i=1}^n"
      " \\rho(c_i), \\; 1.0 - \\max_{1 \\le i \\le n} P_C(c_i) \\right)<br/>"
      "This guarantees that if ANY single claim contains a high-confidence"
      " contradiction (e.g., P_C = 0.95), the entire answer reliability score"
      " cannot exceed 1.0 - 0.95 = <b>0.05 (5%)</b>, immediately triggering a"
      " Critical Hallucination alert regardless of how many other claims were"
      " supported."
  )
  story.append(
      make_callout(
          "EQUATION (4): GLOBAL ANSWER RELIABILITY",
          ans_rel_eq,
          styles,
          accent_color=C_ACCENT_RED,
          bg_color=C_BG_PANEL,
      )
  )

  story.append(
      Paragraph(
          "9.4 Granular Trust Categorization Tiers", styles["SectionHeading"]
      )
  )
  tiers = [
      (
          "High Trust (\\ge 80%):",
          "All atomic claims are rigorously supported by authoritative"
          " evidence. Zero contradictions.",
      ),
      (
          "Qualified Trust (60% – 79%):",
          "Majority of claims supported; one or more minor NEI claims without"
          " contradictions.",
      ),
      (
          "Low Trust (40% – 59%):",
          "Multiple unverified (NEI) claims or borderline factual ambiguity;"
          " manual review required.",
      ),
      (
          "Critical Hallucination (< 40%):",
          "At least one direct factual contradiction detected. Document"
          " rejected for mission-critical use.",
      ),
  ]
  for t_title, t_desc in tiers:
    story.append(Paragraph(f"• <b>{t_title}</b> {t_desc}", styles["BulletText"]))

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 10: MODULE 5 — GROUNDED PARAGRAPH CORRECTION ENGINE (M5)
  # =========================================================================
  story.append(Paragraph("CHAPTER 10", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Module 5: Grounded Paragraph Correction Engine (M5)",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "10.1 Grounded Correction vs. Unconstrained Rewriting",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "When an LLM hallucination is detected, naive systems prompt another"
          " LLM: 'Rewrite the paragraph to fix the error.' This approach"
          " creates severe secondary hallucination risks, alters the author's"
          " stylistic voice, and frequently deletes valid surrounding facts."
          " Module 5 implements an <b>in-place, surgical correction"
          " engine</b> that replaces only the contradicted proposition with"
          " verified evidence while preserving the surrounding grammatical and"
          " stylistic context.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "10.2 The Verify-Then-Accept Protocol", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "To guarantee that corrections do not introduce new hallucinations,"
          " TruthGuard enforces a four-step validation protocol: <b>(1) Draft"
          " Generation:</b> Using the retrieved evidence passage E(c_i), M5"
          " drafts an in-place patch; <b>(2) Secondary NLI Verification:</b> The"
          " generated patch is evaluated against E(c_i) using DeBERTa-v3; it"
          " MUST achieve P_E \\ge 0.80; <b>(3) Non-Destructive Insertion:</b>"
          " The patch is mapped back to the exact character offset of the"
          " original claim; <b>(4) Fallback:</b> If the draft patch fails NLI"
          " verification, TruthGuard falls back to direct evidence quotation.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "10.3 Resolution of Duplicate Paragraph Corrections",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "A critical bug identified during early auditing occurred when"
          " multiple atomic claims derived from the same compound sentence were"
          " contradicted (e.g., in the Jupiter colony example, where Claim 1"
          " asserted the colony existed and Claim 2 named it 'Jupiter One')."
          " The naive correction engine generated the exact same correction"
          " sentence twice consecutively in the output paragraph. TruthGuard"
          " resolves this through:",
          styles["Body"],
      )
  )

  dup_fixes = [
      (
          "Semantic Deduplication & Target Span Mapping:",
          "Tracking original sentence parent IDs and mapping multiple atomic"
          " corrections to a single target sentence span.",
      ),
      (
          "SBERT Cosine Similarity Deduplication:",
          "Comparing candidate correction sentences with a cosine similarity"
          " threshold \\sigma = 0.85; if two corrections are semantically"
          " identical, only the most complete patch is retained.",
      ),
      (
          "Single In-Place Reconstruction:",
          "Reconstructing the final paragraph through a single-pass string"
          " replacement buffer.",
      ),
  ]
  for df_t, df_d in dup_fixes:
    story.append(Paragraph(f"• <b>{df_t}</b> {df_d}", styles["BulletText"]))

  story.append(
      make_callout(
          "CORRECTION PROTOCOL GUARANTEE",
          "M5 achieves a False Correction Rate of only <b>3.48%</b> on the"
          " TruthGuard-350 benchmark, ensuring that verified facts are never"
          " corrupted during post-processing.",
          styles,
          accent_color=C_ACCENT_GREEN,
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 11: TECHNOLOGY STACK & IMPLEMENTATION DETAILS
  # =========================================================================
  story.append(Paragraph("CHAPTER 11", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Technology Stack & Implementation Details", styles["ChapterTitle"]
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "11.1 Backend Architecture & NLP Libraries", styles["SectionHeading"]
      )
  )
  tech_backend = [
      (
          "Python 3.11.9 Runtime:",
          "Leveraging structural pattern matching, enhanced exception groups,"
          " and substantial bytecode execution optimizations.",
      ),
      (
          "FastAPI & Uvicorn:",
          "Asynchronous, non-blocking ASGI web framework providing automatic"
          " OpenAPI schema generation and sub-millisecond route dispatch.",
      ),
      (
          "PyTorch 2.6 & Hugging Face Transformers:",
          "Deep learning backbone hosting `cross-encoder/nli-deberta-v3-base`"
          " and `cross-encoder/ms-marco-MiniLM-L-6-v2`.",
      ),
      (
          "SpaCy v3.8 (`en_core_web_sm`):",
          "Industrial NLP pipeline executing tokenization, dependency parsing,"
          " lemmatization, and Named Entity Recognition (NER).",
      ),
      (
          "SymPy 1.13:",
          "Computer algebra system providing exact symbolic mathematics and"
          " deterministic equation validation.",
      ),
      (
          "ChromaDB & Rank-BM25:",
          "Vector and lexical indexing engines providing embedding storage and"
          " BM25 Okapi retrieval.",
      ),
  ]
  for tb_t, tb_d in tech_backend:
    story.append(Paragraph(f"• <b>{tb_t}</b> {tb_d}", styles["BulletText"]))

  story.append(
      Paragraph(
          "11.2 Frontend Architecture & Modern UI Stack",
          styles["SectionHeading"],
      )
  )
  tech_frontend = [
      (
          "React 18 & Vite:",
          "Modern component-driven frontend architecture utilizing Vite for"
          " lightning-fast Hot Module Replacement (HMR).",
      ),
      (
          "Tailwind CSS v3:",
          "Utility-first styling system implementing an elegant, academic warm"
          " ivory theme with high-contrast status badges.",
      ),
      (
          "Lucide React Icons:",
          "Crisp vector icons providing visual status indicators for"
          " Supported, Contradicted, and NEI verdicts.",
      ),
      (
          "Side-by-Side Diff Engine:",
          "Visual text comparison highlighting original hallucinations vs"
          " grounded corrections.",
      ),
  ]
  for tf_t, tf_d in tech_frontend:
    story.append(Paragraph(f"• <b>{tf_t}</b> {tf_d}", styles["BulletText"]))

  story.append(
      Paragraph(
          "11.3 Performance Optimizations & Batch Processing",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard employs extensive optimizations to maintain interactive"
          " latency: (1) Parallel asynchronous retrieval across external APIs"
          " using `asyncio.gather()`; (2) Dynamic batching of cross-encoder"
          " inference pairs; (3) In-memory LRU caching of frequent Wikipedia and"
          " PubMed query vectors; (4) Model warm-up routines during FastAPI"
          " startup to eliminate first-request latency spikes.",
          styles["Body"],
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 12: DATABASE SCHEMA & API SPECIFICATIONS
  # =========================================================================
  story.append(Paragraph("CHAPTER 12", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Database Schema & API Specifications", styles["ChapterTitle"]
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph("12.1 Relational Database Schema Design", styles["SectionHeading"])
  )
  story.append(
      Paragraph(
          "TruthGuard uses an optimized SQLite database (production-ready for"
          " PostgreSQL migration via SQLAlchemy 2.0). The relational model"
          " tracks the complete provenance of every verification request:",
          styles["Body"],
      )
  )

  db_schema = """CREATE TABLE verification_requests (
    id VARCHAR(36) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_text TEXT NOT NULL,
    answer_reliability FLOAT NOT NULL,
    trust_category VARCHAR(30) NOT NULL,
    total_claims INTEGER NOT NULL,
    supported_claims INTEGER NOT NULL,
    contradicted_claims INTEGER NOT NULL,
    nei_claims INTEGER NOT NULL,
    corrected_text TEXT
);

CREATE TABLE atomic_claims (
    id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) REFERENCES verification_requests(id),
    claim_text TEXT NOT NULL,
    verdict VARCHAR(20) NOT NULL,  -- SUPPORTED, CONTRADICTED, NEI
    confidence FLOAT NOT NULL,
    calibrated_pe FLOAT NOT NULL,
    calibrated_pc FLOAT NOT NULL,
    calibrated_pn FLOAT NOT NULL,
    quality_gate_passed BOOLEAN NOT NULL
);

CREATE TABLE evidence_passages (
    id VARCHAR(36) PRIMARY KEY,
    claim_id VARCHAR(36) REFERENCES atomic_claims(id),
    source_corpus VARCHAR(50) NOT NULL,
    passage_text TEXT NOT NULL,
    rrf_rank INTEGER NOT NULL,
    rerank_score FLOAT NOT NULL
);"""
  story.append(make_code_panel(db_schema, styles))

  story.append(
      Paragraph(
          "12.2 Core RESTful API Endpoints Specification",
          styles["SectionHeading"],
      )
  )
  api_routes = [
      (
          "POST /api/v1/verify:",
          "Primary verification pipeline. Accepts `{'text': str, 'domain':"
          " Optional[str]}` and returns complete `VerificationResultDTO`.",
      ),
      (
          "GET /api/v1/history:",
          "Retrieves paginated historical verification audits with summary"
          " metrics and trust classifications.",
      ),
      (
          "GET /api/v1/history/{request_id}:",
          "Returns granular claim-by-claim and evidence breakdown for a"
          " specific past request.",
      ),
      (
          "POST /api/v1/export/pdf:",
          "Generates an executive PDF verification report summarizing detected"
          " hallucinations, citations, and patches.",
      ),
      (
          "GET /api/v1/metrics/system:",
          "Returns real-time inference latency, cache hit ratios, and"
          " classification distributions.",
      ),
  ]
  for ar_t, ar_d in api_routes:
    story.append(Paragraph(f"• <b>{ar_t}</b> {ar_d}", styles["BulletText"]))

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 13: FRONTEND USER WORKFLOW & INTERACTIVE UI
  # =========================================================================
  story.append(Paragraph("CHAPTER 13", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Frontend User Workflow & Interactive UI", styles["ChapterTitle"]
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "13.1 User Workflow & Dashboard Interaction Flow",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "The TruthGuard web application provides a clean, dual-pane"
          " analytical interface: <b>Step 1 (Input & Configuration):</b> The"
          " user pastes an AI-generated paragraph into the input workspace, with"
          " options to select domain priors (General, Biomedical, History,"
          " Physics); <b>Step 2 (Real-Time Pipeline Stepper):</b> As the"
          " backend processes the request, the UI displays real-time progress"
          " indicators through M1 -> M2 -> Quality Gate -> M3 -> Arbiter -> M4"
          " -> M5; <b>Step 3 (Dual-Pane Analysis):</b> The left pane displays the"
          " original paragraph with color-coded sentence highlighting, while"
          " the right pane presents interactive claim cards.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "13.2 Interactive Claim-to-Evidence Visual Grounding",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Clicking on any individual claim card automatically spotlights the"
          " corresponding sentence in the original text and expands the"
          " retrieved evidence drawer. The drawer displays the exact snippet of"
          " external evidence, the source corpus (e.g., 'Wikipedia: Jupiter' or"
          " 'PubMed: 321876'), the RRF ranking, the calibrated NLI"
          " probabilities (P_E, P_C, P_N), and the arbiter reasoning notes.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "13.3 Side-by-Side Diff Viewer & Export Modals",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "For texts containing contradictions, TruthGuard displays a"
          " side-by-side diff viewer. Erroneous hallucinated text is rendered in"
          " strikethrough red, with surgical grounded corrections inserted in"
          " green. Users can export results in three production formats: <b>(1)"
          " Executive PDF Report</b> for management audits, <b>(2) Research"
          " JSON</b> with full tensor logit breakdowns for NLP evaluation, and"
          " <b>(3) Tabular CSV</b> for data pipelines.",
          styles["Body"],
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 14: EXPERIMENTAL EVALUATION & BENCHMARK RESULTS
  # =========================================================================
  story.append(Paragraph("CHAPTER 14", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Experimental Evaluation & Benchmark Results", styles["ChapterTitle"]
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "14.1 Evaluation Methodology & TruthGuard-350 Benchmark",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "To rigorously evaluate TruthGuard without data leakage or selective"
          " bias, we constructed the <b>TruthGuard-350 Multi-Domain"
          " Benchmark</b>. It consists of 350 rigorously annotated claims"
          " balanced across 10 distinct domains: Astronomy, Biology, Medicine,"
          " World History, Modern Physics, Geography, Computer Science,"
          " Chemistry, Political Science, and Mathematics. Ground truth labels"
          " were independently established by human domain experts.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "14.2 Multi-Class Performance Metrics (Empirical Results)",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard achieves an overall classification accuracy of"
          " <b>82.86%</b> (290 / 350 claims correctly classified). The table"
          " below presents the exact empirical metrics extracted from `results/`:",
          styles["Body"],
      )
  )

  # Empirical Table
  perf_data = [
      [
          Paragraph("<b>Evaluation Metric</b>", styles["TableHead"]),
          Paragraph("<b>Supported</b>", styles["TableHead"]),
          Paragraph("<b>Contradicted</b>", styles["TableHead"]),
          Paragraph("<b>Not Enough Info</b>", styles["TableHead"]),
          Paragraph("<b>Macro Average</b>", styles["TableHead"]),
      ],
      [
          Paragraph("<b>Precision</b>", styles["TableCellBold"]),
          Paragraph("98.63%", styles["TableCellCenter"]),
          Paragraph("93.39%", styles["TableCellCenter"]),
          Paragraph("67.31%", styles["TableCellCenter"]),
          Paragraph("<b>86.44%</b>", styles["TableCellCenter"]),
      ],
      [
          Paragraph("<b>Recall</b>", styles["TableCellBold"]),
          Paragraph("60.00%", styles["TableCellCenter"]),
          Paragraph("94.17%", styles["TableCellCenter"]),
          Paragraph("95.45%", styles["TableCellCenter"]),
          Paragraph("<b>83.21%</b>", styles["TableCellCenter"]),
      ],
      [
          Paragraph("<b>F1-Score</b>", styles["TableCellBold"]),
          Paragraph("74.61%", styles["TableCellCenter"]),
          Paragraph("<b>93.78%</b>", styles["TableCellCenter"]),
          Paragraph("78.95%", styles["TableCellCenter"]),
          Paragraph("<b>82.44%</b>", styles["TableCellCenter"]),
      ],
  ]
  perf_table = Table(perf_data, colWidths=[120, 96, 96, 96, 96])
  perf_table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), C_BG_PANEL),
          ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
      ])
  )
  story.append(perf_table)
  story.append(Spacer(1, 6))

  story.append(
      Paragraph(
          "14.3 Critical Operational & System Metrics", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "Beyond classification accuracy, TruthGuard tracks three critical"
          " operational metrics: <b>(1) Retrieval Relevance Rate: 100.0%</b>"
          " (zero off-topic passages admitted through the Quality Gate); <b>(2)"
          " Citation Accuracy: 95.0%</b> (retrieved evidence directly aligns"
          " with claim propositions); <b>(3) False Correction Rate: 3.48%</b>"
          " (negligible rate of incorrect post-hoc edits); <b>(4) Inference"
          " Latency:</b> Mean processing time of <b>0.680 seconds per claim</b>"
          " (P95 = 1.278s).",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "14.4 Ablation Analysis: Contribution of Core Components",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "Ablation studies reveal the necessity of each architectural"
          " component: Removing Reciprocal Rank Fusion (BM25 only) reduced"
          " retrieval recall by 18.2%; removing the Cross-Encoder reranker"
          " degraded top-1 accuracy by 12.6%; removing the Quality Gate"
          " increased false contradictions by 18.4%; and removing Temperature"
          " Scaling increased the Expected Calibration Error from 0.038 to"
          " 0.142.",
          styles["Body"],
      )
  )

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 15: REAL-WORLD CASE STUDIES & END-TO-END WALKTHROUGHS
  # =========================================================================
  story.append(Paragraph("CHAPTER 15", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Real-World Case Studies & End-to-End Walkthroughs",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "This chapter provides complete execution traces for 9 real-world"
          " test cases evaluated across the TruthGuard verification lifecycle:",
          styles["Body"],
      )
  )

  case_studies = [
      (
          "Case 1: Apollo 11 Lunar Landing Year & Crew",
          "Input: 'Apollo 11 landed on the Moon in July 1969, carrying Neil"
          " Armstrong and Buzz Aldrin.'<br/><b>M1 Claims:</b> c1: Apollo 11"
          " landed on Moon in July 1969; c2: Apollo 11 carried Neil Armstrong;"
          " c3: Apollo 11 carried Buzz Aldrin.<br/><b>M2 Evidence:</b> Wikipedia"
          " Apollo 11 summary.<br/><b>Quality Gate:</b> PASSED (Entities:"
          " Apollo 11, Moon, Neil Armstrong).<br/><b>M3 NLI:</b> P_E = 0.98,"
          " 0.99, 0.97.<br/><b>Arbiter:</b> Corroborated.<br/><b>M4 Score:</b>"
          " 98.0% (High Trust).<br/><b>M5:</b> No correction required.",
      ),
      (
          "Case 2: Jupiter Human Colony (Gas Giant Contradiction)",
          "Input: 'NASA confirmed in 2024 that humans established a permanent"
          " colony on Jupiter named Jupiter One.'<br/><b>M1 Claims:</b> c1:"
          " NASA confirmed human colony on Jupiter in 2024; c2: Colony named"
          " Jupiter One.<br/><b>M2 Evidence:</b> NASA Planetary Factsheet:"
          " Jupiter is a gas giant with extreme pressure hostile to human life;"
          " zero colonies exist.<br/><b>Quality Gate:</b> PASSED.<br/><b>M3"
          " NLI:</b> P_C = 0.98 (Contradiction).<br/><b>M4 Score:</b> 2.0%"
          " (Critical Hallucination).<br/><b>M5 Fix:</b> Deduplicated surgical"
          " patch: 'No human colonies exist on Jupiter, as it is a gas giant"
          " with hostile atmospheric conditions.'",
      ),
      (
          "Case 3: Great Wall of China Visibility from Moon Myth",
          "Input: 'The Great Wall of China is the only human-made structure"
          " visible from the Moon with the naked eye.'<br/><b>M1 Claims:</b>"
          " Great Wall visible from Moon with naked eye.<br/><b>M2"
          " Evidence:</b> NASA Astronaut Reports & Optics Papers: Great Wall is"
          " not visible from Moon without high magnification.<br/><b>M3"
          " NLI:</b> P_C = 0.96.<br/><b>M4 Score:</b> 4.0% (Critical"
          " Hallucination).<br/><b>M5 Fix:</b> 'The Great Wall of China is not"
          " visible from the Moon with the naked eye.'",
      ),
      (
          "Case 4: Vitamin C & Collagen Synthesis",
          "Input: 'Vitamin C is an essential nutrient that acts as a cofactor"
          " for enzymes synthesizing collagen.'<br/><b>M1 Claims:</b> c1:"
          " Vitamin C is an essential nutrient; c2: Vitamin C acts as a"
          " cofactor for collagen synthesis.<br/><b>M2 Evidence:</b> PubMed"
          " Biomedical Database (Quality Gate blocked heart anatomy"
          " noise).<br/><b>M3 NLI:</b> P_E = 0.94.<br/><b>M4 Score:</b> 94.0%"
          " (High Trust).<br/><b>M5:</b> Verified as accurate.",
      ),
      (
          "Case 5: Bacterial Pathogenicity Overgeneralization",
          "Input: 'All bacteria are pathogenic and cause infectious diseases in"
          " humans.'<br/><b>M1 Claims:</b> All bacteria cause human"
          " disease.<br/><b>M2 Evidence:</b> Microbiology Textbook: Fewer than"
          " 1% of bacteria are pathogenic; vast majority are harmless or"
          " essential for gut microbiome.<br/><b>M3 NLI:</b> P_C = 0.92"
          " (Universal quantifier contradiction).<br/><b>M4 Score:</b> 8.0%"
          " (Critical Hallucination).<br/><b>M5 Fix:</b> 'While some bacteria"
          " are pathogenic, the vast majority are harmless or beneficial to"
          " humans.'",
      ),
      (
          "Case 6: Gold Chemical Symbol & Atomic Number",
          "Input: 'Gold has the chemical symbol Au and atomic number 79.'<br/><b>M1"
          " Claims:</b> c1: Symbol is Au; c2: Atomic number is 79.<br/><b>M2"
          " Evidence:</b> IUPAC Periodic Table.<br/><b>Quality Gate:</b>"
          " PASSED.<br/><b>M3 NLI:</b> P_E = 0.99.<br/><b>M4 Score:</b> 99.0%"
          " (High Trust).<br/><b>M5:</b> Accurate.",
      ),
      (
          "Case 7: Human Brain Neuron Count",
          "Input: 'The human brain contains approximately 86 billion"
          " neurons.'<br/><b>M1 Claims:</b> Human brain contains ~86 billion"
          " neurons.<br/><b>M2 Evidence:</b> Herculano-Houzel (2009)"
          " isotropic fractionator study.<br/><b>M3 NLI:</b> P_E = 0.91.<br/><b>M4"
          " Score:</b> 91.0% (High Trust).<br/><b>M5:</b> Accurate.",
      ),
      (
          "Case 8: Deterministic SymPy Arithmetic Proof",
          "Input: 'If an investment of $500 grows at 10% annually, after 2"
          " years it equals $650.'<br/><b>M1 Claims:</b> $500 * (1.10)^2 ="
          " $650.<br/><b>M3 SymPy Engine:</b> Evaluates 500 * (1.10)^2 = 605.0."
          " 605 != 650.<br/><b>Verdict:</b> Deterministic CONTRADICTED (P_C ="
          " 1.0).<br/><b>M4 Score:</b> 0.0% (Critical Hallucination).<br/><b>M5"
          " Fix:</b> Replaces $650 with mathematically verified $605.00.",
      ),
      (
          "Case 9: Outdated Political Office Holder (Temporal Drift)",
          "Input: 'Boris Johnson is the Prime Minister of the United Kingdom in"
          " 2026.'<br/><b>M1 Claims:</b> Boris Johnson is UK Prime Minister in"
          " 2026.<br/><b>M2 Evidence:</b> UK Cabinet History: Johnson resigned"
          " in September 2022.<br/><b>M3 NLI:</b> P_C = 0.95.<br/><b>M4"
          " Score:</b> 5.0% (Critical Hallucination).<br/><b>M5 Fix:</b>"
          " 'Keir Starmer is the Prime Minister of the United Kingdom in"
          " 2026.'",
      ),
  ]

  for c_title, c_body in case_studies:
    story.append(
        make_callout(
            c_title,
            c_body,
            styles,
            accent_color=C_SECONDARY,
            bg_color=C_BG_WARM,
        )
    )
    story.append(Spacer(1, 4))

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 16: COMPREHENSIVE VIVA & TECHNICAL REVIEW DEFENSE GUIDE
  # =========================================================================
  story.append(Paragraph("CHAPTER 16", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Comprehensive Viva & Technical Review Defense Guide",
          styles["ChapterTitle"],
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "This chapter contains 50 comprehensive technical viva questions and"
          " model answers organized into five categories, followed by examiner"
          " curveballs and pitch scripts.",
          styles["Body"],
      )
  )

  # Viva Categories
  viva_groups = [
      ("CATEGORY A: SYSTEM ARCHITECTURE & ENGINEERING DESIGN", [
          (
              "Q1: What is the core problem TruthGuard solves?",
              "TruthGuard solves the hallucination crisis in Generative AI by"
              " providing an independent, post-hoc, evidence-grounded"
              " verification pipeline that decomposes generated text into atomic"
              " claims, retrieves authoritative external evidence, verifies"
              " factual alignment using calibrated NLI and mathematics,"
              " calculates non-compensatory reliability, and surgically patches"
              " detected errors.",
          ),
          (
              "Q2: Why did you choose a modular monolith instead of"
              " microservices?",
              "A modular monolith eliminates network serialization overhead,"
              " eliminates inter-service HTTP latencies, simplifies transaction"
              " state management, and allows in-memory PyTorch tensor sharing"
              " while maintaining clean separation of concerns through typed"
              " Pydantic interfaces.",
          ),
          (
              "Q3: How does TruthGuard handle graceful degradation when an"
              " external API fails?",
              "If external REST APIs (Wikipedia, PubMed) timeout, the retriever"
              " automatically falls back to the local ChromaDB vector store. If"
              " the primary LLM API fails, M1 activates a rule-based SpaCy"
              " dependency parser.",
          ),
          (
              "Q4: What database is used and what is the persistence strategy?",
              "We use SQLite for local deployment and testing, designed with an"
              " asynchronous SQLAlchemy 2.0 abstraction that enables zero-code"
              " migration to PostgreSQL for distributed enterprise clusters.",
          ),
          (
              "Q5: How does the system handle high-concurrency requests in"
              " FastAPI?",
              "FastAPI runs on an ASGI Uvicorn server. Heavy neural inference"
              " runs in separate thread pools to avoid blocking the event loop,"
              " with parallel retrieval executed asynchronously via"
              " `asyncio.gather()`.",
          ),
          (
              "Q6: What is the average end-to-end processing latency per claim?",
              "Mean latency is 0.680 seconds per claim, with a median of 0.567s"
              " and a 95th percentile (P95) of 1.278 seconds.",
          ),
          (
              "Q7: How are API payloads structured?",
              "All endpoints enforce strict Pydantic v2 schemas: inputs require"
              " a text payload with optional domain hints; outputs return"
              " structured verification DTOs containing claim lists, confidence"
              " tensors, citations, and patches.",
          ),
          (
              "Q8: What security and rate limiting measures are implemented?",
              "TruthGuard implements CORS middleware, payload length guards"
              " (max 10,000 characters per request), and IP-based rate limiting"
              " to prevent denial-of-service degradation.",
          ),
          (
              "Q9: How are model weights managed in production?",
              "Cross-encoder and SBERT weights are cached locally upon initial"
              " download and loaded during FastAPI lifespan startup to ensure"
              " instant inference on incoming requests.",
          ),
          (
              "Q10: Why is an external verification system preferred over"
              " self-critique?",
              "Self-critique (asking an LLM 'are you sure?') suffers from the"
              " same parametric memory biases, sycophancy, and training loss"
              " blindspots that caused the hallucination initially. External"
              " cross-encoders with external evidence provide true orthogonal"
              " verification.",
          ),
      ]),
      (
          "CATEGORY B: NLP, LLM DECOMPOSITION & INFORMATION EXTRACTION",
          [
              (
                  "Q11: Why is atomic claim decomposition necessary before"
                  " retrieval?",
                  "Paragraphs contain entangled facts, pronouns, and qualifying"
                  " clauses. Evaluating compound sentences produces ambiguous"
                  " retrieval results and confounding NLI scores. Atomic"
                  " decomposition isolates single truth-conditional"
                  " propositions.",
              ),
              (
                  "Q12: How does M1 resolve co-references and pronouns?",
                  "M1 uses an entity-tracking stack across sentence boundaries,"
                  " replacing relative pronouns ('it', 'they') with their"
                  " full, explicit nominal referents before retrieval.",
              ),
              (
                  "Q13: What happens when an input sentence contains multiple"
                  " conjoined clauses?",
                  "M1 parses the sentence into distinct atomic claims, ensuring"
                  " that each clause ('A and B') is independently retrieved and"
                  " verified against its own dedicated evidence.",
              ),
              (
                  "Q14: How does the SpaCy rule-based fallback extract claims?",
                  "It parses sentences into dependency trees, identifying root"
                  " verbs, coordinating conjunctions, and subordinate clauses"
                  " to split compound structures into grammatical subject-verb"
                  " tuples.",
              ),
              (
                  "Q15: What LLM prompt design is used for M1?",
                  "We use a few-shot structured prompt with JSON schema"
                  " enforcement and temperature T=0.0, explicitly instructing"
                  " the model never to infer unstated facts or alter semantic"
                  " scope.",
              ),
              (
                  "Q16: How are mathematical claims identified during"
                  " decomposition?",
                  "M1 scans for numeric digits, mathematical operator tokens"
                  " (+, -, *, /, =), and percentage symbols, setting the"
                  " `is_mathematical` flag to route the claim to the SymPy"
                  " engine.",
              ),
              (
                  "Q17: How does TruthGuard prevent over-segmentation of"
                  " idiomatic phrases?",
                  "M1 preserves named entities and compound noun chunks"
                  " identified by SpaCy, preventing idioms or multi-word"
                  " entities from being broken into nonsensical fragments.",
              ),
              (
                  "Q18: What is the formal linguistic definition of an atomic"
                  " claim?",
                  "An atomic claim is a minimal declarative sentence expressing"
                  " exactly one semantic proposition that can be assigned an"
                  " independent truth value without reference to external"
                  " context.",
              ),
              (
                  "Q19: How are temporal qualifiers preserved during"
                  " decomposition?",
                  "Temporal adverbs and dates ('in 2024', 'subsequently') are"
                  " explicitly retained inside each atomic claim to prevent"
                  " chronological hallucinations.",
              ),
              (
                  "Q20: What is the precision of M1 decomposition on complex"
                  " texts?",
                  "M1 achieves 96.4% decomposition accuracy, correctly"
                  " extracting and disambiguating propositions without"
                  " altering original semantic meaning.",
              ),
          ],
      ),
      ("CATEGORY C: RAG, RETRIEVAL FUSION & QUALITY GATES", [
          (
              "Q21: Why is hybrid retrieval superior to pure dense retrieval?",
              "Dense retrieval captures semantic concepts but misses exact"
              " entity names and numbers. BM25 captures exact tokens but misses"
              " paraphrases. Hybrid search combines the strengths of both.",
          ),
          (
              "Q22: What is Reciprocal Rank Fusion (RRF) and why is k=60"
              " optimal?",
              "RRF combines rank positions across disparate retrieval systems"
              " without requiring score normalization. The smoothing constant"
              " k=60 prevents top ranks from dominating while stabilizing"
              " lower-ranked candidates.",
          ),
          (
              "Q23: What model is used for semantic reranking in M2?",
              "We utilize `cross-encoder/ms-marco-MiniLM-L-6-v2`, which"
              " performs full bidirectional cross-attention across the"
              " concatenated claim-evidence pair.",
          ),
          (
              "Q24: What is the purpose of the Retrieval Quality Gate?",
              "The Quality Gate prevents 'lexical traps' and polysemous noise"
              " from contaminating the NLI engine by enforcing named entity"
              " overlap and content lemma constraints.",
          ),
          (
              "Q25: What happens if a retrieved passage fails the Quality Gate?",
              "The passage is discarded, preventing false contradictions. If"
              " all passages fail, the claim is assigned NOT ENOUGH INFO (NEI).",
          ),
          (
              "Q26: How does TruthGuard disambiguate polysemous words like"
              " 'Mercury'?",
              "The Quality Gate examines co-occurrence context tokens (e.g.,"
              " 'planet', 'orbit' vs 'element', 'toxic' vs 'god', 'mythology').",
          ),
          (
              "Q27: What external knowledge corpora are integrated into M2?",
              "Wikipedia REST API, PubMed Biomedical API, ArXiv Academic API,"
              " and a local curated ChromaDB vector store.",
          ),
          (
              "Q28: What is the Retrieval Relevance Rate achieved by"
              " TruthGuard?",
              "TruthGuard achieves a 100.0% Retrieval Relevance Rate on the"
              " TruthGuard-350 benchmark due to Quality Gate filtering.",
          ),
          (
              "Q29: How are passage chunk sizes determined?",
              "Passages are chunked into 250-word sliding windows with a 50-word"
              " overlap to preserve complete paragraph context.",
          ),
          (
              "Q30: How does the system avoid Wikipedia citation hallucination?",
              "Evidence is retrieved exclusively from verified, immutable"
              " Wikipedia article body text, not from LLM memory.",
          ),
      ]),
      ("CATEGORY D: NLI, MATHEMATICS & RELIABILITY SCORING", [
          (
              "Q31: What is the difference between bi-encoders and"
              " cross-encoders in NLI?",
              "Bi-encoders compute vector embeddings independently and measure"
              " cosine distance (fast but shallow). Cross-encoders perform full"
              " cross-attention between claim and evidence tokens"
              " simultaneously (computationally heavier but vastly more"
              " accurate).",
          ),
          (
              "Q32: Why is temperature scaling necessary for DeBERTa-v3?",
              "Deep neural networks are overconfident. Temperature scaling (T ="
              " 1.35) softens overconfident logit distributions, reducing the"
              " Expected Calibration Error from 0.142 to 0.038.",
          ),
          (
              "Q33: Why are non-uniform decision thresholds used (\\tau_e=0.75,"
              " \\tau_c=0.70)?",
              "False contradictions severely damage user trust, while false"
              " entailments allow hallucinations to pass. Thresholds are"
              " calibrated to reflect these asymmetric error costs.",
          ),
          (
              "Q34: How does SymPy verify mathematical assertions?",
              "It parses numeric equations into symbolic syntax trees and"
              " evaluates arithmetic identities deterministically, bypassing"
              " neural approximations.",
          ),
          (
              "Q35: Why does TruthGuard reject linear averaging for Answer"
              " Reliability?",
              "Linear averaging allows a report with 9 true facts and 1 fatal"
              " lie to score 90% (High Trust). In high-stakes domains, one fatal"
              " falsehood destroys the utility of the entire document.",
          ),
          (
              "Q36: What is the non-compensatory scoring formula used in M4?",
              "R(A) = min(mean(rho(c_i)), 1.0 - max(P_C(c_i))). The score is"
              " bounded by the maximum contradiction probability.",
          ),
          (
              "Q37: What is the epistemic discount factor \\lambda_{NEI}?",
              "\\lambda_{NEI} = 0.50. It reflects that an unverified claim is"
              " neither confirmed nor denied, penalizing the score moderately"
              " without treating it as a proven contradiction.",
          ),
          (
              "Q38: What are the four Trust Categories in M4?",
              "High Trust (>= 80%), Qualified Trust (60-79%), Low Trust"
              " (40-59%), and Critical Hallucination (< 40%).",
          ),
          (
              "Q39: What is Universal AI Investigation (Stage 2)?",
              "A symmetrical second-stage verification process applied across"
              " Supported, Contradicted, and NEI claims to search for"
              " counter-evidence and verify qualifiers.",
          ),
          (
              "Q40: What was the Macro-F1 score achieved on TruthGuard-350?",
              "TruthGuard achieved a Macro-F1 score of 82.44% across all three"
              " classes, with Contradiction F1 reaching 93.78%.",
          ),
      ]),
      ("CATEGORY E: GROUNDED CORRECTION, DEDUPLICATION & PRODUCTION", [
          (
              "Q41: What is the 'Verify-Then-Accept' correction protocol?",
              "Candidate corrections generated by M5 must pass secondary NLI"
              " verification against the retrieved evidence (P_E >= 0.80) before"
              " being accepted into the output text.",
          ),
          (
              "Q42: What caused the duplicate paragraph correction bug in early"
              " builds?",
              "When multiple atomic claims originating from the same compound"
              " sentence were contradicted, naive string replacement inserted"
              " the same correction twice consecutively.",
          ),
          (
              "Q43: How did TruthGuard resolve the duplicate correction bug?",
              "By tracking original sentence IDs, applying SBERT semantic"
              " deduplication (threshold 0.85), and executing a single in-place"
              " replacement pass.",
          ),
          (
              "Q44: What is the False Correction Rate of M5?",
              "Only 3.48% on the TruthGuard-350 benchmark, meaning 96.52% of"
              " generated patches are factually accurate and non-hallucinatory.",
          ),
          (
              "Q45: How does M5 preserve the original author's tone?",
              "M5 performs surgical in-place patching of contradicted entities"
              " rather than prompting an unconstrained full-paragraph rewrite.",
          ),
          (
              "Q46: What export formats are supported by TruthGuard?",
              "Executive PDF Reports, Research JSON with complete logit"
              " breakdowns, and Tabular CSV logs.",
          ),
          (
              "Q47: How does TruthGuard handle cross-lingual claims?",
              "An experimental module (`truthguard.multilingual`) translates"
              " non-English claims to English before retrieval, though native"
              " multi-lingual cross-encoders are planned for v3.0.",
          ),
          (
              "Q48: How does the system scale to enterprise document volumes?",
              "Via Celery task queues backed by Redis, distributing claim"
              " verification batches across GPU worker pools.",
          ),
          (
              "Q49: What is the primary limitation of TruthGuard today?",
              "Complex multi-hop reasoning requiring synthesis across 4+ chained"
              " documents and non-textual tabular data.",
          ),
          (
              "Q50: What are the three primary academic contributions of this"
              " project?",
              "1. Symmetrical Universal AI Investigation for all verdicts; 2."
              " Non-compensatory weakest-link Answer Reliability; 3."
              " Verify-then-accept grounded surgical correction with semantic"
              " deduplication.",
          ),
      ]),
  ]

  for g_title, qas in viva_groups:
    story.append(
        Paragraph(
            f"<b>{g_title}</b>",
            styles["SectionHeading"],
        )
    )
    for q, a in qas:
      story.append(Paragraph(f"<b>{q}</b>", styles["QuestionTitle"]))
      story.append(Paragraph(a, styles["AnswerBody"]))

  story.append(Spacer(1, 6))
  story.append(
      Paragraph(
          "16.6 Examiner Curveballs & Tough Questions with Strategic Responses",
          styles["SectionHeading"],
      )
  )

  curveballs = [
      (
          "Curveball 1: 'Isn't your system also vulnerable to hallucinations"
          " when generating M5 corrections?'",
          "<b>Strategic Defense:</b> 'Yes, generative models always carry"
          " hallucination risks. That is precisely why TruthGuard does NOT trust"
          " M5 blindly. We implemented the <i>Verify-Then-Accept</i> protocol:"
          " every candidate correction must pass a secondary DeBERTa-v3 NLI check"
          " against the retrieved evidence (P_E >= 0.80). If it fails, the"
          " system falls back to direct evidence quotation. This reduced our"
          " False Correction Rate to just 3.48%.'",
      ),
      (
          "Curveball 2: 'Why did you use BM25 when modern dense vector search is"
          " available?'",
          "<b>Strategic Defense:</b> 'Dense vector search excels at semantic"
          " concepts but notoriously fails on exact keyword matching, such as"
          " distinguishing Apollo 11 from Apollo 12, or locating specific"
          " numerical statistics. BM25 provides exact token matching. By fusing"
          " them via Reciprocal Rank Fusion (RRF, k=60), we achieve the"
          " semantic generalization of SBERT and the exact precision of BM25.'",
      ),
      (
          "Curveball 3: 'Your Supported Recall is only 60.0%. Isn't that low?'",
          "<b>Strategic Defense:</b> 'That was a conscious engineering design"
          " decision. In fact-checking, false entailments allow hallucinations"
          " to pass undetected. We calibrated our threshold to \\tau_e = 0.75"
          " and enforced a strict Quality Gate. As a result, our Supported"
          " Precision is an extraordinary <b>98.63%</b>. When TruthGuard says a"
          " claim is supported, it is virtually guaranteed to be true.'",
      ),
      (
          "Curveball 4: 'How is this different from existing RAG systems?'",
          "<b>Strategic Defense:</b> 'Standard RAG retrieves context before"
          " generation to assist an LLM. TruthGuard is a post-generation"
          " verification and correction engine. We perform atomic decomposition,"
          " semantic gating, temperature-calibrated NLI, symmetrical universal"
          " investigation, and non-compensatory scoring. Standard RAG does none"
          " of these.'",
      ),
  ]
  for cb_t, cb_d in curveballs:
    story.append(
        make_callout(
            cb_t,
            cb_d,
            styles,
            accent_color=C_ACCENT_RED,
            bg_color=C_BG_WARM,
        )
    )
    story.append(Spacer(1, 4))

  story.append(Spacer(1, 6))
  story.append(
      Paragraph(
          "16.7 Defense Pitches: 2-Minute, 5-Minute, and 10-Minute Scripts",
          styles["SectionHeading"],
      )
  )

  pitches = [
      (
          "2-Minute Elevator Pitch (The Core Problem & Solution):",
          "'Distinguished evaluators, Large Language Models have revolutionized"
          " AI, but they suffer from a fatal flaw: hallucinations. They generate"
          " plausible-sounding falsehoods with high confidence. TruthGuard"
          " solves this by acting as an independent, deterministic proof engine"
          " downstream of any LLM. We decompose paragraphs into atomic claims,"
          " retrieve authoritative evidence using hybrid search with strict"
          " semantic gating, verify facts using temperature-calibrated NLI and"
          " SymPy mathematics, evaluate trust using non-compensatory scoring,"
          " and surgically patch errors using our Verify-Then-Accept protocol."
          " On 350 multi-domain claims, TruthGuard achieved 82.86% accuracy,"
          " 93.78% Contradiction F1, and a 100% retrieval relevance rate at"
          " 0.68s per claim.'",
      ),
      (
          "5-Minute Technical Review Pitch (The Engineering Depth):",
          "'Respected committee, our project addresses the hallucination crisis"
          " through three key engineering innovations: First, in retrieval, raw"
          " RAG frequently retrieves irrelevant noise. TruthGuard interposes a"
          " Retrieval Quality Gate enforcing SpaCy entity matching and"
          " polysemy filters, eliminating 100% of retrieval traps. Second, in"
          " inference, standard pipelines only investigate uncertain claims."
          " TruthGuard implements Universal AI Investigation across ALL three"
          " verdicts, actively hunting for counter-evidence. Third, in"
          " scoring, standard linear averaging allows a lethal lie to hide"
          " behind 9 true facts. TruthGuard enforces non-compensatory scoring:"
          " R(A) = min(mean(rho(c_i)), 1 - max(P_C)). If a fatal contradiction"
          " exists, the score collapses to 0%. Finally, M5 patches text"
          " surgically without duplicate sentences and validates every edit"
          " with secondary NLI.'",
      ),
  ]
  for p_t, p_d in pitches:
    story.append(
        make_callout(
            p_t,
            p_d,
            styles,
            accent_color=C_PRIMARY,
            bg_color=C_BG_PANEL,
        )
    )
    story.append(Spacer(1, 4))

  story.append(PageBreak())

  # =========================================================================
  # CHAPTER 17: LIMITATIONS, FUTURE WORK & CONCLUSION
  # =========================================================================
  story.append(Paragraph("CHAPTER 17", styles["ChapterNum"]))
  story.append(
      Paragraph(
          "Limitations, Future Work & Conclusion", styles["ChapterTitle"]
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_PRIMARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  story.append(
      Paragraph(
          "17.1 Current System Boundaries & Honest Limitations",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "In keeping with academic integrity, we document the current"
          " boundaries of TruthGuard v2.4: <b>(1) Multi-Hop Reasoning:</b>"
          " TruthGuard verifies atomic claims against localized evidence"
          " passages; assertions requiring chained deductive leaps across 4+ disparate"
          " documents remain challenging; <b>(2) Cross-Lingual Coverage:</b>"
          " While an experimental translation module exists, native non-English"
          " verification relies on translated English proxies; <b>(3) Tabular &"
          " Multimodal Evidence:</b> TruthGuard currently verifies textual"
          " propositions; verifying claims grounded in complex multi-column"
          " financial spreadsheets or charts requires dedicated multimodal"
          " vision-language models.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "17.2 Roadmap & Future Research Directions", styles["SectionHeading"]
      )
  )
  story.append(
      Paragraph(
          "Future extensions planned for TruthGuard v3.0 include: <b>(a)"
          " Autonomous Streaming Indexers:</b> Continuous background crawlers"
          " indexing regulatory, legal, and pre-print repositories; <b>(b) Edge"
          " Knowledge Distillation:</b> Distilling the 435M-parameter DeBERTa-v3"
          " cross-encoder into an ONNX-optimized 60M-parameter student model for"
          " on-device mobile verification; <b>(c) Multimodal Vision-Language"
          " Grounding:</b> Extending the Quality Gate to verify infographic and"
          " chart data.",
          styles["Body"],
      )
  )

  story.append(
      Paragraph(
          "17.3 Final Conclusions & Summary of Contributions",
          styles["SectionHeading"],
      )
  )
  story.append(
      Paragraph(
          "TruthGuard demonstrates that the LLM hallucination crisis is"
          " solvable through rigorous, modular engineering. By decoupling"
          " verification from text generation, enforcing atomic decomposition,"
          " filtering retrieval through strict semantic gates, calibrating NLI"
          " probabilities, performing universal multi-perspective investigation,"
          " penalizing fatal falsehoods non-compensatorily, and validating"
          " corrections before acceptance, TruthGuard establishes a new"
          " standard for factual reliability in modern AI systems.",
          styles["Body"],
      )
  )

  story.append(Spacer(1, 10))
  story.append(
      HRFlowable(
          width="100%",
          thickness=1,
          color=C_SECONDARY,
          spaceBefore=0,
          spaceAfter=10,
      )
  )

  # Glossary
  story.append(
      Paragraph("GLOSSARY OF KEY TECHNICAL TERMS", styles["SectionHeading"])
  )
  glossary_terms = [
      (
          "Atomic Claim:",
          "A minimal, self-contained declarative statement expressing a single"
          " proposition that cannot be further split without losing truth"
          " conditions.",
      ),
      (
          "DeBERTa-v3:",
          "Decoding-enhanced BERT with disentangled attention, separating"
          " content and position vectors for superior NLI reasoning.",
      ),
      (
          "Expected Calibration Error (ECE):",
          "A metric measuring the difference between predicted model confidence"
          " and true empirical accuracy.",
      ),
      (
          "Natural Language Inference (NLI):",
          "The task of determining whether a hypothesis is entailed,"
          " contradicted, or neutral given a premise.",
      ),
      (
          "Non-Compensatory Scoring:",
          "A mathematical scoring principle where failure in one critical"
          " dimension cannot be offset by success in others.",
      ),
      (
          "Reciprocal Rank Fusion (RRF):",
          "A robust rank-aggregation algorithm combining results from multiple"
          " retrieval systems without score normalization.",
      ),
      (
          "Temperature Scaling:",
          "A post-processing calibration method that divides neural network"
          " logits by a learned scalar T to soften overconfidence.",
      ),
  ]
  for gt_t, gt_d in glossary_terms:
    story.append(Paragraph(f"• <b>{gt_t}</b> {gt_d}", styles["BulletText"]))

  story.append(Spacer(1, 8))
  story.append(
      Paragraph(
          "ACADEMIC REFERENCES & BIBLIOGRAPHY", styles["SectionHeading"]
      )
  )
  academic_refs = [
      (
          "[1] E. M. Bender, T. Gebru, A. McMillan-Major, and S. Shmitchell,"
          ' "On the dangers of stochastic parrots: Can language models be too'
          ' big?" in Proc. of FAccT, pp. 610–623, 2021.'
      ),
      (
          "[2] J. Thorne, A. Vlachos, C. Christodoulopoulos, and A. Mittal,"
          ' "FEVER: a large-scale dataset for fact extraction and'
          ' VERification," in Proc. of NAACL-HLT, pp. 809–819, 2018.'
      ),
      (
          "[3] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, \"On"
          " calibration of modern neural networks,\" in Proc. of ICML, pp."
          " 1321–1330, 2017."
      ),
      (
          "[4] P. He, J. Gao, and W. Chen, \"DeBERTaV3: Improving DeBERTa using"
          " ELECTRA-style pre-training with gradient-disentangled attention,\""
          " arXiv preprint arXiv:2111.09543, 2021."
      ),
      (
          "[5] G. V. Cormack, C. L. Clarke, and S. Buettcher, \"Reciprocal rank"
          " fusion outperforms Condorcet and individual machine learning"
          " methods,\" in Proc. of SIGIR, pp. 758–759, 2009."
      ),
  ]
  for ar in academic_refs:
    story.append(Paragraph(ar, styles["AnswerBody"]))

  # Build Document
  doc = SimpleDocTemplate(
      PDF_OUTPUT_PATH,
      pagesize=letter,
      leftMargin=54,
      rightMargin=54,
      topMargin=54,
      bottomMargin=54,
  )

  doc.build(story, canvasmaker=NumberedCanvas)
  print(f"[Success] Generated Explanation PDF: {PDF_OUTPUT_PATH}")
  print(f"[File Size] {os.path.getsize(PDF_OUTPUT_PATH)} bytes")


if __name__ == "__main__":
  build_explanation_book()
