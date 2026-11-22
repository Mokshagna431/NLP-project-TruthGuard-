/**
 * Comprehensive Presets & Analytics Data for TruthGuard & Crosscheck Proof Desk
 */

export const PRESET_DOCUMENTS = [
  {
    id: 'renaissance',
    title: 'The Renaissance',
    wordCount: 324,
    credibilityScore: 63,
    claimsSummary: {
      accurate: 5,
      inaccurate: 3,
      subjective: 0,
      total: 8
    },
    sections: [
      {
        heading: null,
        paragraphs: [
          {
            spans: [
              {
                text: 'The Renaissance, a period of cultural and artistic flourishing, spanned from the 17th to 20th centuries, centered in Asia.',
                status: 'inaccurate',
                claimId: 'claim-1'
              },
              {
                text: ' ',
                status: 'normal'
              },
              {
                text: 'This era witnessed a revival of classical Greek and Roman knowledge, leading to significant advancements in various fields.',
                status: 'accurate',
                claimId: 'claim-2'
              }
            ]
          }
        ]
      },
      {
        heading: 'Artistic Revolution',
        paragraphs: [
          {
            spans: [
              {
                text: 'One of the most notable developments of the Renaissance was the emergence of groundbreaking artistic styles. The renowned Leonardo da Vinci, often considered the quintessential Renaissance man, created iconic masterpieces such as the Mona Lisa. ',
                status: 'normal'
              },
              {
                text: 'Da Vinci created the Statue of David.',
                status: 'inaccurate',
                claimId: 'claim-3'
              },
              {
                text: ' Other influential artists included ',
                status: 'normal'
              },
              {
                text: 'Pablo Picasso',
                status: 'inaccurate',
                claimId: 'claim-4'
              },
              {
                text: ', Michelangelo, whose Sistine Chapel ceiling remains a marvel of Renaissance art, and Raphael, known for his harmonious and idealized depictions of human figures.',
                status: 'normal'
              }
            ]
          }
        ]
      },
      {
        heading: 'Scientific Discoveries',
        paragraphs: [
          {
            spans: [
              {
                text: 'The Renaissance also marked a period of scientific inquiry and innovation. ',
                status: 'normal'
              },
              {
                text: 'Galileo Galilei, a pioneering astronomer, used his telescope to make groundbreaking observations of the solar system, challenging the prevailing geocentric view of the universe.',
                status: 'accurate',
                claimId: 'claim-5'
              },
              {
                text: ' ',
                status: 'normal'
              },
              {
                text: 'Johannes Kepler, another prominent scientist, discovered the elliptical orbits of planets, revolutionizing our understanding of celestial mechanics.',
                status: 'accurate',
                claimId: 'claim-6'
              }
            ]
          }
        ]
      },
      {
        heading: 'Humanistic Ideals',
        paragraphs: [
          {
            spans: [
              {
                text: 'Humanism, a philosophical movement that emphasized the potential and value of human beings, was central to the Renaissance. Humanists focused on studying classical literature, history, and philosophy, seeking to understand and improve human nature. ',
                status: 'normal'
              },
              {
                text: 'The renowned scholar Petrarch is often considered the father of humanism,',
                status: 'accurate',
                claimId: 'claim-7'
              },
              {
                text: ' while the influential thinker ',
                status: 'normal'
              },
              {
                text: 'Erasmus promoted humanist ideals through his writings and translations.',
                status: 'accurate',
                claimId: 'claim-8'
              }
            ]
          }
        ]
      }
    ],
    plainText: `The Renaissance

The Renaissance, a period of cultural and artistic flourishing, spanned from the 17th to 20th centuries, centered in Asia. This era witnessed a revival of classical Greek and Roman knowledge, leading to significant advancements in various fields.

Artistic Revolution
One of the most notable developments of the Renaissance was the emergence of groundbreaking artistic styles. The renowned Leonardo da Vinci, often considered the quintessential Renaissance man, created iconic masterpieces such as the Mona Lisa. Da Vinci created the Statue of David. Other influential artists included Pablo Picasso, Michelangelo, whose Sistine Chapel ceiling remains a marvel of Renaissance art, and Raphael, known for his harmonious and idealized depictions of human figures.

Scientific Discoveries
The Renaissance also marked a period of scientific inquiry and innovation. Galileo Galilei, a pioneering astronomer, used his telescope to make groundbreaking observations of the solar system, challenging the prevailing geocentric view of the universe. Johannes Kepler, another prominent scientist, discovered the elliptical orbits of planets, revolutionizing our understanding of celestial mechanics.

Humanistic Ideals
Humanism, a philosophical movement that emphasized the potential and value of human beings, was central to the Renaissance. Humanists focused on studying classical literature, history, and philosophy, seeking to understand and improve human nature. The renowned scholar Petrarch is often considered the father of humanism, while the influential thinker Erasmus promoted humanist ideals through his writings and translations.`,
    correctedText: `The Renaissance

The Renaissance, a period of cultural and artistic flourishing, spanned from the 14th to 17th centuries, centered in Europe. This era witnessed a revival of classical Greek and Roman knowledge, leading to significant advancements in various fields.

Artistic Revolution
One of the most notable developments of the Renaissance was the emergence of groundbreaking artistic styles. The renowned Leonardo da Vinci, often considered the quintessential Renaissance man, created iconic masterpieces such as the Mona Lisa. Michelangelo created the Statue of David. Other influential artists included Sandro Botticelli, Michelangelo, whose Sistine Chapel ceiling remains a marvel of Renaissance art, and Raphael, known for his harmonious and idealized depictions of human figures.

Scientific Discoveries
The Renaissance also marked a period of scientific inquiry and innovation. Galileo Galilei, a pioneering astronomer, used his telescope to make groundbreaking observations of the solar system, challenging the prevailing geocentric view of the universe. Johannes Kepler, another prominent scientist, discovered the elliptical orbits of planets, revolutionizing our understanding of celestial mechanics.

Humanistic Ideals
Humanism, a philosophical movement that emphasized the potential and value of human beings, was central to the Renaissance. Humanists focused on studying classical literature, history, and philosophy, seeking to understand and improve human nature. The renowned scholar Petrarch is often considered the father of humanism, while the influential thinker Erasmus promoted humanist ideals through his writings and translations.`,
    claims: [
      {
        id: 'claim-1',
        status: 'Inaccurate',
        claim: 'The Renaissance spanned from the 17th to 20th centuries, centered in Asia.',
        justification: 'The Renaissance actually occurred from the 14th to the 17th centuries, primarily in Europe, not Asia. This period is well-documented in historical records and academic sources such as Wikipedia.',
        source: 'https://en.wikipedia.org/wiki/Renaissance',
        sourceTitle: 'Wikipedia: Renaissance',
        probabilities: { p_e: 0.02, p_c: 0.96, p_n: 0.02 },
        suggestedRevision: 'The Renaissance spanned from the 14th to the 17th centuries, centered in Europe.'
      },
      {
        id: 'claim-2',
        status: 'Accurate',
        claim: 'The Renaissance witnessed a revival of classical Greek and Roman knowledge, leading to significant advancements in various fields.',
        justification: 'The Renaissance is characterized by a renewed interest in classical Greek and Roman knowledge, which had a profound impact on art, science, literature, and philosophy. This is supported by numerous historical accounts and scholarly works.',
        source: 'https://en.wikipedia.org/wiki/Renaissance',
        sourceTitle: 'Wikipedia: Renaissance',
        probabilities: { p_e: 0.94, p_c: 0.02, p_n: 0.04 }
      },
      {
        id: 'claim-3',
        status: 'Inaccurate',
        claim: 'Leonardo da Vinci created the Statue of David.',
        justification: 'Leonardo da Vinci did not create the Statue of David. The Statue of David was actually sculpted by Michelangelo Buonarroti. This information is widely available in art history resources and biographies of both artists.',
        source: 'https://en.wikipedia.org/wiki/David_(Michelangelo)',
        sourceTitle: 'Wikipedia: David (Michelangelo)',
        probabilities: { p_e: 0.01, p_c: 0.98, p_n: 0.01 },
        suggestedRevision: 'Michelangelo Buonarroti sculpted the Statue of David.'
      },
      {
        id: 'claim-4',
        status: 'Inaccurate',
        claim: 'Pablo Picasso was an influential artist of the Renaissance.',
        justification: 'Pablo Picasso was a 20th-century Spanish painter and sculptor co-founding the Cubist movement, born in 1881, long after the Renaissance concluded in the 17th century.',
        source: 'https://en.wikipedia.org/wiki/Pablo_Picasso',
        sourceTitle: 'Wikipedia: Pablo Picasso',
        probabilities: { p_e: 0.03, p_c: 0.95, p_n: 0.02 },
        suggestedRevision: 'Influential Renaissance artists included Sandro Botticelli and Michelangelo.'
      },
      {
        id: 'claim-5',
        status: 'Accurate',
        claim: 'Galileo Galilei used his telescope to make observations challenging the geocentric view of the universe.',
        justification: 'Galileo Galilei made landmark telescopic discoveries (moons of Jupiter, phases of Venus) published in Sidereus Nuncius (1610), providing physical evidence against Ptolemaic geocentrism.',
        source: 'https://en.wikipedia.org/wiki/Galileo_Galilei',
        sourceTitle: 'Wikipedia: Galileo Galilei',
        probabilities: { p_e: 0.97, p_c: 0.01, p_n: 0.02 }
      },
      {
        id: 'claim-6',
        status: 'Accurate',
        claim: 'Johannes Kepler discovered the elliptical orbits of planets, revolutionizing celestial mechanics.',
        justification: "Kepler's first law of planetary motion, published in Astronomia Nova (1609), demonstrated that planets orbit the Sun in ellipses with the Sun at one focus.",
        source: 'https://en.wikipedia.org/wiki/Johannes_Kepler',
        sourceTitle: "Wikipedia: Johannes Kepler",
        probabilities: { p_e: 0.96, p_c: 0.01, p_n: 0.03 }
      },
      {
        id: 'claim-7',
        status: 'Accurate',
        claim: 'Petrarch is often considered the father of humanism.',
        justification: 'Francesco Petrarca (Petrarch) is celebrated across academic literature as the "Father of Humanism" and a catalyst of the 14th-century Italian Renaissance.',
        source: 'https://en.wikipedia.org/wiki/Petrarch',
        sourceTitle: 'Wikipedia: Petrarch',
        probabilities: { p_e: 0.95, p_c: 0.02, p_n: 0.03 }
      },
      {
        id: 'claim-8',
        status: 'Accurate',
        claim: 'Erasmus promoted humanist ideals through his writings and translations.',
        justification: 'Desiderius Erasmus of Rotterdam was the foremost Christian humanist of Northern Europe, publishing critical editions of the Greek New Testament and influential satirical works.',
        source: 'https://en.wikipedia.org/wiki/Erasmus',
        sourceTitle: 'Wikipedia: Desiderius Erasmus',
        probabilities: { p_e: 0.93, p_c: 0.02, p_n: 0.05 }
      }
    ]
  },
  {
    id: 'eiffel',
    title: 'Eiffel Tower (Iconic Hallucination Test)',
    wordCount: 88,
    credibilityScore: 33,
    claimsSummary: {
      accurate: 1,
      inaccurate: 2,
      subjective: 0,
      total: 3
    },
    sections: [
      {
        heading: 'Architecture History',
        paragraphs: [
          {
            spans: [
              {
                text: 'The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris. ',
                status: 'accurate',
                claimId: 'eiffel-1'
              },
              {
                text: 'It was constructed in 1892',
                status: 'inaccurate',
                claimId: 'eiffel-2'
              },
              {
                text: ' and ',
                status: 'normal'
              },
              {
                text: 'was designed by Leonardo da Vinci.',
                status: 'inaccurate',
                claimId: 'eiffel-3'
              }
            ]
          }
        ]
      }
    ],
    plainText: 'The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris. It was constructed in 1892 and was designed by Leonardo da Vinci.',
    correctedText: 'The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris. It was constructed from 1887 to 1889 and was designed by Maurice Koechlin, Émile Nouguier, and built by Gustave Eiffel.',
    claims: [
      {
        id: 'eiffel-1',
        status: 'Accurate',
        claim: 'The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris.',
        justification: 'Physical architectural records confirm the Eiffel Tower is located on the Champ de Mars in the 7th arrondissement of Paris, France.',
        source: 'https://en.wikipedia.org/wiki/Eiffel_Tower',
        sourceTitle: 'Wikipedia: Eiffel Tower',
        probabilities: { p_e: 0.99, p_c: 0.0, p_n: 0.01 }
      },
      {
        id: 'eiffel-2',
        status: 'Inaccurate',
        claim: 'The Eiffel Tower was constructed in 1892.',
        justification: 'Construction took place between 1887 and 1889 as the entrance arch for the 1889 Exposition Universelle.',
        source: 'https://en.wikipedia.org/wiki/Eiffel_Tower',
        sourceTitle: 'Wikipedia: Eiffel Tower',
        probabilities: { p_e: 0.01, p_c: 0.98, p_n: 0.01 },
        suggestedRevision: 'It was constructed between 1887 and 1889.'
      },
      {
        id: 'eiffel-3',
        status: 'Inaccurate',
        claim: 'The Eiffel Tower was designed by Leonardo da Vinci.',
        justification: 'Da Vinci died in 1519, centuries prior to Eiffel Tower planning. The tower was designed by Maurice Koechlin and Émile Nouguier, and built by Gustave Eiffel.',
        source: 'https://en.wikipedia.org/wiki/Gustave_Eiffel',
        sourceTitle: 'Wikipedia: Gustave Eiffel',
        probabilities: { p_e: 0.0, p_c: 0.99, p_n: 0.01 },
        suggestedRevision: 'It was designed by Maurice Koechlin and built by Gustave Eiffel.'
      }
    ]
  },
  {
    id: 'apollo',
    title: 'Apollo 11 Moon Mission (Entity Inversion)',
    wordCount: 76,
    credibilityScore: 50,
    claimsSummary: {
      accurate: 1,
      inaccurate: 1,
      subjective: 0,
      total: 2
    },
    sections: [
      {
        heading: 'Lunar Landing',
        paragraphs: [
          {
            spans: [
              {
                text: 'Apollo 11 was the American spaceflight that landed humans on the Moon in July 1969. ',
                status: 'accurate',
                claimId: 'apollo-1'
              },
              {
                text: 'Buzz Aldrin was the mission commander who first stepped onto the lunar surface.',
                status: 'inaccurate',
                claimId: 'apollo-2'
              }
            ]
          }
        ]
      }
    ],
    plainText: 'Apollo 11 was the American spaceflight that landed humans on the Moon in July 1969. Buzz Aldrin was the mission commander who first stepped onto the lunar surface.',
    correctedText: 'Apollo 11 was the American spaceflight that landed humans on the Moon in July 1969. Neil Armstrong was the mission commander who first stepped onto the lunar surface, accompanied by lunar module pilot Buzz Aldrin.',
    claims: [
      {
        id: 'apollo-1',
        status: 'Accurate',
        claim: 'Apollo 11 landed humans on the Moon in July 1969.',
        justification: 'NASA mission records document the Apollo 11 Lunar Module Eagle touchdown on July 20, 1969.',
        source: 'https://www.nasa.gov/mission_pages/apollo/missions/apollo11.html',
        sourceTitle: 'NASA: Apollo 11 Mission Overview',
        probabilities: { p_e: 0.98, p_c: 0.01, p_n: 0.01 }
      },
      {
        id: 'apollo-2',
        status: 'Inaccurate',
        claim: 'Buzz Aldrin was the mission commander who first stepped onto the lunar surface.',
        justification: 'Neil Armstrong was the commander of Apollo 11 and the first human to step onto the Moon. Buzz Aldrin served as the Lunar Module Pilot.',
        source: 'https://en.wikipedia.org/wiki/Neil_Armstrong',
        sourceTitle: 'Wikipedia: Neil Armstrong',
        probabilities: { p_e: 0.02, p_c: 0.97, p_n: 0.01 },
        suggestedRevision: 'Neil Armstrong was the commander and first to step onto the surface, followed by Buzz Aldrin.'
      }
    ]
  }
];

export const ANALYTICS_DATA = {
  kpis: [
    { label: 'TOTAL PROOFS', value: '3,412', subtitle: '+18% vs prev period' },
    { label: 'AVG TIME TO VERDICT', value: '2.1s', subtitle: 'Target: < 3.0s' },
    { label: 'AUTO-VERIFIED', value: '61%', subtitle: 'High-confidence NLI pass' },
    { label: 'DISPUTED VERDICTS', value: '0.4%', subtitle: 'Well below 0.5% cap' }
  ],
  verdictMix: {
    verified: 2047,
    misleading: 614,
    falseClaims: 512,
    unverified: 239,
    total: 3412
  },
  topicsVolume: [
    { topic: 'Politics', count: 1084, percentage: 88 },
    { topic: 'Health', count: 742, percentage: 68 },
    { topic: 'Finance', count: 618, percentage: 56 },
    { topic: 'Tech & AI', count: 512, percentage: 46 },
    { topic: 'Climate', count: 456, percentage: 40 }
  ],
  busiestHour: {
    time: '08:00–09:00',
    description: 'Morning wire ingest + overnight viral backlog'
  },
  calibrationNote: {
    headline: 'CONFIDENCE CALIBRATION',
    content: 'Verdicts filed at 90%+ confidence were later disputed in 0.2% of cases — within the 0.5% target. Calibration drift: none detected.',
    ece: '0.041 (DeBERTa-v3 temperature calibrated with L-BFGS, T=0.2633)'
  },
  // 30 days daily proofs data (values normalized between ~40 and 100, last bar red)
  dailyProofs: [
    { date: 'Jun 7', count: 88 },
    { date: 'Jun 8', count: 95 },
    { date: 'Jun 9', count: 102 },
    { date: 'Jun 10', count: 74 },
    { date: 'Jun 11', count: 98 },
    { date: 'Jun 12', count: 115 },
    { date: 'Jun 13', count: 124 },
    { date: 'Jun 14', count: 108 },
    { date: 'Jun 15', count: 89 },
    { date: 'Jun 16', count: 92 },
    { date: 'Jun 17', count: 104 },
    { date: 'Jun 18', count: 110 },
    { date: 'Jun 19', count: 130 },
    { date: 'Jun 20', count: 122 },
    { date: 'Jun 21', count: 116 },
    { date: 'Jun 22', count: 98 },
    { date: 'Jun 23', count: 85 },
    { date: 'Jun 24', count: 101 },
    { date: 'Jun 25', count: 119 },
    { date: 'Jun 26', count: 128 },
    { date: 'Jun 27', count: 135 },
    { date: 'Jun 28', count: 120 },
    { date: 'Jun 29', count: 104 },
    { date: 'Jun 30', count: 96 },
    { date: 'Jul 1', count: 112 },
    { date: 'Jul 2', count: 138 },
    { date: 'Jul 3', count: 144 },
    { date: 'Jul 4', count: 126 },
    { date: 'Jul 5', count: 132 },
    { date: 'Jul 6', count: 156, isCurrent: true }
  ]
};
