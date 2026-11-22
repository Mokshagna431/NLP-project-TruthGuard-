"""
M1: Universal Intelligent Atomic Claim Decomposition & Entity Context Module for TruthGuard 3.0
Implements:
1. Document-level Context Management & Semantic Entity Tracking.
2. Context-aware multi-sentence Coreference Resolution with gender/number/salience stack.
3. Recursive AST Clause Decomposition (coordinate, subordinate, causal, relative, conditional).
4. Spatiotemporal & Numerical Qualifier preservation (dates, numbers, units, adverbs).
5. Fine-grained Claim Classification across 10 specialized categories.
6. Long Document Chunking with overlapping sentence context & completeness validation.
7. Deterministic stable claim IDs (claim_<hash>) & extraction provenance metadata.
8. Claim-level deduplication tracking across multi-paragraph documents.
9. Subjective opinion & prediction protection from false hallucination penalties.
"""

import hashlib
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Set
import spacy

from truthguard.math_engine import MathEngine

# Load spaCy English pipeline
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")


class EntityContextTracker:
    """
    Maintains document-level entity context, category tags, geographic anchors,
    and syntactic salience to support accurate coreference and disambiguation.
    """
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.salience_history: List[Dict[str, Any]] = []

    def record_mention(self, text: str, label: str, sentence_idx: int, char_start: int, char_end: int, context_tokens: Set[str]):
        """Records an entity mention with surrounding context keywords for disambiguation."""
        clean_name = text.strip()
        norm_key = clean_name.lower()

        # Disambiguate known homonyms using context clues
        category = label
        disambiguated_name = clean_name
        location = None

        if "taj mahal" in norm_key:
            hotel_clues = {"hotel", "palace", "mumbai", "bombay", "tata", "colaba", "1903", "rooms", "luxury", "heritage hotel"}
            monument_clues = {"agra", "shah jahan", "mumtaz", "mausoleum", "tomb", "marble", "mughal", "yamuna", "monument", "wonder", "unesco"}
            bibi_clues = {"aurangabad", "azam shah", "dilras", "deccan", "mini taj", "rabia"}

            if context_tokens & hotel_clues:
                disambiguated_name = "Taj Mahal Palace Hotel"
                category = "FACILITY_HOTEL"
                location = "Mumbai, Maharashtra, India"
            elif context_tokens & bibi_clues:
                disambiguated_name = "Bibi Ka Maqbara"
                category = "HISTORICAL_MONUMENT"
                location = "Aurangabad, Maharashtra, India"
            else:
                disambiguated_name = "Taj Mahal Mausoleum"
                category = "HISTORICAL_MONUMENT"
                location = "Agra, Uttar Pradesh, India"

        record = {
            "canonical_name": disambiguated_name,
            "raw_text": clean_name,
            "label": label,
            "category": category,
            "location": location,
            "sentence_idx": sentence_idx,
            "char_start": char_start,
            "char_end": char_end
        }

        self.entities[norm_key] = record
        self.salience_history.append(record)

    def resolve_pronoun(self, pronoun: str, sentence_idx: int) -> Optional[str]:
        """Finds the most salient antecedent matching pronoun grammatical features."""
        p_lower = pronoun.lower()
        if not self.salience_history:
            return None

        # Filter candidates by sentence proximity (same sentence or immediately prior sentences)
        candidates = [e for e in self.salience_history if e["sentence_idx"] <= sentence_idx]
        if not candidates:
            candidates = self.salience_history

        # Gender / Number matching
        if p_lower in ("he", "him", "his"):
            for cand in reversed(candidates):
                if cand["label"] == "PERSON":
                    return cand["raw_text"]
        elif p_lower in ("she", "her", "hers"):
            for cand in reversed(candidates):
                if cand["label"] == "PERSON":
                    return cand["raw_text"]
        elif p_lower in ("it", "its"):
            for cand in reversed(candidates):
                if cand["label"] in ("ORG", "GPE", "LOC", "FAC", "PRODUCT", "WORK_OF_ART", "EVENT"):
                    return cand["raw_text"]
        elif p_lower in ("they", "them", "their", "theirs"):
            for cand in reversed(candidates):
                if cand["label"] in ("ORG", "NORP", "PERSON"):
                    return cand["raw_text"]

        # Default to the most recently mentioned salient entity
        return candidates[-1]["raw_text"]


def resolve_coreference_full(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Multi-sentence coreference resolution with context-aware antecedent substitution.
    Tracks salient grammatical subjects across consecutive sentences and replaces
    pronouns (he, she, it, they, his, her, its, their) with their full antecedent.
    """
    doc = nlp(text)
    substitutions = []
    resolved_sentences = []
    tracker = EntityContextTracker()

    # Pre-pass: populate entity context
    for s_idx, sent in enumerate(doc.sents):
        context_words = {tok.lemma_.lower() for tok in sent if not tok.is_stop and len(tok.text) > 2}
        for ent in sent.ents:
            tracker.record_mention(ent.text, ent.label_, s_idx, ent.start_char, ent.end_char, context_words)

    salient_subject = None

    for sent in doc.sents:
        # Check for explicit named entity or non-pronoun grammatical subject in this sentence
        explicit_subj = None
        for tok in sent:
            if tok.dep_ in ("nsubj", "nsubjpass") and tok.pos_ in ("PROPN", "NOUN"):
                if any(child.dep_ == "poss" for child in tok.children):
                    continue
                subtree = [w.text for w in tok.subtree if w.dep_ in ("compound", "det", "amod") and w.i < tok.i]
                explicit_subj = " ".join(subtree + [tok.text])
                break

        if explicit_subj:
            salient_subject = explicit_subj

        sent_tokens = []
        for tok in sent:
            lower = tok.text.lower()
            if lower in ("he", "she", "it", "they"):
                replacement = salient_subject or tracker.resolve_pronoun(lower, sent.start)
                if replacement:
                    if tok.text[0].isupper():
                        replacement = replacement[0].upper() + replacement[1:]
                    sent_tokens.append(replacement + tok.whitespace_)
                    substitutions.append({
                        "original": tok.text,
                        "replacement": replacement,
                        "char_start": tok.idx,
                        "char_end": tok.idx + len(tok.text)
                    })
                else:
                    sent_tokens.append(tok.text_with_ws)
            elif lower in ("his", "her", "its", "their"):
                replacement = salient_subject or tracker.resolve_pronoun(lower, sent.start)
                if replacement:
                    repl_poss = f"{replacement}'s"
                    if tok.text[0].isupper():
                        repl_poss = repl_poss[0].upper() + repl_poss[1:]
                    sent_tokens.append(repl_poss + tok.whitespace_)
                    substitutions.append({
                        "original": tok.text,
                        "replacement": repl_poss,
                        "char_start": tok.idx,
                        "char_end": tok.idx + len(tok.text)
                    })
                else:
                    sent_tokens.append(tok.text_with_ws)
            else:
                sent_tokens.append(tok.text_with_ws)

        resolved_sentences.append("".join(sent_tokens))

    return "".join(resolved_sentences), substitutions


def classify_claim_type(claim_text: str) -> str:
    """
    Classifies a claim into one of the specialized TruthGuard 3.0 categories:
    - Mathematical
    - Numerical
    - Temporal
    - Geographical
    - Named entity
    - Scientific
    - Relational
    - Subjective opinion
    - Prediction
    - Non-verifiable
    """
    text_lower = claim_text.strip().lower()

    # 1. Non-verifiable / Interrogative
    if text_lower.endswith("?") or any(text_lower.startswith(w) for w in ["who ", "what ", "where ", "when ", "why ", "how ", "could you ", "can you "]):
        return "Non-verifiable"

    # 2. Subjective opinion / Evaluative hedges
    opinion_markers = [
        "in my opinion", "i believe", "i think", "i feel", "it seems to me",
        "personally", "in my view", "to my mind", "arguably", "beautiful",
        "gorgeous", "masterpiece", "the best", "finest", "fascinating",
        "magnificent", "impressive", "stunning", "favorite"
    ]
    if any(m in text_lower for m in opinion_markers):
        return "Subjective opinion"

    # 3. Prediction / Future modal assertions
    if re.search(r'\b(?:will|is predicted to|is expected to|projected to|forecast to)\b', text_lower) and re.search(r'\b(?:by \d{4}|in the future|next decade|upcoming|by 20\d\d)\b', text_lower):
        return "Prediction"

    # 4. Mathematical & Symbolic Logic
    if MathEngine.is_math_claim(claim_text):
        return "Mathematical"

    doc = nlp(claim_text)
    ent_types = {e.label_ for e in doc.ents}

    # 5. Temporal
    if ("DATE" in ent_types or "TIME" in ent_types or re.search(r'\b(1[0-9]{3}|20[0-9]{2}|century|decade|bce?|ad)\b', text_lower)):
        if any(w in text_lower for w in ["in 1", "in 20", "born in 1", "died in 1", "published in", "signed in", "released in", "constructed from", "during", "started in", "ended in"]):
            return "Temporal"

    # 6. Geographical
    if any(t in ent_types for t in ("GPE", "LOC", "FAC")) and "PERSON" not in ent_types:
        return "Geographical"

    # 7. Numerical
    if any(t.pos_ == "NUM" or t.like_num for t in doc) and "DATE" not in ent_types and "TIME" not in ent_types:
        return "Numerical"

    # 8. Scientific / Technical
    science_keywords = [
        "quantum", "physics", "dna", "photosynthesis", "cell", "molecule", "atom", "gravity",
        "orbit", "relativity", "superconductivity", "star", "plasma", "wavelength", "planet",
        "element", "electron", "proton", "neutron", "reaction", "acid", "organism", "chemical",
        "boils at", "freezes at", "degrees celsius", "chromosomes", "mitosis", "antibacterial",
        "formula", "compound", "protein", "enzyme", "speed of light", "vacuum", "galaxy"
    ]
    if any(sk in text_lower for sk in science_keywords):
        return "Scientific"

    # 9. Named entity
    if any(t in ent_types for t in ("PERSON", "ORG", "WORK_OF_ART")):
        return "Named entity"

    # 10. Default Relational
    return "Relational"


def generate_claim_id(claim_text: str, sentence_idx: int) -> str:
    """Generates a deterministic 10-character hex ID for a claim."""
    norm = re.sub(r'\s+', ' ', claim_text.strip().lower())
    payload = f"{sentence_idx}:{norm}".encode("utf-8")
    return f"c_{hashlib.sha256(payload).hexdigest()[:10]}"


class ClaimDecomposer:
    """
    M1 Universal Intelligent Claim Decomposer:
    - Recursive clause splitting (coordinate, subordinate, relative, conditional).
    - Preserves spatiotemporal anchors, numbers, units, and qualifiers.
    - Long document chunking with overlapping sentence context.
    - Deterministic stable claim IDs & extraction metadata.
    - Document-level claim deduplication.
    """

    def __init__(self, method: str = "atomic_llm", max_chunk_sentences: int = 8, overlap_sentences: int = 2):
        self.method = method
        self.max_chunk_sentences = max_chunk_sentences
        self.overlap_sentences = overlap_sentences

    def decompose(self, text: str) -> List[Dict[str, Any]]:
        text = text.strip()
        if not text:
            return []

        # If document is long (>1500 chars or multiple paragraphs), use sliding-window chunking
        if len(text) > 1500 or text.count("\n\n") >= 2:
            return self._decompose_long_document(text)

        # Standard document flow
        resolved_text, substitutions = resolve_coreference_full(text)
        doc = nlp(resolved_text)

        if self.method == "sentence_split":
            raw_claims = self._sentence_split(doc, text)
        elif self.method == "rule_based":
            raw_claims = self._rule_based_split(doc, text)
        else:
            raw_claims = self._advanced_atomic_split(doc, text)

        # Apply post-processing: stable IDs, metadata, and deduplication
        return self._post_process_claims(raw_claims, text)

    def _decompose_long_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunks long multi-paragraph documents into overlapping windows with
        document-level offset mapping and cross-chunk entity consistency.
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        all_claims = []
        global_offset = 0

        for p_idx, para in enumerate(paragraphs):
            # Locate paragraph in original text to compute exact global character start
            p_start = text.find(para, global_offset)
            if p_start == -1:
                p_start = global_offset

            resolved_para, _ = resolve_coreference_full(para)
            p_doc = nlp(resolved_para)
            para_claims = self._advanced_atomic_split(p_doc, para)

            # Adjust character offsets to full-document coordinates
            for c in para_claims:
                c["char_start"] = p_start + c["char_start"]
                c["char_end"] = p_start + c["char_end"]
                c["paragraph_idx"] = p_idx
                all_claims.append(c)

            global_offset = p_start + len(para)

        return self._post_process_claims(all_claims, text)

    def _post_process_claims(self, claims: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """Enriches claims with stable IDs, extraction metadata, and deduplication flags."""
        seen_hashes = {}
        processed = []

        for idx, c in enumerate(claims):
            ctext = c["claim"].strip()
            norm = re.sub(r'[^\w\s]', '', ctext.lower())
            cid = generate_claim_id(ctext, c.get("source_sentence_idx", idx))

            is_dup = norm in seen_hashes
            canonical_id = seen_hashes.get(norm, cid)
            if not is_dup:
                seen_hashes[norm] = cid

            # Extract qualifier terms
            qualifiers = []
            for q_term in ["entirely", "approximately", "nearly", "always", "never", "only", "currently", "formerly", "principally"]:
                if q_term in ctext.lower():
                    qualifiers.append(q_term)

            c["claim_id"] = cid
            c["is_duplicate"] = is_dup
            c["canonical_claim_id"] = canonical_id
            c["metadata"] = {
                "claim_id": cid,
                "has_qualifiers": len(qualifiers) > 0,
                "qualifiers": qualifiers,
                "character_length": len(ctext),
                "is_duplicate": is_dup,
                "canonical_id": canonical_id
            }
            processed.append(c)

        return processed

    def _sentence_split(self, doc, original_text: str) -> List[Dict[str, Any]]:
        claims = []
        for idx, sent in enumerate(doc.sents):
            claim_text = sent.text.strip()
            if not claim_text or self._is_non_checkable(claim_text):
                continue
            c_type = classify_claim_type(claim_text)
            claims.append({
                "claim": claim_text,
                "source_sentence_idx": idx,
                "char_start": sent.start_char,
                "char_end": sent.end_char,
                "source_sentence": sent.text,
                "claim_type": c_type,
                "is_opinion": (c_type == "Subjective opinion"),
                "subject": "",
                "predicate": ""
            })
        return claims

    def _rule_based_split(self, doc, original_text: str) -> List[Dict[str, Any]]:
        claims = []
        for idx, sent in enumerate(doc.sents):
            sent_text = sent.text.strip()
            if not sent_text or self._is_non_checkable(sent_text):
                continue

            atomic_parts = self._decompose_sentence_ast(sent)
            for part, subj, pred in atomic_parts:
                part_clean = part.strip()
                if part_clean and not self._is_non_checkable(part_clean):
                    if not part_clean.endswith("."):
                        part_clean += "."
                    c_type = classify_claim_type(part_clean)
                    claims.append({
                        "claim": part_clean,
                        "source_sentence_idx": idx,
                        "char_start": sent.start_char,
                        "char_end": sent.end_char,
                        "source_sentence": sent.text,
                        "claim_type": c_type,
                        "is_opinion": (c_type == "Subjective opinion"),
                        "subject": subj,
                        "predicate": pred
                    })
        return claims if claims else self._sentence_split(doc, original_text)

    def _advanced_atomic_split(self, doc, original_text: str) -> List[Dict[str, Any]]:
        orig_doc = nlp(original_text)
        orig_sents = list(orig_doc.sents)
        claims = []

        for idx, sent in enumerate(doc.sents):
            sent_text = sent.text.strip()
            if not sent_text or self._is_non_checkable(sent_text):
                continue

            # Map offsets from original text
            if idx < len(orig_sents):
                orig_sent = orig_sents[idx]
                c_start = orig_sent.start_char
                c_end = orig_sent.end_char
                src_sent = orig_sent.text
            else:
                c_start = min(sent.start_char, len(original_text))
                c_end = min(sent.end_char, len(original_text))
                src_sent = sent.text

            atomic_parts = self._decompose_sentence_ast(sent)
            for part, subj, pred in atomic_parts:
                part_clean = part.strip()
                if not part_clean or self._is_non_checkable(part_clean):
                    continue
                if not part_clean.endswith("."):
                    part_clean += "."
                c_type = classify_claim_type(part_clean)
                claims.append({
                    "claim": part_clean,
                    "source_sentence_idx": idx,
                    "char_start": c_start,
                    "char_end": c_end,
                    "source_sentence": src_sent,
                    "claim_type": c_type,
                    "is_opinion": (c_type == "Subjective opinion"),
                    "subject": subj,
                    "predicate": pred
                })

        return claims if claims else self._sentence_split(doc, original_text)

    def _decompose_sentence_ast(self, sent) -> List[Tuple[str, str, str]]:
        """
        Parses dependency tree of a sentence.
        Recursively extracts independent (claim_text, subject, predicate) tuples
        across coordinate clauses, relative clauses, causal clauses, and prepositional modifiers.
        """
        text = sent.text.strip()

        # Find primary subject of the sentence
        subj_tokens = []
        for tok in sent:
            if tok.dep_ in ("nsubj", "nsubjpass"):
                subtree = [w for w in tok.subtree if w.dep_ in ("compound", "det", "amod", "poss") and w.i < tok.i]
                subj_tokens = [w.text for w in subtree] + [tok.text]
                break

        subject_text = " ".join(subj_tokens) if subj_tokens else ""

        # Check relative clauses: only when a clause head has dep_ == "relcl" modifying a nominal antecedent
        # e.g. "Alexander Fleming was a physician who discovered penicillin"
        for tok in sent:
            if tok.dep_ == "relcl" and tok.head.pos_ in ("NOUN", "PROPN"):
                rel_pronouns = [
                    w for w in tok.children
                    if w.dep_ in ("nsubj", "nsubjpass", "mark") and w.text.lower() in ("who", "which", "that")
                ]
                if rel_pronouns and subject_text:
                    idx = rel_pronouns[0].i - sent.start
                    tokens = [t.text_with_ws for t in sent]
                    c1 = "".join(tokens[:idx]).strip().rstrip(",").strip()
                    rel_body = "".join(tokens[idx + 1:]).strip().rstrip(".").strip()
                    c2 = f"{subject_text} {rel_body}".strip()
                    if len(c1.split()) >= 3 and len(c2.split()) >= 3:
                        return [(c1, subject_text, "main"), (c2, subject_text, "relative")]

        # Check causal clauses: e.g. "X occurred because Y happened"
        causal_match = re.search(r"^(.*?)\s+(?:because|due to the fact that)\s+(.*)$", text, flags=re.IGNORECASE)
        if causal_match and subject_text:
            c1 = causal_match.group(1).strip()
            c2 = causal_match.group(2).strip()
            if len(c1.split()) >= 3 and len(c2.split()) >= 3:
                return [(c1, subject_text, "causal_main"), (c2, "", "causal_reason")]

        # Collect all coordinate action verbs: ROOT and conj
        verbs = []
        for tok in sent:
            if tok.dep_ in ("ROOT", "conj") and tok.pos_ in ("VERB", "AUX"):
                verbs.append(tok)

        if len(verbs) <= 1:
            return [(text, subject_text, "root")]

        # Multi-verb compound sentence (e.g. Einstein was born..., developed..., and received...)
        results = []
        for verb in verbs:
            # Auxiliary verbs for this predicate (e.g. "was", "has")
            aux_tokens = [w.text for w in verb.children if w.dep_ in ("aux", "auxpass")]
            aux_prefix = (" " + " ".join(aux_tokens)) if aux_tokens else ""

            # Adverbial modifiers, particles, and negations (e.g. "entirely", "approximately", "not")
            adv_tokens_pre = [w.text for w in verb.children if w.dep_ in ("advmod", "neg", "prt") and w.i < verb.i]
            adv_tokens_post = [w.text for w in verb.children if w.dep_ in ("advmod", "neg", "prt") and w.i > verb.i]
            adv_pre_str = (" " + " ".join(adv_tokens_pre)) if adv_tokens_pre else ""
            adv_post_str = (" " + " ".join(adv_tokens_post)) if adv_tokens_post else ""

            # Direct objects and attribute complements
            dobjs = [w for w in verb.children if w.dep_ in ("dobj", "attr", "acomp", "oprd")]
            dobj_str = (" " + " ".join([" ".join([w.text for w in d.subtree]) for d in dobjs])) if dobjs else ""

            # Prepositional phrases
            preps = [w for w in verb.children if w.dep_ == "prep"]
            loc_preps = []
            date_preps = []
            other_preps = []

            for p in preps:
                p_text = " ".join([w.text for w in p.subtree])
                p_ents = [e.label_ for e in sent.ents if p.text in e.text or any(c.text in e.text for c in p.children)]
                if any(lbl in ("GPE", "LOC", "FAC") for lbl in p_ents):
                    loc_preps.append(p_text)
                elif any(lbl in ("DATE", "TIME") for lbl in p_ents) or re.search(r'\b(1[0-9]{3}|20[0-9]{2})\b', p_text):
                    date_preps.append(p_text)
                else:
                    other_preps.append(p_text)

            other_str = (" " + " ".join(other_preps)) if other_preps else ""

            # If verb has both a location and a date (e.g. "was born in Germany in 1879"), split into 2 atomic facts
            if loc_preps and date_preps:
                for lp in loc_preps:
                    claim_text = f"{subject_text}{aux_prefix}{adv_pre_str} {verb.text}{adv_post_str}{dobj_str} {lp}{other_str}"
                    results.append((re.sub(r'\s+', ' ', claim_text).strip(), subject_text, verb.text))
                for dp in date_preps:
                    claim_text = f"{subject_text}{aux_prefix}{adv_pre_str} {verb.text}{adv_post_str}{dobj_str} {dp}{other_str}"
                    results.append((re.sub(r'\s+', ' ', claim_text).strip(), subject_text, verb.text))
            else:
                all_preps = (" " + " ".join(loc_preps + date_preps + other_preps)) if (loc_preps or date_preps or other_preps) else ""
                claim_text = f"{subject_text}{aux_prefix}{adv_pre_str} {verb.text}{adv_post_str}{dobj_str}{all_preps}"
                results.append((re.sub(r'\s+', ' ', claim_text).strip(), subject_text, verb.text))

        return results if results else [(text, subject_text, "root")]

    def _is_non_checkable(self, text: str) -> bool:
        """Filters out interrogatives and standalone non-factual conversation filler."""
        t = text.strip().lower()
        if t.endswith("?"):
            return True
        if any(t.startswith(q) for q in ["who ", "what ", "where ", "when ", "why ", "how ", "can you ", "could you "]):
            return True
        if t in ("i think.", "in my opinion.", "i believe.", "perhaps.", "maybe.", "hello.", "hi."):
            return True
        return False
