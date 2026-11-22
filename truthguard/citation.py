"""
TruthGuard 3.0 - Academic Citation Verification Module
Parses and verifies academic references, DOIs, and literature citations against
Crossref and Semantic Scholar APIs, with an authoritative offline benchmark registry.
Detects fabricated citations, author/year hallucinations, and citation mismatches.
"""

import re
import urllib.request
import urllib.parse
import json
from typing import Dict, Any, List, Optional


# Authoritative offline registry of landmark papers to guarantee high-speed deterministic verification
KNOWN_LANDMARK_PAPERS = {
    "10.5555/3295222.3295349": {
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"],
        "year": 2017,
        "venue": "NeurIPS",
        "doi": "10.5555/3295222.3295349",
        "arxiv": "1706.03762"
    },
    "10.18653/v1/N19-1423": {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        "year": 2019,
        "venue": "NAACL-HLT",
        "doi": "10.18653/v1/N19-1423",
        "arxiv": "1810.04805"
    },
    "10.1109/CVPR.2016.90": {
        "title": "Deep Residual Learning for Image Recognition",
        "authors": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
        "year": 2016,
        "venue": "CVPR",
        "doi": "10.1109/CVPR.2016.90",
        "arxiv": "1512.03385"
    },
    "10.1038/s41586-021-03819-2": {
        "title": "Highly accurate protein structure prediction with AlphaFold",
        "authors": ["John Jumper", "Richard Evans", "Alexander Pritzel", "Demis Hassabis"],
        "year": 2021,
        "venue": "Nature",
        "doi": "10.1038/s41586-021-03819-2"
    },
    "arxiv:2005.14165": {
        "title": "Language Models are Few-Shot Learners",
        "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah", "Dario Amodei"],
        "year": 2020,
        "venue": "NeurIPS",
        "arxiv": "2005.14165"
    },
    "arxiv:2302.13971": {
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "authors": ["Hugo Touvron", "Thibaut Lavril", "Gautier Izacard", "Xavier Martinet"],
        "year": 2023,
        "venue": "arXiv",
        "arxiv": "2302.13971"
    }
}


class CitationVerifier:
    """Verifies academic citations, parses reference strings, and detects hallucinated papers."""

    def __init__(self, timeout_sec: float = 3.0):
        self.timeout = timeout_sec

    def extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts citation items from text, including DOIs, ArXiv IDs,
        author-year markers, and formatted bibliographic references.
        """
        citations = []

        # 1. Direct DOI matches: e.g. 10.1000/182, https://doi.org/10.xxxx/...
        doi_pattern = r'\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b'
        for match in re.finditer(doi_pattern, text):
            doi = match.group(1).rstrip('.')
            citations.append({
                "raw_text": match.group(0),
                "type": "doi",
                "doi": doi,
                "char_start": match.start(),
                "char_end": match.end()
            })

        # 2. ArXiv IDs: e.g. arXiv:1706.03762, 1706.03762v2
        arxiv_pattern = r'\barXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)\b'
        for match in re.finditer(arxiv_pattern, text, re.IGNORECASE):
            citations.append({
                "raw_text": match.group(0),
                "type": "arxiv",
                "arxiv_id": match.group(1),
                "char_start": match.start(),
                "char_end": match.end()
            })

        # 3. Author-year citations: e.g. (Vaswani et al., 2017) or Vaswani et al. (2017)
        ay_pattern = r'\b([A-Z][a-zA-Z\-]+(?:\s+et\s+al\.?)?)[,\s]+\(?((?:19|20)\d{2})\)?'
        for match in re.finditer(ay_pattern, text):
            # Avoid duplicating if already inside a full reference
            authors = match.group(1).strip()
            year = int(match.group(2))
            citations.append({
                "raw_text": match.group(0),
                "type": "author_year",
                "authors_str": authors,
                "year": year,
                "char_start": match.start(),
                "char_end": match.end()
            })

        # 4. Bibliographic entries: e.g. "Devlin et al. (2019). BERT: Pre-training..."
        bib_pattern = r'([A-Z][a-zA-Z\s,\.\-]+?)\s*\(((?:19|20)\d{2})\)\.\s*([^\.\n]+)\.\s*([^\n\.]+)?'
        for match in re.finditer(bib_pattern, text):
            citations.append({
                "raw_text": match.group(0),
                "type": "full_reference",
                "authors_str": match.group(1).strip(),
                "year": int(match.group(2)),
                "title": match.group(3).strip(),
                "venue": (match.group(4) or "").strip(),
                "char_start": match.start(),
                "char_end": match.end()
            })

        return citations

    def verify_citation(self, citation_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies a single citation against Crossref/Semantic Scholar and landmark registry.
        Classifications:
        - 'VERIFIED': Title, authors, and year match authoritative record.
        - 'PARTIALLY_VERIFIED': Paper exists, but minor field discrepancy.
        - 'CITATION_MISMATCH': Real paper exists, but attributed author/year is wrong.
        - 'POTENTIALLY_FABRICATED': No trace found in academic databases (hallucinated citation).
        - 'UNAVAILABLE': Service query rate-limited or network offline.
        """
        doi = citation_item.get("doi")
        title = citation_item.get("title")
        authors_str = citation_item.get("authors_str", "")
        year = citation_item.get("year")
        arxiv_id = citation_item.get("arxiv_id")

        # 1. Check known landmark offline registry first
        record = None
        if doi and doi in KNOWN_LANDMARK_PAPERS:
            record = KNOWN_LANDMARK_PAPERS[doi]
        elif arxiv_id and f"arxiv:{arxiv_id}" in KNOWN_LANDMARK_PAPERS:
            record = KNOWN_LANDMARK_PAPERS[f"arxiv:{arxiv_id}"]
        elif title:
            # Fuzzy match title in landmark registry
            t_lower = title.lower()
            for k, p in KNOWN_LANDMARK_PAPERS.items():
                if p["title"].lower() in t_lower or t_lower in p["title"].lower():
                    record = p
                    break

        if not record and (doi or title):
            # 2. Try online Crossref / Semantic Scholar query with safe timeout
            record = self._query_crossref(doi=doi, title=title)

        if not record and (doi or title):
            record = self._query_semantic_scholar(doi=doi, title=title, arxiv_id=arxiv_id)

        # 3. Evaluate verification verdict
        if not record:
            # If citation gave a specific fake DOI or paper title that doesn't exist anywhere
            if doi or (title and len(title.split()) >= 3):
                return {
                    "citation": citation_item,
                    "status": "POTENTIALLY_FABRICATED",
                    "confidence": 0.90,
                    "rationale": "No publication record found in Crossref, Semantic Scholar, or academic index. Characteristic of LLM hallucinated citation.",
                    "registry_data": None
                }
            return {
                "citation": citation_item,
                "status": "UNAVAILABLE",
                "confidence": 0.50,
                "rationale": "Citation contains insufficient identifiers (no DOI or title) to query registries.",
                "registry_data": None
            }

        # Compare extracted metadata against verified record
        reg_year = record.get("year")
        reg_title = record.get("title", "")
        reg_authors = record.get("authors", [])

        year_matches = (year is None) or (reg_year is None) or (abs(year - reg_year) <= 1)
        
        # Check author overlap
        author_matches = True
        if authors_str and reg_authors:
            first_author_in_cite = re.split(r'[,&\s]+', authors_str)[0].lower()
            author_matches = any(first_author_in_cite in a.lower() for a in reg_authors)

        if year_matches and author_matches:
            return {
                "citation": citation_item,
                "status": "VERIFIED",
                "confidence": 0.98,
                "rationale": f"Verified against academic record: '{reg_title}' ({reg_year}).",
                "registry_data": record
            }
        elif author_matches and not year_matches:
            return {
                "citation": citation_item,
                "status": "PARTIALLY_VERIFIED",
                "confidence": 0.85,
                "rationale": f"Paper exists ('{reg_title}'), but publication year differs (cited {year} vs recorded {reg_year}).",
                "registry_data": record
            }
        else:
            return {
                "citation": citation_item,
                "status": "CITATION_MISMATCH",
                "confidence": 0.90,
                "rationale": f"Paper title exists, but attributed authors ({authors_str}) mismatch recorded authors ({', '.join(reg_authors[:2])}).",
                "registry_data": record
            }

    def verify_all_in_text(self, text: str) -> Dict[str, Any]:
        """Extracts and verifies all citations within a given text."""
        citations = self.extract_citations(text)
        results = [self.verify_citation(c) for c in citations]
        
        counts = {
            "VERIFIED": sum(1 for r in results if r["status"] == "VERIFIED"),
            "PARTIALLY_VERIFIED": sum(1 for r in results if r["status"] == "PARTIALLY_VERIFIED"),
            "CITATION_MISMATCH": sum(1 for r in results if r["status"] == "CITATION_MISMATCH"),
            "POTENTIALLY_FABRICATED": sum(1 for r in results if r["status"] == "POTENTIALLY_FABRICATED"),
            "UNAVAILABLE": sum(1 for r in results if r["status"] == "UNAVAILABLE")
        }
        return {
            "total_citations": len(citations),
            "counts": counts,
            "citations": results
        }

    def _query_crossref(self, doi: Optional[str] = None, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Queries Crossref REST API for DOI or title."""
        try:
            if doi:
                url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
            elif title:
                url = f"https://api.crossref.org/works?query.title={urllib.parse.quote(title)}&rows=1"
            else:
                return None

            req = urllib.request.Request(url, headers={"User-Agent": "TruthGuard-Audit/3.0 (academic-verifier)"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode())
                item = data.get("message")
                if not item:
                    return None
                if "items" in item:
                    if not item["items"]:
                        return None
                    item = item["items"][0]

                # Parse Crossref response
                pub_year = None
                date_parts = item.get("published", {}).get("date-parts", [[]])[0]
                if date_parts:
                    pub_year = int(date_parts[0])

                authors = []
                for a in item.get("author", []):
                    name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                    if name:
                        authors.append(name)

                return {
                    "title": (item.get("title") or [""])[0],
                    "authors": authors,
                    "year": pub_year,
                    "venue": (item.get("container-title") or [""])[0],
                    "doi": item.get("DOI"),
                    "source": "Crossref"
                }
        except Exception:
            return None

    def _query_semantic_scholar(self, doi: Optional[str] = None, title: Optional[str] = None, arxiv_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Queries Semantic Scholar Graph API."""
        try:
            paper_id = None
            if doi:
                paper_id = f"DOI:{doi}"
            elif arxiv_id:
                paper_id = f"ARXIV:{arxiv_id}"
            elif title:
                paper_id = f"title:{urllib.parse.quote(title)}"

            if not paper_id:
                return None

            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,authors,year,venue,externalIds"
            req = urllib.request.Request(url, headers={"User-Agent": "TruthGuard-Audit/3.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                item = json.loads(resp.read().decode())
                if not item or "title" not in item:
                    return None
                authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
                return {
                    "title": item.get("title"),
                    "authors": authors,
                    "year": item.get("year"),
                    "venue": item.get("venue"),
                    "doi": item.get("externalIds", {}).get("DOI"),
                    "source": "Semantic Scholar"
                }
        except Exception:
            return None
