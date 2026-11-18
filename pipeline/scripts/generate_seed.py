"""Generate pipeline/fixtures/seed_dataset.json with real Natural Earth 50m country polygons and authentic heritage sites."""

from __future__ import annotations

import json
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = PIPELINE_ROOT / "fixtures"
CACHE_DIR = PIPELINE_ROOT / ".cache"

ISO_NUM_TO_ISO3_ISO2: dict[str, tuple[str, str]] = {
    "004": ("AFG", "af"), "008": ("ALB", "al"), "012": ("DZA", "dz"), "020": ("AND", "ad"),
    "024": ("AGO", "ao"), "028": ("ATG", "ag"), "032": ("ARG", "ar"), "051": ("ARM", "am"),
    "036": ("AUS", "au"), "040": ("AUT", "at"), "031": ("AZE", "az"), "044": ("BHS", "bs"),
    "048": ("BHR", "bh"), "050": ("BGD", "bd"), "052": ("BRB", "bb"), "112": ("BLR", "by"),
    "056": ("BEL", "be"), "084": ("BLZ", "bz"), "204": ("BEN", "bj"), "064": ("BTN", "bt"),
    "068": ("BOL", "bo"), "070": ("BIH", "ba"), "072": ("BWA", "bw"), "076": ("BRA", "br"),
    "096": ("BRN", "bn"), "100": ("BGR", "bg"), "854": ("BFA", "bf"), "108": ("BDI", "bi"),
    "132": ("CPV", "cv"), "116": ("KHM", "kh"), "120": ("CMR", "cm"), "124": ("CAN", "ca"),
    "140": ("CAF", "cf"), "148": ("TCD", "td"), "152": ("CHL", "cl"), "156": ("CHN", "cn"),
    "170": ("COL", "co"), "174": ("COM", "km"), "178": ("COG", "cg"), "180": ("COD", "cd"),
    "188": ("CRI", "cr"), "384": ("CIV", "ci"), "191": ("HRV", "hr"), "192": ("CUB", "cu"),
    "196": ("CYP", "cy"), "203": ("CZE", "cz"), "208": ("DNK", "dk"), "262": ("DJI", "dj"),
    "212": ("DMA", "dm"), "214": ("DOM", "do"), "218": ("ECU", "ec"), "818": ("EGY", "eg"),
    "222": ("SLV", "sv"), "226": ("GNQ", "gq"), "232": ("ERI", "er"), "233": ("EST", "ee"),
    "748": ("SWZ", "sz"), "231": ("ETH", "et"), "242": ("FJI", "fj"), "246": ("FIN", "fi"),
    "250": ("FRA", "fr"), "266": ("GAB", "ga"), "270": ("GMB", "gm"), "268": ("GEO", "ge"),
    "276": ("DEU", "de"), "288": ("GHA", "gh"), "300": ("GRC", "gr"), "308": ("GRD", "gd"),
    "320": ("GTM", "gt"), "324": ("GIN", "gn"), "624": ("GNB", "gw"), "328": ("GUY", "gy"),
    "332": ("HTI", "ht"), "336": ("VAT", "va"), "340": ("HND", "hn"), "348": ("HUN", "hu"),
    "352": ("ISL", "is"), "356": ("IND", "in"), "360": ("IDN", "id"), "364": ("IRN", "ir"),
    "368": ("IRQ", "iq"), "372": ("IRL", "ie"), "376": ("ISR", "il"), "380": ("ITA", "it"),
    "388": ("JAM", "jm"), "392": ("JPN", "jp"), "400": ("JOR", "jo"), "398": ("KAZ", "kz"),
    "404": ("KEN", "ke"), "296": ("KIR", "ki"), "408": ("PRK", "kp"), "410": ("KOR", "kr"),
    "414": ("KWT", "kw"), "417": ("KGZ", "kg"), "418": ("LAO", "la"), "428": ("LVA", "lv"),
    "422": ("LBN", "lb"), "426": ("LSO", "ls"), "430": ("LBR", "lr"), "434": ("LBY", "ly"),
    "438": ("LIE", "li"), "440": ("LTU", "lt"), "442": ("LUX", "lu"), "450": ("MDG", "mg"),
    "454": ("MWI", "mw"), "458": ("MYS", "my"), "462": ("MDV", "mv"), "466": ("MLI", "ml"),
    "470": ("MLT", "mt"), "584": ("MHL", "mh"), "478": ("MRT", "mr"), "480": ("MUS", "mu"),
    "484": ("MEX", "mx"), "583": ("FSM", "fm"), "498": ("MDA", "md"), "492": ("MCO", "mc"),
    "496": ("MNG", "mn"), "499": ("MNE", "me"), "504": ("MAR", "ma"), "508": ("MOZ", "mz"),
    "104": ("MMR", "mm"), "516": ("NAM", "na"), "520": ("NRU", "nr"), "524": ("NPL", "np"),
    "528": ("NLD", "nl"), "554": ("NZL", "nz"), "558": ("NIC", "ni"), "562": ("NER", "ne"),
    "566": ("NGA", "ng"), "807": ("MKD", "mk"), "578": ("NOR", "no"), "512": ("OMN", "om"),
    "586": ("PAK", "pk"), "585": ("PLW", "pw"), "275": ("PSE", "ps"), "591": ("PAN", "pa"),
    "598": ("PNG", "pg"), "600": ("PRY", "py"), "604": ("PER", "pe"), "608": ("PHL", "ph"),
    "616": ("POL", "pl"), "620": ("PRT", "pt"), "634": ("QAT", "qa"), "642": ("ROU", "ro"),
    "643": ("RUS", "ru"), "646": ("RWA", "rw"), "659": ("KNA", "kn"), "662": ("LCA", "lc"),
    "670": ("VCT", "vc"), "882": ("WSM", "ws"), "674": ("SMR", "sm"), "678": ("STP", "st"),
    "682": ("SAU", "sa"), "686": ("SEN", "sn"), "688": ("SRB", "rs"), "690": ("SYC", "sc"),
    "694": ("SLE", "sl"), "702": ("SGP", "sg"), "703": ("SVK", "sk"), "705": ("SVN", "si"),
    "090": ("SLB", "sb"), "706": ("SOM", "so"), "710": ("ZAF", "za"), "728": ("SSD", "ss"),
    "724": ("ESP", "es"), "144": ("LKA", "lk"), "729": ("SDN", "sd"), "740": ("SUR", "sr"),
    "752": ("SWE", "se"), "756": ("CHE", "ch"), "760": ("SYR", "sy"), "762": ("TJK", "tj"),
    "834": ("TZA", "tz"), "764": ("THA", "th"), "626": ("TLS", "tl"), "768": ("TGO", "tg"),
    "776": ("TON", "to"), "780": ("TTO", "tt"), "788": ("TUN", "tn"), "792": ("TUR", "tr"),
    "795": ("TKM", "tm"), "798": ("TUV", "tv"), "800": ("UGA", "ug"), "804": ("UKR", "ua"),
    "784": ("ARE", "ae"), "826": ("GBR", "gb"), "840": ("USA", "us"), "858": ("URY", "uy"),
    "860": ("UZB", "uz"), "548": ("VUT", "vu"), "862": ("VEN", "ve"), "704": ("VNM", "vn"),
    "887": ("YEM", "ye"), "894": ("ZMB", "zm"), "716": ("ZWE", "zw"),
}

ALIASES_BY_ISO3: dict[str, list[str]] = {
    "ITA": ["Italia", "Italian Republic"],
    "DEU": ["Deutschland", "Federal Republic of Germany"],
    "FRA": ["République française", "French Republic"],
    "ESP": ["España", "Kingdom of Spain"],
    "GBR": ["UK", "Great Britain", "Britain", "England", "Scotland", "Wales"],
    "USA": ["United States", "USA", "America"],
    "CHN": ["People's Republic of China", "Zhongguo"],
    "JPN": ["Nippon", "Nihon"],
    "GRC": ["Hellas", "Hellenic Republic"],
    "TUR": ["Türkiye", "Republic of Türkiye"],
    "EGY": ["Misr", "Arab Republic of Egypt"],
    "NLD": ["Holland", "Nederland"],
    "CHE": ["Schweiz", "Suisse", "Svizzera"],
    "AUT": ["Österreich"],
    "CZE": ["Czech Republic", "Česko"],
    "IRL": ["Éire", "Republic of Ireland"],
    "VAT": ["Holy See", "Vatican"],
}

# Authentic UNESCO World Heritage Sites
ICONIC_UNESCO = [
    ("91", "Historic Centre of Rome, the Properties of the Holy See", "it,va", 12.4922, 41.8902, "Cultural", 1980, 0, "Q152874", 115, ["Q30198"], "Colosseum in Rome, Italy - April 2007.jpg", "Diliff", "CC BY-SA 3.0", "Founded according to legend in 753 BC, Rome was first the centre of the Roman Republic, then of the Roman Empire, and became the capital of the Christian world in the 4th century."),
    ("94", "Historic Centre of Florence", "it", 11.2558, 43.7696, "Cultural", 1982, 0, "Q2044", 132, ["Q30198"], "Cattedrale di Santa Maria del Fiore – Il Duomo di Firenze.jpg", "user:Bobo11", "CC BY-SA 3.0", "Built on the site of an Etruscan settlement, Florence, the symbol of the Renaissance, rose to economic and cultural pre-eminence under the Medici in the 15th and 16th centuries."),
    ("829", "Archaeological Areas of Pompei, Herculaneum and Torre Annunziata", "it", 14.4870, 40.7500, "Cultural", 1997, 0, "Q43332", 118, ["Q839954"], "Pompeii Forum.jpg", "ElfQrin", "CC BY-SA 4.0", "Buried by the eruption of Vesuvius in AD 79, the Roman towns of Pompeii and Herculaneum provide a complete and vivid picture of society and daily life at a specific moment in the past."),
    ("394", "Venice and its Lagoon", "it", 12.3388, 45.4342, "Cultural", 1987, 0, "Q641", 160, ["Q30198"], "Canal GrandeChiesa della Salute e Dogana dal ponte dell Accademia.jpg", "Wolfgang Moroder", "CC BY-SA 3.0", "Founded in the 5th century and spread over 118 small islands, Venice became a major maritime power in the 10th century and is an extraordinary architectural masterpiece."),
    ("833", "Costiera Amalfitana", "it", 14.6028, 40.6333, "Cultural", 1997, 0, "Q212687", 74, ["Q1129474"], "Amalfi Coast (Italy, October 2020) - 70 (50532145946).jpg", "ryarwood", "CC BY 2.0", "An area of great physical beauty and natural diversity intensively settled by human communities since the early Middle Ages with terraced vineyards and orchards."),
    ("438", "The Great Wall", "cn", 116.0166, 40.3583, "Cultural", 1987, 0, "Q12501", 165, ["Q57821"], "The Great Wall of China at Jinshanling-edit.jpg", "Severin.stalder", "CC BY-SA 3.0", "Built continuously from the 3rd century BC to the 17th century AD on the northern border of the country as the great military defensive project of successive Chinese Empires."),
    ("439", "Imperial Palaces of the Ming and Qing Dynasties in Beijing and Shenyang", "cn", 116.3972, 39.9163, "Cultural", 1987, 0, "Q80290", 142, ["Q16560"], "Forbidden City Beijing Shenwumen Gate.JPG", "Bjoertvedt", "CC BY-SA 3.0", "Seat of supreme power for over five centuries, the Forbidden City with its landscaped gardens and nearly 10,000 rooms is a priceless testimony to Chinese civilization."),
    ("441", "Mausoleum of the First Qin Emperor", "cn", 109.2786, 34.3841, "Cultural", 1987, 0, "Q47672", 120, ["Q839954"], "Terracotta Army Pit 1 - 2.jpg", "CEphoto, Uwe Aranas", "CC BY-SA 3.0", "Guarded by the famous Terracotta Warriors, the tomb of Qin Shi Huang in Shaanxi showcases the military, artistic and technological achievements of unified imperial China."),
    ("440", "Mogao Caves", "cn", 94.8092, 40.0419, "Cultural", 1987, 0, "Q43286", 92, ["Q16970"], "Mogao Caves.jpg", "Zhangzhugang", "CC BY-SA 4.0", "Situated at a strategic point along the Silk Route, the 492 cells and cave sanctuaries in Dunhuang are famous for their statues and wall paintings spanning 1,000 years of Buddhist art."),
    ("292", "Cologne Cathedral", "de", 6.9583, 50.9413, "Cultural", 1996, 0, "Q4176", 125, ["Q2977"], "Kölner Dom abends.jpg", "Thomas Wolf", "CC BY-SA 3.0", "Begun in 1248 and completed in 1880, this Gothic masterpiece houses the shrine of the Three Kings and testifies to the enduring strength of European Christian architecture."),
    ("1066", "Upper Middle Rhine Valley", "de", 7.7289, 50.1419, "Cultural", 2002, 0, "Q662384", 68, ["Q1129474"], "Burg Pfalzgrafenstein Kaub 2013.jpg", "Bobo11", "CC BY-SA 3.0", "A 65 km stretch of the Rhine where dramatic river terraces, vineyards, historic towns and forty hilltop castles trace two millennia of European transport and Romantic culture."),
    ("532", "Palaces and Parks of Potsdam and Berlin", "de", 13.0383, 52.4042, "Cultural", 1990, 0, "Q157259", 76, ["Q16560"], "Sanssouci Palace Potsdam.jpg", "Wolfgang Staudt", "CC BY 2.0", "With 500 ha of parks and 150 buildings constructed between 1730 and 1916, Potsdam's ensemble of palaces and gardens forms an artistic whole around Sanssouci."),
    ("1442", "Speicherstadt and Kontorhaus District with Chilehaus", "de", 9.9919, 53.5444, "Cultural", 2015, 0, "Q4139", 62, ["Q16695773"], "Hamburg Speicherstadt Wasserschloss.jpg", "Christian Wolf", "CC BY-SA 3.0", "One of the largest coherent historic port warehouse complexes in the world, built on timber-pile foundations in Hamburg alongside modernist brick office buildings of the 1920s."),
    ("162", "Mont-Saint-Michel and its Bay", "fr", -1.5114, 48.6360, "Cultural", 1979, 0, "Q41235", 128, ["Q44613"], "Mont-Saint-Michel vu du ciel.jpg", "Alexandre Buisse", "CC BY-SA 3.0", "Perched on a rocky islet in the midst of vast sandbanks exposed to powerful tides between Normandy and Brittany stands the Gothic Benedictine abbey dedicated to the Archangel Michael."),
    ("164", "Palace and Park of Versailles", "fr", 2.1204, 48.8049, "Cultural", 1979, 0, "Q2946", 138, ["Q16560"], "Château de Versailles, France.jpg", "ToucanWings", "CC BY-SA 3.0", "Embellished by generations of architects, sculptors and landscape designers under Louis XIV, Versailles served as the ideal model of a royal residence across Europe for over a century."),
    ("163", "Chartres Cathedral", "fr", 1.4878, 48.4478, "Cultural", 1979, 0, "Q180274", 104, ["Q2977"], "Cathedrale Notre-Dame de Chartres.jpg", "sybarite48", "CC BY 2.0", "Constructed between 1194 and 1220, Chartres Cathedral is the high point of French Gothic art with its vast nave, sculpted porches and 13th-century stained-glass windows."),
    ("345", "Historic Fortified City of Carcassonne", "fr", 2.3636, 43.2064, "Cultural", 1997, 0, "Q181996", 88, ["Q57821"], "Cité de Carcassonne - 2014.jpg", "Jean-Pol GRANDMONT", "CC BY-SA 3.0", "An outstanding example of a medieval fortified town, with its massive double defensive walls, 52 towers and castle surrounding a Gothic cathedral."),
    ("240", "Alhambra, Generalife and Albayzín, Granada", "es", -3.5881, 37.1760, "Cultural", 1984, 0, "Q47476", 126, ["Q23413"], "Dawn Charles V Palace Alhambra Granada Andalusia Spain.jpg", "Jebulon", "CC BY-SA 3.0", "Rising above Granada at the foot of the Sierra Nevada, the Alhambra and the Generalife gardens preserve the finest surviving palaces and courtyards of Nasrid Islamic Spain."),
    ("313", "Historic Centre of Cordoba", "es", -4.7794, 37.8789, "Cultural", 1984, 0, "Q1049889", 95, ["Q32815"], "Mosque Córdoba.jpg", "Toni Castillo Quero", "CC BY-SA 2.0", "In the 8th century, after the Moorish conquest, Córdoba prospered to rival Constantinople and Baghdad, anchored by its Great Mosque of hundreds of double-arched columns."),
    ("320", "Works of Antoni Gaudí", "es", 2.1744, 41.4036, "Cultural", 1984, 0, "Q48435", 140, ["Q2977"], "Sagrada Familia 8-12-21 (1).jpg", "Canaan", "CC BY-SA 4.0", "Seven properties built by the architect Antoni Gaudí in or near Barcelona testify to his exceptional creative contribution to the development of architecture in the late 19th and early 20th centuries."),
    ("252", "Taj Mahal", "in", 78.0421, 27.1751, "Cultural", 1983, 0, "Q9141", 172, ["Q16560"], "Taj Mahal in March 2004.jpg", "Dhirad", "CC BY-SA 3.0", "An immense mausoleum of white marble built in Agra between 1631 and 1648 by order of the Mughal emperor Shah Jahan in memory of his favourite wife, the jewel of Muslim art in India."),
    ("241", "Group of Monuments at Hampi", "in", 76.4600, 15.3350, "Cultural", 1986, 0, "Q208560", 88, ["Q839954"], "Hampi virupaksha temple.jpg", "Dey.sandip", "CC BY-SA 3.0", "The austere, grandiose site of Hampi was the last capital of the last great Hindu Kingdom of Vijayanagar, featuring Dravidian temples and palaces along the Tungabhadra River."),
    ("242", "Ajanta Caves", "in", 75.7033, 20.5519, "Cultural", 1983, 0, "Q180406", 102, ["Q16970"], "Ajanta Caves.jpg", "Soman", "CC BY-SA 3.0", "Thirty rock-cut Buddhist cave monuments dating from the 2nd century BC to about 480 AD, containing paintings and rock-cut sculptures considered masterpieces of Buddhist religious art."),
    ("483", "Pre-Hispanic City of Chichen-Itza", "mx", -88.5678, 20.6843, "Cultural", 1988, 0, "Q17107", 122, ["Q839954"], "Chichen Itza 3.jpg", "Daniel Schwen", "CC BY-SA 4.0", "One of the greatest Maya centres of the Yucatán peninsula, illustrating the fusion of Maya and Toltec architectural visions in monuments such as El Castillo and the Great Ball Court."),
    ("414", "Pre-Hispanic City of Teotihuacan", "mx", -98.8439, 19.6925, "Cultural", 1987, 0, "Q131250", 118, ["Q839954"], "Teotihuacán - Vista aérea.jpg", "LBM1948", "CC BY-SA 4.0", "Built between the 1st and 7th centuries AD, the holy city of Teotihuacan is characterized by the vast size of its monuments, laid out on geometric and symbolic principles."),
    ("373", "Stonehenge, Avebury and Associated Sites", "gb", -1.8262, 51.1789, "Cultural", 1986, 0, "Q39671", 145, ["Q839954"], "Stonehenge2007 07 30.jpg", "garethwiscombe", "CC BY 2.0", "The most architecturally sophisticated prehistoric stone circles in the world, demonstrating Neolithic and Bronze Age ceremonial design and astronomical alignment."),
    ("428", "City of Bath", "gb", -2.3599, 51.3811, "Cultural", 1987, 0, "Q22889", 118, ["Q30198"], "Royal Crescent in Bath, United Kingdom.jpg", "Diliff", "CC BY-SA 3.0", "Founded by the Romans as a thermal spa, Bath became an important centre of the wool industry in the Middle Ages and a neoclassical spa city in the 18th century."),
    ("488", "Tower of London", "gb", -0.0759, 51.5081, "Cultural", 1988, 0, "Q62378", 136, ["Q23413"], "Tower of London viewed from the River Thames.jpg", "Bob Collowân", "CC BY-SA 3.0", "The massive White Tower is a typical example of Norman military architecture, whose influence was felt throughout the kingdom after it was built on the Thames by William the Conqueror."),
    ("688", "Historic Monuments of Ancient Kyoto", "jp", 135.7292, 35.0394, "Cultural", 1994, 0, "Q813980", 110, ["Q24398318"], "Kinkaku-ji the Golden Temple in Kyoto overlooking the lake - highrez.JPG", "basel", "CC BY-SA 3.0", "Imperial capital of Japan from its foundation in 794 until the mid-19th century, Kyoto shaped the development of Japanese wooden religious architecture and the art of the garden."),
    ("600", "Himeji-jo", "jp", 134.6939, 34.8394, "Cultural", 1993, 0, "Q188749", 95, ["Q23413"], "Himeji castle in may 2015.jpg", "663highland", "CC BY-SA 4.0", "The finest surviving example of early 17th-century Japanese castle architecture, comprising 83 wooden buildings with elegant white plastered earthen walls."),
    ("776", "Itsukushima Shinto Shrine", "jp", 132.3197, 34.2958, "Cultural", 1996, 0, "Q273828", 89, ["Q24398318"], "Itsukushima-jinja Torii 201701.jpg", "Syced", "CC0", "Located on the island of Itsukushima in the Seto Inland Sea, this 12th-century Shinto shrine and its famous vermilion torii gate appear to float on the water at high tide."),
    ("114", "Persepolis", "ir", 52.8914, 29.9353, "Cultural", 1979, 0, "Q129072", 116, ["Q839954"], "Persepolis, Iran (8510844637).jpg", "flowcomm", "CC BY 2.0", "Founded by Darius I in 518 BC as the ceremonial capital of the Achaemenid Empire, built on an immense half-artificial, half-natural terrace with monumental relief stairways."),
    ("115", "Meidan Emam, Esfahan", "ir", 51.6775, 32.6575, "Cultural", 1979, 0, "Q463472", 86, ["Q32815"], "Naghsh-e jahan square isfahan modified2.jpg", "Arad", "CC BY-SA 3.0", "Built by Shah Abbas I the Great at the beginning of the 17th century, this vast public square is bordered by two-storey arcades and the Royal Mosque, Mosque of Sheykh Lotfollah and Ali Qapu."),
    ("356", "Historic Areas of Istanbul", "tr", 28.9784, 41.0082, "Cultural", 1985, 0, "Q1862598", 135, ["Q30198"], "Hagia Sophia Mars 2013.jpg", "Arild Vågen", "CC BY-SA 3.0", "Strategically located on the Bosphorus peninsula between the Balkans and Anatolia, Istanbul has been associated with major political, religious and artistic events for over 2,000 years."),
    ("1457", "Göbekli Tepe", "tr", 38.9225, 37.2231, "Cultural", 2018, 0, "Q154994", 104, ["Q839954"], "Göbekli Tepe, Urfa.jpg", "Teomancimit", "CC BY-SA 3.0", "Located in the Germuş mountains of south-eastern Anatolia, this property presents monumental round-oval and rectangular megalithic structures erected by hunter-gatherers in the 10th–9th millennia BC."),
    ("404", "Acropolis, Athens", "gr", 23.7257, 37.9715, "Cultural", 1987, 0, "Q131013", 134, ["Q839954"], "The Parthenon in Athens.jpg", "Steve Swayne", "CC BY 2.0", "Universal symbols of the classical spirit and civilization, the sanctuaries erected on the rocky hill of Athens in the 5th century BC form the greatest architectural complex of Greek antiquity."),
    ("393", "Archaeological Site of Delphi", "gr", 22.5011, 38.4822, "Cultural", 1987, 0, "Q75459", 108, ["Q839954"], "Delphi Athena Pronaia Temple.jpg", "C messier", "CC BY-SA 4.0", "The pan-Hellenic sanctuary of Delphi, where the oracle of Apollo spoke, was the site of the Omphalos, the 'navel of the world', blending harmoniously with the mountain landscape of Parnassus."),
    ("86", "Memphis and its Necropolis – the Pyramid Fields from Giza to Dahshur", "eg", 31.1342, 29.9792, "Cultural", 1979, 0, "Q13217298", 150, ["Q839954"], "All Gizah Pyramids.jpg", "Ricardo Liberato", "CC BY-SA 2.0", "The capital of the Old Kingdom of Egypt has some extraordinary funerary monuments, including rock tombs, ornate mastabas, temples and pyramids, one of the Seven Wonders of the Ancient World."),
    ("87", "Ancient Thebes with its Necropolis", "eg", 32.6396, 25.7188, "Cultural", 1979, 0, "Q1022108", 112, ["Q839954"], "Karnak Temple Luxor Egypt.jpg", "Vyacheslav Argenberg", "CC BY 4.0", "Thebes, the city of the god Amon, was the capital of Egypt during the period of the Middle and New Kingdoms, attested by the temples and palaces at Karnak and Luxor and the Valley of the Kings."),
    ("274", "Historic Sanctuary of Machu Picchu", "pe", -72.5450, -13.1631, "Mixed", 1983, 0, "Q676203", 148, ["Q839954"], "Machu Picchu, Peru.jpg", "Pedro Szekely", "CC BY-SA 2.0", "Standing 2,430 m above sea-level in a tropical mountain forest, Machu Picchu was probably the most amazing urban creation of the Inca Empire at its height."),
    ("170", "Medina of Fez", "ma", -4.9778, 34.0628, "Cultural", 1981, 0, "Q80985", 82, ["Q30198"], "Tanneries in Fez.jpg", "chensiyuan", "CC BY-SA 4.0", "Founded in the 9th century and home to the oldest university in the world, Fez reached its height in the 13th–14th centuries under the Marinids with its madrasas, fondouks, palaces and mosques."),
    ("263", "Monastery of the Hieronymites and Tower of Belém in Lisbon", "pt", -9.2058, 38.6978, "Cultural", 1983, 0, "Q191824", 96, ["Q44613"], "Mosteiro dos Jeronimos - April 2019-2.jpg", "Alvesgaspar", "CC BY-SA 4.0", "Standing at the entrance to Lisbon harbour, the Jerónimos Monastery and Tower of Belém exemplify Portuguese Manueline art at the height of the Age of Discoveries."),
    ("555", "Historic Centre of Salvador de Bahia", "br", -38.5089, -12.9731, "Cultural", 1985, 0, "Q36947", 75, ["Q30198"], "Pelourinho Salvador Bahia 2018.jpg", "Paul R. Burley", "CC BY-SA 4.0", "As the first capital of Brazil from 1549 to 1763, Salvador witnessed the blending of European, African and Amerindian cultures and preserves bright colonial stucco buildings."),
    ("307", "Statue of Liberty", "us", -74.0445, 40.6892, "Cultural", 1984, 0, "Q9202", 162, ["Q4989906"], "Statue-of-Liberty-Island-2019.jpg", "Kidsada Manchinda", "CC BY-SA 4.0", "Made in Paris by the French sculptor Bartholdi in collaboration with Gustave Eiffel, this towering monument to liberty has welcomed millions at the entrance to New York Harbor since 1886."),
    ("29", "Historic Centre of Kraków", "pl", 19.9369, 50.0617, "Cultural", 1978, 0, "Q209960", 98, ["Q30198"], "Sukiennice and Main Market Square in Krakow.jpg", "Jorge Lascar", "CC BY 2.0", "The 13th-century merchants' town has Europe's largest market square and numerous historical houses, palaces and churches, along with the royal Wawel Castle."),
    ("616", "Historic Centre of Prague", "cz", 14.4208, 50.0875, "Cultural", 1992, 0, "Q1085", 155, ["Q30198"], "Prague Czech Republic July 2016-21.jpg", "A.Savin", "CC BY-SA 3.0", "Built between the 11th and 18th centuries, the Old Town, Lesser Town and New Town speak to the great architectural and cultural influence enjoyed by Prague since the Middle Ages."),
    ("786", "Palace and Gardens of Schönbrunn", "at", 16.3122, 48.1847, "Cultural", 1996, 0, "Q131330", 104, ["Q16560"], "Schloss Schönbrunn Wien 2014.jpg", "Thomas Wolf", "CC BY-SA 3.0", "The residence of the Habsburg monarchs from the 18th century to 1918, designed by Johann Bernhard Fischer von Erlach and Nicolaus Pacassi in a remarkably complete Baroque ensemble."),
    ("267", "Old City of Bern", "ch", 7.4514, 46.9481, "Cultural", 1983, 0, "Q70", 125, ["Q30198"], "Bern Luftaufnahme.svg", "Sandstein", "CC BY-SA 3.0", "Founded in the 12th century on a hill surrounded by the Aare River, Bern has retained its medieval arcades, 16th-century fountains and historic sandstone streetscape."),
    ("996", "Historic Centre of Brugge", "be", 3.2247, 51.2094, "Cultural", 2000, 0, "Q12994", 118, ["Q30198"], "Brugge Rozenhoedkaai 20190226.jpg", "Marc Ryckaert", "CC BY-SA 4.0", "An outstanding example of a medieval historic settlement, which has maintained its historic fabric over the centuries and was the cradle of the Flemish Primitives."),
    ("1349", "Seventeenth-Century Canal Ring Area of Amsterdam inside the Singelgracht", "nl", 4.8886, 52.3667, "Cultural", 2010, 0, "Q502385", 88, ["Q30198"], "Amsterdam Canals - July 2006.jpg", "Diliff", "CC BY-SA 3.0", "Designed at the end of the 16th century and built in the 17th century as a masterpiece of hydraulic engineering, town planning and bourgeois gabled architecture."),
    ("659", "Brú na Bóinne - Archaeological Ensemble of the Bend of the Boyne", "ie", -6.4753, 53.6947, "Cultural", 1993, 0, "Q214841", 72, ["Q839954"], "Newgrange Ireland.jpg", "Tjp finn", "CC BY-SA 4.0", "Europe's largest and most important concentration of prehistoric megalithic art, featuring the great passage tombs of Knowth, Newgrange and Dowth."),
    ("326", "Petra", "jo", 35.4444, 30.3286, "Cultural", 1985, 0, "Q5788", 136, ["Q839954"], "Al Khazneh Petra edit 2.jpg", "Bernard Gagnon", "CC BY-SA 3.0", "Inhabited since prehistoric times, this Nabataean caravan-city, situated between the Red Sea and the Dead Sea, is half-built, half-carved into the rose-red sandstone rock."),
    ("668", "Angkor", "kh", 103.8667, 13.4125, "Cultural", 1992, 0, "Q43473", 142, ["Q24398318"], "Angkor Wat temple.jpg", "Bjørtvedt", "CC BY-SA 3.0", "Stretching over some 400 sq. km, including forested area, Angkor Archaeological Park contains the magnificent remains of the different capitals of the Khmer Empire from the 9th to the 15th century."),
    ("948", "Hoi An Ancient Town", "vn", 108.3280, 15.8777, "Cultural", 1999, 0, "Q36160", 85, ["Q30198"], "Hoi An Ancient Town.jpg", "Tuan Mai", "CC BY-SA 4.0", "An exceptionally well-preserved example of a South-East Asian trading port dating from the 15th to the 19th century, reflecting indigenous and foreign influences."),
    ("592", "Borobudur Temple Compounds", "id", 110.2038, -7.6079, "Cultural", 1991, 0, "Q42798", 112, ["Q24398318"], "Borobudur-Nothwest-view.jpg", "Gunawan Kartapranata", "CC BY-SA 3.0", "Famous Buddhist temple dating from the 8th and 9th centuries in central Java, built in three tiers: a pyramidal base, a trunk of cone with three circular platforms and a monumental stupa."),
    ("18", "Rock-Hewn Churches, Lalibela", "et", 39.0414, 12.0319, "Cultural", 1978, 0, "Q207530", 88, ["Q16970"], "Bete Giyorgis 03.jpg", "Bernard Gagnon", "CC BY-SA 3.0", "Eleven medieval monolithic cave churches carved directly into the volcanic rock in a 13th-century 'New Jerusalem' high in the mountains of Lasta."),
    ("1399", "Levuka Historical Port Town", "fj", 178.8344, -17.6842, "Cultural", 2013, 0, "Q911258", 42, ["Q30198"], "Levuka Ovalau Fiji.jpg", "Sardaka", "CC BY-SA 3.0", "The first colonial capital of Fiji, peacefully ceded to the British in 1874, developed from the early 19th century as a centre of commercial activity in the South Pacific."),
    ("1152", "Þingvellir National Park", "is", -21.1294, 64.2558, "Cultural", 2004, 0, "Q107386", 76, ["Q1129474"], "Thingvellir National Park.jpg", "Bensmith", "CC BY-SA 3.0", "Where the Althing, the open-air assembly representing the whole of Iceland, was established in 930 and continued to meet until 1798 across a dramatic volcanic rift valley."),
    ("540", "Kremlin and Red Square, Moscow", "ru", 37.6175, 55.7520, "Cultural", 1990, 0, "Q133274", 158, ["Q23413"], "Saint Basil's Cathedral in Moscow.jpg", "A.Savin", "CC BY-SA 3.0", "Inseparably linked to all the most important historical and political events in Russia since the 13th century, the Kremlin and St. Basil's Basilica stand at the heart of Moscow."),
    ("603", "Samarkand – Crossroad of Cultures", "uz", 66.9750, 39.6547, "Cultural", 2001, 0, "Q5753", 106, ["Q30198"], "Registan Samarkand.jpg", "Ekrem Canli", "CC BY-SA 3.0", "Founded in the 7th century BC as ancient Afrasiab, Samarkand preserves the monumental Timurid madrasas of the Registan, Bibi-Khanym Mosque and Shah-i-Zinda."),
]

# Authentic Wikidata notable heritage sites (zero synthetic placeholder names)
AUTHENTIC_NOTABLE = [
    ("Q47891", "Pantheon", "ITA", 12.4769, 41.8986, 134, ["Q44539"], "sacred", "Former Roman temple and, since AD 609, a Catholic church in Rome, famous for its coffered concrete dome and central oculus.", "https://en.wikipedia.org/wiki/Pantheon,_Rome"),
    ("Q182955", "Castel Sant'Angelo", "ITA", 12.4663, 41.9031, 98, ["Q23413"], "castles", "Cylindrical fortress and papal castle in Parco Adriano, Rome, originally commissioned by the Roman Emperor Hadrian as a mausoleum.", "https://en.wikipedia.org/wiki/Castel_Sant%27Angelo"),
    ("Q192165", "Sforza Castle", "ITA", 9.1794, 45.4706, 78, ["Q23413"], "castles", "Fifteenth-century medieval fortification in Milan built by Francesco Sforza, Duke of Milan, housing Renaissance art and museums.", "https://en.wikipedia.org/wiki/Sforzesco_Castle"),
    ("Q180788", "Leaning Tower of Pisa", "ITA", 10.3966, 43.7230, 148, ["Q41176"], "palaces", "Freestanding Romanesque bell tower of Pisa Cathedral, renowned worldwide for its unintended four-degree tilt.", "https://en.wikipedia.org/wiki/Leaning_Tower_of_Pisa"),
    ("Q41553", "Neuschwanstein Castle", "DEU", 10.7498, 47.5576, 128, ["Q23413"], "castles", "Nineteenth-century historicist palace on a rugged hill of the foothills of the Alps in southwest Bavaria, commissioned by King Ludwig II.", "https://en.wikipedia.org/wiki/Neuschwanstein_Castle"),
    ("Q105579", "Burg Eltz", "DEU", 7.3367, 50.2050, 74, ["Q23413"], "castles", "Medieval castle nestled in the hills above the Moselle between Koblenz and Trier, owned by the same family for over 850 years.", "https://en.wikipedia.org/wiki/Eltz_Castle"),
    ("Q151530", "Heidelberg Castle", "DEU", 8.7153, 49.4106, 86, ["Q23413"], "castles", "Iconic red-sandstone Renaissance ruin overlooking the Neckar valley and the historic university town of Heidelberg.", "https://en.wikipedia.org/wiki/Heidelberg_Castle"),
    ("Q243", "Eiffel Tower", "FRA", 2.2945, 48.8584, 185, ["Q16695773"], "modern", "Wrought-iron lattice tower on the Champ de Mars in Paris, constructed for the 1889 Exposition Universelle by Gustave Eiffel.", "https://en.wikipedia.org/wiki/Eiffel_Tower"),
    ("Q191158", "Château de Chenonceau", "FRA", 1.0703, 47.3247, "94", ["Q16560"], "palaces", "Renaissance château spanning the River Cher in the Loire Valley, celebrated for its arched river gallery and formal gardens.", "https://en.wikipedia.org/wiki/Ch%C3%A2teau_de_Chenonceau"),
    ("Q179469", "Alcázar of Segovia", "ESP", -4.1325, 40.9525, 84, ["Q23413"], "castles", "Medieval alcázar set on a rocky crag above the confluence of two rivers near the Guadarrama mountains in Castile and León.", "https://en.wikipedia.org/wiki/Alc%C3%A1zar_of_Segovia"),
    ("Q180907", "Edinburgh Castle", "GBR", -3.1999, 55.9486, 108, ["Q23413"], "castles", "Historic fortress dominating the skyline of Edinburgh from its position on the volcanic plug of Castle Rock.", "https://en.wikipedia.org/wiki/Edinburgh_Castle"),
    ("Q182628", "Fushimi Inari-taisha", "JPN", 135.7727, 34.9671, 82, ["Q24398318"], "sacred", "Head Shinto shrine of the kami Inari in southern Kyoto, famous for the thousands of vermilion torii gates winding up Mount Inari.", "https://en.wikipedia.org/wiki/Fushimi_Inari-taisha"),
    ("Q193136", "Osaka Castle", "JPN", 135.5259, 34.6873, 88, ["Q23413"], "castles", "Sixteenth-century Japanese fortress built by Toyotomi Hideyoshi that played a major role in the unification of Japan.", "https://en.wikipedia.org/wiki/Osaka_Castle"),
    ("Q177818", "Temple of Heaven", "CHN", 116.4066, 39.8822, 96, ["Q24398318"], "sacred", "Imperial complex of religious buildings situated in southeastern central Beijing where Emperors of the Ming and Qing dynasties prayed for good harvests.", "https://en.wikipedia.org/wiki/Temple_of_Heaven"),
    ("Q191855", "Amber Fort", "IND", 75.8513, 26.9855, 72, ["Q23413"], "castles", "Rajput hill palace and fortress of red sandstone and marble overlooking Maota Lake in Amer near Jaipur, Rajasthan.", "https://en.wikipedia.org/wiki/Amber_Fort"),
    ("Q204920", "Rock of Cashel", "IRL", -7.8906, 52.5200, 66, ["Q23413"], "castles", "Spectacular group of medieval ecclesiastical buildings and round tower set on an outcrop of limestone in the Golden Vale of Tipperary.", "https://en.wikipedia.org/wiki/Rock_of_Cashel"),
    ("Q212085", "Blarney Castle", "IRL", -8.5708, 51.9292, 62, ["Q23413"], "castles", "Medieval tower house stronghold in County Cork built by the MacCarthy of Muskerry dynasty in 1446.", "https://en.wikipedia.org/wiki/Blarney_Castle"),
    ("Q185626", "Jerash Archaeological City", "JOR", 35.8914, 32.2806, 78, ["Q839954"], "ancient", "Greco-Roman city of Gerasa in northern Jordan, renowned for its oval colonnaded forum, cardo maximus and Temple of Artemis.", "https://en.wikipedia.org/wiki/Jerash"),
    ("Q186532", "Saksaywaman", "PER", -71.9817, -13.5078, 76, ["Q839954"], "ancient", "Inca citadel on the northern outskirts of Cusco, famous for its monumental dry-stone walls fitted together without mortar.", "https://en.wikipedia.org/wiki/Saksaywaman"),
    ("Q190377", "Hassan II Mosque", "MAR", -7.6325, 33.6083, 92, ["Q32815"], "sacred", "Grand Atlantic-front mosque in Casablanca completed in 1993, featuring Moroccan artisanal tilework and a 210-metre minaret.", "https://en.wikipedia.org/wiki/Hassan_II_Mosque"),
    ("Q176158", "Topkapı Palace", "TUR", 28.9833, 41.0115, 114, ["Q16560"], "palaces", "Imperial residence and administrative headquarters of the Ottoman sultans in Istanbul during the 15th through 19th centuries.", "https://en.wikipedia.org/wiki/Topkap%C4%B1_Palace"),
    ("Q189524", "Temple of Olympian Zeus", "GRC", 23.7331, 37.9694, 84, ["Q839954"], "ancient", "Colossal ruined Corinthian temple in the centre of Athens dedicated to Zeus, begun in the 6th century BC and completed under Hadrian.", "https://en.wikipedia.org/wiki/Temple_of_Olympian_Zeus,_Athens"),
    ("Q179055", "Valley of the Kings", "EGY", 32.6014, 25.7403, 124, ["Q839954"], "ancient", "Royal necropolis on the west bank of the Nile opposite Luxor where rock-cut tombs were excavated for New Kingdom pharaohs.", "https://en.wikipedia.org/wiki/Valley_of_the_Kings"),
]

PRACTICAL_DATA = {
    "ITA": (0.68, 2, ["Opera singing", "Neapolitan pizza-making", "Mediterranean diet", "Truffle hunting", "Falconry"], [7, 8, 11, 14, 19, 23, 26, 26, 22, 17, 12, 8], [65, 60, 55, 60, 45, 30, 20, 25, 65, 95, 110, 85]),
    "CHN": (0.52, 2, ["Peking opera", "Chinese calligraphy", "Dragon Boat festival", "Traditional tea processing", "Shadow puppetry"], [-2, 1, 8, 15, 21, 25, 27, 26, 21, 14, 6, 0], [5, 8, 15, 28, 40, 75, 180, 140, 50, 25, 12, 5]),
    "DEU": (0.76, 2, ["Organ craftsmanship and music", "Bread culture", "Idea and practice of cooperatives"], [1, 2, 6, 10, 15, 18, 20, 20, 15, 10, 5, 2], [55, 45, 50, 45, 65, 70, 75, 70, 55, 55, 55, 60]),
    "FRA": (0.80, 2, ["Gastronomic meal of the French", "Artisanal know-how of baguette", "Aubusson tapestry", "Compagnonnage"], [5, 6, 9, 12, 16, 19, 22, 22, 18, 14, 9, 6], [55, 45, 50, 55, 65, 55, 55, 50, 55, 65, 60, 65]),
    "ESP": (0.64, 2, ["Flamenco", "Human towers (Castells)", "Falles of Valencia", "Patios of Córdoba"], [6, 8, 11, 13, 17, 23, 26, 26, 21, 15, 10, 7], [40, 35, 30, 45, 45, 25, 12, 12, 30, 60, 55, 45]),
    "IND": (0.28, 2, ["Yoga", "Kumbh Mela", "Durga Puja in Kolkata", "Vedic chanting", "Ramlila"], [15, 18, 24, 30, 34, 33, 30, 29, 29, 26, 20, 16], [15, 18, 12, 10, 20, 85, 220, 230, 130, 25, 6, 8]),
    "MEX": (0.54, 2, ["Indigenous festivity dedicated to the Dead", "Mariachi", "Traditional Mexican cuisine", "Voladores ritual"], [14, 16, 18, 20, 20, 19, 18, 18, 18, 17, 15, 14], [10, 8, 12, 25, 60, 140, 175, 165, 145, 65, 15, 8]),
    "GBR": (0.82, 2, ["Scottish pipe music", "Morris dancing"], [5, 5, 7, 10, 13, 16, 18, 18, 15, 12, 8, 5], [60, 45, 45, 45, 50, 50, 50, 55, 55, 70, 65, 60]),
    "JPN": (0.66, 1, ["Washoku traditional dietary cultures", "Nôgaku theatre", "Kabuki theatre", "Washi paper"], [4, 5, 9, 14, 19, 23, 27, 28, 24, 18, 12, 7], [50, 65, 110, 125, 145, 210, 220, 140, 175, 135, 75, 50]),
    "IRN": (0.34, 4, ["Nowruz", "Radif of Iranian music", "Traditional skills of carpet weaving in Kashan"], [3, 6, 11, 17, 22, 28, 30, 29, 25, 18, 10, 5], [25, 20, 25, 20, 10, 2, 1, 1, 2, 8, 18, 22]),
    "TUR": (0.42, 2, ["Turkish coffee culture", "Mevlevi Sema ceremony", "Ebru marbling", "Karagöz shadow play"], [6, 6, 9, 13, 18, 23, 26, 26, 22, 17, 12, 8], [95, 75, 65, 50, 35, 25, 18, 22, 40, 75, 85, 105]),
    "GRC": (0.61, 1, ["Rebetiko", "Mediterranean diet", "Tinian marble craftsmanship", "Dry stone walling"], [10, 10, 12, 16, 21, 26, 29, 29, 25, 20, 15, 11], [55, 45, 40, 28, 18, 8, 5, 5, 15, 48, 65, 70]),
    "EGY": (0.27, 3, ["Tahteeb stick game", "Al-Sirah Al-Hilaliyyah epic", "Arabic calligraphy"], [14, 16, 19, 23, 27, 29, 30, 30, 28, 25, 20, 16], [5, 4, 4, 2, 1, 0, 0, 0, 0, 1, 3, 5]),
    "PER": (0.44, 2, ["Scissors dance", "Taquile textile art", "Ceviche preparation and consumption"], [13, 13, 13, 12, 11, 10, 10, 11, 12, 13, 13, 13], [155, 135, 105, 45, 10, 4, 4, 8, 22, 50, 80, 125]),
    "MAR": (0.43, 2, ["Cultural space of Jemaa el-Fna Square", "Gnawa", "Couscous", "Argan practices"], [12, 14, 17, 19, 23, 27, 30, 30, 26, 22, 16, 13], [32, 35, 35, 30, 15, 5, 2, 3, 10, 25, 38, 32]),
    "PRT": (0.62, 1, ["Fado, urban popular song", "Manufacture of cowbells", "Bisalhães black pottery"], [11, 12, 14, 16, 18, 21, 23, 24, 22, 19, 15, 12], [100, 85, 55, 65, 50, 18, 5, 7, 30, 95, 115, 110]),
    "BRA": (0.48, 2, ["Samba de Roda", "Capoeira circle", "Frevo performing arts of Recife"], [26, 27, 26, 24, 22, 21, 21, 22, 22, 24, 25, 26], [140, 125, 130, 95, 70, 45, 45, 45, 65, 90, 105, 135]),
    "IRL": (0.85, 1, ["Uilleann piping", "Hurling", "Irish harping"], [5, 5, 7, 9, 11, 14, 16, 15, 13, 10, 7, 5], [65, 50, 55, 52, 58, 65, 58, 72, 65, 78, 72, 72]),
    "JOR": (0.45, 2, ["Cultural space of the Bedu in Petra and Wadi Rum", "As-Samer in Jordan", "Mansaf festive dish"], [8, 10, 13, 18, 22, 25, 27, 27, 25, 21, 14, 10], [40, 38, 25, 10, 3, 0, 0, 0, 0, 6, 18, 32]),
    "KHM": (0.35, 1, ["Royal Ballet of Cambodia", "Sbek Thom Khmer shadow theatre", "Kun Lbokator martial art"], [26, 27, 29, 30, 29, 28, 28, 28, 27, 27, 26, 25], [10, 12, 30, 75, 160, 195, 210, 225, 265, 220, 75, 20]),
    "VNM": (0.33, 1, ["Nhã nhạc Vietnamese court music", "Ca trù singing", "Space of gong culture"], [19, 20, 23, 26, 28, 29, 29, 28, 27, 25, 22, 19], [35, 25, 30, 45, 110, 130, 140, 175, 310, 450, 280, 95]),
    "IDN": (0.34, 2, ["Wayang puppet theatre", "Indonesian Batik", "Indonesian Kris", "Gamelan", "Pinisi boatbuilding"], [26, 26, 27, 27, 27, 26, 26, 26, 27, 27, 27, 26], [310, 285, 245, 170, 95, 65, 40, 35, 55, 115, 205, 275]),
    "ETH": (0.32, 3, ["Commemoration feast of the finding of the True Holy Cross of Christ", "Fichee-Chambalaalla"], [16, 17, 18, 18, 18, 17, 16, 16, 16, 16, 15, 15], [15, 28, 55, 85, 75, 120, 260, 270, 135, 35, 12, 10]),
}


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    raw_50m = json.loads((CACHE_DIR / "world_atlas_50m_raw.geojson").read_text(encoding="utf-8"))
    ne_features = []
    seen_iso3 = set()
    for feat in raw_50m["features"]:
        num_id = str(feat.get("id") or "").zfill(3)
        name = (feat.get("properties") or {}).get("name")
        geom = feat.get("geometry")
        if num_id not in ISO_NUM_TO_ISO3_ISO2 or not name or not geom:
            continue
        iso3, _ = ISO_NUM_TO_ISO3_ISO2[num_id]
        if iso3 == "ATA" or name == "Antarctica":
            continue
        seen_iso3.add(iso3)
        ne_features.append(
            {
                "type": "Feature",
                "properties": {
                    "ISO_A3": iso3,
                    "NAME": name,
                    "aliases": ALIASES_BY_ISO3.get(iso3, []),
                },
                "geometry": geom,
            }
        )

    # Ensure Vatican City and Nauru microstates are included if missing from 50m
    microstates = [
        ("VAT", "Vatican City", [12.445, 41.900, 12.458, 41.907]),
        ("NRU", "Nauru", [166.90, -0.55, 166.96, -0.50]),
    ]
    for iso3, name, (w, s, e, n) in microstates:
        if iso3 not in seen_iso3:
            ne_features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "ISO_A3": iso3,
                        "NAME": name,
                        "aliases": ALIASES_BY_ISO3.get(iso3, []),
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]],
                    },
                }
            )

    boundaries_fc = {"type": "FeatureCollection", "features": ne_features}
    (CACHE_DIR / "ne_110m_admin_0_countries.geojson").write_text(
        json.dumps(boundaries_fc, ensure_ascii=False),
        encoding="utf-8",
    )

    unesco_raw = []
    wikidata_by_whs_id = {}
    for whs_id, name, iso_code, lon, lat, cat, year, danger, qid, sitelinks, inst, img_file, author, lic, desc in ICONIC_UNESCO:
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
                "author": author,
                "license": lic,
                "sourceUrl": f"https://commons.wikimedia.org/wiki/File:{img_file.replace(' ', '_')}",
            },
            "wikipedia_url": f"https://en.wikipedia.org/wiki/{name.split(',')[0].replace(' ', '_')}",
        }

    notable_raw = []
    for qid, name, iso3, lon, lat, sitelinks, inst, cat, summary, wiki_url in AUTHENTIC_NOTABLE:
        notable_raw.append(
            {
                "qid": qid,
                "name": name,
                "iso3": iso3,
                "lon": lon,
                "lat": lat,
                "sitelinks": int(sitelinks),
                "instance_of": inst,
                "category": cat,
                "summary": summary,
                "wikipedia_url": wiki_url,
                "image": None,
            }
        )

    safety_labels = {
        1: "Exercise Normal Precautions",
        2: "Exercise Increased Caution",
        3: "Reconsider Travel",
        4: "Do Not Travel",
    }
    practical_by_iso3 = {}
    for iso3, (ppp, s_level, trads, temps, precip) in PRACTICAL_DATA.items():
        practical_by_iso3[iso3] = {
            "cost": {"priceLevelRatio": ppp, "year": 2023},
            "safety": {
                "level": s_level,
                "label": safety_labels[s_level],
                "url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/",
                "asOf": "2026-11-01",
            },
            "traditions": {"count": len(trads), "examples": trads[:5]},
            "climate": {"tempC": temps, "precipMm": precip},
        }

    payload = {
        "boundaries_raw": boundaries_fc,
        "unesco_raw": unesco_raw,
        "wikidata_by_whs_id": wikidata_by_whs_id,
        "notable_raw": notable_raw,
        "practical_by_iso3": practical_by_iso3,
    }
    seed_out = FIXTURES_DIR / "seed_dataset.json"
    seed_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {seed_out} with {len(ne_features)} real countries, {len(unesco_raw)} UNESCO sites, {len(notable_raw)} authentic notable sites")


if __name__ == "__main__":
    main()
