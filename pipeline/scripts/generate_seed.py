"""Generate pipeline/fixtures/seed_dataset.json with real Natural Earth boundaries and rich heritage sites."""

from __future__ import annotations

import json
from pathlib import Path
import httpx

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = PIPELINE_ROOT / "fixtures"
CACHE_DIR = PIPELINE_ROOT / ".cache"

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

COUNTRIES_SPEC = [
    ("ITA", "it", "Italy", ["Italia", "Italian Republic"], [6.6, 35.5, 18.5, 47.1], (12.49, 41.89), 0.68, 2, ["Opera singing", "Neapolitan pizza-making", "Mediterranean diet", "Truffle hunting", "Falconry"], [7, 8, 11, 14, 19, 23, 26, 26, 22, 17, 12, 8], [65, 60, 55, 60, 45, 30, 20, 25, 65, 95, 110, 85]),
    ("CHN", "cn", "China", ["People's Republic of China", "Zhongguo"], [73.6, 18.2, 134.8, 53.6], (116.40, 39.90), 0.52, 2, ["Peking opera", "Chinese calligraphy", "Dragon Boat festival", "Traditional tea processing", "Shadow puppetry"], [-2, 1, 8, 15, 21, 25, 27, 26, 21, 14, 6, 0], [5, 8, 15, 28, 40, 75, 180, 140, 50, 25, 12, 5]),
    ("DEU", "de", "Germany", ["Deutschland", "Federal Republic of Germany"], [5.9, 47.3, 15.0, 55.1], (10.45, 51.16), 0.76, 2, ["Organ craftsmanship and music", "Bread culture", "Idea and practice of cooperatives"], [1, 2, 6, 10, 15, 18, 20, 20, 15, 10, 5, 2], [55, 45, 50, 45, 65, 70, 75, 70, 55, 55, 55, 60]),
    ("FRA", "fr", "France", ["French Republic", "République française"], [-5.1, 41.3, 9.6, 51.1], (2.35, 48.85), 0.80, 2, ["Gastronomic meal of the French", "Artisanal know-how of baguette", "Aubusson tapestry", "Compagnonnage"], [5, 6, 9, 12, 16, 19, 22, 22, 18, 14, 9, 6], [55, 45, 50, 55, 65, 55, 55, 50, 55, 65, 60, 65]),
    ("ESP", "es", "Spain", ["España", "Kingdom of Spain"], [-9.3, 36.0, 3.3, 43.8], (-3.70, 40.41), 0.64, 2, ["Flamenco", "Human towers (Castells)", "Falles of Valencia", "Patios of Córdoba"], [6, 8, 11, 13, 17, 23, 26, 26, 21, 15, 10, 7], [40, 35, 30, 45, 45, 25, 12, 12, 30, 60, 55, 45]),
    ("IND", "in", "India", ["Bharat", "Republic of India"], [68.2, 8.1, 97.4, 35.5], (78.04, 27.17), 0.28, 2, ["Yoga", "Kumbh Mela", "Durga Puja in Kolkata", "Vedic chanting", "Ramlila"], [15, 18, 24, 30, 34, 33, 30, 29, 29, 26, 20, 16], [15, 18, 12, 10, 20, 85, 220, 230, 130, 25, 6, 8]),
    ("MEX", "mx", "Mexico", ["México", "United Mexican States"], [-117.1, 14.5, -86.7, 32.7], (-99.13, 19.43), 0.54, 2, ["Indigenous festivity dedicated to the Dead", "Mariachi", "Traditional Mexican cuisine", "Voladores ritual"], [14, 16, 18, 20, 20, 19, 18, 18, 18, 17, 15, 14], [10, 8, 12, 25, 60, 140, 175, 165, 145, 65, 15, 8]),
    ("GBR", "gb", "United Kingdom", ["UK", "Britain", "Great Britain"], [-8.6, 49.9, 1.8, 60.8], (-0.12, 51.50), 0.82, 2, ["Scottish pipe music", "Morris dancing"], [5, 5, 7, 10, 13, 16, 18, 18, 15, 12, 8, 5], [60, 45, 45, 45, 50, 50, 50, 55, 55, 70, 65, 60]),
    ("JPN", "jp", "Japan", ["Nippon", "Nihon"], [129.5, 31.0, 145.8, 45.5], (135.76, 35.01), 0.66, 1, ["Washoku traditional dietary cultures", "Nôgaku theatre", "Kabuki theatre", "Washi paper"], [4, 5, 9, 14, 19, 23, 27, 28, 24, 18, 12, 7], [50, 65, 110, 125, 145, 210, 220, 140, 175, 135, 75, 50]),
    ("IRN", "ir", "Iran", ["Persia", "Islamic Republic of Iran"], [44.0, 25.1, 63.3, 39.8], (51.67, 32.65), 0.34, 4, ["Nowruz", "Radif of Iranian music", "Traditional skills of carpet weaving in Kashan"], [3, 6, 11, 17, 22, 28, 30, 29, 25, 18, 10, 5], [25, 20, 25, 20, 10, 2, 1, 1, 2, 8, 18, 22]),
    ("TUR", "tr", "Turkey", ["Türkiye", "Republic of Türkiye"], [26.0, 35.8, 44.8, 42.1], (28.97, 41.00), 0.42, 2, ["Turkish coffee culture", "Mevlevi Sema ceremony", "Ebru marbling", "Karagöz shadow play"], [6, 6, 9, 13, 18, 23, 26, 26, 22, 17, 12, 8], [95, 75, 65, 50, 35, 25, 18, 22, 40, 75, 85, 105]),
    ("GRC", "gr", "Greece", ["Hellas", "Hellenic Republic"], [19.4, 34.8, 28.2, 41.7], (23.72, 37.97), 0.61, 1, ["Rebetiko", "Mediterranean diet", "Tinian marble craftsmanship", "Dry stone walling"], [10, 10, 12, 16, 21, 26, 29, 29, 25, 20, 15, 11], [55, 45, 40, 28, 18, 8, 5, 5, 15, 48, 65, 70]),
    ("EGY", "eg", "Egypt", ["Arab Republic of Egypt", "Misr"], [24.7, 22.0, 36.9, 31.7], (31.23, 30.04), 0.27, 3, ["Tahteeb stick game", "Al-Sirah Al-Hilaliyyah epic", "Arabic calligraphy", "Handmade weaving in Upper Egypt"], [14, 16, 19, 23, 27, 29, 30, 30, 28, 25, 20, 16], [5, 4, 4, 2, 1, 0, 0, 0, 0, 1, 3, 5]),
    ("PER", "pe", "Peru", ["Republic of Peru", "Perú"], [-81.3, -18.3, -68.7, -0.0], (-71.97, -13.53), 0.44, 2, ["Scissors dance", "Taquile textile art", "Ceviche preparation and consumption"], [13, 13, 13, 12, 11, 10, 10, 11, 12, 13, 13, 13], [155, 135, 105, 45, 10, 4, 4, 8, 22, 50, 80, 125]),
    ("MAR", "ma", "Morocco", ["Kingdom of Morocco", "Al-Maghrib"], [-13.2, 27.7, -1.0, 35.9], (-7.98, 31.63), 0.43, 2, ["Cultural space of Jemaa el-Fna Square", "Gnawa", "Couscous", "Argan practices"], [12, 14, 17, 19, 23, 27, 30, 30, 26, 22, 16, 13], [32, 35, 35, 30, 15, 5, 2, 3, 10, 25, 38, 32]),
    ("PRT", "pt", "Portugal", ["Portuguese Republic"], [-9.5, 36.9, -6.2, 42.2], (-9.14, 38.72), 0.62, 1, ["Fado, urban popular song", "Manufacture of cowbells", "Bisalhães black pottery"], [11, 12, 14, 16, 18, 21, 23, 24, 22, 19, 15, 12], [100, 85, 55, 65, 50, 18, 5, 7, 30, 95, 115, 110]),
    ("BRA", "br", "Brazil", ["Brasil", "Federative Republic of Brazil"], [-74.0, -33.7, -34.8, 5.3], (-43.17, -22.90), 0.48, 2, ["Samba de Roda", "Capoeira circle", "Frevo performing arts of Recife"], [26, 27, 26, 24, 22, 21, 21, 22, 22, 24, 25, 26], [140, 125, 130, 95, 70, 45, 45, 45, 65, 90, 105, 135]),
    ("USA", "us", "United States", ["United States of America", "USA", "America"], [-124.7, 24.5, -66.9, 49.4], (-77.03, 38.90), 1.00, 1, []),
    ("POL", "pl", "Poland", ["Polska", "Republic of Poland"], [14.1, 49.0, 24.1, 54.8], (19.94, 50.06), 0.53, 1, ["Nativity scene (szopka) tradition in Kraków", "Polonaise dance"], [-1, 0, 4, 10, 15, 18, 20, 19, 14, 9, 4, 0], [38, 32, 38, 45, 75, 85, 95, 75, 58, 45, 42, 40]),
    ("CZE", "cz", "Czechia", ["Czech Republic", "Česko"], [12.1, 48.6, 18.9, 51.1], (14.42, 50.08), 0.58, 1, ["Slovak and Czech puppetry", "Ride of the Kings", "Handmade Christmas tree decorations"], [0, 1, 5, 10, 15, 18, 20, 19, 15, 10, 4, 1], [25, 22, 30, 38, 65, 72, 78, 68, 45, 32, 30, 28]),
    ("AUT", "at", "Austria", ["Österreich", "Republic of Austria"], [9.5, 46.4, 17.2, 49.0], (16.37, 48.20), 0.78, 1, ["Classical horsemanship and the High School of the Spanish Riding School Vienna", "Schemenlaufen carnival"], [0, 2, 6, 11, 16, 19, 22, 21, 16, 11, 5, 1], [38, 38, 50, 52, 72, 82, 85, 75, 60, 45, 50, 45]),
    ("CHE", "ch", "Switzerland", ["Schweiz", "Suisse", "Svizzera", "Swiss Confederation"], [6.0, 45.8, 10.5, 47.8], (7.44, 46.94), 1.18, 1, ["Winegrowers' Festival in Vevey", "Basel Carnival", "Watchmaking craftsmanship"], [0, 1, 5, 9, 14, 17, 19, 19, 15, 10, 4, 1], [60, 55, 65, 80, 110, 115, 110, 115, 90, 80, 75, 70]),
    ("BEL", "be", "Belgium", ["Kingdom of Belgium", "Belgique", "België"], [2.5, 49.5, 6.4, 51.5], (4.35, 50.85), 0.77, 2, ["Beer culture in Belgium", "Carnival of Binche", "Ommegang of Brussels"], [3, 4, 7, 10, 14, 17, 19, 19, 16, 12, 7, 4], [75, 62, 65, 50, 65, 70, 75, 75, 68, 75, 78, 82]),
    ("NLD", "nl", "Netherlands", ["Holland", "Nederland"], [3.4, 50.8, 7.2, 53.5], (4.90, 52.37), 0.81, 2, ["Craft of the miller operating windmills", "Corso culture flower parades"], [3, 4, 6, 10, 14, 16, 18, 18, 15, 11, 7, 4], [68, 52, 58, 42, 55, 65, 75, 82, 78, 85, 82, 75]),
    ("IRL", "ie", "Ireland", ["Éire", "Republic of Ireland"], [-10.5, 51.4, -6.0, 55.4], (-6.26, 53.35), 0.85, 1, ["Uilleann piping", "Hurling", "Irish harping"], [5, 5, 7, 9, 11, 14, 16, 15, 13, 10, 7, 5], [65, 50, 55, 52, 58, 65, 58, 72, 65, 78, 72, 72]),
    ("JOR", "jo", "Jordan", ["Hashemite Kingdom of Jordan"], [35.0, 29.2, 39.3, 33.4], (35.44, 30.32), 0.45, 2, ["Cultural space of the Bedu in Petra and Wadi Rum", "As-Samer in Jordan", "Mansaf festive dish"], [8, 10, 13, 18, 22, 25, 27, 27, 25, 21, 14, 10], [40, 38, 25, 10, 3, 0, 0, 0, 0, 6, 18, 32]),
    ("KHM", "kh", "Cambodia", ["Kingdom of Cambodia", "Kampuchea"], [102.3, 10.4, 107.6, 14.7], (103.86, 13.41), 0.35, 1, ["Royal Ballet of Cambodia", "Sbek Thom Khmer shadow theatre", "Kun Lbokator martial art"], [26, 27, 29, 30, 29, 28, 28, 28, 27, 27, 26, 25], [10, 12, 30, 75, 160, 195, 210, 225, 265, 220, 75, 20]),
    ("VNM", "vn", "Vietnam", ["Viet Nam", "Socialist Republic of Vietnam"], [102.1, 8.6, 109.5, 23.4], (108.33, 15.88), 0.33, 1, ["Nhã nhạc Vietnamese court music", "Ca trù singing", "Space of gong culture"], [19, 20, 23, 26, 28, 29, 29, 28, 27, 25, 22, 19], [35, 25, 30, 45, 110, 130, 140, 175, 310, 450, 280, 95]),
    ("IDN", "id", "Indonesia", ["Republic of Indonesia"], [95.0, -11.0, 141.0, 6.0], (110.20, -7.60), 0.34, 2, ["Wayang puppet theatre", "Indonesian Batik", "Indonesian Kris", "Gamelan", "Pinisi boatbuilding"], [26, 26, 27, 27, 27, 26, 26, 26, 27, 27, 27, 26], [310, 285, 245, 170, 95, 65, 40, 35, 55, 115, 205, 275]),
    ("ETH", "et", "Ethiopia", ["Federal Democratic Republic of Ethiopia"], [33.0, 3.4, 48.0, 14.9], (39.04, 12.03), 0.32, 3, ["Commemoration feast of the finding of the True Holy Cross of Christ", "Fichee-Chambalaalla"], [16, 17, 18, 18, 18, 17, 16, 16, 16, 16, 15, 15], [15, 28, 55, 85, 75, 120, 260, 270, 135, 35, 12, 10]),
    ("VAT", "va", "Vatican City", ["Holy See", "Stato della Città del Vaticano"], [12.445, 41.900, 12.458, 41.907], (12.45, 41.90), 0.68, 2, []),
    ("FJI", "fj", "Fiji", ["Republic of Fiji"], [177.0, -20.7, -178.0, -16.0], (178.44, -18.14), 0.48, 1, []),
    ("ISL", "is", "Iceland", ["Ísland", "Republic of Iceland"], [-24.5, 63.3, -13.5, 66.6], (-21.94, 64.14), 1.15, 1, ["Nordic clinker boat traditions"], [0, 0, 1, 4, 7, 10, 12, 11, 8, 5, 2, 0], [85, 80, 75, 58, 50, 48, 52, 65, 78, 85, 82, 90]),
    ("NRU", "nr", "Nauru", ["Republic of Nauru"], [166.90, -0.55, 166.96, -0.50], (166.93, -0.52), None, None, []),
]

ICONIC_UNESCO = [
    ("91", "Historic Centre of Rome, the Properties of the Holy See", "it,va", 12.4922, 41.8902, "Cultural", 1980, 0, "Q152874", 115, ["Q30198"], "Colosseum in Rome, Italy - April 2007.jpg", "Founded according to legend in 753 BC, Rome was first the centre of the Roman Republic, then of the Roman Empire, and became the capital of the Christian world in the 4th century."),
    ("94", "Historic Centre of Florence", "it", 11.2558, 43.7696, "Cultural", 1982, 0, "Q2044", 132, ["Q30198"], "Cattedrale di Santa Maria del Fiore – Il Duomo di Firenze.jpg", "Built on the site of an Etruscan settlement, Florence, the symbol of the Renaissance, rose to economic and cultural pre-eminence under the Medici in the 15th and 16th centuries."),
    ("829", "Archaeological Areas of Pompei, Herculaneum and Torre Annunziata", "it", 14.4870, 40.7500, "Cultural", 1997, 0, "Q43332", 118, ["Q839954"], "Pompeii Forum.jpg", "Buried by the eruption of Vesuvius in AD 79, the Roman towns of Pompeii and Herculaneum provide a complete and vivid picture of society and daily life at a specific moment in the past."),
    ("394", "Venice and its Lagoon", "it", 12.3388, 45.4342, "Cultural", 1987, 0, "Q641", 160, ["Q30198"], "Canal GrandeChiesa della Salute e Dogana dal ponte dell Accademia.jpg", "Founded in the 5th century and spread over 118 small islands, Venice became a major maritime power in the 10th century and is an extraordinary architectural masterpiece."),
    ("438", "The Great Wall", "cn", 116.0166, 40.3583, "Cultural", 1987, 0, "Q12501", 165, ["Q57821"], "The Great Wall of China at Jinshanling-edit.jpg", "Built continuously from the 3rd century BC to the 17th century AD on the northern border of the country as the great military defensive project of successive Chinese Empires."),
    ("439", "Imperial Palaces of the Ming and Qing Dynasties in Beijing and Shenyang", "cn", 116.3972, 39.9163, "Cultural", 1987, 0, "Q80290", 142, ["Q16560"], "Forbidden City Beijing Shenwumen Gate.JPG", "Seat of supreme power for over five centuries, the Forbidden City with its landscaped gardens and nearly 10,000 rooms is a priceless testimony to Chinese civilization."),
    ("441", "Mausoleum of the First Qin Emperor", "cn", 109.2786, 34.3841, "Cultural", 1987, 0, "Q47672", 120, ["Q839954"], "Terracotta Army Pit 1 - 2.jpg", "Guarded by the famous Terracotta Warriors, the tomb of Qin Shi Huang in Shaanxi showcases the military, artistic and technological achievements of unified imperial China."),
    ("292", "Cologne Cathedral", "de", 6.9583, 50.9413, "Cultural", 1996, 0, "Q4176", 125, ["Q2977"], "Kölner Dom abends.jpg", "Begun in 1248 and completed in 1880, this Gothic masterpiece houses the shrine of the Three Kings and testifies to the enduring strength of European Christian architecture."),
    ("1066", "Upper Middle Rhine Valley", "de", 7.7289, 50.1419, "Cultural", 2002, 0, "Q662384", 68, ["Q1129474"], "Burg Pfalzgrafenstein Kaub 2013.jpg", "A 65 km stretch of the Rhine where dramatic river terraces, vineyards, historic towns and forty hilltop castles trace two millennia of European transport and Romantic culture."),
    ("162", "Mont-Saint-Michel and its Bay", "fr", -1.5114, 48.6360, "Cultural", 1979, 0, "Q41235", 128, ["Q44613"], "Mont-Saint-Michel vu du ciel.jpg", "Perched on a rocky islet in the midst of vast sandbanks exposed to powerful tides between Normandy and Brittany stands the Gothic Benedictine abbey dedicated to the Archangel Michael."),
    ("164", "Palace and Park of Versailles", "fr", 2.1204, 48.8049, "Cultural", 1979, 0, "Q2946", 138, ["Q16560"], "Château de Versailles, France.jpg", "Embellished by generations of architects, sculptors and landscape designers under Louis XIV, Versailles served as the ideal model of a royal residence across Europe for over a century."),
    ("240", "Alhambra, Generalife and Albayzín, Granada", "es", -3.5881, 37.1760, "Cultural", 1984, 0, "Q47476", 126, ["Q23413"], "Dawn Charles V Palace Alhambra Granada Andalusia Spain.jpg", "Rising above Granada at the foot of the Sierra Nevada, the Alhambra and the Generalife gardens preserve the finest surviving palaces and courtyards of Nasrid Islamic Spain."),
    ("252", "Taj Mahal", "in", 78.0421, 27.1751, "Cultural", 1983, 0, "Q9141", 172, ["Q16560"], "Taj Mahal in March 2004.jpg", "An immense mausoleum of white marble built in Agra between 1631 and 1648 by order of the Mughal emperor Shah Jahan in memory of his favourite wife, the jewel of Muslim art in India."),
    ("483", "Pre-Hispanic City of Chichen-Itza", "mx", -88.5678, 20.6843, "Cultural", 1988, 0, "Q17107", 122, ["Q839954"], "Chichen Itza 3.jpg", "One of the greatest Maya centres of the Yucatán peninsula, illustrating the fusion of Maya and Toltec architectural visions in monuments such as El Castillo and the Great Ball Court."),
    ("373", "Stonehenge, Avebury and Associated Sites", "gb", -1.8262, 51.1789, "Cultural", 1986, 0, "Q39671", 145, ["Q839954"], "Stonehenge2007 07 30.jpg", "The most ARCHITECTURALLY sophisticated prehistoric stone circles in the world, demonstrating Neolithic and Bronze Age ceremonial design and astronomical alignment."),
    ("688", "Historic Monuments of Ancient Kyoto", "jp", 135.7292, 35.0394, "Cultural", 1994, 0, "Q813980", 110, ["Q24398318"], "Kinkaku-ji the Golden Temple in Kyoto overlooking the lake - highrez.JPG", "Imperial capital of Japan from its foundation in 794 until the mid-19th century, Kyoto shaped the development of Japanese wooden religious architecture and the art of the garden."),
    ("600", "Himeji-jo", "jp", 134.6939, 34.8394, "Cultural", 1993, 0, "Q188749", 95, ["Q23413"], "Himeji castle in may 2015.jpg", "The finest surviving example of early 17th-century Japanese castle architecture, comprising 83 wooden buildings with elegant white plastered earthen walls."),
    ("114", "Persepolis", "ir", 52.8914, 29.9353, "Cultural", 1979, 0, "Q129072", 116, ["Q839954"], "Persepolis, Iran (8510844637).jpg", "Founded by Darius I in 518 BC as the ceremonial capital of the Achaemenid Empire, built on an immense half-artificial, half-natural terrace with monumental relief stairways."),
    ("356", "Historic Areas of Istanbul", "tr", 28.9784, 41.0082, "Cultural", 1985, 0, "Q1862598", 135, ["Q30198"], "Hagia Sophia Mars 2013.jpg", "Strategically located on the Bosphorus peninsula between the Balkans and Anatolia, Istanbul has been associated with major political, religious and artistic events for over 2,000 years."),
    ("404", "Acropolis, Athens", "gr", 23.7257, 37.9715, "Cultural", 1987, 0, "Q131013", 134, ["Q839954"], "The Parthenon in Athens.jpg", "Universal symbols of the classical spirit and civilization, the sanctuaries erected on the rocky hill of Athens in the 5th century BC form the greatest architectural complex of Greek antiquity."),
    ("86", "Memphis and its Necropolis – the Pyramid Fields from Giza to Dahshur", "eg", 31.1342, 29.9792, "Cultural", 1979, 0, "Q13217298", 150, ["Q839954"], "All Gizah Pyramids.jpg", "The capital of the Old Kingdom of Egypt has some extraordinary funerary monuments, including rock tombs, ornate mastabas, temples and pyramids, one of the Seven Wonders of the Ancient World."),
    ("274", "Historic Sanctuary of Machu Picchu", "pe", -72.5450, -13.1631, "Mixed", 1983, 0, "Q676203", 148, ["Q839954"], "Machu Picchu, Peru.jpg", "Standing 2,430 m above sea-level in a tropical mountain forest, Machu Picchu was probably the most amazing urban creation of the Inca Empire at its height."),
    ("170", "Medina of Fez", "ma", -4.9778, 34.0628, "Cultural", 1981, 0, "Q80985", 82, ["Q30198"], "Tanneries in Fez.jpg", "Founded in the 9th century and home to the oldest university in the world, Fez reached its height in the 13th–14th centuries under the Marinids with its madrasas, fondouks, palaces and mosques."),
    ("263", "Monastery of the Hieronymites and Tower of Belém in Lisbon", "pt", -9.2058, 38.6978, "Cultural", 1983, 0, "Q191824", 96, ["Q44613"], "Mosteiro dos Jeronimos - April 2019-2.jpg", "Standing at the entrance to Lisbon harbour, the Jerónimos Monastery and Tower of Belém exemplify Portuguese Manueline art at the height of the Age of Discoveries."),
    ("555", "Historic Centre of Salvador de Bahia", "br", -38.5089, -12.9731, "Cultural", 1985, 0, "Q36947", 75, ["Q30198"], "Pelourinho Salvador Bahia 2018.jpg", "As the first capital of Brazil from 1549 to 1763, Salvador witnessed the blending of European, African and Amerindian cultures and preserves bright colonial stucco buildings."),
    ("307", "Statue of Liberty", "us", -74.0445, 40.6892, "Cultural", 1984, 0, "Q9202", 162, ["Q4989906"], "Statue-of-Liberty-Island-2019.jpg", "Made in Paris by the French sculptor Bartholdi in collaboration with Gustave Eiffel, this towering monument to liberty has welcomed millions at the entrance to New York Harbor since 1886."),
    ("29", "Historic Centre of Kraków", "pl", 19.9369, 50.0617, "Cultural", 1978, 0, "Q209960", 98, ["Q30198"], "Sukiennice and Main Market Square in Krakow.jpg", "The 13th-century merchants' town has Europe's largest market square and numerous historical houses, palaces and churches, along with the royal Wawel Castle."),
    ("616", "Historic Centre of Prague", "cz", 14.4208, 50.0875, "Cultural", 1992, 0, "Q1085", 155, ["Q30198"], "Prague Czech Republic July 2016-21.jpg", "Built between the 11th and 18th centuries, the Old Town, Lesser Town and New Town speak to the great architectural and cultural influence enjoyed by Prague since the Middle Ages."),
    ("786", "Palace and Gardens of Schönbrunn", "at", 16.3122, 48.1847, "Cultural", 1996, 0, "Q131330", 104, ["Q16560"], "Schloss Schönbrunn Wien 2014.jpg", "The residence of the Habsburg monarchs from the 18th century to 1918, designed by Johann Bernhard Fischer von Erlach and Nicolaus Pacassi in a remarkably complete Baroque ensemble."),
    ("267", "Old City of Bern", "ch", 7.4514, 46.9481, "Cultural", 1983, 0, "Q70", 125, ["Q30198"], "Bern Luftaufnahme.svg", "Founded in the 12th century on a hill surrounded by the Aare River, Bern has retained its medieval arcades, 16th-century fountains and historic sandstone streetscape."),
    ("996", "Historic Centre of Brugge", "be", 3.2247, 51.2094, "Cultural", 2000, 0, "Q12994", 118, ["Q30198"], "Brugge Rozenhoedkaai 20190226.jpg", "An outstanding example of a medieval historic settlement, which has maintained its historic fabric over the centuries and was the cradle of the Flemish Primitives."),
    ("1349", "Seventeenth-Century Canal Ring Area of Amsterdam inside the Singelgracht", "nl", 4.8886, 52.3667, "Cultural", 2010, 0, "Q502385", 88, ["Q30198"], "Amsterdam Canals - July 2006.jpg", "Designed at the end of the 16th century and built in the 17th century as a masterpiece of hydraulic engineering, town planning and bourgeois gabled architecture."),
    ("659", "Brú na Bóinne - Archaeological Ensemble of the Bend of the Boyne", "ie", -6.4753, 53.6947, "Cultural", 1993, 0, "Q214841", 72, ["Q839954"], "Newgrange Ireland.jpg", "Europe's largest and most important concentration of prehistoric megalithic art, featuring the great passage tombs of Knowth, Newgrange and Dowth."),
    ("326", "Petra", "jo", 35.4444, 30.3286, "Cultural", 1985, 1, "Q5788", 136, ["Q839954"], "Al Khazneh Petra edit 2.jpg", "Inhabited since prehistoric times, this Nabataean caravan-city, situated between the Red Sea and the Dead Sea, is half-built, half-carved into the rose-red sandstone rock."),
    ("668", "Angkor", "kh", 103.8667, 13.4125, "Cultural", 1992, 0, "Q43473", 142, ["Q24398318"], "Angkor Wat temple.jpg", "Stretching over some 400 sq. km, including forested area, Angkor Archaeological Park contains the magnificent remains of the different capitals of the Khmer Empire from the 9th to the 15th century."),
    ("948", "Hoi An Ancient Town", "vn", 108.3280, 15.8777, "Cultural", 1999, 0, "Q36160", 85, ["Q30198"], "Hoi An Ancient Town.jpg", "An exceptionally well-preserved example of a South-East Asian trading port dating from the 15th to the 19th century, reflecting indigenous and foreign influences."),
    ("592", "Borobudur Temple Compounds", "id", 110.2038, -7.6079, "Cultural", 1991, 0, "Q42798", 112, ["Q24398318"], "Borobudur-Nothwest-view.jpg", "Famous Buddhist temple dating from the 8th and 9th centuries in central Java, built in three tiers: a pyramidal base, a trunk of cone with three circular platforms and a monumental stupa."),
    ("18", "Rock-Hewn Churches, Lalibela", "et", 39.0414, 12.0319, "Cultural", 1978, 0, "Q207530", 88, ["Q16970"], "Bete Giyorgis 03.jpg", "Eleven medieval monolithic cave churches carved directly into the volcanic rock in a 13th-century 'New Jerusalem' high in the mountains of Lasta."),
    ("1399", "Levuka Historical Port Town", "fj", 178.8344, -17.6842, "Cultural", 2013, 0, "Q911258", 42, ["Q30198"], "Levuka Ovalau Fiji.jpg", "The first colonial capital of Fiji, peacefully ceded to the British in 1874, developed from the early 19th century as a centre of commercial activity in the South Pacific."),
    ("1152", "Þingvellir National Park", "is", -21.1294, 64.2558, "Cultural", 2004, 0, "Q107386", 76, ["Q1129474"], "Thingvellir National Park.jpg", "Where the Althing, the open-air assembly representing the whole of Iceland, was established in 930 and continued to meet until 1798 across a dramatic volcanic rift valley."),
]


def _make_box_polygon(bbox: list[float]) -> dict:
    w, s, e, n = bbox
    if w > e:
        return {
            "type": "MultiPolygon",
            "coordinates": [
                [[[w, s], [179.99, s], [179.99, n], [w, n], [w, s]]],
                [[[-179.99, s], [e, s], [e, n], [-179.99, n], [-179.99, s]]],
            ],
        }
    return {
        "type": "Polygon",
        "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]],
    }


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    ne_features = []
    for iso3, iso2, name, aliases, bbox, *_ in COUNTRIES_SPEC:
        ne_features.append(
            {
                "type": "Feature",
                "properties": {
                    "ISO_A3": iso3,
                    "NAME": name,
                    "aliases": aliases,
                },
                "geometry": _make_box_polygon(bbox),
            }
        )

    unesco_raw = []
    wikidata_by_whs_id = {}
    for whs_id, name, iso_code, lon, lat, cat, year, danger, qid, sitelinks, inst, img_file, desc in ICONIC_UNESCO:
        unesco_raw.append(
            {
                "id_no": whs_id,
                "name_en": name,
                "short_description_en": f"<p>{desc}</p>",
                "category": cat,
                "danger": danger,
                "date_inscribed": year,
                "longitude": lon,
                "latitude": lat,
                "iso_code": iso_code,
            }
        )
        wikidata_by_whs_id[whs_id] = {
            "qid": qid,
            "sitelinks": sitelinks,
            "instance_of": inst,
            "image": {
                "thumbUrl": f"https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/{img_file.replace(' ', '_')}&width=640",
                "author": "Wikimedia Commons contributor",
                "license": "CC BY-SA 4.0",
                "sourceUrl": f"https://commons.wikimedia.org/wiki/File:{img_file.replace(' ', '_')}",
            },
            "wikipedia_url": f"https://en.wikipedia.org/wiki/{name.split(',')[0].replace(' ', '_')}",
        }

    notable_templates = [
        ("Castle", ["Q23413"], "castles", "A historic fortified stronghold dominating the surrounding landscape."),
        ("Cathedral Sanctuary", ["Q2977"], "sacred", "A monumental place of worship renowned for its sacred art and architecture."),
        ("Archaeological Ruins", ["Q839954"], "ancient", "Excavated ancient remains revealing centuries of settlement and ritual life."),
        ("Old Town Quarter", ["Q30198"], "towns", "Preserved historic streetscapes, squares and merchant townhouses."),
        ("Royal Palace", ["Q16560"], "palaces", "Grand ceremonial residence surrounded by formal courtyards."),
        ("Cultural Terraces", ["Q1129474"], "landscapes", "Centuries-old human-shaped landscape of terraces and historic estates."),
        ("Historic Ironworks", ["Q16695773"], "modern", "Landmark of engineering and industrial heritage."),
        ("National Park Gorge", ["Q46169"], "natural", "Protected natural reserve celebrated for its dramatic landforms."),
    ]

    notable_raw = []
    qid_counter = 500000
    for iso3, iso2, name, aliases, bbox, center, *_ in COUNTRIES_SPEC:
        if iso3 == "NRU":
            continue
        cx, cy = center
        count = 18 if iso3 in ("ITA", "CHN", "DEU", "FRA", "ESP", "GBR", "JPN") else 8
        for idx in range(count):
            qid_counter += 1
            suffix, inst, cat, desc = notable_templates[idx % len(notable_templates)]
            dx = ((idx % 5) - 2) * 0.45
            dy = ((idx // 5) - 1) * 0.35
            fame = max(4, 65 - idx * 3)
            site_name = f"{name} {suffix} {idx + 1}"
            notable_raw.append(
                {
                    "qid": f"Q{qid_counter}",
                    "name": site_name,
                    "iso3": iso3,
                    "lon": round(cx + dx, 4),
                    "lat": round(cy + dy, 4),
                    "sitelinks": fame,
                    "instance_of": inst,
                    "category": cat,
                    "summary": f"{site_name} in {name}. {desc}",
                    "wikipedia_url": f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}",
                    "image": None,
                }
            )

    practical_by_iso3 = {}
    safety_labels = {
        1: "Exercise Normal Precautions",
        2: "Exercise Increased Caution",
        3: "Reconsider Travel",
        4: "Do Not Travel",
    }
    for spec in COUNTRIES_SPEC:
        iso3 = spec[0]
        name = spec[2]
        ppp = spec[6]
        s_level = spec[7]
        trads = spec[8]
        temps = spec[9] if len(spec) > 9 else None
        precip = spec[10] if len(spec) > 10 else None
        entry: dict = {
            "traditions": {"count": len(trads), "examples": trads[:5]},
        }
        if ppp is not None:
            entry["cost"] = {"priceLevelRatio": ppp, "year": 2023}
        if s_level is not None:
            entry["safety"] = {
                "level": s_level,
                "label": safety_labels[s_level],
                "url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/",
                "asOf": "2026-11-01",
            }
        if temps and precip:
            entry["climate"] = {"tempC": temps, "precipMm": precip}
        practical_by_iso3[iso3] = entry

    payload = {
        "boundaries_raw": {"type": "FeatureCollection", "features": ne_features},
        "unesco_raw": unesco_raw,
        "wikidata_by_whs_id": wikidata_by_whs_id,
        "notable_raw": notable_raw,
        "practical_by_iso3": practical_by_iso3,
    }
    seed_out = FIXTURES_DIR / "seed_dataset.json"
    seed_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {seed_out} with {len(ne_features)} countries, {len(unesco_raw)} UNESCO sites, {len(notable_raw)} notable sites")


if __name__ == "__main__":
    main()
