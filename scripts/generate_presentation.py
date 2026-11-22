"""
TruthGuard Professional PowerPoint Presentation & PDF Generator
Generates:
  - TruthGuard_Documentation/TruthGuard_Project_Presentation.pptx
  - TruthGuard_Documentation/TruthGuard_Project_Presentation.pdf
Format: 20.0 x 11.25 in 16:9 widescreen layout
Theme: MAVIS warm ivory/cream palette with RythuMithra header hierarchy
"""

import os
import sys
import win32com.client
import pythoncom
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PPTX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "TruthGuard_Documentation", "TruthGuard_Project_Presentation.pptx"))
PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "TruthGuard_Documentation", "TruthGuard_Project_Presentation.pdf"))

# Color Constants (MAVIS Theme)
C_BG_CREAM   = RGBColor(0xFA, 0xF7, 0xF2)  # #FAF7F2 Warm Ivory Canvas
C_PANEL_TAN  = RGBColor(0xEF, 0xE9, 0xDF)  # #EFE9DF Tan / Beige Card Panel
C_CARD_LIGHT = RGBColor(0xF6, 0xF2, 0xEB)  # #F6F2EB Slightly Lighter Card
C_BORDER     = RGBColor(0xD5, 0xC8, 0xB5)  # #D5C8B5 Thin Muted Brown Border
C_PRIMARY    = RGBColor(0x37, 0x20, 0x14)  # #372014 Deep Dark Espresso Brown
C_SECONDARY  = RGBColor(0x5D, 0x44, 0x29)  # #5D4429 Rich Coffee Heading
C_TERTIARY   = RGBColor(0x71, 0x5B, 0x43)  # #715B43 Mid Brown / Muted Text
C_ACCENT_GRN = RGBColor(0x2D, 0x5A, 0x27)  # #2D5A27 Forest Green (Supported)
C_ACCENT_RED = RGBColor(0x8B, 0x1E, 0x1E)  # #8B1E1E Brick Red (Contradicted)
C_ACCENT_GLD = RGBColor(0xA4, 0x70, 0x12)  # #A47012 Warm Amber / Gold (NEI)
C_TEXT_DARK  = RGBColor(0x22, 0x22, 0x22)  # #222222 Off-Black Body
C_WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

TOTAL_SLIDES = 18

def set_slide_background(slide):
    # Add a full canvas rectangle as background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(20.0), Inches(11.25))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG_CREAM
    bg.line.fill.background()
    return bg

def add_header(slide, kicker_text, title_text, subtitle_text=""):
    header_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.55), Inches(18.0), Inches(1.35))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    # Kicker
    p_kicker = tf.paragraphs[0]
    p_kicker.text = kicker_text.upper()
    p_kicker.font.size = Pt(11)
    p_kicker.font.bold = True
    p_kicker.font.color.rgb = C_SECONDARY
    p_kicker.space_after = Pt(3)

    # Title
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(26)
    p_title.font.bold = True
    p_title.font.color.rgb = C_PRIMARY
    p_title.space_after = Pt(3)

    # Subtitle
    if subtitle_text:
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = C_TERTIARY

def add_footer(slide, current_slide, total_slides=TOTAL_SLIDES):
    # Separator Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(10.45), Inches(18.0), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = C_BORDER
    line.line.fill.background()

    footer_box = slide.shapes.add_textbox(Inches(1.0), Inches(10.55), Inches(18.0), Inches(0.45))
    tf = footer_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "TruthGuard | NLP & Generative AI Research Project | Capstone Presentation"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TERTIARY

    p_right = tf.add_paragraph()
    p_right.text = f"Slide {current_slide} of {total_slides}"
    p_right.alignment = PP_ALIGN.RIGHT
    p_right.font.size = Pt(9.5)
    p_right.font.bold = True
    p_right.font.color.rgb = C_SECONDARY

def add_card(slide, left, top, width, height, bg_color=C_PANEL_TAN, border_color=C_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.0)
    return shape

def add_metric_badge(slide, left, top, width, height, value_text, label_text, sub_text="", accent_color=C_PRIMARY):
    card = add_card(slide, left, top, width, height, bg_color=C_CARD_LIGHT, border_color=C_BORDER)
    tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.2), Inches(width - 0.4), Inches(height - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_val = tf.paragraphs[0]
    p_val.text = value_text
    p_val.font.size = Pt(28)
    p_val.font.bold = True
    p_val.font.color.rgb = accent_color
    p_val.space_after = Pt(2)

    p_lbl = tf.add_paragraph()
    p_lbl.text = label_text
    p_lbl.font.size = Pt(12)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = C_PRIMARY
    p_lbl.space_after = Pt(2)

    if sub_text:
        p_sub = tf.add_paragraph()
        p_sub.text = sub_text
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = C_TERTIARY

def build_presentation():
    print("[Starting] Building TruthGuard Professional PowerPoint Presentation...")
    prs = Presentation()
    prs.slide_width = Inches(20.0)
    prs.slide_height = Inches(11.25)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Decorative Border Frame
    frame = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(18.4), Inches(9.65))
    frame.fill.solid()
    frame.fill.fore_color.rgb = C_CARD_LIGHT
    frame.line.color.rgb = C_BORDER
    frame.line.width = Pt(1.5)

    tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(1.4), Inches(17.0), Inches(5.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "MAJOR CAPSTONE PROJECT — NLP & GENERATIVE AI RESEARCH"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = C_SECONDARY
    p1.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "TruthGuard: AI-Powered Evidence-Grounded\nHallucination Detection, Verification & Correction"
    p2.font.size = Pt(40)
    p2.font.bold = True
    p2.font.color.rgb = C_PRIMARY
    p2.space_after = Pt(14)

    p3 = tf1.add_paragraph()
    p3.text = "A Modular End-to-End Proof Desk for Atomic Claim Decomposition, Hybrid Multi-Source Retrieval,\nCalibrated NLI Inference, Universal AI Investigation, and Grounded Paragraph Patching"
    p3.font.size = Pt(16)
    p3.font.color.rgb = C_TERTIARY

    # Key Badges on Title
    badges = [
        ("82.86%", "Benchmark Accuracy", "TruthGuard-350 Multi-Domain", C_PRIMARY),
        ("93.78%", "Contradiction F1", "State-of-the-Art Hallucination Catch", C_ACCENT_RED),
        ("100.0%", "Retrieval Relevance", "Quality Gate Zero Noise Filtering", C_ACCENT_GRN),
        ("0.68s", "Mean Latency / Claim", "Real-Time Interactive Performance", C_SECONDARY),
    ]
    for i, (b_val, b_lbl, b_sub, b_col) in enumerate(badges):
        add_metric_badge(s1, 1.5 + (i * 4.3), 6.5, 4.0, 1.8, b_val, b_lbl, b_sub, b_col)

    # Footer meta
    tbm = s1.shapes.add_textbox(Inches(1.5), Inches(8.8), Inches(17.0), Inches(1.0))
    tfm = tbm.text_frame
    pm = tfm.paragraphs[0]
    pm.text = "Candidate / Presenter: NLP Engineering & Research Team  |  Academic Year 2026-2027  |  Technology: PyTorch, DeBERTa-v3, FastAPI, React 18"
    pm.font.size = Pt(11)
    pm.font.color.rgb = C_TERTIARY

    # =========================================================================
    # SLIDE 2: MOTIVATION & PROBLEM STATEMENT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "1. Motivation & Background", "The Hallucination Crisis in Large Language Models", "Why autoregressive language generation fundamentally decouples fluency from empirical factuality")
    add_footer(s2, 2)

    col_w = 5.75
    cards_s2 = [
        ("The Stochastic Parrot Problem", "LLMs optimize next-token likelihood, not truth", [
            "Trained on next-token prediction loss over massive, noisy web datasets.",
            "Possess no internal world model, physical grounding, or truth verification layer.",
            "Confidently synthesize ungrounded claims with high linguistic polish.",
            "High confidence is mathematically decoupled from factual correctness."
        ]),
        ("Taxonomy of Hallucinations", "Five critical manifestation patterns", [
            "Entity Confusion: Misassigning actions, discoveries, or clinical properties.",
            "Temporal Drift: Asserting outdated historical facts as present realities.",
            "Numerical & Arithmetic Drift: Fabricating statistics, formulas, and dates.",
            "Quantifier Inflation: Generalizing localized truths to absolute claims ('all').",
            "Pure Fabrications: Non-existent legal cases, fake planets, imaginary colonies."
        ]),
        ("High-Stakes Societal Impact", "Catastrophic consequences in production", [
            "Clinical Medicine: Fabricating contraindications or toxic pharmacological dosages.",
            "Legal & Jurisprudence: Citing non-existent judicial rulings and statutes.",
            "Finance & Policy: Misreporting quarterly earnings and regulatory compliance.",
            "Why Prompting Fails: Self-critique suffers from the same parametric biases."
        ])
    ]
    for i, (title, sub, bullets) in enumerate(cards_s2):
        x = 1.0 + (i * 6.15)
        add_card(s2, x, 2.3, col_w, 7.8, bg_color=C_CARD_LIGHT)
        tb = s2.shapes.add_textbox(Inches(x + 0.35), Inches(2.6), Inches(col_w - 0.7), Inches(7.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = C_SECONDARY
        ps.space_after = Pt(14)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(10)

    # =========================================================================
    # SLIDE 3: THE TRUTHGUARD SOLUTION
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "2. Solution Overview", "TruthGuard: The Autonomous Evidence-Grounded Proof Desk", "Decoupling text generation from factual verification through a deterministic five-module pipeline")
    add_footer(s3, 3)

    pillars = [
        ("Pillar 1: Claim Atomicity", "Decomposing complex paragraphs into minimal, self-contained truth-conditional propositions with co-reference resolution.", C_PRIMARY),
        ("Pillar 2: Gated Hybrid Retrieval", "Combining BM25 lexical precision with SBERT dense embeddings, fused via RRF and guarded by strict entity matching.", C_SECONDARY),
        ("Pillar 3: Calibrated NLI & Math", "Temperature-scaled DeBERTa-v3 inference combined with a deterministic SymPy engine for exact numerical proofs.", C_ACCENT_GRN),
        ("Pillar 4: Universal Investigation", "Symmetrical Stage 2 AI verification across all three outcomes (Supported, Contradicted, NEI) to catch nuance.", C_ACCENT_GLD),
        ("Pillar 5: Non-Compensatory Scoring", "Enforcing weakest-link reliability where one fatal lie collapses trust, avoiding deceptive linear averages.", C_ACCENT_RED),
        ("Pillar 6: Verify-Then-Accept Edits", "Secondary NLI validation of surgical paragraph corrections with semantic deduplication to eliminate duplicate text.", C_PRIMARY),
    ]
    for i, (p_title, p_desc, p_accent) in enumerate(pillars):
        row = i // 3
        col = i % 3
        x = 1.0 + (col * 6.15)
        y = 2.3 + (row * 3.9)
        add_card(s3, x, y, 5.85, 3.5, bg_color=C_CARD_LIGHT)
        
        # Left accent stripe
        stripe = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.12), Inches(3.5))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = p_accent
        stripe.line.fill.background()

        tb = s3.shapes.add_textbox(Inches(x + 0.35), Inches(y + 0.3), Inches(5.2), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = p_title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY
        p.space_after = Pt(8)

        pd = tf.add_paragraph()
        pd.text = p_desc
        pd.font.size = Pt(11.5)
        pd.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "3. System Architecture", "End-to-End Five-Module Pipeline Architecture", "Synchronous and asynchronous flow from raw text input to grounded correction and persistence")
    add_footer(s4, 4)

    steps = [
        ("M1", "Claim Decomposer", "Few-Shot LLM + SpaCy\nCo-Reference Disambiguation\nClause Splitting", C_PRIMARY),
        ("M2", "Hybrid Retrieval", "BM25 + SBERT (all-MiniLM)\nRRF Fusion (k=60)\nCross-Encoder Reranker", C_SECONDARY),
        ("GATE", "Quality Gate", "SpaCy NER Overlap\n2-Token Content Lemma\nPolysemy Context Filter", C_ACCENT_GLD),
        ("M3", "Calibrated NLI", "DeBERTa-v3 Cross-Encoder\nTemperature Scaling (T=1.35)\nSymPy Exact Math Verifier", C_PRIMARY),
        ("STAGE 2", "Universal Arbiter", "Adversarial Counter-Search\nSupported / Contradicted / NEI\nBayesian Belief Synthesis", C_ACCENT_GRN),
        ("M4", "Reliability Scoring", "Non-Compensatory Formula\nWeakest-Link Penalty\nTrust Tier Categorization", C_ACCENT_RED),
        ("M5", "Grounded Correction", "Verify-Then-Accept Protocol\nSemantic Deduplication Fix\nIn-Place Surgical Patching", C_PRIMARY),
    ]
    card_w = 2.4
    spacing = 0.2
    for i, (badge, name, details, accent) in enumerate(steps):
        x = 1.0 + (i * (card_w + spacing))
        add_card(s4, x, 2.5, card_w, 7.5, bg_color=C_CARD_LIGHT)
        
        # Top Header Box
        top_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(2.5), Inches(card_w), Inches(1.1))
        top_box.fill.solid()
        top_box.fill.fore_color.rgb = accent
        top_box.line.fill.background()

        t_tb = s4.shapes.add_textbox(Inches(x), Inches(2.55), Inches(card_w), Inches(1.0))
        t_tf = t_tb.text_frame
        t_tf.word_wrap = True
        tp = t_tf.paragraphs[0]
        tp.alignment = PP_ALIGN.CENTER
        tp.text = badge
        tp.font.size = Pt(13)
        tp.font.bold = True
        tp.font.color.rgb = C_WHITE

        tp2 = t_tf.add_paragraph()
        tp2.alignment = PP_ALIGN.CENTER
        tp2.text = name
        tp2.font.size = Pt(10)
        tp2.font.color.rgb = RGBColor(0xDF, 0xD7, 0xCB)

        # Body details
        b_tb = s4.shapes.add_textbox(Inches(x + 0.15), Inches(3.8), Inches(card_w - 0.3), Inches(5.8))
        b_tf = b_tb.text_frame
        b_tf.word_wrap = True
        bp = b_tf.paragraphs[0]
        bp.text = details
        bp.font.size = Pt(10.5)
        bp.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 5: MODULE 1 — ATOMIC CLAIM EXTRACTION
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "4. Module 1: Claim Extraction", "M1: Atomic Claim Extraction & Disambiguation", "Deconstructing complex discourse into minimal, verifiable propositions without semantic loss")
    add_footer(s5, 5)

    add_card(s5, 1.0, 2.3, 8.7, 7.8, bg_color=C_CARD_LIGHT)
    tb_m1 = s5.shapes.add_textbox(Inches(1.4), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_m1 = tb_m1.text_frame
    tf_m1.word_wrap = True

    p = tf_m1.paragraphs[0]
    p.text = "Extraction Principles & Rules"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(12)

    m1_rules = [
        ("Semantic Atomicity:", "Every atomic claim must express exactly one subject-predicate-object assertion. Compound sentences are recursively decomposed."),
        ("Co-Reference Resolution:", "All relative and personal pronouns ('it', 'he', 'they', 'the mission') are replaced with explicit nominal referents from preceding context."),
        ("Clause Isolation:", "Coordinated clauses ('and', 'but') and relative clauses ('which was') are factored into independent declarative statements."),
        ("Qualifier Preservation:", "Strict preservation of temporal markers ('in 2024'), modal adverbs ('allegedly'), and numeric quantities."),
        ("Fallback Parsing:", "If the primary few-shot LLM fails, an offline SpaCy dependency parser segments sentences using syntactic tree analysis.")
    ]
    for r_title, r_desc in m1_rules:
        pr = tf_m1.add_paragraph()
        pr.text = f"•  {r_title}  {r_desc}"
        pr.font.size = Pt(11)
        pr.font.color.rgb = C_TEXT_DARK
        pr.space_after = Pt(8)

    # Right Card: Worked Example
    add_card(s5, 10.3, 2.3, 8.7, 7.8, bg_color=C_PANEL_TAN)
    tb_ex = s5.shapes.add_textbox(Inches(10.7), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_ex = tb_ex.text_frame
    tf_ex.word_wrap = True

    pe = tf_ex.paragraphs[0]
    pe.text = "Decomposition Walkthrough"
    pe.font.size = Pt(18)
    pe.font.bold = True
    pe.font.color.rgb = C_PRIMARY
    pe.space_after = Pt(12)

    ex_text = [
        ("Input Text:", "'NASA confirmed in 2024 that humans established a permanent colony on Jupiter named Jupiter One, which accommodates 250 scientists.'"),
        ("Atomic Claim 1:", "'NASA confirmed in 2024 that humans established a permanent colony on Jupiter.' (Entities: NASA, Jupiter, 2024)"),
        ("Atomic Claim 2:", "'The permanent colony on Jupiter is named Jupiter One.' (Pronoun resolved: 'which' -> 'The permanent colony')"),
        ("Atomic Claim 3:", "'Jupiter One accommodates 250 scientists.' (Entities: Jupiter One, 250 scientists)"),
        ("Key Benefit:", "If Claim 1 and Claim 2 are contradicted, Claim 3 is evaluated separately without corrupting overall retrieval.")
    ]
    for et, ed in ex_text:
        pe2 = tf_ex.add_paragraph()
        pe2.text = f"<b>{et}</b><br/>{ed}"
        pe2.font.size = Pt(11)
        pe2.font.color.rgb = C_TEXT_DARK
        pe2.space_after = Pt(8)

    # =========================================================================
    # SLIDE 6: MODULE 2 — HYBRID EVIDENCE RETRIEVAL
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "5. Module 2: Evidence Retrieval", "M2: Multi-Source Hybrid Lexical-Dense Search", "Overcoming retrieval blindspots by combining keyword precision with embedding semantics")
    add_footer(s6, 6)

    m2_cols = [
        ("1. Lexical Search (BM25)", "Exact Keyword & Token Matching", [
            "Indexes tokens using BM25 Okapi with parameters k1=1.5 and b=0.75.",
            "Crucial for identifying exact entity names, historical dates, and technical nomenclature.",
            "Eliminates dense vector blindness where 'Apollo 11' and 'Apollo 12' map to similar embeddings.",
            "Operates locally over pre-indexed reference corpora and dynamic API buffers."
        ], C_PRIMARY),
        ("2. Dense Semantic Search", "Embedding-Based Concept Retrieval", [
            "Encodes claim and corpus passages into 384-dimensional dense vectors using SBERT (all-MiniLM-L6-v2).",
            "Computes cosine similarity over ChromaDB vector store.",
            "Captures deep paraphrasing where keywords differ but factual meaning is identical.",
            "Enables semantic matching across synonyms and alternative phrasings."
        ], C_SECONDARY),
        ("3. Fusion & Reranking", "RRF Aggregation & Cross-Encoder", [
            "Reciprocal Rank Fusion (RRF, k=60) merges disparate rank distributions without score normalization.",
            "Top-20 fused candidates are fed to Cross-Encoder (ms-marco-MiniLM-L-6-v2).",
            "Evaluates concatenated [CLS] Claim [SEP] Passage [SEP] with full bidirectional self-attention.",
            "Multi-Source Adapters: Wikipedia, PubMed, ArXiv, and ChromaDB."
        ], C_ACCENT_GRN)
    ]
    for i, (title, sub, bullets, accent) in enumerate(m2_cols):
        x = 1.0 + (i * 6.15)
        add_card(s6, x, 2.3, col_w, 7.8, bg_color=C_CARD_LIGHT)
        tb = s6.shapes.add_textbox(Inches(x + 0.35), Inches(2.6), Inches(col_w - 0.7), Inches(7.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = C_PRIMARY
        ps.space_after = Pt(14)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(10)

    # =========================================================================
    # SLIDE 7: RETRIEVAL QUALITY GATE
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "6. Quality Control", "The Retrieval Quality Gate: Semantic Noise Elimination", "Deterministic filtering mechanisms preventing spurious passages from poisoning the NLI model")
    add_footer(s7, 7)

    qg_cards = [
        ("The 'Lexical Trap' Dilemma", "Why Raw Retrieval Fails in Open-Domain Fact Checking", [
            "Raw retrievers frequently return high-scoring passages that share words but lack factual relevance.",
            "Observed Bug: Vitamin C claim retrieved heart tissue passages because both mentioned 'tissue' and 'scurvy'.",
            "Observed Bug: Bacteria claim retrieved Apollo 11 passages because both mentioned 'sterilization'.",
            "If passed to NLI, poisoned evidence causes severe False Contradictions or False Entailments."
        ]),
        ("Three Deterministic Quality Constraints", "Rigorous filtering applied to every retrieved passage", [
            "1. Named Entity Overlap: All PERSON, ORG, GPE, and PRODUCT entities must appear in candidate passage.",
            "2. Two-Token Content Lemma Match: At least 2 lemmatized nouns/verbs must match the claim proposition.",
            "3. Polysemy Context Filter: Disambiguating polysemous entities (e.g., 'Mercury' as planet vs element vs god).",
            "Outcome: If all candidates fail, claim is marked QualityRejected and assigned NEI safely."
        ]),
        ("Empirical Validation & Impact", "Dramatic performance gain across the benchmark", [
            "Retrieval Relevance Rate: Increased from 76.2% to a perfect 100.0%.",
            "False Contradiction Reduction: Downstream NLI false contradictions dropped by 18.4%.",
            "Zero Contaminated Contexts: Ensures the inference engine evaluates only authoritative, relevant evidence.",
            "Audit Traceability: All rejected passages are logged with rejection reason for human review."
        ])
    ]
    for i, (title, sub, bullets) in enumerate(qg_cards):
        x = 1.0 + (i * 6.15)
        add_card(s7, x, 2.3, col_w, 7.8, bg_color=C_CARD_LIGHT)
        tb = s7.shapes.add_textbox(Inches(x + 0.35), Inches(2.6), Inches(col_w - 0.7), Inches(7.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = C_SECONDARY
        ps.space_after = Pt(14)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(10)

    # =========================================================================
    # SLIDE 8: MODULE 3 — CALIBRATED NLI & MATH
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "7. Module 3: NLI & Mathematics", "M3: Calibrated Natural Language Inference & SymPy Verifier", "Transforming neural logit distributions into empirical probabilities and verifying exact calculations")
    add_footer(s8, 8)

    add_card(s8, 1.0, 2.3, 8.7, 7.8, bg_color=C_CARD_LIGHT)
    tb_nli = s8.shapes.add_textbox(Inches(1.4), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_nli = tb_nli.text_frame
    tf_nli.word_wrap = True

    p = tf_nli.paragraphs[0]
    p.text = "DeBERTa-v3 & Temperature Scaling"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)

    nli_bullets = [
        ("Disentangled Attention:", "DeBERTa-v3 projects content and relative position vectors into separate matrices, drastically improving syntactic awareness of negation and scope."),
        ("Logit Overconfidence:", "Raw neural networks exhibit severe overconfidence. Softmax probabilities cluster at >0.95 even on incorrect predictions."),
        ("Temperature Calibration (T=1.35):", "Logits are scaled via P(y=k) = exp(z_k / 1.35) / sum(exp(z_j / 1.35)). Expected Calibration Error (ECE) dropped from 0.142 to 0.038."),
        ("Non-Uniform Decision Thresholds:", "Supported requires P_E >= 0.75; Contradicted requires P_C >= 0.70; otherwise classified as NEI. Reflects real-world cost asymmetry.")
    ]
    for bt, bd in nli_bullets:
        pb = tf_nli.add_paragraph()
        pb.text = f"•  <b>{bt}</b>  {bd}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_after = Pt(8)

    # Right Card: SymPy Verifier
    add_card(s8, 10.3, 2.3, 8.7, 7.8, bg_color=C_PANEL_TAN)
    tb_sym = s8.shapes.add_textbox(Inches(10.7), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_sym = tb_sym.text_frame
    tf_sym.word_wrap = True

    p = tf_sym.paragraphs[0]
    p.text = "Deterministic SymPy Math Engine"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)

    sym_bullets = [
        ("Neural Math Failure:", "Language models are notorious for arithmetic drift, sign errors, and plausible calculation hallucinations."),
        ("AST Parsing:", "Mathematical assertions are routed directly to SymPy, parsed into Abstract Syntax Trees, and solved symbolically."),
        ("Exact Equivalence Testing:", "Evaluates expressions: f(x) == g(x). Zero approximation or floating-point rounding errors."),
        ("Deterministic Certainty:", "If SymPy proves an identity false, it emits a deterministic Contradiction with P_C = 1.0, bypassing neural ambiguity."),
        ("Example:", "'$500 compounded at 10% for 2 years equals $650' -> SymPy evaluates 500*(1.1)^2 = 605 != 650 -> Contradiction confirmed.")
    ]
    for bt, bd in sym_bullets:
        pb = tf_sym.add_paragraph()
        pb.text = f"•  <b>{bt}</b>  {bd}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_after = Pt(8)

    # =========================================================================
    # SLIDE 9: UNIVERSAL AI INVESTIGATION
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "8. Universal AI Arbiter", "Universal Multi-Perspective AI Investigation Engine", "Symmetrical Stage 2 fact-checking across Supported, Contradicted, and NEI claims")
    add_footer(s9, 9)

    stage2_cards = [
        ("SUPPORTED Investigation", "Adversarial Counter-Evidence Hunting", [
            "Does not assume initial entailment is correct.",
            "Generates adversarial counter-queries targeting known exceptions.",
            "Checks numerical boundaries and temporal validity.",
            "Detects subtle qualifier violations (e.g., 'all' vs 'some').",
            "Result: Caught 14 false positive Supported claims in benchmark."
        ], C_ACCENT_GRN),
        ("CONTRADICTED Investigation", "Nuance & Context Verification", [
            "Verifies whether contradiction stems from out-of-date facts.",
            "Distinguishes between direct falsehoods and active scientific debate.",
            "Checks for differing regional conventions or unit definitions.",
            "Ensures system does not falsely flag legitimate alternative truths.",
            "Result: Prevents false accusations of AI hallucination."
        ], C_ACCENT_RED),
        ("NOT ENOUGH INFO Investigation", "Targeted Deep Decomposition", [
            "Decomposes unverified claims into targeted sub-questions.",
            "Formulates secondary search vectors across deep corpora.",
            "Consults PubMed and ArXiv specialized domain adapters.",
            "Converts ambiguous claims into verified verdicts where possible.",
            "Result: Reduced unnecessary NEI classifications by 22%."
        ], C_ACCENT_GLD)
    ]
    for i, (title, sub, bullets, accent) in enumerate(stage2_cards):
        x = 1.0 + (i * 6.15)
        add_card(s9, x, 2.3, col_w, 7.8, bg_color=C_CARD_LIGHT)
        tb = s9.shapes.add_textbox(Inches(x + 0.35), Inches(2.6), Inches(col_w - 0.7), Inches(7.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = C_PRIMARY
        ps.space_after = Pt(14)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(10)

    # =========================================================================
    # SLIDE 10: MODULE 4 — RELIABILITY SCORING
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "9. Module 4: Reliability Scoring", "M4: Non-Compensatory Answer Reliability Scoring", "The weakest-link mathematical formulation preventing lethal errors from being masked by true statements")
    add_footer(s10, 10)

    add_card(s10, 1.0, 2.3, 8.7, 7.8, bg_color=C_CARD_LIGHT)
    tb_m4 = s10.shapes.add_textbox(Inches(1.4), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_m4 = tb_m4.text_frame
    tf_m4.word_wrap = True

    p = tf_m4.paragraphs[0]
    p.text = "The Weakest-Link Principle"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)

    m4_bullets = [
        ("The Linear Averaging Fallacy:", "In high-stakes domains (medicine, law, flight control), 9 verified facts do NOT compensate for 1 fatal falsehood. Averaging 90% true + 0% = 90% (High Trust) is lethal."),
        ("Claim Reliability Formula rho(c):", "rho(c) = w_auth * w_rel * P_E for Supported; rho(c) = 0.0 for Contradicted; rho(c) = 0.50 * P_N for NEI."),
        ("Non-Compensatory Global Formula:", "R(A) = min( (1/n) * sum(rho(c_i)), 1.0 - max(P_C) ). Bounded strictly by the maximum contradiction probability."),
        ("Safety Guarantee:", "If ANY single claim contains a high-confidence contradiction (P_C = 0.95), global Answer Reliability cannot exceed 5.0%, instantly flagging a Critical Hallucination.")
    ]
    for bt, bd in m4_bullets:
        pb = tf_m4.add_paragraph()
        pb.text = f"•  <b>{bt}</b>  {bd}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_after = Pt(8)

    # Right Card: Trust Tiers
    add_card(s10, 10.3, 2.3, 8.7, 7.8, bg_color=C_PANEL_TAN)
    tb_tiers = s10.shapes.add_textbox(Inches(10.7), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_tiers = tb_tiers.text_frame
    tf_tiers.word_wrap = True

    p = tf_tiers.paragraphs[0]
    p.text = "Operational Trust Categories"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(12)

    tier_cards = [
        ("HIGH TRUST (>= 80%)", "All atomic claims supported by authoritative evidence. Zero contradictions. Safe for autonomous downstream usage.", C_ACCENT_GRN),
        ("QUALIFIED TRUST (60% – 79%)", "Majority of claims supported; minor unverified (NEI) claims present. Zero contradictions. Acceptable with advisory.", C_SECONDARY),
        ("LOW TRUST (40% – 59%)", "Multiple unverified claims or borderline evidence ambiguity. Human-in-the-loop audit strictly recommended.", C_ACCENT_GLD),
        ("CRITICAL HALLUCINATION (< 40%)", "At least one factual contradiction detected. Document immediately rejected for mission-critical use.", C_ACCENT_RED)
    ]
    for tt, td, tc in tier_cards:
        pt = tf_tiers.add_paragraph()
        pt.text = f"<b>{tt}</b>"
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = tc
        pt.space_after = Pt(2)
        
        pd = tf_tiers.add_paragraph()
        pd.text = td
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = C_TEXT_DARK
        pd.space_after = Pt(8)

    # =========================================================================
    # SLIDE 11: MODULE 5 — GROUNDED PARAGRAPH CORRECTION
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10. Module 5: Grounded Correction", "M5: Grounded Paragraph Correction Engine", "Verify-Then-Accept protocol with semantic deduplication and non-destructive surgical patching")
    add_footer(s11, 11)

    m5_cols = [
        ("Verify-Then-Accept Protocol", "Preventing Secondary Hallucinations", [
            "Draft generation: M5 synthesizes an in-place correction using retrieved evidence.",
            "Secondary NLI Check: Candidate patch must pass DeBERTa-v3 check against evidence (P_E >= 0.80).",
            "Surgical Patching: Replaces only the contradicted entity span; preserves surrounding tone and style.",
            "Fallback: If draft fails NLI, system falls back to direct evidence quotation.",
            "False Correction Rate: Kept to an exceptional 3.48%."
        ], C_PRIMARY),
        ("Semantic Deduplication Fix", "Resolving the Duplicate Correction Bug", [
            "Bug Observed: When multiple claims from one sentence were contradicted, M5 repeated the correction twice.",
            "Fix 1: Parent Sentence ID Tracking maps atomic claims to original sentence boundaries.",
            "Fix 2: SBERT Cosine Similarity Deduplication merges corrections exceeding threshold sigma = 0.85.",
            "Fix 3: Single-pass text reconstruction buffer eliminates duplicate sentence emission.",
            "Result: 100% resolution of duplicate sentence generation."
        ], C_SECONDARY),
        ("Style & Tone Preservation", "Non-Destructive Text Surgery", [
            "Zero unconstrained rewrites: Avoids prompting an LLM to rewrite the entire text.",
            "Minimum Edit Distance: Changes the minimum number of tokens necessary to achieve factual truth.",
            "Preserves Authorship: Keeps original grammar, transition words, and stylistic voice intact.",
            "Interactive Diff Viewer: Highlights original falsehoods in red and verified patches in green."
        ], C_ACCENT_GRN)
    ]
    for i, (title, sub, bullets, accent) in enumerate(m5_cols):
        x = 1.0 + (i * 6.15)
        add_card(s11, x, 2.3, col_w, 7.8, bg_color=C_CARD_LIGHT)
        tb = s11.shapes.add_textbox(Inches(x + 0.35), Inches(2.6), Inches(col_w - 0.7), Inches(7.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = C_PRIMARY
        ps.space_after = Pt(14)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(10)

    # =========================================================================
    # SLIDE 12: TECH STACK & IMPLEMENTATION
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11. Implementation Details", "Technology Stack & Modular Monolith Architecture", "Enterprise-grade Python 3.11 backend and modern React 18 responsive dashboard")
    add_footer(s12, 12)

    tech_cards = [
        ("Core Backend Runtime", "Python 3.11.9 + FastAPI ASGI", [
            "FastAPI non-blocking asynchronous request pipeline with automatic OpenAPI documentation.",
            "Strict typing and serialization contracts using Pydantic v2 schemas.",
            "Lifespan event handlers for GPU model pre-loading and cache initialization.",
            "Asynchronous thread pools for heavy PyTorch neural inference."
        ]),
        ("NLP & Deep Learning", "DeBERTa-v3, SBERT, SpaCy & SymPy", [
            "PyTorch 2.6 hosting cross-encoder/nli-deberta-v3-base and ms-marco reranker.",
            "sentence-transformers/all-MiniLM-L6-v2 for 384-dimensional dense semantic embeddings.",
            "SpaCy v3.8 (en_core_web_sm) for tokenization, dependency parsing, and NER.",
            "SymPy 1.13 for exact symbolic mathematics and equation verification."
        ]),
        ("Vector & Storage Layer", "ChromaDB, BM25 & SQLite", [
            "ChromaDB local vector store for fast embedding similarity search.",
            "rank-bm25 Okapi lexical index for exact keyword matching.",
            "SQLite relational persistence with SQLAlchemy 2.0 ORM abstraction.",
            "Zero-migration architecture ready for enterprise PostgreSQL."
        ]),
        ("Frontend Application", "React 18 + Vite + Tailwind CSS", [
            "React 18 component-driven architecture with Vite HMR.",
            "Tailwind CSS v3 implementing MAVIS warm ivory theme.",
            "Lucide React vector icon library for visual status cues.",
            "Side-by-side visual diff viewer with interactive evidence drawer."
        ])
    ]
    for i, (title, sub, bullets) in enumerate(tech_cards):
        row = i // 2
        col = i % 2
        x = 1.0 + (col * 9.2)
        y = 2.3 + (row * 3.9)
        add_card(s12, x, y, 8.8, 3.5, bg_color=C_CARD_LIGHT)
        tb = s12.shapes.add_textbox(Inches(x + 0.35), Inches(y + 0.25), Inches(8.1), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(10.5)
        ps.font.bold = True
        ps.font.color.rgb = C_SECONDARY
        ps.space_after = Pt(8)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(10)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(4)

    # =========================================================================
    # SLIDE 13: DATABASE & APIS
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "12. Data & APIs", "Relational Database Schema & RESTful API Specifications", "Complete audit provenance and high-throughput asynchronous communication contracts")
    add_footer(s13, 13)

    add_card(s13, 1.0, 2.3, 8.7, 7.8, bg_color=C_CARD_LIGHT)
    tb_db = s13.shapes.add_textbox(Inches(1.4), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_db = tb_db.text_frame
    tf_db.word_wrap = True

    p = tf_db.paragraphs[0]
    p.text = "Relational Provenance Schema"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)

    db_details = [
        ("verification_requests:", "Tracks request_id, raw_text, answer_reliability, trust_category, claim counts, and corrected_text."),
        ("atomic_claims:", "Stores claim_id, request_id, claim_text, verdict (Supported, Contradicted, NEI), calibrated probabilities (P_E, P_C, P_N), and quality_gate_passed."),
        ("evidence_passages:", "Stores passage_id, claim_id, source_corpus, passage_text, rrf_rank, and rerank_score."),
        ("audit_metrics:", "Logs processing latency, token counts, cache hits, and arbiter reasoning notes."),
        ("Foreign Key Integrity:", "Cascading foreign keys guarantee complete end-to-end provenance for regulatory auditing.")
    ]
    for dbt, dbd in db_details:
        pb = tf_db.add_paragraph()
        pb.text = f"•  <b>{dbt}</b>  {dbd}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_after = Pt(8)

    # Right Card: REST APIs
    add_card(s13, 10.3, 2.3, 8.7, 7.8, bg_color=C_PANEL_TAN)
    tb_api = s13.shapes.add_textbox(Inches(10.7), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_api = tb_api.text_frame
    tf_api.word_wrap = True

    p = tf_api.paragraphs[0]
    p.text = "RESTful Endpoint Architecture"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)

    api_details = [
        ("POST /api/v1/verify:", "Primary verification endpoint. Ingests raw text, returns claim breakdown, calibrated confidences, citations, and patches."),
        ("GET /api/v1/history:", "Returns paginated audit history with summary statistics, trust categories, and filter parameters."),
        ("GET /api/v1/history/{id}:", "Granular retrieval of complete claim-to-evidence graph for a specific verification execution."),
        ("POST /api/v1/export/pdf:", "Generates formal executive verification PDF reports with executive summary and side-by-side diffs."),
        ("Security & Guards:", "CORS middleware, payload length guards (max 10k chars), and IP-based rate limiting.")
    ]
    for apt, apd in api_details:
        pb = tf_api.add_paragraph()
        pb.text = f"•  <b>{apt}</b>  {apd}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_after = Pt(8)

    # =========================================================================
    # SLIDE 14: FRONTEND WORKFLOW
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "13. User Experience", "Frontend Dashboard & Interactive Verification Workflow", "Dual-pane analytical interface with claim-to-evidence visual grounding and side-by-side diffs")
    add_footer(s14, 14)

    fe_cards = [
        ("Step 1: Ingestion & Domain Setup", "Input Workspace & Presets", [
            "User inputs arbitrary LLM text into the responsive input workspace.",
            "Optional domain selection: General, Biomedical, Physics, History.",
            "Configurable verification strictness thresholds.",
            "One-click sample loading for quick demonstration."
        ]),
        ("Step 2: Real-Time Pipeline Stepper", "Visual Stage Indicators", [
            "Live progress tracking across M1 -> M2 -> Quality Gate -> M3 -> Arbiter -> M4 -> M5.",
            "Real-time feedback on claim extraction and retrieval counts.",
            "Eliminates user uncertainty during multi-stage inference.",
            "Instant error trapping and user notifications."
        ]),
        ("Step 3: Dual-Pane Grounding", "Claim-to-Evidence Spotlight", [
            "Left pane displays original text with color-coded sentence highlighting.",
            "Right pane shows interactive claim cards with verdict status badges.",
            "Clicking a claim card spotlights the sentence and expands evidence drawer.",
            "Displays RRF rank, cross-encoder score, and calibrated probabilities."
        ]),
        ("Step 4: Surgical Diff & Export", "In-Place Patching & Reports", [
            "Side-by-side diff viewer highlighting red strikethroughs vs green patches.",
            "Executive PDF Report generation for management audits.",
            "Research JSON export with complete logit distributions.",
            "Tabular CSV export for downstream data pipelines."
        ])
    ]
    for i, (title, sub, bullets) in enumerate(fe_cards):
        row = i // 2
        col = i % 2
        x = 1.0 + (col * 9.2)
        y = 2.3 + (row * 3.9)
        add_card(s14, x, y, 8.8, 3.5, bg_color=C_CARD_LIGHT)
        tb = s14.shapes.add_textbox(Inches(x + 0.35), Inches(y + 0.25), Inches(8.1), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(10.5)
        ps.font.bold = True
        ps.font.color.rgb = C_SECONDARY
        ps.space_after = Pt(8)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(10)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(4)

    # =========================================================================
    # SLIDE 15: EXPERIMENTAL BENCHMARKS
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "14. Evaluation & Results", "Experimental Benchmarks: TruthGuard-350 Multi-Domain", "Empirical validation across 350 annotated claims across 10 academic and scientific domains")
    add_footer(s15, 15)

    # KPI Row
    bench_kpis = [
        ("82.86%", "Overall Accuracy", "290 / 350 Correctly Classified", C_PRIMARY),
        ("93.78%", "Contradiction F1", "Precision 93.39% | Recall 94.17%", C_ACCENT_RED),
        ("98.63%", "Supported Precision", "Near-Zero False Entailments", C_ACCENT_GRN),
        ("100.0%", "Retrieval Relevance", "Quality Gate Zero Noise Filtering", C_SECONDARY),
    ]
    for i, (b_val, b_lbl, b_sub, b_col) in enumerate(bench_kpis):
        add_metric_badge(s15, 1.0 + (i * 4.6), 2.3, 4.3, 1.8, b_val, b_lbl, b_sub, b_col)

    # Table on Slide 15
    rows, cols = 4, 5
    tbl_shape = s15.shapes.add_table(rows, cols, Inches(1.0), Inches(4.5), Inches(18.0), Inches(2.5))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(4.0)
    tbl.columns[1].width = Inches(3.5)
    tbl.columns[2].width = Inches(3.5)
    tbl.columns[3].width = Inches(3.5)
    tbl.columns[4].width = Inches(3.5)

    headers = ["Evaluation Metric", "Supported Class", "Contradicted Class", "Not Enough Info (NEI)", "Macro Average"]
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PANEL_TAN
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY
        p.alignment = PP_ALIGN.CENTER

    data = [
        ["Precision", "98.63%", "93.39%", "67.31%", "86.44%"],
        ["Recall", "60.00%", "94.17%", "95.45%", "83.21%"],
        ["F1-Score", "74.61%", "93.78%", "78.95%", "82.44%"]
    ]
    for r_idx, row_data in enumerate(data):
        for c_idx, val in enumerate(row_data):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD_LIGHT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11)
            p.font.bold = (c_idx == 0 or c_idx == 4 or (r_idx == 2 and c_idx == 2))
            p.font.color.rgb = C_TEXT_DARK
            p.alignment = PP_ALIGN.CENTER

    # Bottom Callout Box
    add_card(s15, 1.0, 7.3, 18.0, 2.8, bg_color=C_CARD_LIGHT)
    tb_bc = s15.shapes.add_textbox(Inches(1.4), Inches(7.5), Inches(17.2), Inches(2.3))
    tf_bc = tb_bc.text_frame
    tf_bc.word_wrap = True

    p = tf_bc.paragraphs[0]
    p.text = "Operational Metrics & Benchmark Insights"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(4)

    bc_text = (
        "•  <b>False Correction Rate: 3.48%</b> — Kept exceptionally low via the Verify-Then-Accept protocol.<br/>"
        "•  <b>Citation Accuracy: 95.0%</b> — Grounded citations directly align with specific claim propositions.<br/>"
        "•  <b>Inference Latency: 0.680s / claim</b> — Mean processing latency allows interactive real-time fact-checking.<br/>"
        "•  <b>Asymmetric Threshold Impact:</b> Setting tau_e = 0.75 yielded 98.63% Supported Precision, eliminating false entailments in high-stakes contexts."
    )
    pb = tf_bc.add_paragraph()
    pb.text = bc_text
    pb.font.size = Pt(11)
    pb.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 16: REAL TEST CASES
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "15. Case Studies", "Real-World Verification Case Studies", "Demonstrating pipeline behavior across scientific, historical, biomedical, and mathematical inputs")
    add_footer(s16, 16)

    cases = [
        ("Case A: Gas Giant Colonization", "Astronomy / Space Science",
         "Input: 'NASA confirmed in 2024 that humans established a colony on Jupiter named Jupiter One.'\n\n"
         "• M1: Decomposed into 3 atomic propositions.\n"
         "• M2: Retrieved NASA Planetary Factsheet.\n"
         "• Quality Gate: PASSED (Entity: Jupiter).\n"
         "• M3 NLI: Contradiction (P_C = 0.98).\n"
         "• M4 Score: 2.0% (Critical Hallucination).\n"
         "• M5 Fix: In-place patch without duplication.", C_ACCENT_RED),
        ("Case B: Vitamin C & Collagen", "Biomedical & Nutrition",
         "Input: 'Vitamin C is an essential nutrient that acts as a cofactor for collagen synthesis.'\n\n"
         "• M1: Decomposed into nutrient & cofactor claims.\n"
         "• M2: PubMed search retrieved biochemical papers.\n"
         "• Quality Gate: Blocked spurious heart anatomy noise.\n"
         "• M3 NLI: Entailment (P_E = 0.94).\n"
         "• M4 Score: 94.0% (High Trust).\n"
         "• M5: Verified factual; no correction needed.", C_ACCENT_GRN),
        ("Case C: SymPy Deterministic Proof", "Mathematical Computing",
         "Input: 'An investment of $500 compounded at 10% annually for 2 years yields $650.'\n\n"
         "• M1: Flagged as mathematical proposition.\n"
         "• M3 SymPy: Evaluates 500 * (1.1)^2 = 605 != 650.\n"
         "• Deterministic Contradiction: P_C = 1.0.\n"
         "• M4 Score: 0.0% (Critical Hallucination).\n"
         "• M5 Fix: Replaced $650 with verified $605.00.\n"
         "• Result: Zero neural arithmetic hallucination.", C_PRIMARY),
    ]
    for i, (title, sub, details, accent) in enumerate(cases):
        x = 1.0 + (i * 6.15)
        add_card(s16, x, 2.3, col_w, 7.8, bg_color=C_CARD_LIGHT)
        tb = s16.shapes.add_textbox(Inches(x + 0.35), Inches(2.6), Inches(col_w - 0.7), Inches(7.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = C_PRIMARY
        ps.space_after = Pt(12)

        for line in details.split("\n"):
            pl = tf.add_paragraph()
            pl.text = line
            pl.font.size = Pt(10.5)
            pl.font.color.rgb = C_TEXT_DARK
            pl.space_after = Pt(3)

    # =========================================================================
    # SLIDE 17: LIMITATIONS & FUTURE ROADMAP
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "16. Roadmap & Vision", "Current System Boundaries & Future Research Roadmap", "Honest academic documentation of operational boundaries and planned v3.0 capabilities")
    add_footer(s17, 17)

    add_card(s17, 1.0, 2.3, 8.7, 7.8, bg_color=C_CARD_LIGHT)
    tb_lim = s17.shapes.add_textbox(Inches(1.4), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_lim = tb_lim.text_frame
    tf_lim.word_wrap = True

    p = tf_lim.paragraphs[0]
    p.text = "Current Operational Boundaries"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_RED
    p.space_after = Pt(10)

    limits = [
        ("Multi-Hop Reasoning:", "Verifying claims requiring synthesis across 4+ chained documents remains computationally expensive and susceptible to retrieval drift."),
        ("Cross-Lingual Verification:", "Non-English claims rely on automated translation to English proxies; native multilingual cross-encoders are required for regional nuance."),
        ("Multimodal & Tabular Data:", "Currently verifies textual propositions; verifying claims grounded in complex multi-column spreadsheets or charts requires vision-language models."),
        ("Closed-Domain Private Corpora:", "Indexing private enterprise intranets requires custom authentication connectors and data ingestion pipelines.")
    ]
    for lt, ld in limits:
        pb = tf_lim.add_paragraph()
        pb.text = f"•  <b>{lt}</b>  {ld}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_after = Pt(8)

    # Right Card: Roadmap
    add_card(s17, 10.3, 2.3, 8.7, 7.8, bg_color=C_PANEL_TAN)
    tb_rm = s17.shapes.add_textbox(Inches(10.7), Inches(2.6), Inches(7.9), Inches(7.2))
    tf_rm = tb_rm.text_frame
    tf_rm.word_wrap = True

    p = tf_rm.paragraphs[0]
    p.text = "TruthGuard v3.0 Planned Extensions"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_GRN
    p.space_after = Pt(10)

    roadmap = [
        ("Autonomous Streaming Crawlers:", "Continuous background indexing of pre-print servers, regulatory filings, and news feeds for zero-latency retrieval."),
        ("Edge Model Distillation:", "Distilling the 435M DeBERTa-v3 cross-encoder into an ONNX-optimized 60M student model for on-device mobile verification."),
        ("Vision-Language Grounding:", "Extending the Quality Gate to verify infographic, chart, and medical imaging data via multimodal transformers."),
        ("Distributed GPU Cluster:", "Deploying Celery task queues backed by Redis to scale verification throughput to thousands of documents per hour.")
    ]
    for rt, rd in roadmap:
        pb = tf_rm.add_paragraph()
        pb.text = f"•  <b>{rt}</b>  {rd}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_after = Pt(8)

    # =========================================================================
    # SLIDE 18: CONCLUSION & SUMMARY
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18)
    add_header(s18, "17. Conclusion & Viva Summary", "Summary of Contributions & Academic Defense Takeaways", "TruthGuard establishes an end-to-end deterministic proof desk for reliable GenAI deployment")
    add_footer(s18, 18)

    c_cards = [
        ("Key Innovation 1: Universal AI Investigation", "Decoupled Verification Desk", [
            "Transformed one-sided fact checking into symmetrical Stage 2 investigation.",
            "Actively hunts for counter-evidence across Supported and Contradicted claims.",
            "Eliminated false entailments stemming from quantifier inflation.",
            "Achieved 93.78% Contradiction F1 score on TruthGuard-350."
        ]),
        ("Key Innovation 2: Weakest-Link Reliability", "Non-Compensatory Scoring", [
            "Replaced naive linear averaging with R(A) = min(mean, 1 - max(P_C)).",
            "Guarantees that a single lethal hallucination destroys global answer trust.",
            "Essential for clinical medicine, jurisprudence, and finance.",
            "Four calibrated trust tiers for automated decision systems."
        ]),
        ("Key Innovation 3: Verify-Then-Accept Patching", "Surgical Grounded Edits", [
            "Resolved the duplicate paragraph correction bug via semantic deduplication.",
            "Enforced secondary DeBERTa-v3 NLI check before accepting candidate edits.",
            "Maintains an exceptional 3.48% False Correction Rate.",
            "Preserves original author style, voice, and non-contradicted context."
        ])
    ]
    for i, (title, sub, bullets) in enumerate(c_cards):
        x = 1.0 + (i * 6.15)
        add_card(s18, x, 2.3, col_w, 7.8, bg_color=C_CARD_LIGHT)
        tb = s18.shapes.add_textbox(Inches(x + 0.35), Inches(2.6), Inches(col_w - 0.7), Inches(7.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY
        p.space_after = Pt(2)

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = C_SECONDARY
        ps.space_after = Pt(14)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_after = Pt(10)

    # Save PPTX
    prs.save(PPTX_PATH)
    print(f"[Success] Generated PowerPoint Presentation: {PPTX_PATH}")
    print(f"[File Size] {os.path.getsize(PPTX_PATH)} bytes")

def convert_pptx_to_pdf(pptx_file, pdf_file):
    print("[Starting] Exporting PPTX to PDF via PowerPoint COM...")
    pythoncom.CoInitialize()
    ppt = None
    try:
        ppt = win32com.client.Dispatch("PowerPoint.Application")
        prs = ppt.Presentations.Open(pptx_file, WithWindow=False)
        # ppSaveAsPDF = 32
        prs.SaveAs(pdf_file, 32)
        prs.Close()
        print(f"[Success] Exported Presentation PDF: {pdf_file}")
        print(f"[File Size] {os.path.getsize(pdf_file)} bytes")
    except Exception as e:
        print(f"[Warning] PowerPoint COM export failed ({e})")
    finally:
        if ppt:
            try:
                ppt.Quit()
            except Exception:
                pass

if __name__ == "__main__":
    build_presentation()
    convert_pptx_to_pdf(PPTX_PATH, PDF_PATH)
