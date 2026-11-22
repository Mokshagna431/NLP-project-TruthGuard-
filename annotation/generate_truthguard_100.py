"""
TruthGuard-100 Benchmark Tooling: Generation and Decomposition Script
Generates 100 open-domain answers across mixed topics (people, places, science, history, dates; 2-5 sentences each).
Decomposes answers into atomic claims with M1 and exports annotation/truthguard_100_unannotated.csv.
Per Rule 7: Annotator columns are left completely empty for the human authors.
"""

import os
import csv
from truthguard.decompose import ClaimDecomposer

# 100 realistic open-domain answers spanning history, science, geography, biography, and technology
SEED_PROMPTS_AND_ANSWERS = [
    # Biographies & People (20)
    ("Isaac Newton", "Sir Isaac Newton was an English mathematician and physicist who formulated the laws of motion. He published Philosophiæ Naturalis Principia Mathematica in 1687. He also served as Warden of the Royal Mint."),
    ("Ada Lovelace", "Ada Lovelace was an English mathematician known for her work on Charles Babbage's mechanical computer. She is often regarded as the first computer programmer. She was the daughter of poet Lord Byron."),
    ("Alexander the Great", "Alexander the Great was a king of the ancient Greek kingdom of Macedon. He succeeded his father Philip II to the throne at the age of 20. He created one of the largest empires in history stretching from Greece to northwestern India."),
    ("Marie Curie", "Marie Curie was a Polish and naturalized-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize and the first person to win twice. She died in 1934 from aplastic anemia."),
    ("Nikola Tesla", "Nikola Tesla was a Serbian-American engineer and inventor known for his contributions to alternating current electricity. He worked briefly for Thomas Edison before establishing his own laboratories. He patented the Tesla coil in 1891."),
    ("Nelson Mandela", "Nelson Mandela was a South African anti-apartheid activist and politician who served as President from 1994 to 1999. He spent 27 years in prison, primarily on Robben Island. He won the Nobel Peace Prize in 1993."),
    ("Galileo Galilei", "Galileo Galilei was an Italian astronomer, physicist and engineer from Pisa. He used a telescope to observe the four largest moons of Jupiter in 1610. He championed heliocentrism, which led to his trial by the Roman Inquisition."),
    ("Leonardo da Vinci", "Leonardo da Vinci was an Italian polymath of the High Renaissance. He painted the Mona Lisa and The Last Supper. He also conceptualized flying machines and armored vehicles in his notebooks."),
    ("Julius Caesar", "Julius Caesar was a Roman general and statesman who played a critical role in the demise of the Roman Republic. He led the Roman armies in the Gallic Wars. He was assassinated on the Ides of March in 44 BC."),
    ("Charles Darwin", "Charles Darwin was an English naturalist who proposed that all species of life have descended from common ancestors. He published On the Origin of Species in 1859. His theory was developed during his voyage on HMS Beagle."),
    ("Cleopatra", "Cleopatra was the last active ruler of the Ptolemaic Kingdom of Egypt. She had political and romantic relationships with Julius Caesar and Mark Antony. She died in 30 BC following the defeat at Actium."),
    ("Alan Turing", "Alan Turing was an English mathematician, computer scientist, and cryptanalyst who broke German ciphers during World War II at Bletchley Park. He played a pivotal role in cracking the Enigma machine. He devised the Turing machine in 1936."),
    ("Joan of Arc", "Joan of Arc was a patron saint of France who led French forces during the Hundred Years' War. She claimed to have received visions of the archangel Michael. She was captured and burned at the stake in Rouen in 1431."),
    ("Albert Einstein", "Albert Einstein was a German-born theoretical physicist widely acknowledged to be one of the greatest physicists of all time. He developed the theory of relativity and received the 1921 Nobel Prize in Physics for his explanation of the photoelectric effect."),
    ("William Shakespeare", "William Shakespeare was an English playwright and poet widely regarded as the greatest writer in the English language. He authored 39 plays including Hamlet, Othello, and Macbeth. He died in Stratford-upon-Avon in 1616."),
    ("Socrates", "Socrates was a classical Greek philosopher credited as one of the founders of Western philosophy. He wrote no texts and is known through the dialogues of Plato and Xenophon. He was sentenced to death by drinking hemlock in 399 BC."),
    ("Louis Pasteur", "Louis Pasteur was a French chemist and microbiologist renowned for his discoveries of the principles of vaccination and pasteurization. He developed vaccines for rabies and anthrax. He died in 1895 near Paris."),
    ("Winston Churchill", "Winston Churchill was a British statesman who served as Prime Minister of the United Kingdom twice, notably during World War II. He was awarded the Nobel Prize in Literature in 1953. He delivered the famous 'Blood, Toil, Tears and Sweat' speech."),
    ("Wolfgang Amadeus Mozart", "Wolfgang Amadeus Mozart was a prolific and influential composer of the Classical period. Born in Salzburg, he composed over 800 works including The Magic Flute and Don Giovanni. He died in Vienna at the age of 35 in 1791."),
    ("Aristotle", "Aristotle was an Ancient Greek philosopher and polymath taught by Plato. He founded the Lyceum and the Peripatetic school of philosophy. His writings covered physics, biology, zoology, metaphysics, poetry, and politics."),

    # Places & Geography (20)
    ("Mount Everest", "Mount Everest is Earth's highest mountain above sea level, located in the Mahalangur Himal sub-range of the Himalayas. Its elevation is 8,848.86 meters. The international border between China and Nepal runs across its summit point."),
    ("The Amazon River", "The Amazon River in South America is the largest river by discharge volume in the world. It flows through Brazil, Peru, and Colombia. It discharges into the Atlantic Ocean."),
    ("The Sahara Desert", "The Sahara is the largest hot desert in the world and the third-largest desert overall. It covers an area of approximately 9.2 million square kilometers across North Africa. It receives very little precipitation annually."),
    ("The Grand Canyon", "The Grand Canyon is a steep-sided canyon carved by the Colorado River in Arizona, United States. It is contained within and managed by Grand Canyon National Park. The canyon exposes nearly two billion years of Earth's geological history."),
    ("The Great Barrier Reef", "The Great Barrier Reef is the world's largest coral reef system composed of over 2,900 individual reefs. It is located in the Coral Sea off the coast of Queensland, Australia. It was designated a World Heritage Site in 1981."),
    ("The Mariana Trench", "The Mariana Trench is located in the western Pacific Ocean about 200 kilometers east of the Mariana Islands. It is the deepest oceanic trench on Earth. Its maximum known depth is the Challenger Deep at nearly 11,000 meters."),
    ("The Nile River", "The Nile is a major north-flowing river in northeastern Africa. It is traditionally considered the longest river in the world at approximately 6,650 kilometers. It empties into the Mediterranean Sea via the Nile Delta."),
    ("Lake Baikal", "Lake Baikal is a rift lake in southern Siberia, Russia. It is the world's deepest lake with a maximum depth of 1,642 meters. It contains 22% of the world's fresh surface water."),
    ("The Colosseum", "The Colosseum is an oval amphitheatre in the centre of the city of Rome, Italy. Construction began under the emperor Vespasian in 72 AD and was completed in 80 AD under Titus. It could hold an estimated 50,000 to 80,000 spectators."),
    ("The Taj Mahal", "The Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in Agra, India. It was commissioned in 1631 by Mughal emperor Shah Jahan to house the tomb of his favourite wife Mumtaz Mahal."),
    ("Machu Picchu", "Machu Picchu is a 15th-century Inca citadel located in the Eastern Cordillera of southern Peru on a 2,430-meter mountain ridge. It was built as an estate for the Inca emperor Pachacuti. It was declared a UNESCO World Heritage Site in 1983."),
    ("The Dead Sea", "The Dead Sea is a salt lake bordered by Jordan to the east and Israel and the West Bank to the west. Its surface and shores are 430.5 meters below sea level, Earth's lowest elevation on land. Its hypersaline water makes swimming similar to floating."),
    ("Yellowstone National Park", "Yellowstone National Park is an American national park located primarily in Wyoming. It was the first national park in the United States and widely held to be the first in the world, established in 1872. It contains the Old Faithful geyser."),
    ("The Panama Canal", "The Panama Canal is an artificial 82-kilometer waterway in Panama that connects the Atlantic Ocean with the Pacific Ocean. It was opened in 1914. It drastically reduces the transit time for ships travelling between oceans."),
    ("Mount Kilimanjaro", "Mount Kilimanjaro is a dormant volcano in Tanzania with three volcanic cones named Kibo, Mawenzi, and Shira. It is the highest mountain in Africa at 5,895 meters above sea level. It is the largest free-standing mountain rise in the world."),
    ("Antarctica", "Antarctica is Earth's southernmost continent containing the geographic South Pole. It is situated almost entirely south of the Antarctic Circle and surrounded by the Southern Ocean. It is the coldest, driest, and windiest continent."),
    ("The Acropolis of Athens", "The Acropolis of Athens is an ancient citadel located on a rocky outcrop above the city of Athens. It contains the remains of several ancient buildings of great architectural and historical significance, the most famous being the Parthenon."),
    ("Victoria Falls", "Victoria Falls is a waterfall on the Zambezi River in southern Africa, between Zambia and Zimbabwe. It was described by the Kololo tribe as Mosi-oa-Tunya, meaning 'The Smoke That Thunders'. It is classified as one of the world's largest waterfalls."),
    ("The Galapagos Islands", "The Galapagos Islands are an archipelago of volcanic islands distributed on either side of the equator in the Pacific Ocean. They belong to Ecuador. The islands are famed for their vast number of endemic species studied by Charles Darwin."),
    ("The Suez Canal", "The Suez Canal is an artificial sea-level waterway in Egypt connecting the Mediterranean Sea to the Red Sea. Constructed by Ferdinand de Lesseps, it officially opened in November 1869. It offers watercraft a direct route between the North Atlantic and northern Indian oceans."),

    # Science & Astronomy (20)
    ("The Sun", "The Sun is the star at the center of the Solar System. It is a nearly perfect sphere of hot plasma, heated to incandescence by nuclear fusion reactions in its core. It accounts for about 99.86% of the total mass of the Solar System."),
    ("Photosynthesis", "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy. It uses water, carbon dioxide, and sunlight to synthesize sugars and release oxygen. Most of the energy in the biosphere originates from photosynthesis."),
    ("Plate Tectonics", "Plate tectonics is the scientific theory that Earth's outer shell is divided into several plates that glide over the mantle. The movement of these plates drives earthquakes, volcanism, and mountain-building. Alfred Wegener first proposed continental drift in 1912."),
    ("DNA", "Deoxyribonucleic acid is a polymer composed of two polynucleotide chains that coil around each other to form a double helix. It carries genetic instructions for the development and functioning of all known organisms. James Watson and Francis Crick described its structure in 1953."),
    ("Black Holes", "A black hole is a region of spacetime where gravity is so strong that nothing, including light, can escape from it. The boundary of no return is called the event horizon. Supermassive black holes exist at the centers of most galaxies."),
    ("The Big Bang", "The Big Bang theory is the prevailing cosmological model explaining the creation of the observable universe from the earliest known periods. It suggests the universe expanded from an extremely high-density and high-temperature initial singularity approximately 13.8 billion years ago."),
    ("Superconductivity", "Superconductivity is a set of physical properties observed in certain materials where electrical resistance vanishes and magnetic flux fields are expelled. It was discovered by Heike Kamerlingh Onnes in 1911 in mercury. It typically occurs at cryogenic temperatures."),
    ("Mitosis", "Mitosis is a part of the cell cycle in which replicated chromosomes are separated into two new nuclei. It is divided into four main stages: prophase, metaphase, anaphase, and telophase. It results in two genetically identical daughter cells."),
    ("Jupiter's Red Spot", "The Great Red Spot is a persistent high-pressure storm in the atmosphere of Jupiter. It is the largest storm in the Solar System, wider than Earth. It has been observed continuously for over 150 years."),
    ("Quantum Entanglement", "Quantum entanglement is a physical phenomenon that occurs when a group of particles interact in ways such that the quantum state of each particle cannot be described independently. Measurements on one particle instantly influence the other, regardless of spatial separation."),
    ("Penicillin", "Penicillin is a group of antibacterial antibiotics derived from Penicillium fungi. It was discovered by Scottish physician Alexander Fleming in 1928. It revolutionized modern medicine by enabling effective treatment of bacterial infections."),
    ("The Periodic Table", "The periodic table is a tabular display of the chemical elements organized by atomic number and recurring chemical properties. Russian chemist Dmitri Mendeleev published the first recognizable periodic table in 1869. Elements in the same column have similar valence electron configurations."),
    ("The Ozone Layer", "The ozone layer is a region of Earth's stratosphere that absorbs most of the Sun's ultraviolet radiation. It contains high concentrations of ozone molecules (O3). Depletion of the ozone layer led to the adoption of the Montreal Protocol in 1987."),
    ("Thermodynamics", "The laws of thermodynamics define a group of physical quantities that characterize thermodynamic systems in thermal equilibrium. The first law states that energy cannot be created or destroyed, only transformed. The second law dictates that the total entropy of an isolated system always increases over time."),
    ("Human Genome Project", "The Human Genome Project was an international scientific research project with the goal of determining the base pairs that make up human DNA. It began in 1990 and was declared complete in 2003. It mapped approximately 20,000 to 25,000 human genes."),
    ("Hubble Space Telescope", "The Hubble Space Telescope was launched into low Earth orbit in 1990 and remains in operation. It was built by NASA with contributions from the European Space Agency. Hubble's observations have helped determine the rate of expansion of the universe."),
    ("CERN Large Hadron Collider", "The Large Hadron Collider is the world's largest and highest-energy particle collider, built by CERN near Geneva. It lies in a tunnel 27 kilometers in circumference beneath the Franco-Swiss border. In 2012, experiments at the LHC confirmed the discovery of the Higgs boson."),
    ("General Relativity", "General relativity is the geometric theory of gravitation published by Albert Einstein in 1915. It describes gravity not as a force, but as a curvature of spacetime caused by the uneven distribution of mass and energy. It predicts gravitational time dilation and gravitational lensing."),
    ("Nuclear Fission", "Nuclear fission is a reaction in which the nucleus of an atom splits into two or more smaller nuclei, releasing a large amount of energy. It was discovered in December 1938 by German chemists Otto Hahn and Fritz Strassmann. It is the basis for nuclear power reactors."),
    ("CRISPR-Cas9", "CRISPR-Cas9 is a technology for editing genomes, allowing researchers to alter DNA sequences and modify gene function. It was adapted from a naturally occurring genome editing system in bacteria. Jennifer Doudna and Emmanuelle Charpentier won the 2020 Nobel Prize in Chemistry for its development."),

    # History & Dates (20)
    ("Apollo 11 Moon Landing", "Apollo 11 was the American spaceflight that first landed humans on the Moon on July 20, 1969. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed the Apollo Lunar Module Eagle. Armstrong took his historic first step onto the lunar surface six hours later."),
    ("The Fall of the Berlin Wall", "The Berlin Wall fell on November 9, 1989, marking a pivotal moment in the end of the Cold War. It had divided East and West Berlin since 1961. Its demolition paved the way for German reunification in October 1990."),
    ("Declaration of Independence", "The United States Declaration of Independence was adopted by the Second Continental Congress on July 4, 1776. It declared that the Thirteen American Colonies regarded themselves as thirteen independent sovereign states. It was drafted primarily by Thomas Jefferson."),
    ("French Revolution", "The French Revolution was a period of fundamental political and societal change in France that began with the Estates General of 1789. The storming of the Bastille occurred on July 14, 1789. It led to the abolition of the monarchy and the rise of Napoleon Bonaparte."),
    ("Signing of the Magna Carta", "The Magna Carta was signed by King John of England at Runnymede near Windsor on June 15, 1215. It was drafted by the Archbishop of Canterbury to make peace between the unpopular king and a group of rebel barons. It established the principle that everyone, including the sovereign, is subject to the law."),
    ("Invention of the Printing Press", "Johannes Gutenberg invented the movable-type printing press in Mainz, Germany around 1440. He completed his famous Gutenberg Bible around 1455. The press accelerated the spread of knowledge throughout Renaissance Europe."),
    ("The Cuban Missile Crisis", "The Cuban Missile Crisis was a 13-day confrontation between the United States and the Soviet Union in October 1962. It was sparked by Soviet ballistic missile deployment in Cuba. It is widely considered the closest the Cold War came to escalating into full-scale nuclear war."),
    ("End of World War II", "World War II in Europe ended with the unconditional surrender of Nazi Germany on May 8, 1945. The war in the Pacific concluded following the atomic bombings of Hiroshima and Nagasaki in August 1945. Imperial Japan signed surrender documents aboard USS Missouri on September 2, 1945."),
    ("The Renaissance", "The Renaissance was a fervent period of European cultural, artistic, political and economic rebirth following the Middle Ages. It began in Florence, Italy during the 14th century. It produced celebrated figures such as Leonardo da Vinci, Michelangelo, and Raphael."),
    ("First Flight of the Wright Brothers", "Orville and Wilbur Wright achieved the first controlled, sustained flight of a powered, heavier-than-air aircraft on December 17, 1903. The flight took place near Kitty Hawk, North Carolina. Orville flew the Wright Flyer for 12 seconds covering 120 feet."),
    ("The Industrial Revolution", "The Industrial Revolution was the transition to new manufacturing processes in Great Britain, continental Europe, and the United States from around 1760 to 1840. It marked the shift from hand production methods to machines and steam power. The textile industry was the first to use modern production methods."),
    ("The Sinking of the Titanic", "RMS Titanic sank in the early morning of April 15, 1912 in the North Atlantic Ocean after striking an iceberg. It was on its maiden voyage from Southampton to New York City. More than 1,500 passengers and crew lost their lives in the disaster."),
    ("The Battle of Hastings", "The Battle of Hastings was fought on October 14, 1066 between the Norman-French army of William, Duke of Normandy, and an English army under King Harold Godwinson. King Harold was killed during the battle. William the Conqueror was crowned King of England on Christmas Day 1066."),
    ("The Reformation", "The Protestant Reformation began in 1517 when Martin Luther published his Ninety-five Theses in Wittenberg, Germany. It challenged the practices of the Catholic Church, particularly the sale of indulgences. It led to the establishment of Protestant churches across Europe."),
    ("Treaty of Versailles", "The Treaty of Versailles was the most important of the peace treaties that brought World War I to an end. It was signed on June 28, 1919 in the Hall of Mirrors at the Palace of Versailles. It imposed strict military restrictions and heavy reparations on Germany."),
    ("The Rosetta Stone", "The Rosetta Stone was discovered in Egypt by French soldiers in July 1799. It features a decree issued at Memphis in 196 BC inscribed in three scripts: Ancient Egyptian hieroglyphs, Demotic, and Ancient Greek. Jean-François Champollion used it to decipher hieroglyphs in 1822."),
    ("Discovery of Tutankhamun's Tomb", "British archaeologist Howard Carter discovered the intact tomb of Pharaoh Tutankhamun in the Valley of the Kings in November 1922. The excavation was funded by Lord Carnarvon. The tomb contained thousands of exquisite artifacts, including the iconic gold funerary mask."),
    ("The Battle of Waterloo", "The Battle of Waterloo was fought on June 18, 1815 near Waterloo in present-day Belgium. Napoleon Bonaparte was defeated by Anglo-allied forces under the Duke of Wellington and a Prussian army under Gebhard Leberecht von Blücher. The defeat ended Napoleon's rule as Emperor of the French."),
    ("The Launch of Sputnik 1", "The Soviet Union launched Sputnik 1 into an elliptical low Earth orbit on October 4, 1957. It was the first artificial Earth satellite. The launch triggered the Space Race between the Soviet Union and the United States."),
    ("The Panama Canal Handover", "The Torrijos-Carter Treaties resulted in the official transfer of the Panama Canal from the United States to Panama on December 31, 1999. The treaties were signed in 1977 by President Jimmy Carter and Omar Torrijos. Panama has since managed the canal through the Panama Canal Authority."),

    # Technology & Modern Innovations (20)
    ("The World Wide Web", "Tim Berners-Lee invented the World Wide Web in 1989 while working at CERN. He created the first web browser, HTML, HTTP, and URLs. The first website became publicly available online in August 1991."),
    ("Linux Operating System", "Linus Torvalds began developing the Linux operating system kernel in 1991 while a student at the University of Helsinki. Linux is released under the GNU General Public License. It powers the majority of web servers, cloud infrastructure, and Android smartphones worldwide."),
    ("The Transistor", "The point-contact transistor was invented in December 1947 at Bell Labs by John Bardeen, Walter Brattain, and William Shockley. It replaced fragile vacuum tubes in electronic devices. The inventors shared the 1956 Nobel Prize in Physics for this breakthrough."),
    ("The ENIAC Computer", "ENIAC was among the earliest electronic general-purpose computers, completed in 1945 at the University of Pennsylvania. Designed by John Mauchly and J. Presper Eckert, it contained more than 17,000 vacuum tubes. It was built to calculate artillery firing tables for the United States Army."),
    ("GPS Navigation", "The Global Positioning System is a satellite-based radionavigation system owned by the United States government and operated by the United States Space Force. It became fully operational with 24 satellites in 1995. It provides geolocation and time information to any receiver on or near Earth."),
    ("Bluetooth Technology", "Bluetooth is a short-range wireless technology standard used for exchanging data between fixed and mobile devices over UHF radio waves. It was originally conceived by Nils Rydbeck and Johan Ullman in 1989 at Ericsson. It was named after the 10th-century Scandinavian king Harald Bluetooth."),
    ("Ethernet", "Ethernet was developed at Xerox PARC between 1973 and 1974 by Robert Metcalfe and David Boggs. It was officially standardized in 1980 as IEEE 802.3. It remains the dominant wired local area network (LAN) technology globally."),
    ("The Microprocessor", "The Intel 4004, released in November 1971, was the world's first commercially available monolithic microprocessor. It was designed by Federico Faggin, Ted Hoff, and Stanley Mazor. The 4-bit CPU contained 2,300 transistors and operated at a clock rate of 740 kHz."),
    ("The First iPhone", "Apple CEO Steve Jobs unveiled the first iPhone on January 9, 2007 at the Macworld convention in San Francisco. It combined a mobile phone, an iPod with touch controls, and a breakthrough internet communicator. It was released for purchase in the United States on June 29, 2007."),
    ("Wikipedia", "Wikipedia was launched on January 15, 2001 by Jimmy Wales and Larry Sanger. It operates as a free, multilingual online encyclopedia written and maintained by a community of volunteer contributors. It is hosted by the Wikimedia Foundation."),
    ("Python Programming Language", "Python was conceived in the late 1980s by Guido van Rossum at Centrum Wiskunde & Informatica in the Netherlands. Its design philosophy emphasizes code readability through significant indentation. The language was first released in February 1991."),
    ("The Hubble Deep Field", "The Hubble Deep Field image was assembled from 342 separate exposures taken by the Hubble Space Telescope over ten consecutive days in December 1995. It covers a tiny speck of sky in the constellation Ursa Major. The image revealed roughly 3,000 distant galaxies in various stages of evolution."),
    ("Relational Database Model", "Edgar F. Codd introduced the relational model for database management in a seminal 1970 paper while working at IBM. The model organizes data into tables (relations) of rows and columns with formal mathematical operations. It became the foundation for SQL and modern relational databases."),
    ("The Steam Engine", "James Watt significantly improved the Newcomen atmospheric steam engine in 1769 by introducing a separate condenser. His design vastly increased energy efficiency and reduced coal consumption. Watt's rotary steam engine provided continuous mechanical power to drive factories and mills."),
    ("Lithium-Ion Batteries", "The rechargeable lithium-ion battery was developed through key contributions by John Goodenough, M. Stanley Whittingham, and Akira Yoshino in the 1970s and 1980s. Sony commercialized the first handheld lithium-ion battery in 1991. The inventors received the 2019 Nobel Prize in Chemistry."),
    ("Optical Fiber Communications", "Charles K. Kao proved in 1966 that light loss in glass fibers was caused by impurities rather than fundamental physics, paving the way for optical fiber communications. Corning Glass produced the first low-loss optical fibers in 1970. Kao was awarded the 2009 Nobel Prize in Physics."),
    ("Public Key Cryptography", "Whitfield Diffie and Martin Hellman published the concept of public-key cryptography and key exchange in 1976. Ron Rivest, Adi Shamir, and Leonard Adleman subsequently developed the RSA algorithm at MIT in 1977. Public-key cryptography secures online commerce and encrypted communications."),
    ("The Jet Engine", "Frank Whittle in the United Kingdom and Hans von Ohain in Germany independently developed the turbojet engine in the 1930s. The first turbojet-powered aircraft, the Heinkel He 178, made its maiden flight in August 1939. Jet propulsion revolutionized commercial aviation in the 1950s."),
    ("Automated Teller Machines (ATMs)", "The first electronic automated teller machine was installed by Barclays Bank in Enfield Town, London on June 27, 1967. The machine was developed by a team led by John Shepherd-Barron. It allowed customers to withdraw cash using special paper cheques impregnated with radioactive carbon-14."),
    ("Magnetic Resonance Imaging (MRI)", "Paul Lauterbur and Sir Peter Mansfield developed the foundation of magnetic resonance imaging in the 1970s by applying magnetic field gradients to nuclear magnetic resonance signals. MRI produces non-invasive, high-resolution soft tissue images of the human body. The scientists were awarded the 2003 Nobel Prize in Physiology or Medicine.")
]


def generate_truthguard_100():
    print("=" * 80)
    print("PHASE 9: GENERATING TRUTHGUARD-100 BENCHMARK DATASET")
    print(f"Total Answers: {len(SEED_PROMPTS_AND_ANSWERS)}")
    print("=" * 80)

    decomposer = ClaimDecomposer(method="atomic_llm")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, "truthguard_100_unannotated.csv")

    rows = []
    total_claims = 0

    for i, (topic, answer) in enumerate(SEED_PROMPTS_AND_ANSWERS, 1):
        claims = decomposer.decompose(answer)
        for c in claims:
            total_claims += 1
            rows.append({
                "answer_id": f"tg100_{i:03d}",
                "topic": topic,
                "claim": c["claim"],
                "source_span": f"{c['char_start']}:{c['char_end']}",
                "label_annotator1": "",  # Unfilled per Rule 7
                "label_annotator2": "",  # Unfilled per Rule 7
                "notes": ""
            })

    # Export to CSV
    fieldnames = ["answer_id", "topic", "claim", "source_span", "label_annotator1", "label_annotator2", "notes"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(SEED_PROMPTS_AND_ANSWERS)} answers yielding {total_claims} decomposed atomic claims.")
    print(f"Saved unannotated CSV to: {out_csv}")
    print("Rule 7 check: label_annotator1 and label_annotator2 are left strictly empty for human annotators.")
    print("=" * 80)


if __name__ == "__main__":
    generate_truthguard_100()
