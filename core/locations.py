"""
Hiérarchie Zone -> Pays -> Régions/Wilayas/États utilisée par le formulaire.
"""

LOCATIONS = {
    "Afrique du Nord": {
        "Algérie": [
            "Adrar", "Chlef", "Laghouat", "Oum El Bouaghi", "Batna", "Béjaïa", "Biskra",
            "Béchar", "Blida", "Bouira", "Tamanrasset", "Tébessa", "Tlemcen", "Tiaret",
            "Tizi Ouzou", "Alger", "Djelfa", "Jijel", "Sétif", "Saïda", "Skikda",
            "Sidi Bel Abbès", "Annaba", "Guelma", "Constantine", "Médéa", "Mostaganem",
            "M'Sila", "Mascara", "Ouargla", "Oran", "El Bayadh", "Illizi",
            "Bordj Bou Arréridj", "Boumerdès", "El Tarf", "Tindouf", "Tissemsilt",
            "El Oued", "Khenchela", "Souk Ahras", "Tipaza", "Mila", "Aïn Defla",
            "Naâma", "Aïn Témouchent", "Ghardaïa", "Relizane", "Timimoun",
            "Bordj Badji Mokhtar", "Ouled Djellal", "Béni Abbès", "In Salah",
            "In Guezzam", "Touggourt", "Djanet", "El M'Ghair", "El Meniaa",
        ],
        "Maroc": [
            "Tanger-Tétouan-Al Hoceïma", "L'Oriental", "Fès-Meknès", "Rabat-Salé-Kénitra",
            "Béni Mellal-Khénifra", "Casablanca-Settat", "Marrakech-Safi",
            "Drâa-Tafilalet", "Souss-Massa", "Guelmim-Oued Noun",
            "Laâyoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab",
        ],
        "Tunisie": [
            "Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Zaghouan", "Bizerte",
            "Béja", "Jendouba", "Kef", "Siliana", "Sousse", "Monastir", "Mahdia",
            "Sfax", "Kairouan", "Kasserine", "Sidi Bouzid", "Gabès", "Médenine",
            "Tataouine", "Gafsa", "Tozeur", "Kébili",
        ],
        "Libye": [
            "Tripoli", "Benghazi", "Misrata", "Zaouïa", "Sebha", "Al Bayda",
            "Tobrouk", "Sirte", "Ghat", "Mourzouk",
        ],
        "Mauritanie": [
            "Nouakchott", "Hodh Ech Chargui", "Hodh El Gharbi", "Assaba", "Gorgol",
            "Brakna", "Trarza", "Adrar", "Dakhlet Nouadhibou", "Tagant",
            "Guidimaka", "Tiris Zemmour", "Inchiri",
        ],
        "Égypte": [
            "Le Caire", "Alexandrie", "Gizeh", "Kalyoubia", "Charqiya", "Dakahliya",
            "Beheira", "Minya", "Assiout", "Sohag", "Qena", "Assouan", "Louxor",
            "Port-Saïd", "Ismaïlia", "Suez", "Fayoum",
        ],
    },
    "Golfe Arabique": {
        "Arabie Saoudite": [
            "Riyad", "La Mecque", "Médine", "Charqiya (Est)", "Assir",
            "Tabouk", "Hail", "Al-Jawf", "Jizan", "Najran", "Al-Baha",
            "Al-Qassim", "Frontière Nord",
        ],
        "Émirats Arabes Unis": [
            "Dubaï", "Abou Dabi", "Sharjah", "Ajman", "Umm Al Quwain",
            "Ras Al Khaimah", "Fujairah",
        ],
        "Qatar": [
            "Doha", "Al Rayyan", "Al Wakrah", "Al Khor", "Umm Salal",
            "Al Daayen", "Al Shamal", "Al Shahaniya",
        ],
        "Koweït": [
            "Koweït City", "Hawalli", "Farwaniya", "Ahmadi", "Jahra", "Moubarak Al-Kabir",
        ],
        "Bahreïn": ["Capitale", "Muharraq", "Nord", "Sud"],
        "Oman": [
            "Mascate", "Dhofar", "Musandam", "Buraimi", "Dakhiliya",
            "Batinah Nord", "Batinah Sud", "Charqiya Nord", "Charqiya Sud",
            "Dhahirah", "Wusta",
        ],
    },
    "Europe": {
        "France": [
            "Île-de-France", "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur",
            "Occitanie", "Nouvelle-Aquitaine", "Grand Est", "Hauts-de-France",
            "Normandie", "Bretagne", "Pays de la Loire", "Centre-Val de Loire",
            "Bourgogne-Franche-Comté", "Corse",
        ],
        "Allemagne": [
            "Bavière", "Bade-Wurtemberg", "Rhénanie-du-Nord-Westphalie", "Hesse",
            "Saxe", "Basse-Saxe", "Berlin", "Hambourg", "Brême",
            "Rhénanie-Palatinat", "Sarre", "Schleswig-Holstein",
            "Brandebourg", "Mecklembourg-Poméranie", "Saxe-Anhalt", "Thuringe",
        ],
        "Espagne": [
            "Madrid", "Catalogne", "Andalousie", "Valence", "Pays basque",
            "Galice", "Castille-et-León", "Castille-La Manche", "Canaries",
            "Baléares", "Aragon", "Murcie", "Estrémadure", "Asturies",
            "Navarre", "Cantabrie", "La Rioja",
        ],
        "Italie": [
            "Lombardie", "Latium", "Campanie", "Sicile", "Vénétie", "Piémont",
            "Émilie-Romagne", "Pouilles", "Toscane", "Calabre", "Sardaigne",
            "Ligurie", "Marches", "Abruzzes", "Frioul-Vénétie Julienne",
            "Trentin-Haut-Adige", "Ombrie", "Basilicate", "Molise", "Val d'Aoste",
        ],
        "Royaume-Uni": [
            "Angleterre", "Écosse", "Pays de Galles", "Irlande du Nord",
            "Londres", "Manchester", "Birmingham",
        ],
        "Belgique": ["Bruxelles-Capitale", "Flandre", "Wallonie"],
        "Pays-Bas": [
            "Hollande-Septentrionale", "Hollande-Méridionale", "Utrecht",
            "Brabant-Septentrional", "Gueldre", "Limbourg", "Groningue",
            "Frise", "Overijssel", "Zélande", "Flevoland", "Drenthe",
        ],
        "Suisse": [
            "Zurich", "Genève", "Vaud", "Berne", "Bâle", "Tessin",
            "Argovie", "Neuchâtel", "Fribourg", "Valais",
        ],
        "Portugal": [
            "Lisbonne", "Porto", "Braga", "Setúbal", "Aveiro", "Faro (Algarve)",
            "Coimbra", "Leiria", "Açores", "Madère",
        ],
    },
    "USA": {
        "États-Unis": [
            "Alabama", "Alaska", "Arizona", "Arkansas", "Californie", "Caroline du Nord",
            "Caroline du Sud", "Colorado", "Connecticut", "Dakota du Nord", "Dakota du Sud",
            "Delaware", "Floride", "Géorgie", "Hawaï", "Idaho", "Illinois", "Indiana",
            "Iowa", "Kansas", "Kentucky", "Louisiane", "Maine", "Maryland",
            "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
            "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
            "New York", "Nouveau-Mexique", "Ohio", "Oklahoma", "Oregon",
            "Pennsylvanie", "Rhode Island", "Tennessee", "Texas", "Utah",
            "Vermont", "Virginie", "Virginie-Occidentale", "Washington",
            "Wisconsin", "Wyoming",
        ],
    },
    "Canada": {
        "Canada": [
            "Ontario", "Québec", "Colombie-Britannique", "Alberta", "Manitoba",
            "Saskatchewan", "Nouvelle-Écosse", "Nouveau-Brunswick",
            "Terre-Neuve-et-Labrador", "Île-du-Prince-Édouard",
            "Territoires du Nord-Ouest", "Yukon", "Nunavut",
        ],
    },
}

ZONES = list(LOCATIONS.keys())


def get_countries(zone: str):
    return list(LOCATIONS.get(zone, {}).keys())


def get_regions(zone: str, country: str):
    return LOCATIONS.get(zone, {}).get(country, [])
