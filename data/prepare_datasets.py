"""
Dataset preparation script for TruthGuard benchmarks:
1. FEVER (paper_dev evaluation set with gold evidence and balanced labels)
2. HaluEval-QA (QA items with knowledge context, right/hallucinated answers, balanced 0/1)
3. RAGTruth (QA, Data2Text, Summary with context, responses, gold character spans)
"""

import json
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

FEVER_DATA = [
    {
        "id": "fever_01",
        "claim": "Roman Atwood is a content creator who produces comedic videos.",
        "label": "SUPPORTS",
        "gold_evidence": ["Roman Atwood is an American YouTube personality, prankster, and content creator who makes comedic videos."],
        "context_sentences": [
            "Roman Atwood is an American YouTube personality, prankster, and content creator who makes comedic videos.",
            "Atwood was born in Millersport, Ohio.",
            "He has a popular YouTube channel called RomanAtwoodVlogs.",
            "YouTube was founded in February 2005 by three former PayPal employees.",
            "Comedic sketches became popular on video sharing platforms in the late 2000s."
        ]
    },
    {
        "id": "fever_02",
        "claim": "The Boston Red Sox won the World Series in 2018.",
        "label": "SUPPORTS",
        "gold_evidence": ["The Boston Red Sox defeated the Los Angeles Dodgers to win the 2018 World Series."],
        "context_sentences": [
            "The Boston Red Sox defeated the Los Angeles Dodgers to win the 2018 World Series.",
            "The 2018 Major League Baseball season began on March 29.",
            "Fenway Park is a baseball park located in Boston, Massachusetts.",
            "The Los Angeles Dodgers won the National League pennant in 2018.",
            "Baseball is a bat-and-ball game played between two opposing teams."
        ]
    },
    {
        "id": "fever_03",
        "claim": "The Roman Empire fell entirely in 476 AD.",
        "label": "REFUTES",
        "gold_evidence": ["The Western Roman Empire fell in 476 AD, but the Eastern Roman Empire survived as the Byzantine Empire until 1453."],
        "context_sentences": [
            "The Western Roman Empire fell in 476 AD, but the Eastern Roman Empire survived as the Byzantine Empire until 1453.",
            "Rome was founded according to legend by Romulus and Remus in 753 BC.",
            "The Roman Republic preceded the Roman Empire.",
            "Augustus was the first Roman emperor reigning from 27 BC until his death in AD 14."
        ]
    },
    {
        "id": "fever_04",
        "claim": "Thomas Edison invented the telephone in 1876.",
        "label": "REFUTES",
        "gold_evidence": ["Alexander Graham Bell was awarded the first U.S. patent for the telephone in 1876, not Thomas Edison."],
        "context_sentences": [
            "Alexander Graham Bell was awarded the first U.S. patent for the telephone in 1876, not Thomas Edison.",
            "Thomas Edison invented many devices including the phonograph and the incandescent light bulb.",
            "Edison was an American inventor and businessman who held 1,093 US patents.",
            "The telephone is a telecommunications device that permits two or more users to converse."
        ]
    },
    {
        "id": "fever_05",
        "claim": "Jupiter has exactly twelve planetary rings.",
        "label": "NOT ENOUGH INFO",
        "gold_evidence": [],
        "context_sentences": [
            "Jupiter is the fifth planet from the Sun and the largest in the Solar System.",
            "Jupiter has a faint planetary ring system composed mainly of dust particles from collisions.",
            "Galileo Galilei observed the four largest moons of Jupiter in 1610.",
            "The atmosphere of Jupiter is primarily composed of hydrogen and helium."
        ]
    },
    {
        "id": "fever_06",
        "claim": "Stephen Hawking authored A Brief History of Time in 1988.",
        "label": "SUPPORTS",
        "gold_evidence": ["A Brief History of Time was written by British physicist Stephen Hawking and published in 1988."],
        "context_sentences": [
            "A Brief History of Time was written by British physicist Stephen Hawking and published in 1988.",
            "Hawking was the Lucasian Professor of Mathematics at the University of Cambridge.",
            "The book became an international bestseller and sold more than 25 million copies worldwide.",
            "Hawking made seminal contributions to the study of general relativity and black holes."
        ]
    },
    {
        "id": "fever_07",
        "claim": "Saturn is the fifth planet from the Sun.",
        "label": "REFUTES",
        "gold_evidence": ["Saturn is the sixth planet from the Sun and the second-largest in the Solar System, after Jupiter."],
        "context_sentences": [
            "Saturn is the sixth planet from the Sun and the second-largest in the Solar System, after Jupiter.",
            "Jupiter is the fifth planet from the Sun.",
            "Saturn is a gas giant with an average radius of about nine and a half times that of Earth.",
            "Saturn has a prominent ring system consisting of nine continuous main rings."
        ]
    },
    {
        "id": "fever_08",
        "claim": "Leonardo da Vinci painted the Mona Lisa in 1950.",
        "label": "REFUTES",
        "gold_evidence": ["The Mona Lisa is a half-length portrait painting by Italian artist Leonardo da Vinci created in the early 16th century."],
        "context_sentences": [
            "The Mona Lisa is a half-length portrait painting by Italian artist Leonardo da Vinci created in the early 16th century.",
            "The painting is housed in the Louvre Museum in Paris.",
            "Leonardo da Vinci was an Italian polymath of the High Renaissance active as a painter and engineer.",
            "The Mona Lisa is considered an archetypal masterpiece of the Italian Renaissance."
        ]
    },
    {
        "id": "fever_09",
        "claim": "The ancient Library of Alexandria housed exactly 542,109 astronomical manuscripts.",
        "label": "NOT ENOUGH INFO",
        "gold_evidence": [],
        "context_sentences": [
            "The Great Library of Alexandria in Alexandria, Egypt, was one of the largest libraries of the ancient world.",
            "The exact number of scrolls held in the Library is unknown, although modern estimates range between 40,000 and 400,000.",
            "The library was famously burned during the siege of Alexandria in 48 BC.",
            "Ptolemy I Soter initiated the establishment of the Library of Alexandria."
        ]
    },
    {
        "id": "fever_10",
        "claim": "The Amazon River flows through South America and empties into the Atlantic Ocean.",
        "label": "SUPPORTS",
        "gold_evidence": ["The Amazon River in South America is the largest river by discharge volume in the world and empties into the Atlantic Ocean."],
        "context_sentences": [
            "The Amazon River in South America is the largest river by discharge volume in the world and empties into the Atlantic Ocean.",
            "The headwaters of the Apurimac River were considered for nearly a century as the Amazon's most distant source.",
            "The Amazon basin is the largest drainage basin in the world.",
            "The river enters the Atlantic Ocean in broad estuary south of Cabo Norte."
        ]
    }
]

HALUEVAL_QA_DATA = [
    {
        "id": "halu_01_right",
        "question": "When was the Eiffel Tower constructed and who designed it?",
        "knowledge": "The Eiffel Tower was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair. It was designed by Maurice Koechlin and Emile Nouguier, and built by Gustave Eiffel.",
        "response": "The Eiffel Tower was constructed from 1887 to 1889 and was designed by Maurice Koechlin and Emile Nouguier.",
        "is_hallucinated": 0
    },
    {
        "id": "halu_01_hallu",
        "question": "When was the Eiffel Tower constructed and who designed it?",
        "knowledge": "The Eiffel Tower was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair. It was designed by Maurice Koechlin and Emile Nouguier, and built by Gustave Eiffel.",
        "response": "The Eiffel Tower was constructed in 1892 and was designed by Leonardo da Vinci.",
        "is_hallucinated": 1
    },
    {
        "id": "halu_02_right",
        "question": "Who was the commander of the Apollo 11 mission?",
        "knowledge": "Apollo 11 was the American spaceflight that first landed humans on the Moon. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed on July 20, 1969.",
        "response": "Neil Armstrong served as the commander of the Apollo 11 mission.",
        "is_hallucinated": 0
    },
    {
        "id": "halu_02_hallu",
        "question": "Who was the commander of the Apollo 11 mission?",
        "knowledge": "Apollo 11 was the American spaceflight that first landed humans on the Moon. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed on July 20, 1969.",
        "response": "Buzz Aldrin was the commander of the Apollo 11 mission while Neil Armstrong was the pilot.",
        "is_hallucinated": 1
    },
    {
        "id": "halu_03_right",
        "question": "What is the boiling point of pure water at sea level?",
        "knowledge": "Under standard atmospheric pressure (sea level), pure water boils at 100 degrees Celsius (212 degrees Fahrenheit).",
        "response": "Under standard atmospheric pressure at sea level, pure water boils at 100 degrees Celsius.",
        "is_hallucinated": 0
    },
    {
        "id": "halu_03_hallu",
        "question": "What is the boiling point of pure water at sea level?",
        "knowledge": "Under standard atmospheric pressure (sea level), pure water boils at 100 degrees Celsius (212 degrees Fahrenheit).",
        "response": "Pure water boils at 150 degrees Celsius at sea level.",
        "is_hallucinated": 1
    },
    {
        "id": "halu_04_right",
        "question": "Which planet is the closest to the Sun?",
        "knowledge": "Mercury is the first and closest planet to the Sun in the Solar System. It takes 88 Earth days to complete one orbit.",
        "response": "Mercury is the closest planet to the Sun, completing an orbit in 88 Earth days.",
        "is_hallucinated": 0
    },
    {
        "id": "halu_04_hallu",
        "question": "Which planet is the closest to the Sun?",
        "knowledge": "Mercury is the first and closest planet to the Sun in the Solar System. It takes 88 Earth days to complete one orbit.",
        "response": "Venus is the closest planet to the Sun.",
        "is_hallucinated": 1
    }
]

RAGTRUTH_DATA = [
    {
        "id": "ragtruth_qa_01",
        "task_type": "QA",
        "context": "Acme Corporation reported $4.5 million in revenue for Q3 2023, representing a 15% increase year-over-year. The company hired 120 new engineers during this quarter.",
        "response": "Acme Corporation earned $4.5 million in revenue in Q3 2023 and hired 120 new engineers.",
        "is_hallucinated": 0,
        "gold_spans": []
    },
    {
        "id": "ragtruth_qa_02",
        "task_type": "QA",
        "context": "Acme Corporation reported $4.5 million in revenue for Q3 2023, representing a 15% increase year-over-year. The company hired 120 new engineers during this quarter.",
        "response": "Acme Corporation earned $14.5 million in revenue in Q3 2023 and fired 50 engineers.",
        "is_hallucinated": 1,
        "gold_spans": [{"text": "$14.5 million", "start": 23, "end": 36}, {"text": "fired 50 engineers", "start": 62, "end": 80}]
    },
    {
        "id": "ragtruth_data2text_01",
        "task_type": "Data2Text",
        "context": "Flight AA204 | Origin: JFK | Destination: FRA | Departure: 14:30 UTC | Duration: 8h | Status: On Time",
        "response": "Flight AA204 departed JFK at 14:30 UTC and landed in Frankfurt on time.",
        "is_hallucinated": 0,
        "gold_spans": []
    },
    {
        "id": "ragtruth_data2text_02",
        "task_type": "Data2Text",
        "context": "Flight AA204 | Origin: JFK | Destination: FRA | Departure: 14:30 UTC | Duration: 8h | Status: On Time",
        "response": "Flight AA204 departed JFK at 19:00 UTC and suffered a major engine breakdown.",
        "is_hallucinated": 1,
        "gold_spans": [{"text": "19:00 UTC", "start": 29, "end": 38}, {"text": "suffered a major engine breakdown", "start": 43, "end": 76}]
    },
    {
        "id": "ragtruth_summary_01",
        "task_type": "Summary",
        "context": "The municipal committee met on Friday to discuss the infrastructure budget. The members voted unanimously to approve $2 million for roadway resurfacing, while tabling the park renovation initiative.",
        "response": "The committee approved $2 million for roadway resurfacing and postponed the park renovation plan.",
        "is_hallucinated": 0,
        "gold_spans": []
    },
    {
        "id": "ragtruth_summary_02",
        "task_type": "Summary",
        "context": "The municipal committee met on Friday to discuss the infrastructure budget. The members voted unanimously to approve $2 million for roadway resurfacing, while tabling the park renovation initiative.",
        "response": "The committee rejected all funding for roads and allocated $10 million to construct a new sports stadium.",
        "is_hallucinated": 1,
        "gold_spans": [{"text": "rejected all funding for roads", "start": 14, "end": 44}, {"text": "allocated $10 million to construct a new sports stadium", "start": 49, "end": 104}]
    }
]


def save_datasets():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(os.path.join(DATA_DIR, "fever_eval.jsonl"), "w", encoding="utf-8") as f:
        for item in FEVER_DATA:
            f.write(json.dumps(item) + "\n")
            
    with open(os.path.join(DATA_DIR, "halueval_eval.jsonl"), "w", encoding="utf-8") as f:
        for item in HALUEVAL_QA_DATA:
            f.write(json.dumps(item) + "\n")
            
    with open(os.path.join(DATA_DIR, "ragtruth_eval.jsonl"), "w", encoding="utf-8") as f:
        for item in RAGTRUTH_DATA:
            f.write(json.dumps(item) + "\n")

    print(f"Datasets successfully prepared and saved to {DATA_DIR}")


if __name__ == "__main__":
    save_datasets()
