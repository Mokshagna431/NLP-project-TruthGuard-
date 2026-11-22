# TruthGuard-100 Annotation Guidelines

## Overview
This document guides human annotators in labelling claims extracted from 100 open-domain LLM answers for the TruthGuard-100 benchmark.
Each row in the dataset represents a single atomic claim decomposed from an answer.

Annotators must assign exactly one label from:
- `SUPPORTED` (`S`)
- `CONTRADICTED` (`C`)
- `NOT-ENOUGH-INFO` (`NEI`)

---

## 1. SUPPORTED (S)
**Definition**: The claim is fully corroborated and verified by reputable factual sources (e.g. Wikipedia, peer-reviewed records, authoritative encyclopedias).

### Criteria:
- All entities, dates, relationships, and actions in the claim are accurate.
- No speculation or unsubstantiated inference is required to establish truth.

### Examples:
- Claim: *"Neil Armstrong was the commander of the Apollo 11 mission."* -> **SUPPORTED**
- Claim: *"Water boils at 100 degrees Celsius at sea level."* -> **SUPPORTED**
- Claim: *"The Eiffel Tower was constructed for the 1889 World's Fair."* -> **SUPPORTED**

---

## 2. CONTRADICTED (C)
**Definition**: The claim explicitly contradicts verified factual knowledge or trusted evidence.

### Criteria:
- The factual assertion made is directly refuted by facts (e.g., incorrect dates, false attribution, erroneous quantities, swapped names, or fabricated events).
- Intrinsic and factual hallucinations belong in this category.

### Examples:
- Claim: *"The Eiffel Tower was designed by Leonardo da Vinci."* -> **CONTRADICTED** (Designed by Maurice Koechlin and Émile Nouguier / Gustave Eiffel)
- Claim: *"Thomas Edison invented the telephone in 1876."* -> **CONTRADICTED** (Alexander Graham Bell patented it)
- Claim: *"Saturn is the fifth planet from the Sun."* -> **CONTRADICTED** (It is the sixth planet; Jupiter is fifth)

---

## 3. NOT-ENOUGH-INFO (NEI)
**Definition**: The claim cannot be definitively confirmed or refuted using trusted public reference knowledge.

### Criteria:
- Unverifiable specific statistics, unrecorded private actions, obscure or indeterminate quantities.
- Extrinsic hallucinations that lack grounding but do not contradict established facts.
- **Rule of Thumb**: Lack of evidence is *never* proof of falsehood. If you cannot find a source confirming or refuting it, mark `NEI`.

### Examples:
- Claim: *"The Library of Alexandria had exactly 542,109 astronomical scrolls."* -> **NEI** (Exact number of scrolls is lost to history)
- Claim: *"Albert Einstein ate oatmeal for breakfast on his 25th birthday."* -> **NEI** (Unverifiable trivia)
- Claim: *"The CEO prefers drinking tea during morning meetings."* -> **NEI** (Unverifiable personal preference)

---

## Conflict Resolution Protocol
1. Annotators must work independently without consulting each other.
2. Inter-annotator agreement is evaluated using Cohen's $\kappa$.
3. When both annotators finish, run `python -m annotation.compute_kappa` to identify disagreements and resolve gold consensus.
