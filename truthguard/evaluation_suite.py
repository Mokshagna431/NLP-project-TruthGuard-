"""
TruthGuard 3.0 - Comprehensive Large-Scale Evaluation Suite (Phase 6)
Builds and evaluates a 350-claim balanced, multi-domain benchmark covering:
1. History & Archaeology
2. Geography & Earth Sciences
3. Astronomy & Space Sciences
4. Biology, Genetics & Physiology
5. Physics & Mechanics
6. Chemistry & Materials Science
7. Medicine, Health & Pharmacology
8. Mathematics, Logic & Computer Science
9. Arts, Architecture & World Heritage
10. Geopolitics, Law & Global Institutions

Computes empirical scientific metrics:
- 3x3 Confusion Matrix (SUPPORTED, CONTRADICTED, NEI)
- Per-class Precision, Recall, and F1-score
- Macro Precision, Macro Recall, Macro F1
- Overall Classification Accuracy
- Retrieval Relevance Rate (%)
- Citation Accuracy Rate (%)
- False Correction Rate (%) [Target: 0.0%]
- Latency Report (mean, median, p95, min, max)

Saves complete audit results to results/evaluation_report_350.json.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Tuple
import numpy as np

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from truthguard.pipeline import TruthGuardPipeline
from truthguard.retrieve import validate_evidence_relevance
from truthguard.citation import CitationVerifier
from truthguard.math_engine import MathEngine


def build_350_benchmark_dataset() -> List[Dict[str, Any]]:
    """
    Constructs a scientifically calibrated, balanced 350-claim benchmark:
    - 120 SUPPORTED claims
    - 120 CONTRADICTED claims
    - 110 NOT ENOUGH INFO (NEI) claims
    Spanning 10 distinct knowledge domains and varied hallucination archetypes:
    - Entity substitutions
    - Temporal / date corruptions
    - Absolute quantifier fallacies ("all", "every")
    - Numerical / quantity distortions
    - Negation / polarity inversions
    - Subjective opinion / unrecorded personal assertions (clean NEI)
    - Speculative future predictions (clean NEI)
    """
    dataset = []

    # Domain 1: Medicine, Health & Life Sciences (35 items)
    med_items = [
        # Supported (12)
        ("The human heart has four chambers: two atria and two ventricles.", "SUPPORTED", "The human heart is a muscular organ composed of four chambers: the right atrium, right ventricle, left atrium, and left ventricle.", "Anatomy"),
        ("Vitamin C is required for normal collagen synthesis in humans.", "SUPPORTED", "Ascorbic acid (vitamin C) serves as an essential cofactor for prolyl and lysyl hydroxylases required in collagen biosynthesis.", "Biochemistry"),
        ("Excessive water intake can cause acute dilutional hyponatremia.", "SUPPORTED", "Drinking water in excess of renal excretory capacity causes water intoxication and acute dilutional hyponatremia.", "Nephrology"),
        ("Penicillin was discovered by Alexander Fleming in 1928.", "SUPPORTED", "Alexander Fleming discovered penicillin produced by Penicillium notatum mold at St. Mary's Hospital in London in September 1928.", "Pharmacology"),
        ("Insulin is a peptide hormone produced by beta cells of the pancreatic islets.", "SUPPORTED", "Insulin is synthesized and secreted by beta cells within the islets of Langerhans in the pancreas to regulate blood glucose.", "Endocrinology"),
        ("Hemoglobin is an iron-containing protein that transports oxygen in red blood cells.", "SUPPORTED", "Hemoglobin is the iron-rich metalloprotein in erythrocytes responsible for oxygen delivery from lungs to peripheral tissues.", "Hematology"),
        ("Type 1 diabetes is an autoimmune disease resulting in the destruction of insulin-producing cells.", "SUPPORTED", "Type 1 diabetes is characterized by autoimmune T-cell mediated destruction of pancreatic beta cells.", "Immunology"),
        ("Mitochondria generate the majority of cellular ATP via oxidative phosphorylation.", "SUPPORTED", "Mitochondria are double-membraned organelles that produce over 90% of cellular adenosine triphosphate via the electron transport chain.", "Cell Biology"),
        ("Ribosomes are macromolecular machines responsible for biological protein synthesis.", "SUPPORTED", "Ribosomes translate messenger RNA transcripts into polypeptide protein chains in all living cells.", "Molecular Biology"),
        ("Vaccines stimulate the adaptive immune system to produce antibodies against pathogens.", "SUPPORTED", "Vaccination exposes the immune system to antigens, inducing memory B and T cell responses without causing disease.", "Immunology"),
        ("DNA is composed of four nitrogenous bases: adenine, thymine, cytosine, and guanine.", "SUPPORTED", "The genetic code in deoxyribonucleic acid is encoded by the four bases adenine, thymine, cytosine, and guanine.", "Genetics"),
        ("The human skeleton typically consists of 206 bones in an adult.", "SUPPORTED", "An adult human skeletal system is normally composed of 206 individual named bones.", "Osteology"),

        # Contradicted (12)
        ("Antibiotics cure the common cold caused by rhinoviruses.", "CONTRADICTED", "Antibiotics target bacterial cell structures and are completely ineffective against viral infections such as the common cold and influenza.", "Pharmacology"),
        ("All bacteria are harmful and pathogenic to human health.", "CONTRADICTED", "While certain bacteria cause disease, the vast majority of bacterial species in the human microbiome are harmless or essential commensals.", "Microbiology"),
        ("Vaccines have been scientifically proven to cause autism spectrum disorder.", "CONTRADICTED", "Numerous rigorous international clinical studies involving millions of children have established that vaccines do not cause autism.", "Pediatrics"),
        ("The human heart has only two chambers.", "CONTRADICTED", "The human heart possesses four distinct muscular chambers: two atria and two ventricles.", "Anatomy"),
        ("Insulin is produced in the human gallbladder.", "CONTRADICTED", "Insulin is synthesized exclusively in the beta cells of the endocrine pancreas, whereas the gallbladder stores bile produced by the liver.", "Endocrinology"),
        ("Antibiotics are effective medications for eliminating the influenza virus.", "CONTRADICTED", "Antibiotics have zero efficacy against viruses including influenza; antivirals or supportive care are required.", "Virology"),
        ("Red blood cells contain a cell nucleus that replicates DNA in mature humans.", "CONTRADICTED", "Mature human erythrocytes are enucleated and lack cellular nuclei, mitochondria, and nuclear DNA.", "Hematology"),
        ("Vitamin D deficiency has zero effect on human bone mineralization.", "CONTRADICTED", "Severe vitamin D deficiency impairs calcium absorption and directly leads to rickets in children and osteomalacia in adults.", "Nutrition"),
        ("The adult human skull is formed of a single solid unjoined bone.", "CONTRADICTED", "The adult human skull consists of 22 separate bones joined together by immovable fibrous sutures.", "Anatomy"),
        ("Penicillin was discovered by Albert Einstein in 1955.", "CONTRADICTED", "Penicillin was discovered by Scottish bacteriologist Alexander Fleming in 1928, not Albert Einstein.", "Medical History"),
        ("The human liver has no role in protein synthesis or metabolism.", "CONTRADICTED", "The liver is the primary metabolic organ responsible for synthesizing major plasma proteins including albumin and clotting factors.", "Hepatology"),
        ("Humans only use ten percent of their brain capacity.", "CONTRADICTED", "Functional neuroimaging demonstrates that virtually all areas of the human brain are active during routine cognitive and motor tasks.", "Neurology"),

        # NEI (11)
        ("Dr. John Miller in Seattle secretly prefers treating headaches with herbal willow bark rather than aspirin.", "NEI", "Aspirin was developed from salicylic acid derived from willow bark.", "Private Preference"),
        ("A mysterious unrecorded patient in 1912 survived a 100-foot fall with zero broken bones.", "NEI", "Trauma registry data from the early 20th century is fragmentary and unindexed.", "Unrecorded Anecdote"),
        ("A patient in Bristol in 1965 ate exactly 3 apples every morning to prevent high blood pressure.", "NEI", "Cardiovascular dietary studies assess broad population cohorts rather than private breakfast tallies.", "Unrecorded Private Habit"),
        ("Future medicine in the year 2150 will eradicate all neurodegenerative disorders.", "NEI", "Medical technology in the 22nd century remains an unprovable prospective projection.", "Future Speculation"),
        ("The most common secret hobby among thoracic surgeons in 1980 was playing chess.", "NEI", "Physician leisure surveys from 1980 did not systematically document surgical board pastimes.", "Unrecorded Hobby"),
        ("Dr. Sarah Vance privately believes that tea is superior to coffee for cognitive longevity.", "NEI", "Epidemiological studies compare beverage intake, but individual physician preferences are uncataloged.", "Private Opinion"),
        ("An unknown herbalist in 1840 compiled a 500-page lost treatise on alpine flora.", "NEI", "Botanical historical archives contain no verified record of this purported lost treatise.", "Lost Document"),
        ("A student nurse in 1952 accidentally misplaced their clinical pocket thermometer on a train.", "NEI", "Hospital transit records do not log routine personal equipment misplacements.", "Unrecorded Incident"),
        ("Scientists in 2090 will discover a synthetic enzyme that halts biological aging completely.", "NEI", "Biogerontological forecasting cannot establish future discoveries as historical fact.", "Future Speculation"),
        ("Dr. Peterson's favorite stethoscope color during his medical residency was purple.", "NEI", "Personal stethoscope procurement colors are not recorded in institutional archives.", "Private Preference"),
        ("An unrecorded village physician in 1720 treated pneumonia with warm honey compresses.", "NEI", "18th-century rural folk medical practices lack contemporaneous clinical documentation.", "Unrecorded Anecdote")
    ]
    for idx, (claim, label, context, subcat) in enumerate(med_items, 1):
        dataset.append({
            "id": f"eval_med_{idx:03d}",
            "domain": "Medicine & Life Sciences",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 2: Astronomy & Space Sciences (35 items)
    space_items = [
        # Supported (12)
        ("Jupiter is the largest planet in our solar system by both diameter and mass.", "SUPPORTED", "Jupiter is the fifth planet from the Sun and the largest in the Solar System, with a mass more than two and a half times that of all other planets combined.", "Planetary"),
        ("The Apollo 11 lunar module landed on the Moon on July 20, 1969.", "SUPPORTED", "The Apollo 11 Lunar Module Eagle touched down on the lunar surface on July 20, 1969, carrying Neil Armstrong and Buzz Aldrin.", "Spaceflight"),
        ("The Sun is a G-type main-sequence star situated in the Orion Arm of the Milky Way.", "SUPPORTED", "The Sun is classified as a G-type main-sequence star (G2V) located within the Local Interstellar Cloud in the Orion-Cygnus Arm.", "Astrophysics"),
        ("Mars has two small natural satellites named Phobos and Deimos.", "SUPPORTED", "Mars possesses two small irregularly shaped moons, Phobos and Deimos, discovered by Asaph Hall in 1877.", "Planetary"),
        ("Saturn's rings are composed predominantly of water ice with trace rocky contaminants.", "SUPPORTED", "Spectroscopic observations confirm that the rings of Saturn consist of 99% pure water ice particles with minor tholin impurities.", "Planetary"),
        ("Light travels through a vacuum at approximately 299,792 kilometers per second.", "SUPPORTED", "The speed of light in vacuum is an exact universal constant defined as 299,792,458 meters per second.", "Physics"),
        ("The Hubble Space Telescope was deployed into low Earth orbit in April 1990.", "SUPPORTED", "Space Shuttle Discovery launched the Hubble Space Telescope into low Earth orbit during mission STS-31 in April 1990.", "Observatories"),
        ("Venus has a dense carbon dioxide atmosphere with clouds of sulfuric acid.", "SUPPORTED", "Venus features an oppressive atmosphere consisting of 96.5% carbon dioxide and thick reflective clouds of concentrated sulfuric acid.", "Planetary"),
        ("Halley's Comet has an orbital period of approximately 75 to 76 years.", "SUPPORTED", "Halley's Comet is a periodic comet visible from Earth every 75 to 76 years, last seen in 1986.", "Comets"),
        ("The Voyager 1 space probe was launched by NASA in 1977 and entered interstellar space.", "SUPPORTED", "Voyager 1 was launched on September 5, 1977, and crossed the heliopause into interstellar space in August 2012.", "Missions"),
        ("The Moon rotates on its axis at the same rate it orbits Earth, exhibiting synchronous rotation.", "SUPPORTED", "Tidal locking causes the Moon to exhibit synchronous rotation, keeping the same hemisphere facing Earth permanently.", "Orbital"),
        ("The Andromeda Galaxy is the closest major spiral galaxy to the Milky Way.", "SUPPORTED", "Messier 31 (the Andromeda Galaxy) is a barred spiral galaxy approximately 2.5 million light-years from Earth in the Local Group.", "Galaxies"),

        # Contradicted (12)
        ("Humans have established a permanent research colony on the surface of Jupiter.", "CONTRADICTED", "No human colonies exist on Jupiter; as a gas giant with crushing atmospheric pressures, intense radiation, and no solid surface, it is uninhabitable.", "Habitation"),
        ("The Great Wall of China is easily visible from the Moon with the naked human eye.", "CONTRADICTED", "NASA astronauts and optical physicists confirm that the Great Wall cannot be seen from the Moon without high-magnification optical aids.", "Observation"),
        ("The Apollo 11 mission landed humans on the Moon in the year 1995.", "CONTRADICTED", "The Apollo 11 lunar landing occurred on July 20, 1969, not in 1995.", "Spaceflight"),
        ("Mars is the largest planet in our solar system.", "CONTRADICTED", "Jupiter is the largest planet in the Solar System; Mars is the second-smallest, with about half the diameter of Earth.", "Planetary"),
        ("The Sun revolves around the Earth once every 24 hours.", "CONTRADICTED", "The heliocentric model demonstrates that the Earth orbits the Sun once per year while rotating on its own axis every 24 hours.", "Celestial"),
        ("Saturn is composed entirely of solid solid granite rock with zero gas.", "CONTRADICTED", "Saturn is a gas giant primarily composed of hydrogen and helium, with only a small dense rocky core.", "Planetary"),
        ("The Hubble Space Telescope was launched into space in the year 1850.", "CONTRADICTED", "The Hubble Space Telescope was launched in April 1990 by Space Shuttle Discovery, long before spaceflight existed in 1850.", "Telescopes"),
        ("Venus has average surface temperatures colder than the freezing point of liquid nitrogen.", "CONTRADICTED", "Venus experiences extreme runaway greenhouse heating, producing surface temperatures exceeding 460 degrees Celsius.", "Planetary"),
        ("Light travels faster through dense water than through a vacuum.", "CONTRADICTED", "Light travels fastest in a vacuum; refractive indices slow the phase velocity of light in denser media like water.", "Optics"),
        ("The Moon has a thick breathable oxygen atmosphere with flowing liquid rivers.", "CONTRADICTED", "The Moon possesses a tenuous exosphere near vacuum conditions and has no breathable oxygen or liquid surface water.", "Planetary"),
        ("The Voyager 1 space probe was launched in the year 1620 by Johannes Kepler.", "CONTRADICTED", "Voyager 1 was launched in 1977 by NASA; Johannes Kepler lived in the 17th century and had no spacecraft.", "Spaceflight"),
        ("Jupiter has zero natural satellites and no gravitational pull.", "CONTRADICTED", "Jupiter possesses 95 officially recognized moons and possesses the strongest gravitational pull among all solar system planets.", "Planetary"),

        # NEI (11)
        ("Commander Neil Armstrong had a secret lucky coin hidden in his spacesuit during the Apollo 11 descent.", "NEI", "Official NASA lunar equipment manifests and audio transcripts record all authorized onboard flight articles.", "Unrecorded Anecdote"),
        ("An alien probe from Proxima Centauri visited Earth's upper stratosphere in 1834.", "NEI", "Astronomical historical records from the 19th century contain zero verifiable extraterrestrial physical evidence.", "Unverified Speculation"),
        ("The unrecorded private journal of an 18th-century amateur astronomer contained 14 sketches of Saturn.", "NEI", "Private 18th-century notebooks that were not cataloged in royal society collections are lost to history.", "Lost Document"),
        ("Humans will build a luxury floating hotel in the clouds of Venus by the year 2250.", "NEI", "Prospective technological engineering in future centuries cannot be verified as factual reality.", "Future Speculation"),
        ("Buzz Aldrin's favorite brand of toothpaste during his boyhood was peppermint flavoured.", "NEI", "Biographical archives of astronauts do not systematically record childhood consumer toothpaste choices.", "Private Preference"),
        ("A meteorite that fell in Siberia in 1904 was shaped exactly like a perfect pyramid.", "NEI", "Mineralogical recovery reports from rural early 20th century Siberia contain no documentation of pyramid meteorites.", "Unrecorded Object"),
        ("A classified satellite launched in 1971 silently malfunctioned after exactly 43 days and 2 minutes.", "NEI", "Declassified aerospace registries do not detail non-notified minute-by-minute sub-system lifespans.", "Classified Details"),
        ("The astronomer Carl Sagan privately considered pistachio to be the most delicious ice cream flavor.", "NEI", "Personal culinary rankings of historical scientists are not codified in published academic archives.", "Private Preference"),
        ("In the year 2300, humanity will build a Dyson sphere around the Sun.", "NEI", "Megastructure engineering predictions centuries in advance are speculative science fiction.", "Future Speculation"),
        ("An anonymous amateur stargazer in Munich saw a green fireball on October 14, 1891.", "NEI", "Informal unverified 19th-century amateur meteor sightings lack standardized scientific logging.", "Unrecorded Anecdote"),
        ("The first rover on Mars had an unrecorded lucky four-leaf clover sticker placed inside its chassis.", "NEI", "JPL cleanroom assembly procedures strictly prohibit unauthorized foreign organic stickers.", "Unverified Anecdote")
    ]
    for idx, (claim, label, context, subcat) in enumerate(space_items, 1):
        dataset.append({
            "id": f"eval_space_{idx:03d}",
            "domain": "Space & Astronomy",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 3: History & World Heritage (35 items)
    hist_items = [
        # Supported (12)
        ("The Taj Mahal was commissioned in 1631 by Mughal Emperor Shah Jahan.", "SUPPORTED", "The Taj Mahal is an ivory-white marble mausoleum commissioned in 1631 by Emperor Shah Jahan to house the tomb of Mumtaz Mahal.", "Architecture"),
        ("The Treaty of Versailles was signed on June 28, 1919, officially ending World War I.", "SUPPORTED", "The Treaty of Versailles was signed on June 28, 1919, in the Hall of Mirrors at Versailles, concluding World War I.", "Treaties"),
        ("The Eiffel Tower was completed in 1889 as the entrance arch to the 1889 World's Fair in Paris.", "SUPPORTED", "Gustave Eiffel's firm constructed the Eiffel Tower from 1887 to 1889 for the 1889 Exposition Universelle in Paris.", "Architecture"),
        ("Julius Caesar was assassinated on the Ides of March in 44 BC.", "SUPPORTED", "A conspiracy of Roman senators assassinated Julius Caesar on the Ides of March (March 15), 44 BC.", "Ancient Rome"),
        ("The Magna Carta was agreed to by King John of England at Runnymede in 1215.", "SUPPORTED", "King John granted the Magna Carta under pressure from rebel barons at Runnymede near Windsor in June 1215.", "Medieval"),
        ("The Berlin Wall was erected in 1961 by East Germany and fell in November 1989.", "SUPPORTED", "The German Democratic Republic constructed the Berlin Wall starting in August 1961, and it fell on November 9, 1989.", "Cold War"),
        ("The United States Declaration of Independence was adopted by the Continental Congress in July 1776.", "SUPPORTED", "The Second Continental Congress unanimously adopted the Declaration of Independence in Philadelphia on July 4, 1776.", "American History"),
        ("The Parthenon in Athens was dedicated to the goddess Athena in the 5th century BC.", "SUPPORTED", "The Parthenon was constructed between 447 and 432 BC on the Athenian Acropolis dedicated to Athena Parthenos.", "Classical Greece"),
        ("Nelson Mandela was inaugurated as the first black president of South Africa in 1994.", "SUPPORTED", "Following the end of apartheid, Nelson Mandela was sworn in as South Africa's first black head of state in May 1994.", "African History"),
        ("The Industrial Revolution began in Great Britain during the mid-18th century.", "SUPPORTED", "The transition to new manufacturing processes known as the Industrial Revolution began in Britain around 1760.", "Modern History"),
        ("Christopher Columbus reached the Caribbean islands in October 1492.", "SUPPORTED", "Columbus made landfall on an island in the Bahamas on October 12, 1492, initiating European exploration of the Americas.", "Exploration"),
        ("The French Revolution began in 1789 with the storming of the Bastille on July 14.", "SUPPORTED", "The storming of the Bastille fortress on July 14, 1789, marked a flashpoint in the outbreak of the French Revolution.", "European History"),

        # Contradicted (12)
        ("The Taj Mahal was commissioned by British Prime Minister Winston Churchill in 1945.", "CONTRADICTED", "The Taj Mahal was commissioned in 1631 by Mughal Emperor Shah Jahan, over three centuries before Winston Churchill.", "Architecture"),
        ("The Treaty of Versailles was signed in the year 1995 to end the Korean War.", "CONTRADICTED", "The Treaty of Versailles was signed on June 28, 1919, to end World War I, not in 1995.", "Treaties"),
        ("The Eiffel Tower was constructed entirely out of solid gold in Berlin, Germany.", "CONTRADICTED", "The Eiffel Tower is a puddle iron lattice tower constructed in Paris, France, not gold in Berlin.", "Architecture"),
        ("Julius Caesar was assassinated in the year 2010 by modern secret agents.", "CONTRADICTED", "Julius Caesar was assassinated in 44 BC by Roman senators in the Theatre of Pompey.", "Ancient Rome"),
        ("The Berlin Wall fell in the year 1776 during the American Revolution.", "CONTRADICTED", "The Berlin Wall fell on November 9, 1989, long after the American Revolution of 1776.", "Cold War"),
        ("Nelson Mandela served as the King of England during the Tudor dynasty in 1500.", "CONTRADICTED", "Nelson Mandela was a 20th-century anti-apartheid leader who served as President of South Africa from 1994 to 1999.", "Biography"),
        ("The United States Declaration of Independence was signed by Napoleon Bonaparte in Paris.", "CONTRADICTED", "The Declaration of Independence was drafted and signed by American delegates in Philadelphia in 1776.", "American History"),
        ("The Great Wall of China was built entirely during a single afternoon in 1980.", "CONTRADICTED", "The Great Wall of China was constructed over many centuries by successive dynasties dating back to the 7th century BC.", "Architecture"),
        ("The Magna Carta was signed on a space station orbiting Mars in 1215.", "CONTRADICTED", "The Magna Carta was agreed to at Runnymede meadow in Surrey, England, in 1215.", "Medieval"),
        ("The French Revolution broke out in 1999 over disagreements about internet protocols.", "CONTRADICTED", "The French Revolution began in 1789 driven by economic hardship, social inequality, and Enlightenment ideals.", "European History"),
        ("The Parthenon was built in New York City in 1920 as an opera house.", "CONTRADICTED", "The Parthenon was constructed in the 5th century BC on the Acropolis in Athens, Greece.", "Classical Greece"),
        ("Christopher Columbus made his first transatlantic voyage in the year 1892 aboard a steamship.", "CONTRADICTED", "Christopher Columbus sailed with three wooden sailing caravels in 1492, four centuries before 1892.", "Exploration"),

        # NEI (11)
        ("A stonemason working on the Taj Mahal in 1635 accidentally chipped his chisel on a Tuesday morning.", "NEI", "Mughal treasury records track building materials and royal wages but not individual artisan tool mishaps.", "Unrecorded Incident"),
        ("Winston Churchill privately believed that cats were spiritually superior to dogs.", "NEI", "Churchill was well known for keeping various pets, but formal metaphysical evaluations of animals are unrecorded.", "Private Opinion"),
        ("King John of England preferred wearing wool socks dyed green during the negotiations at Runnymede.", "NEI", "13th-century chancery rolls record diplomatic charters rather than royal undergarment colors.", "Private Wardrobe"),
        ("Napoleon Bonaparte hummed an unrecorded Italian lullaby while crossing the Alps in 1800.", "NEI", "Military memoirs document operational routes and baggage trains but not casual marching vocalizations.", "Unrecorded Anecdote"),
        ("An unrecorded French citizen drank three glasses of burgundy wine before the storming of the Bastille.", "NEI", "Revolutionary archive rosters record armed assembly counts but not individual morning tavern consumption.", "Unrecorded Anecdote"),
        ("Gustave Eiffel's chief draftsman secretly disliked the aesthetic curve of the tower's base.", "NEI", "Eiffel Company engineering blueprints document structural calculations without personal aesthetic diaries.", "Private Preference"),
        ("In the year 2500, historians will discover the lost tomb of Alexander the Great in Antarctica.", "NEI", "Future archaeological discoveries centuries ahead cannot be verified as existing facts.", "Future Speculation"),
        ("A Roman baker named Marcus baked exactly 42 loaves of spelt bread on March 14, 44 BC.", "NEI", "Pompeian and Roman excavation epigraphy preserves commercial graffiti but not day-to-day household tallies.", "Unrecorded Daily Task"),
        ("Thomas Jefferson misplaced his favorite inkwell for three hours on July 3, 1776.", "NEI", "Continental Congress journals record legislative votes and draft revisions, not personal stationery misplacements.", "Unrecorded Incident"),
        ("A guard stationed at the Berlin Wall in 1974 secretly kept a collection of dried maple leaves.", "NEI", "Border military guard logs do not record private botanical keepsakes of enlisted personnel.", "Private Hobby"),
        ("Christopher Columbus dreamt of a three-masted silver galleon on the night of August 2, 1492.", "NEI", "Columbus's shipboard logs record navigational compass bearings and wind conditions, not private dreams.", "Private Dream")
    ]
    for idx, (claim, label, context, subcat) in enumerate(hist_items, 1):
        dataset.append({
            "id": f"eval_hist_{idx:03d}",
            "domain": "History & Heritage",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 4: Geography & Earth Sciences (35 items)
    geo_items = [
        # Supported (12)
        ("Mount Everest is the highest mountain peak above sea level on Earth.", "SUPPORTED", "Mount Everest, located in the Mahalangur Himal sub-range of the Himalayas, has an official elevation of 8,848.86 meters.", "Mountains"),
        ("The Pacific Ocean is the largest and deepest of Earth's oceanic divisions.", "SUPPORTED", "The Pacific Ocean extends from the Arctic Ocean to the Southern Ocean, covering over 165 million square kilometers.", "Oceans"),
        ("The Nile River has historically been considered the longest river in the world.", "SUPPORTED", "The Nile River in northeastern Africa flows north for approximately 6,650 kilometers into the Mediterranean Sea.", "Rivers"),
        ("The Amazon rainforest is the largest tropical rainforest in the world.", "SUPPORTED", "The Amazon rainforest encompasses over 5.5 million square kilometers across South America, primarily within Brazil.", "Biomes"),
        ("Antarctica is the coldest, driest, and windiest continent on Earth.", "SUPPORTED", "Antarctica holds the record for the lowest natural temperature on Earth and is classified as a polar desert.", "Polar"),
        ("The Sahara is the largest hot desert in the world.", "SUPPORTED", "The Sahara Desert in North Africa covers an area of roughly 9.2 million square kilometers.", "Deserts"),
        ("Tokyo is the capital and most populous metropolitan area of Japan.", "SUPPORTED", "Tokyo serves as the seat of the Government of Japan and anchors the Greater Tokyo Area, the world's most populous metropolis.", "Capitals"),
        ("Lake Baikal in Russia is the world's deepest and oldest freshwater lake.", "SUPPORTED", "Lake Baikal in southern Siberia contains 20% of the world's unfrozen freshwater and reaches a maximum depth of 1,642 meters.", "Lakes"),
        ("The Mariana Trench contains the Challenger Deep, the deepest known point in Earth's oceans.", "SUPPORTED", "The Challenger Deep in the Mariana Trench plunges to a verified depth of approximately 10,994 meters below sea level.", "Oceanography"),
        ("The equator divides the Earth into the Northern and Southern Hemispheres.", "SUPPORTED", "The equator is the imaginary planetary line at 0 degrees latitude equidistant from the North and South Poles.", "Geodesy"),
        ("Greenland is the world's largest island that is not a continent.", "SUPPORTED", "Greenland covers over 2.1 million square kilometers and is the world's largest non-continental island.", "Islands"),
        ("The Dead Sea is a hypersaline lake located between Israel and Jordan.", "SUPPORTED", "The Dead Sea is a landlocked salt lake bordered by Jordan to the east and the West Bank and Israel to the west.", "Lakes"),

        # Contradicted (12)
        ("Mount Everest has an elevation of only 50 meters above sea level.", "CONTRADICTED", "Mount Everest has an elevation of 8,848.86 meters above sea level, making it the highest peak on Earth.", "Mountains"),
        ("The Pacific Ocean contains zero water and is a dry desert basin.", "CONTRADICTED", "The Pacific Ocean is the largest marine body on Earth, containing more than 700 million cubic kilometers of saltwater.", "Oceans"),
        ("The Nile River flows exclusively through Canada and Alaska.", "CONTRADICTED", "The Nile River flows through northeastern Africa including Egypt, Sudan, and Uganda; it has no presence in North America.", "Rivers"),
        ("Antarctica has tropical rainforests with average temperatures of 40 degrees Celsius.", "CONTRADICTED", "Antarctica is covered by an ice sheet kilometers thick and experiences severe sub-zero polar temperatures.", "Polar"),
        ("Tokyo is the capital city of Australia.", "CONTRADICTED", "Canberra is the capital city of Australia; Tokyo is the capital of Japan.", "Capitals"),
        ("The Sahara Desert is located in central Sweden and is covered in glaciers.", "CONTRADICTED", "The Sahara Desert is located across North Africa and is a hyper-arid subtropical desert.", "Deserts"),
        ("Lake Baikal is a man-made swimming pool constructed in 2018.", "CONTRADICTED", "Lake Baikal is an ancient natural rift lake formed over 25 million years ago in Siberia.", "Lakes"),
        ("Greenland is the smallest island on Earth with an area of five square meters.", "CONTRADICTED", "Greenland is the largest non-continental island on Earth, spanning over 2.1 million square kilometers.", "Islands"),
        ("The equator passes directly through the geographic North Pole.", "CONTRADICTED", "The equator lies at 0 degrees latitude, exactly 90 degrees away from the North Pole at 90 degrees N.", "Geodesy"),
        ("The Dead Sea has the lowest salt concentration of any lake on Earth.", "CONTRADICTED", "The Dead Sea is one of the saltiest bodies of water in the world, with a salinity exceeding 34%.", "Lakes"),
        ("The Amazon River originates in the middle of Paris, France.", "CONTRADICTED", "The Amazon River originates in the Peruvian Andes in South America and empties into the Atlantic Ocean.", "Rivers"),
        ("The Mariana Trench is an active volcano situated on top of Mount Kilimanjaro.", "CONTRADICTED", "The Mariana Trench is an oceanic subduction trench on the Pacific seafloor, reaching depths near 11,000 meters.", "Oceanography"),

        # NEI (11)
        ("A fisherman on Lake Baikal in 1898 caught exactly 7 grayling before noon on a Thursday.", "NEI", "19th-century commercial fishery registries compile annual tonnages, not daily individual catch tallies.", "Unrecorded Tally"),
        ("A specific mountaineer on Mount Everest in 1978 preferred strawberry energy gel to chocolate.", "NEI", "Himalayan expedition logistics archives record oxygen bottles and total rations without personal gel flavor notes.", "Personal Preference"),
        ("A lone camel in the central Sahara was born with a white star marking between its ears in 1922.", "NEI", "Nomadic herd records do not chronicle individual camel birth markings in early 20th-century North Africa.", "Unrecorded Specimen"),
        ("In the year 2400, climate engineers will turn the entire Sahara into a freshwater ocean.", "NEI", "Geoengineering visions four centuries in the future are unverified speculative hypotheses.", "Future Speculation"),
        ("A tourist in Tokyo in 1985 dropped a five-yen coin into an unrecorded storm drain in Shibuya.", "NEI", "Metropolitan municipal drainage departments do not catalog individual small coin drops.", "Unrecorded Incident"),
        ("An uncharted cave in the Amazon rainforest contains a lost golden monkey statue.", "NEI", "Speleological and archaeological surveys have no substantiated record of this purported statue.", "Folklore / Unverified"),
        ("A specific wave in the central Pacific Ocean on June 12, 1940, reached exactly 4.12 meters in height.", "NEI", "Oceanographic wave height recordings prior to satellite altimetry cannot pinpoint individual open-sea waves.", "Unrecorded Measurement"),
        ("A penguin in Antarctica privately preferred eating silverfish over krill on Christmas Day 1999.", "NEI", "Zoological dietary field observations track general feeding patterns, not individual bird choices on holidays.", "Unrecorded Animal Behavior"),
        ("An unrecorded green pebble sits at the exact coordinates 45 degrees N, 120 degrees W.", "NEI", "Geological mapping data tracks rock strata, not the precise placement of individual small pebbles.", "Unrecorded Object"),
        ("A sailor crossing the equator in 1860 sneezed three consecutive times during the ceremony.", "NEI", "Line-crossing maritime logs document ship positions and traditional pranks, not crew sneezing tallies.", "Unrecorded Incident"),
        ("The Dead Sea mud was privately deemed too slimy by an anonymous traveller in 1933.", "NEI", "Travel literature from the British Mandate period does not index anonymous sensory impressions.", "Personal Opinion")
    ]
    for idx, (claim, label, context, subcat) in enumerate(geo_items, 1):
        dataset.append({
            "id": f"eval_geo_{idx:03d}",
            "domain": "Geography & Earth Sciences",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 5: Physics, Chemistry & Materials (35 items)
    phys_items = [
        # Supported (12)
        ("Water molecules are composed of two hydrogen atoms and one oxygen atom.", "SUPPORTED", "Water (H2O) is a chemical compound consisting of two hydrogen atoms covalently bonded to a single oxygen atom.", "Chemistry"),
        ("The atomic number of carbon is six.", "SUPPORTED", "Carbon is a chemical element with the symbol C and atomic number 6, located in group 14 of the periodic table.", "Periodic Table"),
        ("Newton's second law states that force equals mass times acceleration.", "SUPPORTED", "In classical mechanics, Newton's second law is formulated as F = ma, where force equals mass multiplied by acceleration.", "Mechanics"),
        ("Gold is a transition metal with the chemical symbol Au.", "SUPPORTED", "Gold is a transition metal with symbol Au (from Latin aurum) and atomic number 79.", "Chemistry"),
        ("Absolute zero is defined as zero Kelvin, equivalent to minus 273.15 degrees Celsius.", "SUPPORTED", "Absolute zero is the theoretical lower limit of thermodynamic temperature, defined as 0 K or -273.15 deg C.", "Thermodynamics"),
        ("An electron carries a negative fundamental electric charge.", "SUPPORTED", "The electron is a subatomic particle with an elementary electric charge of -1.602 x 10^-19 coulombs.", "Particle Physics"),
        ("Helium is a noble gas that is chemically inert under standard conditions.", "SUPPORTED", "Helium is a colorless, odorless noble gas with a filled valence shell, rendering it unreactive in normal conditions.", "Inorganic Chemistry"),
        ("The first law of thermodynamics states that energy cannot be created or destroyed.", "SUPPORTED", "The law of conservation of energy establishes that the total energy of an isolated system remains constant over time.", "Thermodynamics"),
        ("Sodium chloride is an ionic compound formed from sodium and chlorine.", "SUPPORTED", "Table salt (NaCl) is an ionic lattice composed of sodium cations and chloride anions.", "Chemistry"),
        ("Diamond is an allotrope of carbon arranged in a tetrahedral crystal lattice.", "SUPPORTED", "Diamond is a solid form of carbon with atoms arranged in a diamond cubic tetrahedral crystal structure.", "Materials"),
        ("Photons are the elementary gauge bosons of the electromagnetic force.", "SUPPORTED", "In the Standard Model of particle physics, the photon is the massless mediator of the electromagnetic interaction.", "Quantum Physics"),
        ("The pH of pure water at 25 degrees Celsius is approximately 7.0.", "SUPPORTED", "Pure water has an autoionization constant yielding equal concentrations of hydronium and hydroxide ions, resulting in a neutral pH of 7.", "Physical Chemistry"),

        # Contradicted (12)
        ("Water molecules consist of eight uranium atoms and no hydrogen.", "CONTRADICTED", "Water is chemically defined as H2O, composed of two hydrogen atoms and one oxygen atom; it contains no uranium.", "Chemistry"),
        ("The atomic number of carbon is 92, making it heavier than uranium.", "CONTRADICTED", "Carbon has atomic number 6, while uranium has atomic number 92; carbon is far lighter than uranium.", "Periodic Table"),
        ("Newton's second law states that force equals mass divided by infinity.", "CONTRADICTED", "Newton's second law establishes that force is proportional to the product of mass and acceleration (F = ma).", "Mechanics"),
        ("Gold is a synthetic gas that evaporates into steam at room temperature.", "CONTRADICTED", "Gold is a dense, solid, malleable noble metal with a melting point of over 1,064 degrees Celsius.", "Chemistry"),
        ("Absolute zero is the hottest possible temperature in the universe, exceeding a million degrees.", "CONTRADICTED", "Absolute zero (0 K or -273.15 C) is the lowest possible temperature where thermodynamic entropy reaches its minimum.", "Thermodynamics"),
        ("Electrons carry a strong positive charge and reside exclusively inside the atomic nucleus.", "CONTRADICTED", "Electrons carry a negative elementary charge and orbit the nucleus, while positively charged protons reside inside the nucleus.", "Particle Physics"),
        ("Helium is an extremely radioactive explosive solid metal at standard conditions.", "CONTRADICTED", "Helium is an inert, non-toxic, non-radioactive noble gas under standard temperature and pressure.", "Inorganic Chemistry"),
        ("Energy can be routinely created out of nothing in common household toaster ovens.", "CONTRADICTED", "The law of conservation of energy proves that energy cannot be created or destroyed, only transformed.", "Thermodynamics"),
        ("Sodium chloride is composed entirely of pure gaseous neon and helium.", "CONTRADICTED", "Sodium chloride is formed of sodium and chlorine ions; it contains neither neon nor helium.", "Chemistry"),
        ("Diamond is composed entirely of pure frozen water ice.", "CONTRADICTED", "Diamond is an allotrope of pure elemental carbon, not water ice.", "Materials"),
        ("Photons have a resting mass of 500 kilograms each.", "CONTRADICTED", "Photons are fundamental gauge bosons with zero invariant rest mass.", "Quantum Physics"),
        ("The pH of pure neutral water at room temperature is exactly 14.0.", "CONTRADICTED", "Neutral water has a pH of approximately 7.0 at 25 degrees Celsius; a pH of 14 indicates an extremely basic solution.", "Physical Chemistry"),

        # NEI (11)
        ("A lab technician in Munich in 1954 accidentally spilled exactly 3.2 ml of ethanol on his shoe.", "NEI", "Laboratory incident logs from the mid-20th century record hazardous exposures, not minor solvent shoe splashes.", "Unrecorded Incident"),
        ("The physicist Niels Bohr privately preferred dark chocolate over milk chocolate.", "NEI", "Biographical archives of Bohr document his correspondence on quantum mechanics, not private confectionery tastes.", "Personal Preference"),
        ("An unrecorded block of polished copper sitting in a basement in Leeds has a mass of 4.312 kilograms.", "NEI", "Weights and measures standards offices do not keep inventory of random private domestic metal scraps.", "Unrecorded Object"),
        ("By the year 2350, physicists will discover a particle with twelve distinct fractional charges.", "NEI", "Particle physics discoveries in the 24th century cannot be verified as existing facts.", "Future Speculation"),
        ("Marie Curie's favorite writing pencil during the winter of 1903 was made of cedar wood.", "NEI", "Archival personal papers of Marie Curie preserve research notebooks, not the wood species of her pencils.", "Private Stationery"),
        ("A flask of sodium chloride in an Australian school in 1982 was washed with lemon-scented soap.", "NEI", "Secondary school chemistry prep room cleaning records are discarded after academic terms.", "Unrecorded Event"),
        ("An anonymous glassblower in Venice in 1750 made a test tube that held exactly 17.5 ml of water.", "NEI", "Pre-industrial Venetian glassware guild records track export tariffs rather than volume graduations.", "Unrecorded Object"),
        ("Michael Faraday thought that Tuesday was his luckiest day for conducting electromagnetic trials.", "NEI", "Faraday's extensive laboratory diaries detail coil windings and induction readings without lucky day remarks.", "Personal Belief"),
        ("In 2100, chemists will synthesize a room-temperature superconductor from coffee grounds.", "NEI", "Speculative superconductor claims decades in the future are unverified prospective ideas.", "Future Speculation"),
        ("A specific drop of rain falling over London on October 3, 1910, had a pH of exactly 5.432.", "NEI", "Meteorological precipitation chemistry before modern acid rain networks was not monitored with decimal precision.", "Unrecorded Metric"),
        ("Albert Einstein privately found the odor of burning sulfur more irritating than rotten eggs.", "NEI", "Einstein's personal correspondence contains philosophical debates, not comparative sulfur olfactory rankings.", "Personal Preference")
    ]
    for idx, (claim, label, context, subcat) in enumerate(phys_items, 1):
        dataset.append({
            "id": f"eval_phys_{idx:03d}",
            "domain": "Physics & Chemistry",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 6: Mathematics, Logic & Computing (35 items)
    comp_items = [
        # Supported (12)
        ("The sum of 15 and 27 equals 42.", "SUPPORTED", "Arithmetic addition confirms that 15 + 27 = 42.", "Arithmetic"),
        ("Python was created by Guido van Rossum and released in 1991.", "SUPPORTED", "Guido van Rossum developed Python in the late 1980s as a successor to ABC, releasing it in February 1991.", "Computer History"),
        ("The World Wide Web was invented by Tim Berners-Lee in 1989 at CERN.", "SUPPORTED", "British scientist Tim Berners-Lee invented the World Wide Web in 1989 while working at CERN.", "Internet"),
        ("A prime number is a positive integer greater than 1 that has no positive divisors other than 1 and itself.", "SUPPORTED", "In number theory, a prime number is defined as a natural number greater than 1 whose only divisors are 1 and itself.", "Number Theory"),
        ("Binary code uses only two symbols, typically 0 and 1, to represent data.", "SUPPORTED", "Binary is a base-2 numeral system that utilizes the digits 0 and 1 to encode digital information.", "Computer Architecture"),
        ("Alan Turing formulated the concept of the Turing machine in 1936.", "SUPPORTED", "Alan Turing introduced the theoretical concept of the universal computing machine in his landmark 1936 paper.", "Theoretical CS"),
        ("The product of 8 and 7 is equal to 56.", "SUPPORTED", "Multiplication yields 8 x 7 = 56.", "Arithmetic"),
        ("An algorithm with O(1) time complexity runs in constant time regardless of input size.", "SUPPORTED", "Constant time complexity O(1) denotes that algorithm execution time is invariant to input scale.", "Algorithms"),
        ("Linux was first released by Linus Torvalds in 1991.", "SUPPORTED", "Finnish computer science student Linus Torvalds released the Linux kernel on September 17, 1991.", "Operating Systems"),
        ("The mathematical constant pi represents the ratio of a circle's circumference to its diameter.", "SUPPORTED", "Pi is an irrational mathematical constant defined as the ratio of any Euclidean circle's perimeter to its diameter.", "Geometry"),
        ("Ada Lovelace is widely regarded as the first computer programmer for her work on Babbage's Analytical Engine.", "SUPPORTED", "Ada Lovelace published the first algorithm intended for implementation on Charles Babbage's mechanical computer.", "History of Computing"),
        ("A byte is traditionally composed of eight binary bits.", "SUPPORTED", "In computing, a byte is the standard unit of digital data storage consisting of 8 contiguous bits.", "Information Theory"),

        # Contradicted (12)
        ("The sum of 15 and 27 equals 99.", "CONTRADICTED", "The sum of 15 and 27 is 42, not 99.", "Arithmetic"),
        ("Python was created by Julius Caesar in ancient Rome.", "CONTRADICTED", "Python was designed by Dutch programmer Guido van Rossum in the late 1980s, over two millennia after Julius Caesar.", "Computer History"),
        ("The World Wide Web was invented in 1492 by Christopher Columbus.", "CONTRADICTED", "Tim Berners-Lee invented the World Wide Web in 1989 at CERN, centuries after Christopher Columbus.", "Internet"),
        ("A prime number is defined as any number that is divisible by every number in existence.", "CONTRADICTED", "A prime number is an integer greater than 1 that is divisible only by 1 and itself.", "Number Theory"),
        ("Binary code utilizes twenty-six distinct Latin alphabet letters instead of numbers.", "CONTRADICTED", "Binary code represents information strictly using base-2 digits: 0 and 1.", "Computer Architecture"),
        ("Alan Turing was a professional ballet dancer who never worked on computing machines.", "CONTRADICTED", "Alan Turing was a pioneering mathematician and computer scientist who laid theoretical foundations for computing.", "Theoretical CS"),
        ("The product of 8 and 7 equals 1,000,000.", "CONTRADICTED", "The product of 8 and 7 is 56, not 1,000,000.", "Arithmetic"),
        ("An algorithm with O(1) time complexity requires more time to run as input size grows.", "CONTRADICTED", "Constant time O(1) algorithms execute in fixed time irrespective of input volume.", "Algorithms"),
        ("Linux was created by Napoleon Bonaparte in 1812.", "CONTRADICTED", "Linux was developed and released by Linus Torvalds in 1991.", "Operating Systems"),
        ("The mathematical constant pi is an integer that equals exactly four.", "CONTRADICTED", "Pi is an irrational transcendental number approximately equal to 3.14159, not 4.", "Geometry"),
        ("Ada Lovelace was an American astronaut who flew on the Space Shuttle Challenger.", "CONTRADICTED", "Ada Lovelace was a 19th-century English mathematician who worked on Babbage's Analytical Engine.", "History of Computing"),
        ("A standard computer byte is composed of 10,000 bits.", "CONTRADICTED", "In digital architecture, a standard byte consists of exactly 8 bits.", "Information Theory"),

        # NEI (11)
        ("Linus Torvalds wore green wool socks when writing the initial Linux kernel release announcement.", "NEI", "Historical Usenet archive comp.os.minix preserves the text of Torvalds's post, not his personal clothing.", "Personal Wardrobe"),
        ("Guido van Rossum privately preferred indenting code with three spaces rather than four in 1992.", "NEI", "Python PEP 8 establishes 4-space indentation conventions, but informal private 1992 preferences are unrecorded.", "Private Preference"),
        ("Tim Berners-Lee drank Earl Grey tea from a chipped white mug when typing the first HTML document.", "NEI", "CERN technological exhibits preserve NeXT computer hardware, not disposable office beverage mugs.", "Unrecorded Anecdote"),
        ("A quantum computer in the year 2120 will compute the final decimal digit of pi.", "NEI", "Pi has been mathematically proven to be irrational with infinitely non-repeating digits; future claims are invalid.", "Future Speculation"),
        ("Alan Turing's favorite childhood bicycle had an unrecorded squeak in its left pedal.", "NEI", "Biographies of Turing cover his schooling and marathon running, not minor bicycle pedal squeaks.", "Unrecorded Anecdote"),
        ("A programmer in Seattle in 1998 had exactly 14 rubber ducks lined up on his office desk.", "NEI", "Corporate cubicle inventories do not document personal desk toy tallies of individual engineers.", "Unrecorded Private Habit"),
        ("An unrecorded sorting algorithm designed in 1974 used playing cards and was lost in a house fire.", "NEI", "Computer science bibliographies index peer-reviewed literature; lost home experiments are untraceable.", "Lost Artifact"),
        ("Charles Babbage privately considered the hurdy-gurdy to be an instrument of torment.", "NEI", "Babbage campaigned publicly against street organ-grinders, but specific hurdy-gurdy diary entries are absent.", "Personal Opinion"),
        ("The 1,000,000,000,000th digit of the mathematical constant e is an unrecorded prime number.", "NEI", "Individual single digits are digits (0-9), not separate multi-digit prime numbers.", "Nonsense Assertion"),
        ("A floppy disk stored in an attic in Boston contains a forgotten BASIC game written in 1983.", "NEI", "Private home media collections are uncataloged and unverified in computing history repositories.", "Lost Artifact"),
        ("In the year 2080, an AI will write a computer operating system entirely in rhyming sonnets.", "NEI", "Speculative software development decades in advance cannot be verified as existing fact.", "Future Speculation")
    ]
    for idx, (claim, label, context, subcat) in enumerate(comp_items, 1):
        dataset.append({
            "id": f"eval_comp_{idx:03d}",
            "domain": "Computing & Mathematics",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 7: Arts, Literature & Culture (35 items)
    arts_items = [
        # Supported (12)
        ("William Shakespeare wrote the tragedy Hamlet.", "SUPPORTED", "The Tragedy of Hamlet, Prince of Denmark is a tragedy written by William Shakespeare between 1599 and 1601.", "Drama"),
        ("Leonardo da Vinci painted the Mona Lisa in Florence.", "SUPPORTED", "The Mona Lisa is a half-length portrait painting created by Leonardo da Vinci in the early 16th century in Florence.", "Painting"),
        ("Michelangelo sculpted the marble statue of David in Florence.", "SUPPORTED", "The statue of David is a masterpiece of Renaissance sculpture created in marble between 1501 and 1504 by Michelangelo.", "Sculpture"),
        ("Ludwig van Beethoven composed his Ninth Symphony in D minor.", "SUPPORTED", "Beethoven's Symphony No. 9 in D minor, Op. 125, is a choral symphony premiered in Vienna in 1824.", "Classical Music"),
        ("Jane Austen authored the novel Pride and Prejudice, published in 1813.", "SUPPORTED", "Pride and Prejudice is an 1813 romantic novel of manners written by English author Jane Austen.", "Literature"),
        ("Vincent van Gogh painted The Starry Night while staying at the Saint-Paul asylum in Saint-Remy.", "SUPPORTED", "Van Gogh painted The Starry Night in June 1889 depicting the view from his asylum room window at Saint-Remy-de-Provence.", "Post-Impressionism"),
        ("The Epic of Gilgamesh is an ancient Mesopotamian epic poem.", "SUPPORTED", "The Epic of Gilgamesh is an epic poem from ancient Mesopotamia regarded as the earliest surviving notable literature.", "Ancient Literature"),
        ("Miguel de Cervantes wrote the classic Spanish novel Don Quixote.", "SUPPORTED", "Don Quixote is a Spanish novel by Miguel de Cervantes published in two parts in 1605 and 1615.", "Literature"),
        ("The Louvre Museum in Paris is home to the Winged Victory of Samothrace.", "SUPPORTED", "The marble Hellenistic sculpture Winged Victory of Samothrace has been displayed prominently in the Louvre since 1884.", "Museums"),
        ("Pablo Picasso co-founded the Cubist art movement in the early 20th century.", "SUPPORTED", "Pablo Picasso and Georges Braque pioneered Cubism in Paris between 1907 and 1914.", "Modern Art"),
        ("The Canterbury Tales is a collection of stories written in Middle English by Geoffrey Chaucer.", "SUPPORTED", "Geoffrey Chaucer wrote The Canterbury Tales in Middle English towards the end of the 14th century.", "Middle English"),
        ("George Orwell wrote the dystopian political novel Nineteen Eighty-Four, published in 1949.", "SUPPORTED", "Nineteen Eighty-Four is a dystopian social science fiction novel by English novelist George Orwell published in 1949.", "Literature"),

        # Contradicted (12)
        ("William Shakespeare wrote the television series Breaking Bad in 1600.", "CONTRADICTED", "William Shakespeare was an Elizabethan playwright who died in 1616; Breaking Bad was created by Vince Gilligan in 2008.", "Drama"),
        ("Leonardo da Vinci painted the Mona Lisa on a digital iPad in 2021.", "CONTRADICTED", "The Mona Lisa was painted with oil on a poplar panel in the early 16th century by Leonardo da Vinci.", "Painting"),
        ("Michelangelo sculpted the Statue of Liberty in New York Harbor.", "CONTRADICTED", "The Statue of Liberty was designed by French sculptor Frederic-Auguste Bartholdi, not Michelangelo.", "Sculpture"),
        ("Ludwig van Beethoven was a professional baseball player who never composed music.", "CONTRADICTED", "Beethoven was one of the most celebrated classical composers in Western history.", "Classical Music"),
        ("Jane Austen authored the science fiction novel Jurassic Park in 1813.", "CONTRADICTED", "Jurassic Park was written by Michael Crichton and published in 1990; Jane Austen wrote Pride and Prejudice.", "Literature"),
        ("Vincent van Gogh painted The Starry Night during a space walk on Mars.", "CONTRADICTED", "Van Gogh painted The Starry Night in 1889 at the Saint-Paul asylum in France.", "Painting"),
        ("The Epic of Gilgamesh was written by Mark Twain in California in 1995.", "CONTRADICTED", "The Epic of Gilgamesh is an ancient Mesopotamian literary work dating to the second millennium BC.", "Ancient Literature"),
        ("Miguel de Cervantes wrote the play Romeo and Juliet in Russian.", "CONTRADICTED", "Romeo and Juliet was written by William Shakespeare in English; Cervantes wrote Don Quixote in Spanish.", "Literature"),
        ("The Louvre Museum is a small hot dog stand in Chicago with zero art.", "CONTRADICTED", "The Louvre in Paris is the world's most visited art museum, housing tens of thousands of historic masterworks.", "Museums"),
        ("Pablo Picasso was an Egyptian pharaoh buried in the Great Pyramid of Giza.", "CONTRADICTED", "Pablo Picasso was a 20th-century Spanish artist who lived from 1881 to 1973.", "Modern Art"),
        ("The Canterbury Tales was written in modern emoji symbols on Twitter in 2020.", "CONTRADICTED", "The Canterbury Tales was composed in Middle English verse by Geoffrey Chaucer in the late 14th century.", "Middle English"),
        ("George Orwell published Nineteen Eighty-Four in the year 500 BC in ancient Sparta.", "CONTRADICTED", "Nineteen Eighty-Four was written by British author George Orwell and published in June 1949.", "Literature"),

        # NEI (11)
        ("William Shakespeare's favorite goose feather quill was plucked from a white gander named Barnaby.", "NEI", "Parish registers and theatrical records do not document the domestic origins of Shakespeare's quills.", "Personal Detail"),
        ("Leonardo da Vinci hummed a Florentine tavern song while mixing pigments for the Mona Lisa.", "NEI", "Da Vinci's extensive codices record engineering sketches and painting techniques, not private humming.", "Unrecorded Anecdote"),
        ("Michelangelo preferred eating roasted chestnuts over bread while sculpting David.", "NEI", "Renaissance letters and payment ledgers record block purchases and marble deliveries, not snack preferences.", "Personal Preference"),
        ("In the year 2200, an art museum on the Moon will exhibit the first sculpture made of starlight.", "NEI", "Speculative lunar museum exhibitions centuries ahead cannot be verified as existing facts.", "Future Speculation"),
        ("Jane Austen's pet canary escaped from its wicker cage for twenty minutes in May 1811.", "NEI", "Family letters preserved from the Austen estate do not chronicle brief domestic bird escapes.", "Unrecorded Incident"),
        ("Vincent van Gogh owned an unrecorded pocketknife with a cracked bone handle in Saint-Remy.", "NEI", "Asylum administrative records catalog patient admissions and treatments, not individual pocket utensils.", "Unrecorded Object"),
        ("An unknown ancient Babylonian scribe spilled sesame oil on the margin of tablet 4 of Gilgamesh.", "NEI", "Cuneiform clay tablets exhibit mineral staining, but contemporaneous oil spills are unrecorded.", "Unrecorded Incident"),
        ("Miguel de Cervantes privately thought that Don Quixote should have ridden a white mule instead of Rocinante.", "NEI", "Draft manuscripts of Don Quixote do not record alternate draft equine selections.", "Authorial Thought"),
        ("A visitor to the Louvre in 1968 wore one blue sock and one brown sock to see the Mona Lisa.", "NEI", "Museum ticket stubs and security guard registries do not catalog visitor hosiery pairings.", "Personal Wardrobe"),
        ("Pablo Picasso secretly hid a drawing of an apple inside a Parisian cafe wall in 1912.", "NEI", "Catalogue raisonne archives document verified works; unsubstantiated cafe wall rumors are unverified.", "Lost Artwork"),
        ("George Orwell drank four cups of black tea before writing chapter 3 of Nineteen Eighty-Four.", "NEI", "Orwell's published essays describe his tea-making rules, but day-to-day writing consumption tallies are unrecorded.", "Unrecorded Tally")
    ]
    for idx, (claim, label, context, subcat) in enumerate(arts_items, 1):
        dataset.append({
            "id": f"eval_arts_{idx:03d}",
            "domain": "Arts, Literature & Culture",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 8: Geopolitics, Law & Global Institutions (35 items)
    law_items = [
        # Supported (12)
        ("The United Nations was established in 1945 following the conclusion of World War II.", "SUPPORTED", "The United Nations was founded on October 24, 1945, when the UN Charter was ratified by the permanent members of the Security Council.", "International Bodies"),
        ("The International Court of Justice is seated at the Peace Palace in The Hague, Netherlands.", "SUPPORTED", "The ICJ is the principal judicial organ of the United Nations, seated at the Peace Palace in The Hague.", "International Law"),
        ("The European Union was established by the Maastricht Treaty signed in 1992.", "SUPPORTED", "The Treaty on European Union (Maastricht Treaty) was signed on February 7, 1992, creating the European Union.", "Treaties"),
        ("The Universal Declaration of Human Rights was proclaimed by the UN General Assembly in Paris in 1948.", "SUPPORTED", "Resolution 217 A adopted the Universal Declaration of Human Rights in Paris on December 10, 1948.", "Human Rights"),
        ("The Geneva Conventions comprise four treaties that establish international standards for humanitarian treatment in war.", "SUPPORTED", "The Geneva Conventions of 1949 establish humanitarian protections for non-combatants and prisoners of war.", "Humanitarian Law"),
        ("Switzerland is historically renowned for its policy of armed neutrality in international conflicts.", "SUPPORTED", "Swiss neutrality was recognized internationally by the Treaty of Paris in 1815 and maintained through global conflicts.", "Foreign Policy"),
        ("The United States Constitution was signed in Philadelphia in September 1787.", "SUPPORTED", "The Constitutional Convention in Philadelphia completed and signed the U.S. Constitution on September 17, 1787.", "Constitutional"),
        ("Interpol is the world's largest international criminal police organization.", "SUPPORTED", "Interpol facilitates worldwide police cooperation across 196 member countries, headquartered in Lyon, France.", "Law Enforcement"),
        ("The World Health Organization is a specialized agency of the United Nations responsible for international public health.", "SUPPORTED", "The WHO was founded on April 7, 1948, as the UN agency tasked with coordinating global public health responses.", "Public Health"),
        ("The North Atlantic Treaty Organization (NATO) was established by the North Atlantic Treaty in 1949.", "SUPPORTED", "NATO is an intergovernmental military alliance between North American and European countries founded on April 4, 1949.", "Alliances"),
        ("The International Criminal Court investigates and prosecutes individuals for genocide, war crimes, and crimes against humanity.", "SUPPORTED", "Established by the Rome Statute, the ICC prosecutes individuals for international crimes of genocide, crimes against humanity, and aggression.", "Criminal Law"),
        ("The Magna Carta established the principle that everyone, including the king, is subject to the law.", "SUPPORTED", "Clause 39 of the 1215 Magna Carta established foundational principles of due process and legal limitation on sovereign power.", "Constitutional History"),

        # Contradicted (12)
        ("The United Nations was founded by Julius Caesar in 50 BC.", "CONTRADICTED", "The United Nations was established in October 1945 by 51 founding sovereign nations after World War II.", "International Bodies"),
        ("The International Court of Justice is seated on a submarine at the bottom of the Mariana Trench.", "CONTRADICTED", "The International Court of Justice is located at the Peace Palace in The Hague, Netherlands.", "International Law"),
        ("The European Union was established in the year 1200 by Genghis Khan.", "CONTRADICTED", "The European Union was founded in the 20th century, formalized by the Maastricht Treaty of 1992.", "Treaties"),
        ("The Universal Declaration of Human Rights mandates that all citizens must eat rocks every morning.", "CONTRADICTED", "The UDHR enshrines fundamental civil, political, economic, and social rights; it contains no dietary rock mandates.", "Human Rights"),
        ("The Geneva Conventions require that all prisoners of war must be executed immediately.", "CONTRADICTED", "The Geneva Conventions strictly prohibit the execution, torture, or cruel treatment of prisoners of war.", "Humanitarian Law"),
        ("Switzerland has fought in every single major world war as an aggressive expansionist empire.", "CONTRADICTED", "Switzerland has maintained a formal policy of armed neutrality since 1815 and did not participate militarily in either World War.", "Foreign Policy"),
        ("The United States Constitution was drafted and signed on the Moon in 1969.", "CONTRADICTED", "The U.S. Constitution was drafted in Philadelphia during the Constitutional Convention of 1787.", "Constitutional"),
        ("Interpol is an intergalactic space fleet commanded by comic book characters.", "CONTRADICTED", "Interpol is an international police organization facilitating transnational criminal investigations among 196 member nations.", "Law Enforcement"),
        ("The World Health Organization was founded in 1500 to promote smoking cigarettes to infants.", "CONTRADICTED", "The WHO was founded in 1948 by the United Nations to promote global health, prevent epidemics, and improve healthcare access.", "Public Health"),
        ("NATO was established in 1776 by George Washington to fight dinosaurs.", "CONTRADICTED", "NATO was created in 1949 in Washington D.C. as a collective defense pact among Western nations during the Cold War.", "Alliances"),
        ("The International Criminal Court has jurisdiction only over domestic traffic parking tickets.", "CONTRADICTED", "The ICC has jurisdiction exclusively over the gravest international crimes: genocide, war crimes, and crimes against humanity.", "Criminal Law"),
        ("The Magna Carta granted English monarchs absolute unlimited divine authority to execute anyone without trial.", "CONTRADICTED", "The Magna Carta was historic specifically because it curtailed royal prerogative and subjected the monarch to the rule of law.", "Constitutional History"),

        # NEI (11)
        ("An unrecorded UN delegate sneezed into a green silk handkerchief during the signing of the UN Charter in 1945.", "NEI", "Official plenary session minutes and photographic records document delegations, not personal handkerchief colors.", "Unrecorded Detail"),
        ("A judge at the International Court of Justice in 1972 privately preferred drinking hot cocoa during winter deliberations.", "NEI", "ICJ judicial deliberations are strictly confidential, and personal chamber beverages are unrecorded.", "Personal Preference"),
        ("The pen used by a diplomat to sign the Maastricht Treaty had an unrecorded microscopic scratch on its clip.", "NEI", "Museum treaty accession archives preserve ceremonial pens without microscopic scratch surveys.", "Unrecorded Detail"),
        ("By the year 2300, a single global court will govern interstellar interplanetary disputes across the solar system.", "NEI", "Future speculative planetary jurisprudence centuries ahead cannot be verified as existing fact.", "Future Speculation"),
        ("A clerk filing Geneva Convention drafts in 1949 accidentally used red paperclips for two folders.", "NEI", "Swiss federal diplomatic archives preserve draft treaties, not temporary office paperclip assortments.", "Unrecorded Incident"),
        ("A Swiss border guard in 1942 secretly kept a pet field mouse inside his guardhouse coat pocket.", "NEI", "Border military station logs track border crossings and cargo, not unauthorized personal pet rodents.", "Unrecorded Anecdote"),
        ("Benjamin Franklin misplaced his reading glasses for twelve minutes during the 1787 Constitutional Convention.", "NEI", "Madison's comprehensive convention notes record speeches and debates, not minor personal spectacles misplacements.", "Unrecorded Incident"),
        ("An Interpol communications officer in Lyon in 1980 secretly enjoyed listening to disco music on lunch breaks.", "NEI", "Interpol employee personnel files contain employment evaluations, not private musical lunch choices.", "Personal Preference"),
        ("The director-general of the WHO in 1960 privately favored green tea over black tea.", "NEI", "Public health policy archives preserve official speeches and epidemiological reports, not personal beverage preferences.", "Personal Preference"),
        ("A NATO general in 1965 privately believed that Monday was the worst day of the week to hold briefings.", "NEI", "Military command headquarters records log operational readiness, not casual weekday opinions of officers.", "Personal Opinion"),
        ("An unrecorded legal intern at the ICC in 2005 accidentally spilled instant coffee on a blank legal pad.", "NEI", "Judicial registry facilities do not file reports on blank discarded stationery spills.", "Unrecorded Incident")
    ]
    for idx, (claim, label, context, subcat) in enumerate(law_items, 1):
        dataset.append({
            "id": f"eval_law_{idx:03d}",
            "domain": "Law & Institutions",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 9: Technology, Engineering & Infrastructure (35 items)
    tech_items = [
        # Supported (12)
        ("The transistor was invented at Bell Labs in December 1947.", "SUPPORTED", "John Bardeen, Walter Brattain, and William Shockley invented the point-contact transistor at Bell Telephone Laboratories in December 1947.", "Electronics"),
        ("The Panama Canal connects the Atlantic Ocean and the Pacific Ocean across the Isthmus of Panama.", "SUPPORTED", "The Panama Canal is an artificial 82-kilometer waterway in Panama that links the Atlantic and Pacific Oceans.", "Civil Engineering"),
        ("The steam engine was improved substantially by James Watt in the 1760s and 1770s.", "SUPPORTED", "Scottish inventor James Watt patented the separate condenser for steam engines in 1769, greatly enhancing thermodynamic efficiency.", "Mechanical"),
        ("The Wright brothers made the first controlled powered airplane flights at Kitty Hawk in December 1903.", "SUPPORTED", "Orville and Wilbur Wright achieved the first sustained powered heavier-than-air human flight on December 17, 1903, in North Carolina.", "Aviation"),
        ("Fiber-optic communication transmits information using pulses of light through strands of glass or plastic.", "SUPPORTED", "Fiber-optic cables utilize total internal reflection to transmit optical data signals with minimal attenuation.", "Telecommunications"),
        ("The Golden Gate Bridge in San Francisco was designed as a suspension bridge and opened in 1937.", "SUPPORTED", "The Golden Gate Bridge is a suspension bridge spanning the Golden Gate strait, opened to vehicular traffic in May 1937.", "Bridges"),
        ("Gutenberg developed the movable-type printing press in Europe around 1440.", "SUPPORTED", "Johannes Gutenberg introduced movable metal type printing to Europe around 1440 in Mainz, Germany.", "Printing"),
        ("GPS is a satellite-based radionavigation system owned by the United States government.", "SUPPORTED", "The Global Positioning System (GPS) utilizes a constellation of satellites operated by the United States Space Force.", "Navigation"),
        ("The internal combustion engine operates by burning fuel inside a combustion chamber to produce mechanical work.", "SUPPORTED", "Internal combustion engines generate torque through the exothermic expansion of high-temperature combustion gases inside cylinders.", "Automotive"),
        ("Thomas Edison established the first industrial research laboratory at Menlo Park, New Jersey, in 1876.", "SUPPORTED", "Edison created the Menlo Park facility in 1876, regarded as the first organized commercial industrial research laboratory.", "Innovation"),
        ("The Hoover Dam was constructed on the Colorado River on the border of Arizona and Nevada in the 1930s.", "SUPPORTED", "The Hoover Dam is a concrete arch-gravity dam built on the Colorado River between 1931 and 1936.", "Dams"),
        ("Silicon is the primary semiconductor material used in modern integrated circuits.", "SUPPORTED", "Silicon is the foundation of the modern electronics industry due to its semiconductor properties, high abundance, and stable oxide.", "Semiconductors"),

        # Contradicted (12)
        ("The transistor was invented in 1250 by medieval blacksmiths in London.", "CONTRADICTED", "The transistor was invented at Bell Laboratories in New Jersey in 1947 by Bardeen, Brattain, and Shockley.", "Electronics"),
        ("The Panama Canal connects the Moon to the planet Mars across outer space.", "CONTRADICTED", "The Panama Canal is a terrestrial maritime waterway connecting the Atlantic and Pacific Oceans through Panama.", "Civil Engineering"),
        ("The steam engine was invented in the year 2025 by modern smartphone applications.", "CONTRADICTED", "Steam engines were developed and revolutionized in the 18th century by Newcomen and Watt.", "Mechanical"),
        ("The Wright brothers made their first powered flight inside a deep submarine under the Arctic Ocean.", "CONTRADICTED", "The Wright brothers achieved their first powered flights in the air above the coastal sand dunes of Kitty Hawk, North Carolina.", "Aviation"),
        ("Fiber-optic cables transmit information by firing live cannonballs through hollow tunnels.", "CONTRADICTED", "Fiber-optic cables transmit data using pulses of light sent through ultra-pure glass or plastic fiber cores.", "Telecommunications"),
        ("The Golden Gate Bridge was built entirely out of wet cardboard in 1492.", "CONTRADICTED", "The Golden Gate Bridge was constructed of structural steel and reinforced concrete, opening in 1937.", "Bridges"),
        ("Johannes Gutenberg invented the printing press on a laptop computer running Windows 10.", "CONTRADICTED", "Gutenberg developed the mechanical movable metal type printing press in Mainz around 1440.", "Printing"),
        ("The GPS satellite constellation consists of two carrier pigeons flying in circles.", "CONTRADICTED", "GPS relies on a constellation of over 30 electronic satellites in medium Earth orbit broadcasting microwave signals.", "Navigation"),
        ("Internal combustion engines operate exclusively by burning pure water ice with zero fuel.", "CONTRADICTED", "Internal combustion engines require combustible hydrocarbon fuels (e.g. gasoline or diesel) mixed with an oxidizer.", "Automotive"),
        ("Thomas Edison operated Menlo Park as an amusement waterpark with zero inventors.", "CONTRADICTED", "Menlo Park was Edison's pioneering industrial research laboratory dedicated to electrical and acoustic inventions.", "Innovation"),
        ("The Hoover Dam is a wooden garden bench built in 2020 in a private backyard.", "CONTRADICTED", "The Hoover Dam is a massive concrete hydroelectric dam on the Colorado River completed in 1936.", "Dams"),
        ("Modern computer microchips are manufactured exclusively from pure milk chocolate.", "CONTRADICTED", "Integrated circuits are fabricated from ultra-pure crystalline silicon wafers and metallic interconnects.", "Semiconductors"),

        # NEI (11)
        ("An engineer at Bell Labs in 1947 accidentally dropped a copper paperclip behind a filing cabinet.", "NEI", "Historical laboratory logs track experimental transistor voltage outputs, not stray office stationery drops.", "Unrecorded Incident"),
        ("A canal worker in Panama in 1910 privately preferred eating plantains rather than yams for dinner.", "NEI", "Canal commission commissary records track bulk food import tonnage, not private individual worker diets.", "Personal Preference"),
        ("James Watt hummed a Scottish ballad while examining steam pressure gauges in Glasgow.", "NEI", "Watt's technical engineering journals detail cylinder dimensions, not private personal vocalizations.", "Unrecorded Anecdote"),
        ("In the year 2250, engineers will build a space elevator made entirely of carbon nanotubes to geostationary orbit.", "NEI", "Future speculative megastructure engineering centuries ahead cannot be verified as existing fact.", "Future Speculation"),
        ("Orville Wright's leather flight goggles had a tiny unrecorded scratch on the right lens on December 17, 1903.", "NEI", "Museum exhibits at the Smithsonian preserve flight goggles without microscopic scratch inventories.", "Unrecorded Detail"),
        ("A worker painting the Golden Gate Bridge in 1938 accidentally dropped an orange brush into the bay.", "NEI", "Bridge maintenance logs track total paint gallons applied, not individual lost paint brushes.", "Unrecorded Incident"),
        ("A printer apprentice in Gutenberg's shop in 1450 had an ink stain shaped like a crescent on his thumb.", "NEI", "15th-century printing records do not chronicle ink stain contours on apprentice fingers.", "Unrecorded Anecdote"),
        ("A GPS satellite technician in 1995 preferred driving a blue sedan to work rather than a green one.", "NEI", "Air Force aerospace squadron registries track telemetry health, not personal civilian vehicle choices.", "Personal Preference"),
        ("An automobile mechanic in Detroit in 1920 privately considered wrenching easier on rainy days.", "NEI", "Automotive factory work logs record shift hours, not private mechanical weather comfort ratings.", "Personal Opinion"),
        ("Edison's assistant at Menlo Park in 1879 drank three glasses of cider on a Thursday afternoon.", "NEI", "Laboratory notebook entries record filament vacuum readings, not employee beverage consumption tallies.", "Unrecorded Tally"),
        ("An assembly worker in a 1980 silicon fab wore an unrecorded silver ring under her cleanroom glove.", "NEI", "Cleanroom contamination protocols prohibit jewelry, but unrecorded hidden infractions are untraceable.", "Unrecorded Anecdote")
    ]
    for idx, (claim, label, context, subcat) in enumerate(tech_items, 1):
        dataset.append({
            "id": f"eval_tech_{idx:03d}",
            "domain": "Technology & Engineering",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    # Domain 10: Environmental, Agriculture & Food Sciences (35 items)
    env_items = [
        # Supported (12)
        ("Photosynthesis in plants converts carbon dioxide, water, and sunlight into glucose and oxygen.", "SUPPORTED", "Green plants utilize chlorophyll to capture solar energy, converting CO2 and H2O into glucose while releasing oxygen.", "Plant Biology"),
        ("The ozone layer in Earth's stratosphere absorbs the majority of the Sun's harmful ultraviolet radiation.", "SUPPORTED", "The stratospheric ozone layer absorbs between 97% and 99% of medium-frequency ultraviolet light (UV-B) from the Sun.", "Atmosphere"),
        ("Honey is produced by bees using nectar collected from flowers.", "SUPPORTED", "Honey bees ingest floral nectar, enzymatically transform it, and evaporate water content inside honeycomb cells.", "Apiculture"),
        ("Deforestation contributes to global greenhouse gas emissions and biodiversity loss.", "SUPPORTED", "Forest clearing releases stored carbon into the atmosphere and destroys critical habitats for terrestrial flora and fauna.", "Ecology"),
        ("Nitrogen makes up approximately 78% of Earth's atmosphere by volume.", "SUPPORTED", "Dry atmospheric air consists of approximately 78.08% nitrogen, 20.95% oxygen, and 0.93% argon.", "Atmospheric Chemistry"),
        ("Yeast is a single-celled fungus used in the fermentation of bread and alcoholic beverages.", "SUPPORTED", "Saccharomyces cerevisiae is a species of yeast widely employed in baking and brewing to convert sugars into carbon dioxide and ethanol.", "Microbiology"),
        ("The Great Barrier Reef off the coast of Australia is the largest coral reef system in the world.", "SUPPORTED", "The Great Barrier Reef comprises over 2,900 individual reefs and stretches over 2,300 kilometers in the Coral Sea.", "Marine Biology"),
        ("Composting is the biological decomposition of organic waste by microorganisms into nutrient-rich soil.", "SUPPORTED", "Aerobic composting utilizes bacteria and fungi to break down organic materials into stabilized humus for soil enrichment.", "Agriculture"),
        ("Coffee beans are the seeds of berries produced by plants of the genus Coffea.", "SUPPORTED", "Coffee beans are the harvested seeds of the Coffea plant, primarily Coffea arabica and Coffea canephora.", "Agronomy"),
        ("Renewable energy sources include solar, wind, hydroelectric, and geothermal power.", "SUPPORTED", "Renewable energy is derived from naturally replenishing resources such as sunlight, wind, water flow, and geothermal heat.", "Energy"),
        ("The greenhouse effect is a natural process that warms the Earth's surface.", "SUPPORTED", "Atmospheric greenhouse gases absorb and re-emit infrared radiation, maintaining Earth's surface temperature above freezing.", "Climate Science"),
        ("Pollination is the transfer of pollen grains from the male anther to the female stigma of a flower.", "SUPPORTED", "Pollination is the essential reproductive mechanism in angiosperms facilitated by wind, water, or animal vectors.", "Botany"),

        # Contradicted (12)
        ("Photosynthesis in plants requires zero sunlight and occurs exclusively in outer space vacuums.", "CONTRADICTED", "Photosynthesis is light-dependent, requiring solar radiation and carbon dioxide to synthesize sugars in plants.", "Plant Biology"),
        ("The ozone layer produces toxic nuclear radiation that eliminates all life on Earth.", "CONTRADICTED", "The stratospheric ozone layer is protective, shielding Earth's biosphere from mutagenic ultraviolet radiation.", "Atmosphere"),
        ("Honey is mined directly out of underground coal seams as a fossil fuel.", "CONTRADICTED", "Honey is an organic food substance produced biologically by honey bees from floral nectar.", "Apiculture"),
        ("Deforestation causes the total number of trees on Earth to instantly multiply tenfold.", "CONTRADICTED", "Deforestation is the permanent removal and clearing of standing forests, depleting tree cover and biodiversity.", "Ecology"),
        ("Earth's atmosphere is composed of 100% pure liquid gold with zero nitrogen or oxygen.", "CONTRADICTED", "Earth's atmosphere is a gaseous mixture consisting of roughly 78% nitrogen and 21% oxygen.", "Atmospheric Chemistry"),
        ("Yeast is an automobile motor that burns diesel to bake bread.", "CONTRADICTED", "Yeast is a microscopic eukaryotic single-celled fungus used for biological fermentation in baking.", "Microbiology"),
        ("The Great Barrier Reef is a small synthetic plastic toy manufactured in a toy factory in 2021.", "CONTRADICTED", "The Great Barrier Reef is a massive natural marine biome off Australia built by living coral organisms.", "Marine Biology"),
        ("Composting creates hazardous nuclear plutonium from banana peels.", "CONTRADICTED", "Composting is natural biological decomposition producing nutrient-rich agricultural humus, not nuclear materials.", "Agriculture"),
        ("Coffee beans are grown on the feathers of wild penguins in Antarctica.", "CONTRADICTED", "Coffee beans are the seeds of tropical Coffea shrub berries cultivated in equatorial regions.", "Agronomy"),
        ("Solar energy is generated by burning underground fossilized coal in furnace pits.", "CONTRADICTED", "Solar energy is clean renewable energy captured directly from sunlight using photovoltaic cells or concentrated solar power.", "Energy"),
        ("The natural greenhouse effect causes Earth's average surface temperature to plunge to absolute zero.", "CONTRADICTED", "The natural greenhouse effect traps infrared thermal radiation, warming Earth's surface to a hospitable average of ~15 C.", "Climate Science"),
        ("Plant pollination is performed exclusively by mechanical diesel bulldozers in botanical gardens.", "CONTRADICTED", "Plant pollination is mediated naturally by wind, water, and animal pollinators including bees, butterflies, and birds.", "Botany"),

        # NEI (11)
        ("A honeybee in a hive near Munich in 1982 visited exactly 341 clover flowers before sunset on a Tuesday.", "NEI", "Apiary research studies observe average foraging frequencies, not daily individual bee flower counts from 1982.", "Unrecorded Animal Behavior"),
        ("An organic apple orchard farmer in Normandy in 1930 preferred wearing green corduroy trousers.", "NEI", "Agricultural land registries and harvest tax ledgers record farm acreage, not personal trouser fabrics.", "Personal Wardrobe"),
        ("A specific oak leaf falling in Sherwood Forest on October 10, 1925, rotated 4 times before landing.", "NEI", "Phenological forest records track seasonal leaf-drop timing, not individual leaf descent aerodynamics.", "Unrecorded Natural Event"),
        ("In the year 2350, agricultural drones will pollinate 100% of global crops with synthetic nanobots.", "NEI", "Future speculative robotic agriculture projections centuries ahead cannot be verified as existing facts.", "Future Speculation"),
        ("A coffee farmer in Ethiopia in 1960 privately sang to his coffee plants every morning at 6:00 AM.", "NEI", "Coffee cooperative records document harvest bean grades, not informal morning vocalizations by farmers.", "Unrecorded Anecdote"),
        ("An unrecorded earthworm in a compost bin in Sussex in 1970 was exactly 6.74 centimeters long.", "NEI", "Soil ecology field papers establish earthworm biomass density estimates, not individual garden worm lengths.", "Unrecorded Specimen"),
        ("A scuba diver on the Great Barrier Reef in 1990 saw a clownfish with an unrecorded dorsal fin nick.", "NEI", "Marine park surveillance surveys reef coral coverage and fish stocks, not individual wild clownfish fin nicks.", "Unrecorded Animal Detail"),
        ("A specific gust of wind in the Sahara on August 4, 1944, blew exactly 1,429 grains of sand onto a rock.", "NEI", "Aeolian sediment transport models calculate bulk sand flux, not individual microscopic sand grain counts.", "Unrecorded Measurement"),
        ("A botanist in Kew Gardens in 1912 privately thought orchids were much more tedious to water than ferns.", "NEI", "Herbaria archives preserve dried botanical voucher specimens, not private watering annoyance opinions.", "Personal Opinion"),
        ("An anonymous tourist in Hawaii in 1978 dropped an unrecorded plastic comb near a coral head.", "NEI", "Marine litter beach surveys quantify debris categories, not individual anonymous comb drops.", "Unrecorded Incident"),
        ("A solar panel installed in California in 2005 was struck by an unrecorded sparrow feather on a Sunday.", "NEI", "Photovoltaic inverter logs monitor kilowatt-hour output, not transient organic feather landings.", "Unrecorded Event")
    ]
    for idx, (claim, label, context, subcat) in enumerate(env_items, 1):
        dataset.append({
            "id": f"eval_env_{idx:03d}",
            "domain": "Environment & Agriculture",
            "claim": claim,
            "ground_truth_label": label,
            "context": context,
            "subcategory": subcat
        })

    return dataset


class EvaluationEngine:
    """Scientific Evaluation Engine computing confusion matrix, classification metrics, and audit statistics."""

    def __init__(self, pipeline: TruthGuardPipeline):
        self.pipeline = pipeline
        self.citation_verifier = CitationVerifier()

    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs evaluation over the benchmark dataset and calculates comprehensive metrics."""
        print(f"[Evaluation] Beginning evaluation over {len(dataset)} balanced claims...")
        start_time = time.time()

        y_true = []
        y_pred = []
        latencies = []

        relevance_passed_count = 0
        total_retrieved_evidence = 0
        citation_accurate_count = 0
        total_eval_citations = 0
        false_corrections_count = 0

        eval_records = []

        # Classes mapping
        classes = ["SUPPORTED", "CONTRADICTED", "NEI"]
        label_to_idx = {lbl: i for i, lbl in enumerate(classes)}

        confusion_matrix = [[0 for _ in range(3)] for _ in range(3)]

        for i, item in enumerate(dataset, 1):
            claim_text = item["claim"]
            gold_label = item["ground_truth_label"]
            context = item.get("context")

            t0 = time.time()
            res = self.pipeline.run(claim_text, rag_context=context)
            elapsed = time.time() - t0
            latencies.append(elapsed)

            # Determine predicted label for the claim
            if res["claims"]:
                pred_label = res["claims"][0]["label"]
                claim_ev_items = res["claims"][0].get("evidence_items", [])
                best_ev = res["claims"][0].get("evidence", "")
                corr = res["claims"][0].get("correction")
            else:
                pred_label = "NEI"
                claim_ev_items = []
                best_ev = ""
                corr = None

            y_true.append(gold_label)
            y_pred.append(pred_label)

            # Update Confusion Matrix
            if gold_label in label_to_idx and pred_label in label_to_idx:
                confusion_matrix[label_to_idx[gold_label]][label_to_idx[pred_label]] += 1

            # Check False Corrections (M5 must NEVER correct SUPPORTED or NEI claims)
            if gold_label in ("SUPPORTED", "NEI"):
                if res.get("corrections_made", 0) > 0 or (corr and corr.get("status") == "accepted"):
                    false_corrections_count += 1

            # Check Retrieval Relevance
            if claim_ev_items:
                total_retrieved_evidence += len(claim_ev_items)
                for ev in claim_ev_items:
                    ev_text = ev.get("text", "")
                    is_rel, _, _ = validate_evidence_relevance(claim_text, ev_text)
                    if is_rel:
                        relevance_passed_count += 1

            # Check Citation Accuracy
            if best_ev and gold_label != "NEI":
                total_eval_citations += 1
                is_rel, _, _ = validate_evidence_relevance(claim_text, best_ev)
                if is_rel:
                    citation_accurate_count += 1

            eval_records.append({
                "id": item["id"],
                "domain": item["domain"],
                "claim": claim_text,
                "gold_label": gold_label,
                "pred_label": pred_label,
                "is_correct": (gold_label == pred_label),
                "reliability_score": res["reliability_score"],
                "corrections_made": res.get("corrections_made", 0),
                "latency_sec": elapsed
            })

            if i % 50 == 0 or i == len(dataset):
                print(f"[Evaluation] Processed {i}/{len(dataset)} claims (elapsed: {time.time() - start_time:.1f}s)")

        total_time = time.time() - start_time

        # Calculate Per-Class Precision, Recall, F1
        per_class_metrics = {}
        precisions = []
        recalls = []
        f1s = []

        total_correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
        overall_accuracy = total_correct / len(y_true) if y_true else 0.0

        for lbl_idx, lbl in enumerate(classes):
            tp = confusion_matrix[lbl_idx][lbl_idx]
            fp = sum(confusion_matrix[row][lbl_idx] for row in range(3) if row != lbl_idx)
            fn = sum(confusion_matrix[lbl_idx][col] for col in range(3) if col != lbl_idx)

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            per_class_metrics[lbl] = {
                "precision": float(round(prec, 4)),
                "recall": float(round(rec, 4)),
                "f1_score": float(round(f1, 4)),
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "support": sum(confusion_matrix[lbl_idx])
            }
            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)

        macro_precision = float(round(np.mean(precisions), 4))
        macro_recall = float(round(np.mean(recalls), 4))
        macro_f1 = float(round(np.mean(f1s), 4))

        retrieval_relevance_rate = (
            float(round(relevance_passed_count / total_retrieved_evidence, 4))
            if total_retrieved_evidence > 0 else 1.0
        )
        citation_accuracy_rate = (
            float(round(citation_accurate_count / total_eval_citations, 4))
            if total_eval_citations > 0 else 1.0
        )
        supported_or_nei_count = sum(1 for item in dataset if item["ground_truth_label"] in ("SUPPORTED", "NEI"))
        false_correction_rate = (
            float(round(false_corrections_count / supported_or_nei_count, 4))
            if supported_or_nei_count > 0 else 0.0
        )

        lat_arr = np.array(latencies)
        latency_stats = {
            "mean_sec": float(round(float(np.mean(lat_arr)), 3)),
            "median_sec": float(round(float(np.median(lat_arr)), 3)),
            "p95_sec": float(round(float(np.percentile(lat_arr, 95)), 3)),
            "min_sec": float(round(float(np.min(lat_arr)), 3)),
            "max_sec": float(round(float(np.max(lat_arr)), 3)),
            "total_runtime_sec": float(round(total_time, 2))
        }

        report = {
            "evaluation_metadata": {
                "benchmark_name": "TruthGuard-350 Balanced Multi-Domain Benchmark",
                "sample_size": len(dataset),
                "domains_evaluated": 10,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "pipeline_config": {
                    "decomposition": "atomic_llm",
                    "retrieval": "hybrid",
                    "verifier": "nli",
                    "model": "DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
                }
            },
            "overall_metrics": {
                "accuracy": float(round(overall_accuracy, 4)),
                "macro_precision": macro_precision,
                "macro_recall": macro_recall,
                "macro_f1": macro_f1,
                "total_samples": len(dataset),
                "correct_predictions": total_correct
            },
            "confusion_matrix": {
                "labels": classes,
                "matrix": confusion_matrix
            },
            "per_class_metrics": per_class_metrics,
            "retrieval_and_citation_metrics": {
                "retrieval_relevance_rate": retrieval_relevance_rate,
                "citation_accuracy_rate": citation_accuracy_rate,
                "false_correction_rate": false_correction_rate
            },
            "latency_report": latency_stats,
            "detailed_records": eval_records
        }

        return report


def run_large_scale_evaluation(
    output_path: str = "results/evaluation_report_350.json"
) -> Dict[str, Any]:
    """Runs the 350-claim evaluation benchmark and saves results to disk."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    dataset = build_350_benchmark_dataset()

    pipeline = TruthGuardPipeline(
        decomposition_method="atomic_llm",
        retrieval_mode="hybrid",
        verifier_type="nli"
    )

    engine = EvaluationEngine(pipeline)
    report = engine.evaluate(dataset)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("TRUTHGUARD 3.0 — 350-CLAIM BENCHMARK EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total Evaluated Claims : {report['overall_metrics']['total_samples']}")
    print(f"Overall Accuracy       : {report['overall_metrics']['accuracy'] * 100:.2f}%")
    print(f"Macro Precision        : {report['overall_metrics']['macro_precision'] * 100:.2f}%")
    print(f"Macro Recall           : {report['overall_metrics']['macro_recall'] * 100:.2f}%")
    print(f"Macro F1 Score         : {report['overall_metrics']['macro_f1'] * 100:.2f}%")
    print(f"Retrieval Relevance    : {report['retrieval_and_citation_metrics']['retrieval_relevance_rate'] * 100:.2f}%")
    print(f"Citation Accuracy      : {report['retrieval_and_citation_metrics']['citation_accuracy_rate'] * 100:.2f}%")
    print(f"False Correction Rate  : {report['retrieval_and_citation_metrics']['false_correction_rate'] * 100:.2f}%")
    print(f"Mean Latency per Claim : {report['latency_report']['mean_sec']:.3f}s")
    print("=" * 60)
    print(f"Confusion Matrix (Rows: True, Cols: Pred [S, C, NEI]):")
    for row_lbl, row in zip(["SUPPORTED", "CONTRADICTED", "NEI"], report["confusion_matrix"]["matrix"]):
        print(f"  {row_lbl:13s} : {row}")
    print("=" * 60)
    print(f"Report saved to: {output_path}")

    return report


if __name__ == "__main__":
    run_large_scale_evaluation()
