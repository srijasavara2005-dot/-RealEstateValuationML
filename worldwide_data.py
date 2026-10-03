# -*- coding: utf-8 -*-
"""
Worldwide Real Estate, Location, and Currency Engine
Provides complete country-level support for 196+ internationally recognized countries:
- ISO Currency Code, Symbol, Currency Name & Plural Words Suffix
- Dynamic Multiplier relative to USD Base Price (no fixed Rs 96 conversion!)
- Local Construction Cost per sq ft and itemized components
- Multi-tier Administrative Location Hierarchy (Country -> State/Region -> City -> Locality)
- Amount Formatting (Indian numbering vs International standard)
- High-precision Number-to-Words in local currency
- Transparent ML Neighborhood feature mapping
"""

import math

# =====================================================================
# 1. CURATED REAL ESTATE MARKETS (50+ HIGH-DETAIL COUNTRIES)
# =====================================================================

CUSTOM_COUNTRY_DATA = {
    "India": {
        "currency": "₹",
        "currency_code": "INR",
        "currency_name": "Indian Rupee",
        "currency_words_suffix": "Rupees Only",
        "number_system": "indian",
        "rate_multiplier": 84.0,
        "budget_default": 3500000,
        "budget_step": 100000,
        "construction_rate_sqft": 2200,
        "cost_bedroom": 75000,
        "cost_bathroom": 100000,
        "cost_parking": 150000,
        "cost_kitchen": 100000,
        "cost_dining": 50000,
        "cost_balcony": 50000,
        "cost_floor_extra": 300,
        "opt_costs": {
            "Swimming Pool": 450000,
            "Solar Panels": 250000,
            "Lift / Elevator": 400000,
            "Home Office": 80000,
            "Terrace Garden": 120000,
            "Garden / Open Space": 90000
        },
        "admin_unit_name": "State",
        "states": {
            "Telangana": {
                "Hyderabad": [
                    "Banjara Hills", "Jubilee Hills", "Madhapur", "Gachibowli",
                    "Kukatpally", "Miyapur", "Kondapur", "Begumpet", "Hitech City",
                    "Secunderabad", "Ameerpet", "Manikonda", "Uppal", "Other"
                ],
                "Warangal": ["Hanamkonda", "Kazipet", "Subedari", "Other"],
                "Nizamabad": ["Khaleelwadi", "Bodhan Road", "Subhashnagar", "Other"],
                "Karimnagar": ["Collectorate Area", "Mukarampura", "Kothapally", "Other"],
                "Other": ["Central Area", "Suburbs", "Other"]
            },
            "Andhra Pradesh": {
                "Visakhapatnam": [
                    "Madhurawada", "MVP Colony", "Gajuwaka", "Rushikonda",
                    "Siripuram", "Seethammadhara", "Pendurthi", "Other"
                ],
                "Vijayawada": ["Benz Circle", "Moghalrajpuram", "Governorpet", "Other"],
                "Guntur": ["Brodipet", "Arundelpet", "Other"],
                "Other": ["Central Area", "Suburbs", "Other"]
            },
            "Karnataka": {
                "Bengaluru": [
                    "Indiranagar", "Koramangala", "Whitefield", "HSR Layout",
                    "Electronic City", "Jayanagar", "Hebbal", "Other"
                ],
                "Other": ["Central Area", "Suburbs", "Other"]
            },
            "Maharashtra": {
                "Mumbai": ["Bandra", "Andheri", "Juhu", "Powai", "Worli", "South Mumbai", "Other"],
                "Pune": ["Kothrud", "Baner", "Hinjewadi", "Viman Nagar", "Other"],
                "Other": ["Central Area", "Suburbs", "Other"]
            },
            "Tamil Nadu": {
                "Chennai": ["Adyar", "Anna Nagar", "T. Nagar", "Velachery", "Besant Nagar", "Other"],
                "Other": ["Central Area", "Suburbs", "Other"]
            },
            "Delhi NCR": {
                "New Delhi": ["Connaught Place", "Vasant Kunj", "Hauz Khas", "Greater Kailash", "Other"],
                "Gurugram": ["Cyber City", "Golf Course Road", "DLF Phase 5", "Sohna Road", "Other"],
                "Other": ["Central Area", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "USA": {
        "admin_unit_name": "State",
        "currency": "$",
        "currency_code": "USD",
        "currency_name": "US Dollar",
        "currency_words_suffix": "US Dollars Only",
        "number_system": "standard",
        "rate_multiplier": 1.0,
        "budget_default": 350000,
        "budget_step": 10000,
        "construction_rate_sqft": 165,
        "cost_bedroom": 5000,
        "cost_bathroom": 8000,
        "cost_parking": 12000,
        "cost_kitchen": 15000,
        "cost_dining": 4000,
        "cost_balcony": 4000,
        "cost_floor_extra": 25,
        "opt_costs": {
            "Swimming Pool": 25000,
            "Solar Panels": 12000,
            "Lift / Elevator": 20000,
            "Home Office": 4500,
            "Terrace Garden": 6000,
            "Garden / Open Space": 5000
        },
        "states": {
            "California": {
                "Los Angeles": ["Beverly Hills", "Santa Monica", "Downtown LA", "Hollywood", "Pasadena", "Other"],
                "San Francisco": ["Pacific Heights", "Mission District", "SoMa", "Sunset District", "Other"],
                "San Diego": ["La Jolla", "Gaslamp Quarter", "Pacific Beach", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "New York": {
                "New York City": ["Manhattan", "Brooklyn", "Queens", "Staten Island", "Other"],
                "Other": ["Downtown", "Suburbs", "Other"]
            },
            "Texas": {
                "Austin": ["Downtown", "South Congress", "Domain", "Zilker", "Other"],
                "Houston": ["The Heights", "Montrose", "Downtown", "Other"],
                "Dallas": ["Uptown", "Downtown", "Preston Hollow", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Florida": {
                "Miami": ["Brickell", "South Beach", "Coconut Grove", "Coral Gables", "Other"],
                "Orlando": ["Downtown", "Winter Park", "Lake Nona", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Washington": {
                "Seattle": ["Capitol Hill", "Ballard", "Downtown", "Bellevue", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Downtown", "Suburbs", "Other"]
            }
        }
    },
    "UK": {
        "admin_unit_name": "Country / Region",
        "currency": "£",
        "currency_code": "GBP",
        "currency_name": "British Pound",
        "currency_words_suffix": "British Pounds Only",
        "number_system": "standard",
        "rate_multiplier": 0.79,
        "budget_default": 280000,
        "budget_step": 10000,
        "construction_rate_sqft": 145,
        "cost_bedroom": 4500,
        "cost_bathroom": 6500,
        "cost_parking": 10000,
        "cost_kitchen": 12000,
        "cost_dining": 3500,
        "cost_balcony": 3500,
        "cost_floor_extra": 20,
        "opt_costs": {
            "Swimming Pool": 20000,
            "Solar Panels": 9500,
            "Lift / Elevator": 16000,
            "Home Office": 3500,
            "Terrace Garden": 5000,
            "Garden / Open Space": 4000
        },
        "states": {
            "England": {
                "London": ["Mayfair", "Kensington", "Westminster", "Camden", "Canary Wharf", "Greenwich", "Other"],
                "Manchester": ["City Centre", "Didsbury", "Salford Quays", "Other"],
                "Birmingham": ["City Centre", "Edgbaston", "Jewellery Quarter", "Other"],
                "Other": ["City Centre", "Suburbs", "Other"]
            },
            "Scotland": {
                "Edinburgh": ["New Town", "Old Town", "Stockbridge", "Leith", "Other"],
                "Glasgow": ["West End", "City Centre", "Merchant City", "Other"],
                "Other": ["City Centre", "Suburbs", "Other"]
            },
            "Wales": {
                "Cardiff": ["Cardiff Bay", "City Centre", "Pontcanna", "Other"],
                "Other": ["City Centre", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Canada": {
        "admin_unit_name": "Province",
        "currency": "C$",
        "currency_code": "CAD",
        "currency_name": "Canadian Dollar",
        "currency_words_suffix": "Canadian Dollars Only",
        "number_system": "standard",
        "rate_multiplier": 1.36,
        "budget_default": 475000,
        "budget_step": 15000,
        "construction_rate_sqft": 210,
        "cost_bedroom": 6800,
        "cost_bathroom": 10800,
        "cost_parking": 16000,
        "cost_kitchen": 20000,
        "cost_dining": 5400,
        "cost_balcony": 5400,
        "cost_floor_extra": 34,
        "opt_costs": {
            "Swimming Pool": 34000,
            "Solar Panels": 16000,
            "Lift / Elevator": 27000,
            "Home Office": 6000,
            "Terrace Garden": 8000,
            "Garden / Open Space": 6800
        },
        "states": {
            "Ontario": {
                "Toronto": ["Downtown", "Yorkville", "North York", "The Beaches", "Etobicoke", "Other"],
                "Ottawa": ["Centretown", "ByWard Market", "The Glebe", "Kanata", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "British Columbia": {
                "Vancouver": ["Downtown", "Kitsilano", "West End", "Yaletown", "Point Grey", "Other"],
                "Victoria": ["Downtown", "James Bay", "Oak Bay", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Quebec": {
                "Montreal": ["Downtown", "Old Montreal", "Plateau Mont-Royal", "Westmount", "Other"],
                "Quebec City": ["Old Quebec", "Sainte-Foy", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Alberta": {
                "Calgary": ["Downtown", "Beltline", "Kensington", "Other"],
                "Edmonton": ["Downtown", "Strathcona", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Downtown", "Suburbs", "Other"]
            }
        }
    },
    "Australia": {
        "admin_unit_name": "State",
        "currency": "A$",
        "currency_code": "AUD",
        "currency_name": "Australian Dollar",
        "currency_words_suffix": "Australian Dollars Only",
        "number_system": "standard",
        "rate_multiplier": 1.52,
        "budget_default": 530000,
        "budget_step": 15000,
        "construction_rate_sqft": 225,
        "cost_bedroom": 7600,
        "cost_bathroom": 12000,
        "cost_parking": 18000,
        "cost_kitchen": 22500,
        "cost_dining": 6000,
        "cost_balcony": 6000,
        "cost_floor_extra": 38,
        "opt_costs": {
            "Swimming Pool": 38000,
            "Solar Panels": 18000,
            "Lift / Elevator": 30000,
            "Home Office": 6800,
            "Terrace Garden": 9000,
            "Garden / Open Space": 7600
        },
        "states": {
            "New South Wales": {
                "Sydney": ["CBD", "Bondi", "Manly", "Surry Hills", "Paddington", "Chatswood", "Parramatta", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Victoria": {
                "Melbourne": ["CBD", "South Yarra", "St Kilda", "Fitzroy", "Docklands", "Toorak", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Queensland": {
                "Brisbane": ["CBD", "South Bank", "Fortitude Valley", "New Farm", "Other"],
                "Gold Coast": ["Surfers Paradise", "Broadbeach", "Main Beach", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Western Australia": {
                "Perth": ["CBD", "Cottesloe", "Fremantle", "Subiaco", "Other"],
                "Other": ["Metro Area", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "New Zealand": {
        "currency": "NZ$",
        "currency_code": "NZD",
        "currency_name": "New Zealand Dollar",
        "currency_words_suffix": "New Zealand Dollars Only",
        "number_system": "standard",
        "rate_multiplier": 1.64,
        "budget_default": 570000,
        "budget_step": 20000,
        "construction_rate_sqft": 240,
        "cost_bedroom": 8200,
        "cost_bathroom": 13000,
        "cost_parking": 19500,
        "cost_kitchen": 24500,
        "cost_dining": 6500,
        "cost_balcony": 6500,
        "cost_floor_extra": 41,
        "opt_costs": {
            "Swimming Pool": 41000,
            "Solar Panels": 19500,
            "Lift / Elevator": 32500,
            "Home Office": 7300,
            "Terrace Garden": 9800,
            "Garden / Open Space": 8200
        },
        "states": {
            "Auckland": {
                "Auckland": ["Central CBD", "Ponsonby", "Takapuna", "Remuera", "Devonport", "Other"]
            },
            "Wellington": {
                "Wellington": ["Te Aro", "Thorndon", "Oriental Bay", "Kelburn", "Other"]
            },
            "Canterbury": {
                "Christchurch": ["Central City", "Merivale", "Fendalton", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Germany": {
        "admin_unit_name": "Federal State",
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 320000,
        "budget_step": 10000,
        "construction_rate_sqft": 160,
        "cost_bedroom": 5000,
        "cost_bathroom": 7500,
        "cost_parking": 11000,
        "cost_kitchen": 14000,
        "cost_dining": 4000,
        "cost_balcony": 4000,
        "cost_floor_extra": 23,
        "opt_costs": {
            "Swimming Pool": 23000,
            "Solar Panels": 11000,
            "Lift / Elevator": 18500,
            "Home Office": 4200,
            "Terrace Garden": 5600,
            "Garden / Open Space": 4600
        },
        "states": {
            "Berlin": {
                "Berlin": ["Mitte", "Kreuzberg", "Charlottenburg", "Prenzlauer Berg", "Pankow", "Other"]
            },
            "Bavaria": {
                "Munich": ["Altstadt", "Schwabing", "Maxvorstadt", "Bogenhausen", "Nymphenburg", "Other"],
                "Nuremberg": ["Mitte", "Nordstadt", "Other"],
                "Other": ["Central District", "Suburbs", "Other"]
            },
            "Hamburg": {
                "Hamburg": ["Altona", "HafenCity", "Eimsbüttel", "Winterhude", "Other"]
            },
            "Hesse": {
                "Frankfurt": ["Innenstadt", "Westend", "Nordend", "Sachsenhausen", "Other"],
                "Other": ["Central District", "Suburbs", "Other"]
            },
            "North Rhine-Westphalia": {
                "Cologne": ["Altstadt", "Neustadt", "Ehrenfeld", "Other"],
                "Düsseldorf": ["Stadtmitte", "Oberkassel", "Altstadt", "Other"],
                "Other": ["Central District", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "France": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 320000,
        "budget_step": 10000,
        "construction_rate_sqft": 165,
        "cost_bedroom": 5000,
        "cost_bathroom": 7500,
        "cost_parking": 11000,
        "cost_kitchen": 14000,
        "cost_dining": 4000,
        "cost_balcony": 4000,
        "cost_floor_extra": 23,
        "opt_costs": {
            "Swimming Pool": 23000,
            "Solar Panels": 11000,
            "Lift / Elevator": 18500,
            "Home Office": 4200,
            "Terrace Garden": 5600,
            "Garden / Open Space": 4600
        },
        "states": {
            "Île-de-France": {
                "Paris": ["8th Arrondissement", "Le Marais", "Montmartre", "16th Arrondissement", "Saint-Germain", "Other"],
                "Other": ["Suburbs", "Outer Region", "Other"]
            },
            "Provence-Alpes-Côte d'Azur": {
                "Nice": ["Promenade des Anglais", "Cimiez", "Old Town", "Other"],
                "Cannes": ["La Croisette", "California", "Other"],
                "Marseille": ["Vieux-Port", "Prado", "Other"]
            },
            "Auvergne-Rhône-Alpes": {
                "Lyon": ["Presqu'île", "Vieux Lyon", "Part-Dieu", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Italy": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 310000,
        "budget_step": 10000,
        "construction_rate_sqft": 155,
        "cost_bedroom": 4800,
        "cost_bathroom": 7200,
        "cost_parking": 10500,
        "cost_kitchen": 13500,
        "cost_dining": 3800,
        "cost_balcony": 3800,
        "cost_floor_extra": 22,
        "opt_costs": {
            "Swimming Pool": 22000,
            "Solar Panels": 10500,
            "Lift / Elevator": 18000,
            "Home Office": 4000,
            "Terrace Garden": 5400,
            "Garden / Open Space": 4500
        },
        "states": {
            "Lazio": {
                "Rome": ["Centro Storico", "Trastevere", "Parioli", "Prati", "Flaminio", "Other"]
            },
            "Lombardy": {
                "Milan": ["Brera", "Navigli", "Porta Nuova", "CityLife", "Isola", "Other"]
            },
            "Tuscany": {
                "Florence": ["Duomo", "Santa Croce", "Oltrarno", "Other"]
            },
            "Veneto": {
                "Venice": ["San Marco", "Cannaregio", "Dorsoduro", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Spain": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 290000,
        "budget_step": 10000,
        "construction_rate_sqft": 140,
        "cost_bedroom": 4400,
        "cost_bathroom": 6800,
        "cost_parking": 9800,
        "cost_kitchen": 12500,
        "cost_dining": 3500,
        "cost_balcony": 3500,
        "cost_floor_extra": 20,
        "opt_costs": {
            "Swimming Pool": 20000,
            "Solar Panels": 9800,
            "Lift / Elevator": 16500,
            "Home Office": 3800,
            "Terrace Garden": 5000,
            "Garden / Open Space": 4000
        },
        "states": {
            "Madrid": {
                "Madrid": ["Salamanca", "Chamberí", "Retiro", "Centro", "Chamartín", "Other"]
            },
            "Catalonia": {
                "Barcelona": ["Eixample", "Gràcia", "Sarrià-Sant Gervasi", "Gothic Quarter", "Poblenou", "Other"]
            },
            "Andalusia": {
                "Seville": ["Santa Cruz", "Triana", "Nervión", "Other"],
                "Malaga": ["Centro Histórico", "Malagueta", "Marbella", "Other"]
            },
            "Valencia": {
                "Valencia": ["Ciutat Vella", "Eixample", "Ruzafa", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Portugal": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 270000,
        "budget_step": 10000,
        "construction_rate_sqft": 135,
        "cost_bedroom": 4200,
        "cost_bathroom": 6500,
        "cost_parking": 9500,
        "cost_kitchen": 12000,
        "cost_dining": 3400,
        "cost_balcony": 3400,
        "cost_floor_extra": 19,
        "opt_costs": {
            "Swimming Pool": 19000,
            "Solar Panels": 9500,
            "Lift / Elevator": 16000,
            "Home Office": 3600,
            "Terrace Garden": 4800,
            "Garden / Open Space": 3900
        },
        "states": {
            "Lisbon District": {
                "Lisbon": ["Chiado", "Baixa", "Alfama", "Cascais", "Estoril", "Belém", "Other"]
            },
            "Porto District": {
                "Porto": ["Foz do Douro", "Ribeira", "Boavista", "Cedofeita", "Other"]
            },
            "Algarve": {
                "Faro": ["Albufeira", "Lagos", "Vilamoura", "Portimão", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Netherlands": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 350000,
        "budget_step": 10000,
        "construction_rate_sqft": 175,
        "cost_bedroom": 5400,
        "cost_bathroom": 8200,
        "cost_parking": 12000,
        "cost_kitchen": 15000,
        "cost_dining": 4300,
        "cost_balcony": 4300,
        "cost_floor_extra": 25,
        "opt_costs": {
            "Swimming Pool": 25000,
            "Solar Panels": 12000,
            "Lift / Elevator": 20000,
            "Home Office": 4500,
            "Terrace Garden": 6000,
            "Garden / Open Space": 5000
        },
        "states": {
            "North Holland": {
                "Amsterdam": ["Centrum", "Jordaan", "Oud-Zuid", "De Pijp", "Zuidas", "Other"],
                "Haarlem": ["Centrum", "Kleverpark", "Other"]
            },
            "South Holland": {
                "Rotterdam": ["Centrum", "Kralingen", "Kop van Zuid", "Other"],
                "The Hague": ["Centrum", "Scheveningen", "Benoordenhout", "Other"]
            },
            "Utrecht": {
                "Utrecht": ["Binnenstad", "Oost", "Leidsche Rijn", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Belgium": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 330000,
        "budget_step": 10000,
        "construction_rate_sqft": 165,
        "cost_bedroom": 5100,
        "cost_bathroom": 7800,
        "cost_parking": 11500,
        "cost_kitchen": 14500,
        "cost_dining": 4100,
        "cost_balcony": 4100,
        "cost_floor_extra": 24,
        "opt_costs": {
            "Swimming Pool": 24000,
            "Solar Panels": 11500,
            "Lift / Elevator": 19000,
            "Home Office": 4300,
            "Terrace Garden": 5800,
            "Garden / Open Space": 4800
        },
        "states": {
            "Brussels Region": {
                "Brussels": ["European Quarter", "Ixelles", "Uccle", "City Centre", "Woluwe", "Other"]
            },
            "Flanders": {
                "Antwerp": ["Het Zuid", "City Centre", "Zurenborg", "Other"],
                "Ghent": ["Historic Centre", "Patershol", "Other"]
            },
            "Wallonia": {
                "Liège": ["Centre", "Guillemins", "Other"],
                "Other": ["Central District", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Switzerland": {
        "currency": "CHF",
        "currency_code": "CHF",
        "currency_name": "Swiss Franc",
        "currency_words_suffix": "Swiss Francs Only",
        "number_system": "standard",
        "rate_multiplier": 0.90,
        "budget_default": 650000,
        "budget_step": 25000,
        "construction_rate_sqft": 265,
        "cost_bedroom": 8500,
        "cost_bathroom": 13500,
        "cost_parking": 20000,
        "cost_kitchen": 26000,
        "cost_dining": 6800,
        "cost_balcony": 6800,
        "cost_floor_extra": 42,
        "opt_costs": {
            "Swimming Pool": 42000,
            "Solar Panels": 20000,
            "Lift / Elevator": 34000,
            "Home Office": 7600,
            "Terrace Garden": 10200,
            "Garden / Open Space": 8500
        },
        "states": {
            "Zurich": {
                "Zurich": ["Altstadt", "Enge", "Seefeld", "Wiedikon", "Oerlikon", "Other"]
            },
            "Geneva": {
                "Geneva": ["Cologny", "Eaux-Vives", "Champel", "Old Town", "Other"]
            },
            "Vaud": {
                "Lausanne": ["Ouchy", "Centre", "Montchoisi", "Other"],
                "Montreux": ["Lakeside", "Old Town", "Other"]
            },
            "Basel-Stadt": {
                "Basel": ["Grossbasel", "Kleinbasel", "St. Alban", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Austria": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 340000,
        "budget_step": 10000,
        "construction_rate_sqft": 165,
        "cost_bedroom": 5100,
        "cost_bathroom": 7800,
        "cost_parking": 11500,
        "cost_kitchen": 14500,
        "cost_dining": 4100,
        "cost_balcony": 4100,
        "cost_floor_extra": 24,
        "opt_costs": {
            "Swimming Pool": 24000,
            "Solar Panels": 11500,
            "Lift / Elevator": 19000,
            "Home Office": 4300,
            "Terrace Garden": 5800,
            "Garden / Open Space": 4800
        },
        "states": {
            "Vienna": {
                "Vienna": ["Innere Stadt", "Döbling", "Hietzing", "Neubau", "Leopoldstadt", "Other"]
            },
            "Salzburg": {
                "Salzburg": ["Altstadt", "Nonntal", "Aigen", "Other"]
            },
            "Tyrol": {
                "Innsbruck": ["Innenstadt", "Wilten", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Sweden": {
        "currency": "kr",
        "currency_code": "SEK",
        "currency_name": "Swedish Krona",
        "currency_words_suffix": "Swedish Kronor Only",
        "number_system": "standard",
        "rate_multiplier": 10.6,
        "budget_default": 3700000,
        "budget_step": 100000,
        "construction_rate_sqft": 1800,
        "cost_bedroom": 55000,
        "cost_bathroom": 85000,
        "cost_parking": 130000,
        "cost_kitchen": 160000,
        "cost_dining": 45000,
        "cost_balcony": 45000,
        "cost_floor_extra": 270,
        "opt_costs": {
            "Swimming Pool": 270000,
            "Solar Panels": 130000,
            "Lift / Elevator": 220000,
            "Home Office": 48000,
            "Terrace Garden": 65000,
            "Garden / Open Space": 54000
        },
        "states": {
            "Stockholm County": {
                "Stockholm": ["Östermalm", "Södermalm", "Vasastan", "Kungsholmen", "Djurgården", "Other"]
            },
            "Västra Götaland": {
                "Gothenburg": ["Centrum", "Linnéstaden", "Majorna", "Other"]
            },
            "Skåne": {
                "Malmö": ["Västra Hamnen", "Centrum", "Limhamn", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Norway": {
        "currency": "kr",
        "currency_code": "NOK",
        "currency_name": "Norwegian Krone",
        "currency_words_suffix": "Norwegian Kroner Only",
        "number_system": "standard",
        "rate_multiplier": 10.7,
        "budget_default": 3800000,
        "budget_step": 100000,
        "construction_rate_sqft": 1950,
        "cost_bedroom": 60000,
        "cost_bathroom": 92000,
        "cost_parking": 140000,
        "cost_kitchen": 175000,
        "cost_dining": 48000,
        "cost_balcony": 48000,
        "cost_floor_extra": 290,
        "opt_costs": {
            "Swimming Pool": 290000,
            "Solar Panels": 140000,
            "Lift / Elevator": 235000,
            "Home Office": 52000,
            "Terrace Garden": 70000,
            "Garden / Open Space": 58000
        },
        "states": {
            "Oslo": {
                "Oslo": ["Frogner", "Grünerløkka", "Majorstuen", "St. Hanshaugen", "Bygdøy", "Other"]
            },
            "Vestland": {
                "Bergen": ["Sentrum", "Fana", "Åsane", "Other"]
            },
            "Trøndelag": {
                "Trondheim": ["Midtbyen", "Østbyen", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Denmark": {
        "currency": "kr",
        "currency_code": "DKK",
        "currency_name": "Danish Krone",
        "currency_words_suffix": "Danish Kroner Only",
        "number_system": "standard",
        "rate_multiplier": 6.9,
        "budget_default": 2400000,
        "budget_step": 50000,
        "construction_rate_sqft": 1300,
        "cost_bedroom": 38000,
        "cost_bathroom": 60000,
        "cost_parking": 90000,
        "cost_kitchen": 115000,
        "cost_dining": 31000,
        "cost_balcony": 31000,
        "cost_floor_extra": 190,
        "opt_costs": {
            "Swimming Pool": 190000,
            "Solar Panels": 90000,
            "Lift / Elevator": 150000,
            "Home Office": 34000,
            "Terrace Garden": 46000,
            "Garden / Open Space": 38000
        },
        "states": {
            "Capital Region": {
                "Copenhagen": ["Indre By", "Frederiksberg", "Østerbro", "Vesterbro", "Nørrebro", "Other"]
            },
            "Central Denmark": {
                "Aarhus": ["Midtbyen", "Trøjborg", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Finland": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 330000,
        "budget_step": 10000,
        "construction_rate_sqft": 170,
        "cost_bedroom": 5200,
        "cost_bathroom": 8000,
        "cost_parking": 11800,
        "cost_kitchen": 14800,
        "cost_dining": 4200,
        "cost_balcony": 4200,
        "cost_floor_extra": 25,
        "opt_costs": {
            "Swimming Pool": 25000,
            "Solar Panels": 11800,
            "Lift / Elevator": 19500,
            "Home Office": 4400,
            "Terrace Garden": 5900,
            "Garden / Open Space": 4900
        },
        "states": {
            "Uusimaa": {
                "Helsinki": ["Kallio", "Töölö", "Ullanlinna", "Kamppi", "Eira", "Other"],
                "Espoo": ["Tapiola", "Otaniemi", "Other"]
            },
            "Pirkanmaa": {
                "Tampere": ["Keskusta", "Pyynikki", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Ireland": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 360000,
        "budget_step": 10000,
        "construction_rate_sqft": 175,
        "cost_bedroom": 5400,
        "cost_bathroom": 8200,
        "cost_parking": 12000,
        "cost_kitchen": 15200,
        "cost_dining": 4300,
        "cost_balcony": 4300,
        "cost_floor_extra": 25,
        "opt_costs": {
            "Swimming Pool": 25000,
            "Solar Panels": 12000,
            "Lift / Elevator": 20000,
            "Home Office": 4500,
            "Terrace Garden": 6000,
            "Garden / Open Space": 5000
        },
        "states": {
            "Leinster": {
                "Dublin": ["Ballsbridge", "Ranelagh", "City Centre", "Clontarf", "Dún Laoghaire", "Other"]
            },
            "Munster": {
                "Cork": ["City Centre", "Blackrock", "Montenotte", "Other"]
            },
            "Connacht": {
                "Galway": ["City Centre", "Salthill", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Poland": {
        "currency": "zł",
        "currency_code": "PLN",
        "currency_name": "Polish Zloty",
        "currency_words_suffix": "Polish Zlotys Only",
        "number_system": "standard",
        "rate_multiplier": 4.0,
        "budget_default": 1400000,
        "budget_step": 50000,
        "construction_rate_sqft": 580,
        "cost_bedroom": 18000,
        "cost_bathroom": 28000,
        "cost_parking": 42000,
        "cost_kitchen": 52000,
        "cost_dining": 14000,
        "cost_balcony": 14000,
        "cost_floor_extra": 88,
        "opt_costs": {
            "Swimming Pool": 88000,
            "Solar Panels": 42000,
            "Lift / Elevator": 70000,
            "Home Office": 16000,
            "Terrace Garden": 21000,
            "Garden / Open Space": 17500
        },
        "states": {
            "Masovian": {
                "Warsaw": ["Śródmieście", "Mokotów", "Wilanów", "Żoliborz", "Praga", "Other"]
            },
            "Lesser Poland": {
                "Kraków": ["Stare Miasto", "Kazimierz", "Podgórze", "Krowodrza", "Other"]
            },
            "Lower Silesia": {
                "Wrocław": ["Stare Miasto", "Krzyki", "Fabryczna", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Russia": {
        "currency": "₽",
        "currency_code": "RUB",
        "currency_name": "Russian Ruble",
        "currency_words_suffix": "Russian Rubles Only",
        "number_system": "standard",
        "rate_multiplier": 92.0,
        "budget_default": 32000000,
        "budget_step": 1000000,
        "construction_rate_sqft": 13500,
        "cost_bedroom": 420000,
        "cost_bathroom": 650000,
        "cost_parking": 980000,
        "cost_kitchen": 1250000,
        "cost_dining": 340000,
        "cost_balcony": 340000,
        "cost_floor_extra": 2100,
        "opt_costs": {
            "Swimming Pool": 2100000,
            "Solar Panels": 980000,
            "Lift / Elevator": 1650000,
            "Home Office": 380000,
            "Terrace Garden": 500000,
            "Garden / Open Space": 410000
        },
        "states": {
            "Moscow Federal City": {
                "Moscow": ["Arbat", "Tverskoy", "Khamovniki", "Presnensky", "Dorogomilovo", "Other"]
            },
            "Saint Petersburg": {
                "Saint Petersburg": ["Central District", "Petrogradsky", "Vasileostrovsky", "Other"]
            },
            "Novosibirsk Oblast": {
                "Novosibirsk": ["Tsentralny", "Zheleznodorozhny", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Ukraine": {
        "currency": "₴",
        "currency_code": "UAH",
        "currency_name": "Ukrainian Hryvnia",
        "currency_words_suffix": "Ukrainian Hryvnias Only",
        "number_system": "standard",
        "rate_multiplier": 41.0,
        "budget_default": 14000000,
        "budget_step": 500000,
        "construction_rate_sqft": 5800,
        "cost_bedroom": 180000,
        "cost_bathroom": 280000,
        "cost_parking": 420000,
        "cost_kitchen": 520000,
        "cost_dining": 140000,
        "cost_balcony": 140000,
        "cost_floor_extra": 900,
        "opt_costs": {
            "Swimming Pool": 900000,
            "Solar Panels": 420000,
            "Lift / Elevator": 720000,
            "Home Office": 160000,
            "Terrace Garden": 220000,
            "Garden / Open Space": 180000
        },
        "states": {
            "Kyiv": {
                "Kyiv": ["Pechersk", "Podil", "Shevchenkivskyi", "Obolon", "Holosiiv", "Other"]
            },
            "Lviv Oblast": {
                "Lviv": ["Halytskyi", "Frankivskyi", "Lychakivskyi", "Other"]
            },
            "Odesa Oblast": {
                "Odesa": ["Prymorskyi", "Tairova", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "China": {
        "currency": "¥",
        "currency_code": "CNY",
        "currency_name": "Chinese Yuan",
        "currency_words_suffix": "Chinese Yuan Only",
        "number_system": "standard",
        "rate_multiplier": 7.23,
        "budget_default": 2500000,
        "budget_step": 50000,
        "construction_rate_sqft": 1150,
        "cost_bedroom": 35000,
        "cost_bathroom": 55000,
        "cost_parking": 85000,
        "cost_kitchen": 105000,
        "cost_dining": 28000,
        "cost_balcony": 28000,
        "cost_floor_extra": 180,
        "opt_costs": {
            "Swimming Pool": 180000,
            "Solar Panels": 85000,
            "Lift / Elevator": 140000,
            "Home Office": 32000,
            "Terrace Garden": 43000,
            "Garden / Open Space": 36000
        },
        "states": {
            "Beijing": {
                "Beijing": ["Chaoyang", "Haidian", "Dongcheng", "Xicheng", "Other"]
            },
            "Shanghai": {
                "Shanghai": ["Pudong", "Jing'an", "Xuhui", "Huangpu", "Minhang", "Other"]
            },
            "Guangdong": {
                "Shenzhen": ["Nanshan", "Futian", "Luohu", "Bao'an", "Other"],
                "Guangzhou": ["Tianhe", "Yuexiu", "Haizhu", "Other"]
            },
            "Zhejiang": {
                "Hangzhou": ["Xihu", "Gongshu", "Binjiang", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Japan": {
        "admin_unit_name": "Prefecture",
        "currency": "¥",
        "currency_code": "JPY",
        "currency_name": "Japanese Yen",
        "currency_words_suffix": "Japanese Yen Only",
        "number_system": "standard",
        "rate_multiplier": 152.0,
        "budget_default": 53000000,
        "budget_step": 1000000,
        "construction_rate_sqft": 28500,
        "cost_bedroom": 850000,
        "cost_bathroom": 1350000,
        "cost_parking": 2000000,
        "cost_kitchen": 2500000,
        "cost_dining": 680000,
        "cost_balcony": 680000,
        "cost_floor_extra": 4200,
        "opt_costs": {
            "Swimming Pool": 4200000,
            "Solar Panels": 2000000,
            "Lift / Elevator": 3400000,
            "Home Office": 760000,
            "Terrace Garden": 1000000,
            "Garden / Open Space": 850000
        },
        "states": {
            "Tokyo Prefecture": {
                "Tokyo": ["Minato", "Shibuya", "Shinjuku", "Ginza", "Roppongi", "Meguro", "Setagaya", "Other"]
            },
            "Osaka Prefecture": {
                "Osaka": ["Kita / Umeda", "Chuo / Namba", "Tennoji", "Other"]
            },
            "Kyoto Prefecture": {
                "Kyoto": ["Gion", "Nakagyo", "Shimogyo", "Higashiyama", "Other"]
            },
            "Kanagawa": {
                "Yokohama": ["Minato Mirai", "Naka", "Aoba", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "South Korea": {
        "currency": "₩",
        "currency_code": "KRW",
        "currency_name": "South Korean Won",
        "currency_words_suffix": "South Korean Won Only",
        "number_system": "standard",
        "rate_multiplier": 1350.0,
        "budget_default": 470000000,
        "budget_step": 10000000,
        "construction_rate_sqft": 245000,
        "cost_bedroom": 7500000,
        "cost_bathroom": 12000000,
        "cost_parking": 18000000,
        "cost_kitchen": 22000000,
        "cost_dining": 6000000,
        "cost_balcony": 6000000,
        "cost_floor_extra": 38000,
        "opt_costs": {
            "Swimming Pool": 38000000,
            "Solar Panels": 18000000,
            "Lift / Elevator": 30000000,
            "Home Office": 6800000,
            "Terrace Garden": 9000000,
            "Garden / Open Space": 7500000
        },
        "states": {
            "Seoul Special City": {
                "Seoul": ["Gangnam", "Seocho", "Yongsan / Itaewon", "Songpa", "Mapo", "Jongno", "Other"]
            },
            "Gyeonggi Province": {
                "Pangyo": ["Techno Valley", "Baekhyeon", "Other"],
                "Bundang": ["Jeongja", "Sunae", "Other"],
                "Other": ["Suburbs", "Other"]
            },
            "Busan": {
                "Busan": ["Haeundae", "Marine City", "Suyeong", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Singapore": {
        "currency": "S$",
        "currency_code": "SGD",
        "currency_name": "Singapore Dollar",
        "currency_words_suffix": "Singapore Dollars Only",
        "number_system": "standard",
        "rate_multiplier": 1.35,
        "budget_default": 470000,
        "budget_step": 15000,
        "construction_rate_sqft": 250,
        "cost_bedroom": 7500,
        "cost_bathroom": 11800,
        "cost_parking": 17500,
        "cost_kitchen": 22000,
        "cost_dining": 5800,
        "cost_balcony": 5800,
        "cost_floor_extra": 37,
        "opt_costs": {
            "Swimming Pool": 37000,
            "Solar Panels": 17500,
            "Lift / Elevator": 29000,
            "Home Office": 6600,
            "Terrace Garden": 8800,
            "Garden / Open Space": 7400
        },
        "states": {
            "Central Region": {
                "Singapore": ["Orchard", "Marina Bay", "Tanjong Pagar", "Bukit Timah", "Novena", "River Valley", "Other"]
            },
            "East Region": {
                "Singapore East": ["Marine Parade", "Tampines", "Bedok", "Katong", "Other"]
            },
            "West Region": {
                "Singapore West": ["Jurong East", "Clementi", "Buona Vista", "Other"]
            },
            "Other": {
                "Other Area": ["Central", "Suburbs", "Other"]
            }
        }
    },
    "Malaysia": {
        "currency": "RM",
        "currency_code": "MYR",
        "currency_name": "Malaysian Ringgit",
        "currency_words_suffix": "Malaysian Ringgit Only",
        "number_system": "standard",
        "rate_multiplier": 4.75,
        "budget_default": 1650000,
        "budget_step": 50000,
        "construction_rate_sqft": 680,
        "cost_bedroom": 22000,
        "cost_bathroom": 35000,
        "cost_parking": 52000,
        "cost_kitchen": 65000,
        "cost_dining": 17500,
        "cost_balcony": 17500,
        "cost_floor_extra": 110,
        "opt_costs": {
            "Swimming Pool": 110000,
            "Solar Panels": 52000,
            "Lift / Elevator": 88000,
            "Home Office": 20000,
            "Terrace Garden": 26000,
            "Garden / Open Space": 22000
        },
        "states": {
            "Federal Territory": {
                "Kuala Lumpur": ["KLCC", "Bangsar", "Mont Kiara", "Bukit Bintang", "Damansara Heights", "Other"]
            },
            "Selangor": {
                "Petaling Jaya": ["Bandar Utama", "Damansara Utama", "SS2", "Other"],
                "Subang Jaya": ["SS15", "USJ", "Other"]
            },
            "Penang": {
                "George Town": ["Gurney Drive", "Tanjung Tokong", "Batu Ferringhi", "Other"]
            },
            "Johor": {
                "Johor Bahru": ["Medini / Iskandar", "Danga Bay", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Thailand": {
        "currency": "฿",
        "currency_code": "THB",
        "currency_name": "Thai Baht",
        "currency_words_suffix": "Thai Baht Only",
        "number_system": "standard",
        "rate_multiplier": 36.8,
        "budget_default": 12800000,
        "budget_step": 500000,
        "construction_rate_sqft": 4800,
        "cost_bedroom": 160000,
        "cost_bathroom": 260000,
        "cost_parking": 390000,
        "cost_kitchen": 490000,
        "cost_dining": 130000,
        "cost_balcony": 130000,
        "cost_floor_extra": 820,
        "opt_costs": {
            "Swimming Pool": 820000,
            "Solar Panels": 390000,
            "Lift / Elevator": 660000,
            "Home Office": 150000,
            "Terrace Garden": 198000,
            "Garden / Open Space": 165000
        },
        "states": {
            "Bangkok": {
                "Bangkok": ["Sukhumvit", "Silom", "Sathorn", "Thonglor", "Ekkamai", "Ari", "Other"]
            },
            "Phuket": {
                "Phuket": ["Bang Tao", "Patong", "Surin", "Kata", "Other"]
            },
            "Chiang Mai": {
                "Chiang Mai": ["Nimman", "Old City", "Hang Dong", "Other"]
            },
            "Chonburi": {
                "Pattaya": ["Wongamat", "Jomtien", "Central", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Indonesia": {
        "currency": "Rp",
        "currency_code": "IDR",
        "currency_name": "Indonesian Rupiah",
        "currency_words_suffix": "Indonesian Rupiah Only",
        "number_system": "standard",
        "rate_multiplier": 16000.0,
        "budget_default": 5500000000,
        "budget_step": 100000000,
        "construction_rate_sqft": 2400000,
        "cost_bedroom": 75000000,
        "cost_bathroom": 120000000,
        "cost_parking": 180000000,
        "cost_kitchen": 225000000,
        "cost_dining": 60000000,
        "cost_balcony": 60000000,
        "cost_floor_extra": 380000,
        "opt_costs": {
            "Swimming Pool": 380000000,
            "Solar Panels": 180000000,
            "Lift / Elevator": 300000000,
            "Home Office": 68000000,
            "Terrace Garden": 90000000,
            "Garden / Open Space": 75000000
        },
        "states": {
            "Special Capital Region": {
                "Jakarta": ["Menteng", "Kebayoran Baru", "SCBD", "Kuningan", "Pondok Indah", "PIK", "Other"]
            },
            "Bali": {
                "Denpasar / Badung": ["Seminyak", "Canggu", "Ubud", "Sanur", "Uluwatu", "Other"]
            },
            "East Java": {
                "Surabaya": ["Tegalsari", "Gubeng", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Philippines": {
        "currency": "₱",
        "currency_code": "PHP",
        "currency_name": "Philippine Peso",
        "currency_words_suffix": "Philippine Pesos Only",
        "number_system": "standard",
        "rate_multiplier": 58.0,
        "budget_default": 20000000,
        "budget_step": 500000,
        "construction_rate_sqft": 8500,
        "cost_bedroom": 260000,
        "cost_bathroom": 420000,
        "cost_parking": 640000,
        "cost_kitchen": 800000,
        "cost_dining": 210000,
        "cost_balcony": 210000,
        "cost_floor_extra": 1350,
        "opt_costs": {
            "Swimming Pool": 1350000,
            "Solar Panels": 640000,
            "Lift / Elevator": 1080000,
            "Home Office": 240000,
            "Terrace Garden": 320000,
            "Garden / Open Space": 270000
        },
        "states": {
            "National Capital Region": {
                "Metro Manila": ["Makati (Bel-Air / San Lorenzo)", "Bonifacio Global City (BGC)", "Ortigas Center", "Quezon City", "Alabang", "Other"]
            },
            "Central Visayas": {
                "Cebu City": ["Cebu IT Park", "Cebu Business Park", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Vietnam": {
        "currency": "₫",
        "currency_code": "VND",
        "currency_name": "Vietnamese Dong",
        "currency_words_suffix": "Vietnamese Dong Only",
        "number_system": "standard",
        "rate_multiplier": 25400.0,
        "budget_default": 8800000000,
        "budget_step": 200000000,
        "construction_rate_sqft": 3600000,
        "cost_bedroom": 115000000,
        "cost_bathroom": 185000000,
        "cost_parking": 280000000,
        "cost_kitchen": 350000000,
        "cost_dining": 92000000,
        "cost_balcony": 92000000,
        "cost_floor_extra": 580000,
        "opt_costs": {
            "Swimming Pool": 580000000,
            "Solar Panels": 280000000,
            "Lift / Elevator": 460000000,
            "Home Office": 105000000,
            "Terrace Garden": 140000000,
            "Garden / Open Space": 115000000
        },
        "states": {
            "Ho Chi Minh City": {
                "Ho Chi Minh City": ["District 1", "District 2 (Thao Dien)", "District 7 (Phu My Hung)", "Binh Thanh", "Other"]
            },
            "Hanoi": {
                "Hanoi": ["Tay Ho", "Hoan Kiem", "Ba Dinh", "Cau Giay", "Other"]
            },
            "Da Nang": {
                "Da Nang": ["Hai Chau", "Son Tra", "Ngu Hanh Son", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "UAE": {
        "admin_unit_name": "Emirate",
        "currency": "د.إ",
        "currency_code": "AED",
        "currency_name": "UAE Dirham",
        "currency_words_suffix": "UAE Dirhams Only",
        "number_system": "standard",
        "rate_multiplier": 3.67,
        "budget_default": 1300000,
        "budget_step": 50000,
        "construction_rate_sqft": 450,
        "cost_bedroom": 16000,
        "cost_bathroom": 26000,
        "cost_parking": 39000,
        "cost_kitchen": 49000,
        "cost_dining": 13000,
        "cost_balcony": 13000,
        "cost_floor_extra": 80,
        "opt_costs": {
            "Swimming Pool": 80000,
            "Solar Panels": 39000,
            "Lift / Elevator": 65000,
            "Home Office": 15000,
            "Terrace Garden": 20000,
            "Garden / Open Space": 16500
        },
        "states": {
            "Dubai": {
                "Dubai": [
                    "Downtown Dubai", "Palm Jumeirah", "Dubai Marina", "Business Bay",
                    "Arabian Ranches", "Dubai Hills Estate", "Jumeirah", "Emirates Hills", "Other"
                ]
            },
            "Abu Dhabi": {
                "Abu Dhabi": ["Corniche", "Al Reem Island", "Yas Island", "Saadiyat Island", "Al Raha", "Other"]
            },
            "Sharjah": {
                "Sharjah": ["Al Majaz", "Al Nahda", "Muwaileh", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Saudi Arabia": {
        "admin_unit_name": "Province",
        "currency": "ر.س",
        "currency_code": "SAR",
        "currency_name": "Saudi Riyal",
        "currency_words_suffix": "Saudi Riyals Only",
        "number_system": "standard",
        "rate_multiplier": 3.75,
        "budget_default": 1350000,
        "budget_step": 50000,
        "construction_rate_sqft": 480,
        "cost_bedroom": 17000,
        "cost_bathroom": 27000,
        "cost_parking": 41000,
        "cost_kitchen": 52000,
        "cost_dining": 14000,
        "cost_balcony": 14000,
        "cost_floor_extra": 85,
        "opt_costs": {
            "Swimming Pool": 85000,
            "Solar Panels": 41000,
            "Lift / Elevator": 68000,
            "Home Office": 16000,
            "Terrace Garden": 21000,
            "Garden / Open Space": 17500
        },
        "states": {
            "Riyadh Province": {
                "Riyadh": ["Al Olaya", "Al Malqa", "Al Nakheel", "Hittin", "Al Yasmin", "Al Sahafa", "Other"]
            },
            "Makkah Province": {
                "Jeddah": ["Al Corniche", "Al Rawdah", "Al Shati", "Al Mohammadiyyah", "Al Zahra", "Other"]
            },
            "Eastern Province": {
                "Al Khobar": ["Corniche", "Al Hada", "Other"],
                "Dammam": ["Al Faisaliyah", "Al Shati", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Qatar": {
        "currency": "ر.ق",
        "currency_code": "QAR",
        "currency_name": "Qatari Riyal",
        "currency_words_suffix": "Qatari Riyals Only",
        "number_system": "standard",
        "rate_multiplier": 3.64,
        "budget_default": 1300000,
        "budget_step": 50000,
        "construction_rate_sqft": 470,
        "cost_bedroom": 16500,
        "cost_bathroom": 26500,
        "cost_parking": 40000,
        "cost_kitchen": 50000,
        "cost_dining": 13500,
        "cost_balcony": 13500,
        "cost_floor_extra": 82,
        "opt_costs": {
            "Swimming Pool": 82000,
            "Solar Panels": 40000,
            "Lift / Elevator": 66000,
            "Home Office": 15000,
            "Terrace Garden": 20000,
            "Garden / Open Space": 16800
        },
        "states": {
            "Doha": {
                "Doha": ["The Pearl-Qatar", "West Bay", "Lusail City", "Al Sadd", "Al Dafna", "Other"]
            },
            "Al Rayyan": {
                "Al Rayyan": ["Education City", "Al Waab", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Kuwait": {
        "currency": "د.ك",
        "currency_code": "KWD",
        "currency_name": "Kuwaiti Dinar",
        "currency_words_suffix": "Kuwaiti Dinars Only",
        "number_system": "standard",
        "rate_multiplier": 0.31,
        "budget_default": 110000,
        "budget_step": 5000,
        "construction_rate_sqft": 45,
        "cost_bedroom": 1500,
        "cost_bathroom": 2400,
        "cost_parking": 3700,
        "cost_kitchen": 4600,
        "cost_dining": 1200,
        "cost_balcony": 1200,
        "cost_floor_extra": 7,
        "opt_costs": {
            "Swimming Pool": 7700,
            "Solar Panels": 3700,
            "Lift / Elevator": 6200,
            "Home Office": 1400,
            "Terrace Garden": 1900,
            "Garden / Open Space": 1550
        },
        "states": {
            "Capital Governorate": {
                "Kuwait City": ["Sharq", "Dasman", "Mirgab", "Shuwaikh", "Other"]
            },
            "Hawalli Governorate": {
                "Salmiya": ["Arabian Gulf St", "Block 10", "Other"],
                "Hawalli": ["City Centre", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Oman": {
        "currency": "ر.ع.",
        "currency_code": "OMR",
        "currency_name": "Omani Rial",
        "currency_words_suffix": "Omani Rials Only",
        "number_system": "standard",
        "rate_multiplier": 0.38,
        "budget_default": 135000,
        "budget_step": 5000,
        "construction_rate_sqft": 55,
        "cost_bedroom": 1800,
        "cost_bathroom": 3000,
        "cost_parking": 4500,
        "cost_kitchen": 5700,
        "cost_dining": 1500,
        "cost_balcony": 1500,
        "cost_floor_extra": 9,
        "opt_costs": {
            "Swimming Pool": 9500,
            "Solar Panels": 4500,
            "Lift / Elevator": 7600,
            "Home Office": 1700,
            "Terrace Garden": 2300,
            "Garden / Open Space": 1900
        },
        "states": {
            "Muscat Governorate": {
                "Muscat": ["Al Mouj", "Shatti Al Qurum", "Qurum", "Madinat Sultan Qaboos", "Muttrah", "Other"]
            },
            "Dhofar Governorate": {
                "Salalah": ["Hawana Salalah", "Al Haffa", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Israel": {
        "currency": "₪",
        "currency_code": "ILS",
        "currency_name": "Israeli Shekel",
        "currency_words_suffix": "Israeli Shekels Only",
        "number_system": "standard",
        "rate_multiplier": 3.72,
        "budget_default": 1300000,
        "budget_step": 50000,
        "construction_rate_sqft": 620,
        "cost_bedroom": 19000,
        "cost_bathroom": 30000,
        "cost_parking": 45000,
        "cost_kitchen": 58000,
        "cost_dining": 15000,
        "cost_balcony": 15000,
        "cost_floor_extra": 95,
        "opt_costs": {
            "Swimming Pool": 95000,
            "Solar Panels": 45000,
            "Lift / Elevator": 76000,
            "Home Office": 17000,
            "Terrace Garden": 23000,
            "Garden / Open Space": 19000
        },
        "states": {
            "Tel Aviv District": {
                "Tel Aviv": ["Neve Tzedek", "Rothschild", "Old North", "Florentin", "Ramat Aviv", "Other"],
                "Herzliya": ["Herzliya Pituach", "Centre", "Other"]
            },
            "Jerusalem District": {
                "Jerusalem": ["Rehavia", "German Colony", "Yemin Moshe", "Talbiya", "Other"]
            },
            "Haifa District": {
                "Haifa": ["Carmel", "German Colony", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Turkey": {
        "currency": "₺",
        "currency_code": "TRY",
        "currency_name": "Turkish Lira",
        "currency_words_suffix": "Turkish Liras Only",
        "number_system": "standard",
        "rate_multiplier": 32.5,
        "budget_default": 11500000,
        "budget_step": 500000,
        "construction_rate_sqft": 4500,
        "cost_bedroom": 150000,
        "cost_bathroom": 240000,
        "cost_parking": 360000,
        "cost_kitchen": 460000,
        "cost_dining": 120000,
        "cost_balcony": 120000,
        "cost_floor_extra": 750,
        "opt_costs": {
            "Swimming Pool": 750000,
            "Solar Panels": 360000,
            "Lift / Elevator": 620000,
            "Home Office": 140000,
            "Terrace Garden": 190000,
            "Garden / Open Space": 155000
        },
        "states": {
            "Istanbul": {
                "Istanbul": ["Beşiktaş", "Kadıköy", "Şişli", "Sarıyer", "Bebek", "Nişantaşı", "Beyoğlu", "Other"]
            },
            "Ankara": {
                "Ankara": ["Çankaya", "Gaziosmanpaşa", "Kavaklıdere", "Other"]
            },
            "Izmir": {
                "Izmir": ["Konak", "Alsancak", "Karşıyaka", "Çeşme", "Other"]
            },
            "Antalya": {
                "Antalya": ["Lara", "Konyaaltı", "Muratpaşa", "Alanya", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "South Africa": {
        "currency": "R",
        "currency_code": "ZAR",
        "currency_name": "South African Rand",
        "currency_words_suffix": "South African Rand Only",
        "number_system": "standard",
        "rate_multiplier": 18.5,
        "budget_default": 6500000,
        "budget_step": 200000,
        "construction_rate_sqft": 2500,
        "cost_bedroom": 85000,
        "cost_bathroom": 135000,
        "cost_parking": 205000,
        "cost_kitchen": 260000,
        "cost_dining": 68000,
        "cost_balcony": 68000,
        "cost_floor_extra": 420,
        "opt_costs": {
            "Swimming Pool": 420000,
            "Solar Panels": 205000,
            "Lift / Elevator": 345000,
            "Home Office": 78000,
            "Terrace Garden": 105000,
            "Garden / Open Space": 86000
        },
        "states": {
            "Gauteng": {
                "Johannesburg": ["Sandton", "Rosebank", "Hyde Park", "Bryanston", "Houghton", "Other"],
                "Pretoria": ["Waterkloof", "Brooklyn", "Other"]
            },
            "Western Cape": {
                "Cape Town": ["Camps Bay", "Clifton", "V&A Waterfront", "Constantia", "Sea Point", "Other"]
            },
            "KwaZulu-Natal": {
                "Durban": ["Umhlanga", "Berea", "Durban North", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Egypt": {
        "currency": "E£",
        "currency_code": "EGP",
        "currency_name": "Egyptian Pound",
        "currency_words_suffix": "Egyptian Pounds Only",
        "number_system": "standard",
        "rate_multiplier": 48.0,
        "budget_default": 17000000,
        "budget_step": 500000,
        "construction_rate_sqft": 6800,
        "cost_bedroom": 220000,
        "cost_bathroom": 350000,
        "cost_parking": 530000,
        "cost_kitchen": 670000,
        "cost_dining": 175000,
        "cost_balcony": 175000,
        "cost_floor_extra": 1100,
        "opt_costs": {
            "Swimming Pool": 1100000,
            "Solar Panels": 530000,
            "Lift / Elevator": 900000,
            "Home Office": 200000,
            "Terrace Garden": 270000,
            "Garden / Open Space": 220000
        },
        "states": {
            "Cairo Governorate": {
                "Cairo": ["New Cairo", "Zamalek", "Maadi", "Heliopolis", "Garden City", "Other"]
            },
            "Giza Governorate": {
                "Giza": ["Sheikh Zayed City", "6th of October City", "Dokki", "Mohandessin", "Other"]
            },
            "Alexandria": {
                "Alexandria": ["Smouha", "Gleem", "Kafr Abdo", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Nigeria": {
        "currency": "₦",
        "currency_code": "NGN",
        "currency_name": "Nigerian Naira",
        "currency_words_suffix": "Nigerian Naira Only",
        "number_system": "standard",
        "rate_multiplier": 1450.0,
        "budget_default": 500000000,
        "budget_step": 20000000,
        "construction_rate_sqft": 190000,
        "cost_bedroom": 6500000,
        "cost_bathroom": 10500000,
        "cost_parking": 16000000,
        "cost_kitchen": 20000000,
        "cost_dining": 5200000,
        "cost_balcony": 5200000,
        "cost_floor_extra": 33000,
        "opt_costs": {
            "Swimming Pool": 33000000,
            "Solar Panels": 16000000,
            "Lift / Elevator": 27000000,
            "Home Office": 6000000,
            "Terrace Garden": 8000000,
            "Garden / Open Space": 6700000
        },
        "states": {
            "Lagos State": {
                "Lagos": ["Ikoyi", "Victoria Island", "Lekki Phase 1", "Banana Island", "Ikeja GRA", "Other"]
            },
            "Federal Capital Territory": {
                "Abuja": ["Maitama", "Asokoro", "Wuse 2", "Gwarinpa", "Guzape", "Other"]
            },
            "Rivers State": {
                "Port Harcourt": ["Old GRA", "New GRA", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Kenya": {
        "currency": "KSh",
        "currency_code": "KES",
        "currency_name": "Kenyan Shilling",
        "currency_words_suffix": "Kenyan Shillings Only",
        "number_system": "standard",
        "rate_multiplier": 130.0,
        "budget_default": 45000000,
        "budget_step": 1000000,
        "construction_rate_sqft": 17500,
        "cost_bedroom": 580000,
        "cost_bathroom": 920000,
        "cost_parking": 1400000,
        "cost_kitchen": 1750000,
        "cost_dining": 460000,
        "cost_balcony": 460000,
        "cost_floor_extra": 2900,
        "opt_costs": {
            "Swimming Pool": 2900000,
            "Solar Panels": 1400000,
            "Lift / Elevator": 2400000,
            "Home Office": 530000,
            "Terrace Garden": 710000,
            "Garden / Open Space": 600000
        },
        "states": {
            "Nairobi County": {
                "Nairobi": ["Karen", "Runda", "Kilimani", "Kileleshwa", "Westlands", "Muthaiga", "Lavington", "Other"]
            },
            "Mombasa County": {
                "Mombasa": ["Nyali", "Diani", "Kizingo", "Other"]
            },
            "Kisumu County": {
                "Kisumu": ["Milimani", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Brazil": {
        "currency": "R$",
        "currency_code": "BRL",
        "currency_name": "Brazilian Real",
        "currency_words_suffix": "Brazilian Reais Only",
        "number_system": "standard",
        "rate_multiplier": 5.25,
        "budget_default": 1850000,
        "budget_step": 50000,
        "construction_rate_sqft": 780,
        "cost_bedroom": 25000,
        "cost_bathroom": 40000,
        "cost_parking": 60000,
        "cost_kitchen": 75000,
        "cost_dining": 20000,
        "cost_balcony": 20000,
        "cost_floor_extra": 125,
        "opt_costs": {
            "Swimming Pool": 125000,
            "Solar Panels": 60000,
            "Lift / Elevator": 100000,
            "Home Office": 23000,
            "Terrace Garden": 31000,
            "Garden / Open Space": 26000
        },
        "states": {
            "São Paulo": {
                "São Paulo": ["Jardins", "Itaim Bibi", "Pinheiros", "Vila Nova Conceição", "Moema", "Other"]
            },
            "Rio de Janeiro": {
                "Rio de Janeiro": ["Ipanema", "Leblon", "Copacabana", "Barra da Tijuca", "Gávea", "Other"]
            },
            "Federal District": {
                "Brasília": ["Asa Sul", "Asa Norte", "Lago Sul", "Lago Norte", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Mexico": {
        "currency": "Mex$",
        "currency_code": "MXN",
        "currency_name": "Mexican Peso",
        "currency_words_suffix": "Mexican Pesos Only",
        "number_system": "standard",
        "rate_multiplier": 17.5,
        "budget_default": 6100000,
        "budget_step": 200000,
        "construction_rate_sqft": 2500,
        "cost_bedroom": 82000,
        "cost_bathroom": 130000,
        "cost_parking": 195000,
        "cost_kitchen": 245000,
        "cost_dining": 65000,
        "cost_balcony": 65000,
        "cost_floor_extra": 410,
        "opt_costs": {
            "Swimming Pool": 410000,
            "Solar Panels": 195000,
            "Lift / Elevator": 330000,
            "Home Office": 75000,
            "Terrace Garden": 100000,
            "Garden / Open Space": 82000
        },
        "states": {
            "Mexico City": {
                "Mexico City": ["Polanco", "Condesa", "Roma Norte", "Santa Fe", "Lomas de Chapultepec", "Coyoacán", "Other"]
            },
            "Nuevo León": {
                "Monterrey": ["San Pedro Garza García", "Valle Oriente", "Contry", "Other"]
            },
            "Jalisco": {
                "Guadalajara": ["Puerta de Hierro", "Providencia", "Americana", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Argentina": {
        "currency": "$",
        "currency_code": "ARS",
        "currency_name": "Argentine Peso",
        "currency_words_suffix": "Argentine Pesos Only",
        "number_system": "standard",
        "rate_multiplier": 920.0,
        "budget_default": 320000000,
        "budget_step": 10000000,
        "construction_rate_sqft": 125000,
        "cost_bedroom": 4200000,
        "cost_bathroom": 6700000,
        "cost_parking": 10000000,
        "cost_kitchen": 12800000,
        "cost_dining": 3400000,
        "cost_balcony": 3400000,
        "cost_floor_extra": 21000,
        "opt_costs": {
            "Swimming Pool": 21000000,
            "Solar Panels": 10000000,
            "Lift / Elevator": 17000000,
            "Home Office": 3900000,
            "Terrace Garden": 5200000,
            "Garden / Open Space": 4300000
        },
        "states": {
            "Buenos Aires City": {
                "Buenos Aires": ["Recoleta", "Palermo", "Puerto Madero", "Belgrano", "San Telmo", "Other"]
            },
            "Córdoba Province": {
                "Córdoba": ["Nueva Córdoba", "Cerro de las Rosas", "Other"]
            },
            "Santa Fe Province": {
                "Rosario": ["Centro", "Pichincha", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Chile": {
        "currency": "CLP$",
        "currency_code": "CLP",
        "currency_name": "Chilean Peso",
        "currency_words_suffix": "Chilean Pesos Only",
        "number_system": "standard",
        "rate_multiplier": 950.0,
        "budget_default": 330000000,
        "budget_step": 10000000,
        "construction_rate_sqft": 140000,
        "cost_bedroom": 4500000,
        "cost_bathroom": 7200000,
        "cost_parking": 11000000,
        "cost_kitchen": 13800000,
        "cost_dining": 3600000,
        "cost_balcony": 3600000,
        "cost_floor_extra": 23000,
        "opt_costs": {
            "Swimming Pool": 23000000,
            "Solar Panels": 11000000,
            "Lift / Elevator": 18500000,
            "Home Office": 4200000,
            "Terrace Garden": 5600000,
            "Garden / Open Space": 4600000
        },
        "states": {
            "Santiago Metropolitan": {
                "Santiago": ["Las Condes", "Vitacura", "Providencia", "Lo Barnechea", "La Reina", "Other"]
            },
            "Valparaíso Region": {
                "Viña del Mar": ["Reñaca", "Miramar", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Colombia": {
        "currency": "COL$",
        "currency_code": "COP",
        "currency_name": "Colombian Peso",
        "currency_words_suffix": "Colombian Pesos Only",
        "number_system": "standard",
        "rate_multiplier": 3950.0,
        "budget_default": 1380000000,
        "budget_step": 50000000,
        "construction_rate_sqft": 540000,
        "cost_bedroom": 18500000,
        "cost_bathroom": 29500000,
        "cost_parking": 44500000,
        "cost_kitchen": 56000000,
        "cost_dining": 15000000,
        "cost_balcony": 15000000,
        "cost_floor_extra": 92000,
        "opt_costs": {
            "Swimming Pool": 92000000,
            "Solar Panels": 44500000,
            "Lift / Elevator": 75000000,
            "Home Office": 17000000,
            "Terrace Garden": 22500000,
            "Garden / Open Space": 19000000
        },
        "states": {
            "Bogotá D.C.": {
                "Bogotá": ["Chapinero", "Usaquén", "Chicó", "Rosales", "Santa Ana", "Other"]
            },
            "Antioquia": {
                "Medellín": ["El Poblado", "Laureles", "Envigado", "Other"]
            },
            "Valle del Cauca": {
                "Cali": ["Ciudad Jardín", "El Peñón", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Greece": {
        "currency": "€",
        "currency_code": "EUR",
        "currency_name": "Euro",
        "currency_words_suffix": "Euros Only",
        "number_system": "standard",
        "rate_multiplier": 0.92,
        "budget_default": 290000,
        "budget_step": 10000,
        "construction_rate_sqft": 145,
        "cost_bedroom": 4500,
        "cost_bathroom": 7000,
        "cost_parking": 10200,
        "cost_kitchen": 13000,
        "cost_dining": 3600,
        "cost_balcony": 3600,
        "cost_floor_extra": 21,
        "opt_costs": {
            "Swimming Pool": 21000,
            "Solar Panels": 10200,
            "Lift / Elevator": 17000,
            "Home Office": 3900,
            "Terrace Garden": 5200,
            "Garden / Open Space": 4200
        },
        "states": {
            "Attica": {
                "Athens": ["Kolonaki", "Glyfada", "Kifisia", "Plaka", "Vouliagmeni", "Other"]
            },
            "Central Macedonia": {
                "Thessaloniki": ["Kalamaria", "Centre", "Other"]
            },
            "South Aegean": {
                "Mykonos": ["Chora", "Ornos", "Other"],
                "Santorini": ["Oia", "Fira", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Czech Republic": {
        "currency": "Kč",
        "currency_code": "CZK",
        "currency_name": "Czech Koruna",
        "currency_words_suffix": "Czech Korunas Only",
        "number_system": "standard",
        "rate_multiplier": 23.0,
        "budget_default": 8000000,
        "budget_step": 250000,
        "construction_rate_sqft": 3600,
        "cost_bedroom": 110000,
        "cost_bathroom": 175000,
        "cost_parking": 265000,
        "cost_kitchen": 330000,
        "cost_dining": 88000,
        "cost_balcony": 88000,
        "cost_floor_extra": 550,
        "opt_costs": {
            "Swimming Pool": 550000,
            "Solar Panels": 265000,
            "Lift / Elevator": 440000,
            "Home Office": 100000,
            "Terrace Garden": 135000,
            "Garden / Open Space": 110000
        },
        "states": {
            "Prague": {
                "Prague": ["Prague 1 (Old Town)", "Prague 2 (Vinohrady)", "Prague 5 (Smíchov)", "Prague 6 (Dejvice)", "Other"]
            },
            "South Moravian": {
                "Brno": ["Brno-střed", "Královo Pole", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Hungary": {
        "currency": "Ft",
        "currency_code": "HUF",
        "currency_name": "Hungarian Forint",
        "currency_words_suffix": "Hungarian Forints Only",
        "number_system": "standard",
        "rate_multiplier": 365.0,
        "budget_default": 125000000,
        "budget_step": 5000000,
        "construction_rate_sqft": 56000,
        "cost_bedroom": 1750000,
        "cost_bathroom": 2800000,
        "cost_parking": 4200000,
        "cost_kitchen": 5250000,
        "cost_dining": 1400000,
        "cost_balcony": 1400000,
        "cost_floor_extra": 8800,
        "opt_costs": {
            "Swimming Pool": 8800000,
            "Solar Panels": 4200000,
            "Lift / Elevator": 7000000,
            "Home Office": 1600000,
            "Terrace Garden": 2150000,
            "Garden / Open Space": 1750000
        },
        "states": {
            "Central Hungary": {
                "Budapest": ["District V (Belváros)", "District I (Buda Castle)", "District II (Rózsadomb)", "District XIII", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Romania": {
        "currency": "lei",
        "currency_code": "RON",
        "currency_name": "Romanian Leu",
        "currency_words_suffix": "Romanian Lei Only",
        "number_system": "standard",
        "rate_multiplier": 4.6,
        "budget_default": 1600000,
        "budget_step": 50000,
        "construction_rate_sqft": 680,
        "cost_bedroom": 21500,
        "cost_bathroom": 34500,
        "cost_parking": 52000,
        "cost_kitchen": 65000,
        "cost_dining": 17500,
        "cost_balcony": 17500,
        "cost_floor_extra": 110,
        "opt_costs": {
            "Swimming Pool": 110000,
            "Solar Panels": 52000,
            "Lift / Elevator": 88000,
            "Home Office": 20000,
            "Terrace Garden": 26500,
            "Garden / Open Space": 22000
        },
        "states": {
            "Bucharest-Ilfov": {
                "Bucharest": ["Primăverii", "Dorobanți", "Floreasca", "Herăstrău", "Aviatorilor", "Other"]
            },
            "Cluj": {
                "Cluj-Napoca": ["Gheorgheni", "Zorilor", "Andrei Mureșanu", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Pakistan": {
        "currency": "Rs",
        "currency_code": "PKR",
        "currency_name": "Pakistani Rupee",
        "currency_words_suffix": "Pakistani Rupees Only",
        "number_system": "indian",
        "rate_multiplier": 278.0,
        "budget_default": 95000000,
        "budget_step": 2000000,
        "construction_rate_sqft": 6500,
        "cost_bedroom": 220000,
        "cost_bathroom": 350000,
        "cost_parking": 520000,
        "cost_kitchen": 650000,
        "cost_dining": 175000,
        "cost_balcony": 175000,
        "cost_floor_extra": 1100,
        "opt_costs": {
            "Swimming Pool": 1100000,
            "Solar Panels": 520000,
            "Lift / Elevator": 880000,
            "Home Office": 200000,
            "Terrace Garden": 265000,
            "Garden / Open Space": 220000
        },
        "states": {
            "Punjab": {
                "Lahore": ["DHA Phase 5/6", "Gulberg", "Model Town", "Bahria Town", "Cantt", "Other"]
            },
            "Sindh": {
                "Karachi": ["Clifton", "DHA Defence", "PECHS", "KDA", "Other"]
            },
            "Federal Capital": {
                "Islamabad": ["F-6", "F-7", "F-8", "E-7", "Bahria Town", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Bangladesh": {
        "currency": "৳",
        "currency_code": "BDT",
        "currency_name": "Bangladeshi Taka",
        "currency_words_suffix": "Bangladeshi Taka Only",
        "number_system": "indian",
        "rate_multiplier": 118.0,
        "budget_default": 40000000,
        "budget_step": 1000000,
        "construction_rate_sqft": 3200,
        "cost_bedroom": 110000,
        "cost_bathroom": 180000,
        "cost_parking": 270000,
        "cost_kitchen": 340000,
        "cost_dining": 90000,
        "cost_balcony": 90000,
        "cost_floor_extra": 550,
        "opt_costs": {
            "Swimming Pool": 550000,
            "Solar Panels": 270000,
            "Lift / Elevator": 450000,
            "Home Office": 105000,
            "Terrace Garden": 140000,
            "Garden / Open Space": 115000
        },
        "states": {
            "Dhaka Division": {
                "Dhaka": ["Gulshan 1/2", "Banani", "Baridhara Diplomatic", "Dhanmondi", "Uttara", "Other"]
            },
            "Chittagong Division": {
                "Chittagong": ["Khulshi", "Nasirabad", "Agrabad", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Sri Lanka": {
        "currency": "Rs",
        "currency_code": "LKR",
        "currency_name": "Sri Lankan Rupee",
        "currency_words_suffix": "Sri Lankan Rupees Only",
        "number_system": "indian",
        "rate_multiplier": 305.0,
        "budget_default": 105000000,
        "budget_step": 2500000,
        "construction_rate_sqft": 7500,
        "cost_bedroom": 250000,
        "cost_bathroom": 400000,
        "cost_parking": 600000,
        "cost_kitchen": 750000,
        "cost_dining": 200000,
        "cost_balcony": 200000,
        "cost_floor_extra": 1250,
        "opt_costs": {
            "Swimming Pool": 1250000,
            "Solar Panels": 600000,
            "Lift / Elevator": 1000000,
            "Home Office": 230000,
            "Terrace Garden": 310000,
            "Garden / Open Space": 260000
        },
        "states": {
            "Western Province": {
                "Colombo": ["Colombo 07 (Cinnamon Gardens)", "Colombo 03 (Kollupitiya)", "Colombo 04 (Bambalapitiya)", "Mount Lavinia", "Other"]
            },
            "Central Province": {
                "Kandy": ["City Centre", "Peradeniya", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    },
    "Nepal": {
        "currency": "Rs",
        "currency_code": "NPR",
        "currency_name": "Nepalese Rupee",
        "currency_words_suffix": "Nepalese Rupees Only",
        "number_system": "indian",
        "rate_multiplier": 134.0,
        "budget_default": 47000000,
        "budget_step": 1000000,
        "construction_rate_sqft": 3500,
        "cost_bedroom": 125000,
        "cost_bathroom": 200000,
        "cost_parking": 300000,
        "cost_kitchen": 380000,
        "cost_dining": 100000,
        "cost_balcony": 100000,
        "cost_floor_extra": 620,
        "opt_costs": {
            "Swimming Pool": 620000,
            "Solar Panels": 300000,
            "Lift / Elevator": 500000,
            "Home Office": 115000,
            "Terrace Garden": 155000,
            "Garden / Open Space": 130000
        },
        "states": {
            "Bagmati Province": {
                "Kathmandu": ["Lazimpat", "Baluwatar", "Jhamsikhel", "Budhanilkantha", "Baneshwor", "Other"]
            },
            "Gandaki Province": {
                "Pokhara": ["Lakeside", "Damside", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    }
}

# =====================================================================
# 2. COMPLETE WORLDWIDE REGISTRY FOR ALL OTHER RECOGNIZED COUNTRIES
# =====================================================================

GLOBAL_METADATA_REGISTRY = {
    "Afghanistan": ("AFN", "؋", "Afghan Afghani", "Afghan Afghanis Only", 71.0, "Kabul"),
    "Albania": ("ALL", "L", "Albanian Lek", "Albanian Leke Only", 92.5, "Tirana"),
    "Algeria": ("DZD", "د.ج", "Algerian Dinar", "Algerian Dinars Only", 134.0, "Algiers"),
    "Andorra": ("EUR", "€", "Euro", "Euros Only", 0.92, "Andorra la Vella"),
    "Angola": ("AOA", "Kz", "Angolan Kwanza", "Angolan Kwanzas Only", 840.0, "Luanda"),
    "Antigua and Barbuda": ("XCD", "EC$", "East Caribbean Dollar", "East Caribbean Dollars Only", 2.70, "St. John's"),
    "Armenia": ("AMD", "֏", "Armenian Dram", "Armenian Drams Only", 388.0, "Yerevan"),
    "Azerbaijan": ("AZN", "₼", "Azerbaijani Manat", "Azerbaijani Manats Only", 1.70, "Baku"),
    "Bahamas": ("BSD", "B$", "Bahamian Dollar", "Bahamian Dollars Only", 1.0, "Nassau"),
    "Bahrain": ("BHD", ".د.ب", "Bahraini Dinar", "Bahraini Dinars Only", 0.38, "Manama"),
    "Barbados": ("BBD", "Bds$", "Barbadian Dollar", "Barbadian Dollars Only", 2.0, "Bridgetown"),
    "Belarus": ("BYN", "Br", "Belarusian Ruble", "Belarusian Rubles Only", 3.25, "Minsk"),
    "Belize": ("BZD", "BZ$", "Belize Dollar", "Belize Dollars Only", 2.0, "Belize City"),
    "Benin": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Porto-Novo"),
    "Bhutan": ("BTN", "Nu.", "Bhutanese Ngultrum", "Bhutanese Ngultrum Only", 84.0, "Thimphu"),
    "Bolivia": ("BOB", "Bs.", "Bolivian Boliviano", "Bolivian Bolivianos Only", 6.91, "La Paz"),
    "Bosnia and Herzegovina": ("BAM", "KM", "Convertible Mark", "Convertible Marks Only", 1.80, "Sarajevo"),
    "Botswana": ("BWP", "P", "Botswana Pula", "Botswana Pulas Only", 13.5, "Gaborone"),
    "Brunei": ("BND", "B$", "Brunei Dollar", "Brunei Dollars Only", 1.35, "Bandar Seri Begawan"),
    "Bulgaria": ("BGN", "лв", "Bulgarian Lev", "Bulgarian Leva Only", 1.80, "Sofia"),
    "Burkina Faso": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Ouagadougou"),
    "Burundi": ("BIF", "FBu", "Burundian Franc", "Burundian Francs Only", 2850.0, "Gitega"),
    "Cabo Verde": ("CVE", "Esc", "Cape Verdean Escudo", "Cape Verdean Escudos Only", 101.5, "Praia"),
    "Cambodia": ("KHR", "៛", "Cambodian Riel", "Cambodian Riels Only", 4100.0, "Phnom Penh"),
    "Cameroon": ("XAF", "FCFA", "Central African CFA Franc", "Central African CFA Francs Only", 605.0, "Yaoundé"),
    "Central African Republic": ("XAF", "FCFA", "Central African CFA Franc", "Central African CFA Francs Only", 605.0, "Bangui"),
    "Chad": ("XAF", "FCFA", "Central African CFA Franc", "Central African CFA Francs Only", 605.0, "N'Djamena"),
    "Comoros": ("KMF", "CF", "Comorian Franc", "Comorian Francs Only", 453.0, "Moroni"),
    "Congo": ("XAF", "FCFA", "Central African CFA Franc", "Central African CFA Francs Only", 605.0, "Brazzaville"),
    "Costa Rica": ("CRC", "₡", "Costa Rican Colón", "Costa Rican Colones Only", 520.0, "San José"),
    "Croatia": ("EUR", "€", "Euro", "Euros Only", 0.92, "Zagreb"),
    "Cuba": ("CUP", "$", "Cuban Peso", "Cuban Pesos Only", 24.0, "Havana"),
    "Cyprus": ("EUR", "€", "Euro", "Euros Only", 0.92, "Nicosia"),
    "Djibouti": ("DJF", "Fdj", "Djiboutian Franc", "Djiboutian Francs Only", 178.0, "Djibouti"),
    "Dominica": ("XCD", "EC$", "East Caribbean Dollar", "East Caribbean Dollars Only", 2.70, "Roseau"),
    "Dominican Republic": ("DOP", "RD$", "Dominican Peso", "Dominican Pesos Only", 59.0, "Santo Domingo"),
    "DR Congo": ("CDF", "FC", "Congolese Franc", "Congolese Francs Only", 2750.0, "Kinshasa"),
    "Ecuador": ("USD", "$", "US Dollar", "US Dollars Only", 1.0, "Quito"),
    "El Salvador": ("USD", "$", "US Dollar", "US Dollars Only", 1.0, "San Salvador"),
    "Equatorial Guinea": ("XAF", "FCFA", "Central African CFA Franc", "Central African CFA Francs Only", 605.0, "Malabo"),
    "Eritrea": ("ERN", "Nfk", "Eritrean Nakfa", "Eritrean Nakfas Only", 15.0, "Asmara"),
    "Estonia": ("EUR", "€", "Euro", "Euros Only", 0.92, "Tallinn"),
    "Eswatini": ("SZL", "E", "Swazi Lilangeni", "Swazi Emalangeni Only", 18.5, "Mbabane"),
    "Ethiopia": ("ETB", "Br", "Ethiopian Birr", "Ethiopian Birrs Only", 57.0, "Addis Ababa"),
    "Fiji": ("FJD", "FJ$", "Fijian Dollar", "Fijian Dollars Only", 2.25, "Suva"),
    "Gabon": ("XAF", "FCFA", "Central African CFA Franc", "Central African CFA Francs Only", 605.0, "Libreville"),
    "Gambia": ("GMD", "D", "Gambian Dalasi", "Gambian Dalasis Only", 68.0, "Banjul"),
    "Georgia": ("GEL", "₾", "Georgian Lari", "Georgian Laris Only", 2.70, "Tbilisi"),
    "Ghana": ("GHS", "GH₵", "Ghanaian Cedi", "Ghanaian Cedis Only", 14.5, "Accra"),
    "Grenada": ("XCD", "EC$", "East Caribbean Dollar", "East Caribbean Dollars Only", 2.70, "St. George's"),
    "Guatemala": ("GTQ", "Q", "Guatemalan Quetzal", "Guatemalan Quetzals Only", 7.80, "Guatemala City"),
    "Guinea": ("GNF", "FG", "Guinean Franc", "Guinean Francs Only", 8600.0, "Conakry"),
    "Guinea-Bissau": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Bissau"),
    "Guyana": ("GYD", "G$", "Guyanese Dollar", "Guyanese Dollars Only", 209.0, "Georgetown"),
    "Haiti": ("HTG", "G", "Haitian Gourde", "Haitian Gourdes Only", 133.0, "Port-au-Prince"),
    "Honduras": ("HNL", "L", "Honduran Lempira", "Honduran Lempiras Only", 24.7, "Tegucigalpa"),
    "Iceland": ("ISK", "kr", "Icelandic Króna", "Icelandic Krónur Only", 138.0, "Reykjavik"),
    "Iran": ("IRR", "﷼", "Iranian Rial", "Iranian Rials Only", 42000.0, "Tehran"),
    "Iraq": ("IQD", "ع.د", "Iraqi Dinar", "Iraqi Dinars Only", 1310.0, "Baghdad"),
    "Ivory Coast": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Abidjan"),
    "Jamaica": ("JMD", "J$", "Jamaican Dollar", "Jamaican Dollars Only", 155.0, "Kingston"),
    "Jordan": ("JOD", "د.ا", "Jordanian Dinar", "Jordanian Dinars Only", 0.71, "Amman"),
    "Kazakhstan": ("KZT", "₸", "Kazakhstani Tenge", "Kazakhstani Tenges Only", 450.0, "Astana"),
    "Kiribati": ("AUD", "A$", "Australian Dollar", "Australian Dollars Only", 1.52, "Tarawa"),
    "Kyrgyzstan": ("KGS", "с", "Kyrgyzstani Som", "Kyrgyzstani Soms Only", 89.0, "Bishkek"),
    "Laos": ("LAK", "₭", "Lao Kip", "Lao Kips Only", 21500.0, "Vientiane"),
    "Latvia": ("EUR", "€", "Euro", "Euros Only", 0.92, "Riga"),
    "Lebanon": ("LBP", "ل.ل", "Lebanese Pound", "Lebanese Pounds Only", 89500.0, "Beirut"),
    "Lesotho": ("LSL", "L", "Lesotho Loti", "Lesotho Maloti Only", 18.5, "Maseru"),
    "Liberia": ("LRD", "L$", "Liberian Dollar", "Liberian Dollars Only", 192.0, "Monrovia"),
    "Libya": ("LYD", "ل.د", "Libyan Dinar", "Libyan Dinars Only", 4.85, "Tripoli"),
    "Liechtenstein": ("CHF", "CHF", "Swiss Franc", "Swiss Francs Only", 0.90, "Vaduz"),
    "Lithuania": ("EUR", "€", "Euro", "Euros Only", 0.92, "Vilnius"),
    "Luxembourg": ("EUR", "€", "Euro", "Euros Only", 0.92, "Luxembourg City"),
    "Madagascar": ("MGA", "Ar", "Malagasy Ariary", "Malagasy Ariary Only", 4500.0, "Antananarivo"),
    "Malawi": ("MWK", "MK", "Malawian Kwacha", "Malawian Kwachas Only", 1730.0, "Lilongwe"),
    "Maldives": ("MVR", "Rf", "Maldivian Rufiyaa", "Maldivian Rufiyaas Only", 15.4, "Malé"),
    "Mali": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Bamako"),
    "Malta": ("EUR", "€", "Euro", "Euros Only", 0.92, "Valletta"),
    "Marshall Islands": ("USD", "$", "US Dollar", "US Dollars Only", 1.0, "Majuro"),
    "Mauritania": ("MRU", "UM", "Mauritanian Ouguiya", "Mauritanian Ouguiyas Only", 39.5, "Nouakchott"),
    "Mauritius": ("MUR", "₨", "Mauritian Rupee", "Mauritian Rupees Only", 46.5, "Port Louis"),
    "Micronesia": ("USD", "$", "US Dollar", "US Dollars Only", 1.0, "Palikir"),
    "Moldova": ("MDL", "L", "Moldovan Leu", "Moldovan Lei Only", 17.8, "Chisinau"),
    "Monaco": ("EUR", "€", "Euro", "Euros Only", 0.92, "Monaco"),
    "Mongolia": ("MNT", "₮", "Mongolian Tögrög", "Mongolian Tögrögs Only", 3450.0, "Ulaanbaatar"),
    "Montenegro": ("EUR", "€", "Euro", "Euros Only", 0.92, "Podgorica"),
    "Morocco": ("MAD", "د.م.", "Moroccan Dirham", "Moroccan Dirhams Only", 10.0, "Rabat"),
    "Mozambique": ("MZN", "MT", "Mozambican Metical", "Mozambican Meticais Only", 63.8, "Maputo"),
    "Myanmar": ("MMK", "K", "Myanmar Kyat", "Myanmar Kyats Only", 2100.0, "Naypyidaw"),
    "Namibia": ("NAD", "N$", "Namibian Dollar", "Namibian Dollars Only", 18.5, "Windhoek"),
    "Nauru": ("AUD", "A$", "Australian Dollar", "Australian Dollars Only", 1.52, "Yaren"),
    "Nicaragua": ("NIO", "C$", "Nicaraguan Córdoba", "Nicaraguan Córdobas Only", 36.8, "Managua"),
    "Niger": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Niamey"),
    "North Korea": ("KPW", "₩", "North Korean Won", "North Korean Won Only", 900.0, "Pyongyang"),
    "North Macedonia": ("MKD", "ден", "Macedonian Denar", "Macedonian Denars Only", 56.5, "Skopje"),
    "Palau": ("USD", "$", "US Dollar", "US Dollars Only", 1.0, "Ngerulmud"),
    "Palestine": ("ILS", "₪", "Israeli Shekel", "Israeli Shekels Only", 3.72, "Ramallah"),
    "Panama": ("PAB", "B/.", "Panamanian Balboa", "Panamanian Balboas Only", 1.0, "Panama City"),
    "Papua New Guinea": ("PGK", "K", "Papua New Guinean Kina", "Papua New Guinean Kina Only", 3.85, "Port Moresby"),
    "Paraguay": ("PYG", "₲", "Paraguayan Guaraní", "Paraguayan Guaraníes Only", 7500.0, "Asunción"),
    "Peru": ("PEN", "S/.", "Peruvian Sol", "Peruvian Soles Only", 3.75, "Lima"),
    "Rwanda": ("RWF", "FRw", "Rwandan Franc", "Rwandan Francs Only", 1300.0, "Kigali"),
    "Saint Kitts and Nevis": ("XCD", "EC$", "East Caribbean Dollar", "East Caribbean Dollars Only", 2.70, "Basseterre"),
    "Saint Lucia": ("XCD", "EC$", "East Caribbean Dollar", "East Caribbean Dollars Only", 2.70, "Castries"),
    "Saint Vincent and the Grenadines": ("XCD", "EC$", "East Caribbean Dollar", "East Caribbean Dollars Only", 2.70, "Kingstown"),
    "Samoa": ("WST", "WS$", "Samoan Tālā", "Samoan Tālā Only", 2.75, "Apia"),
    "San Marino": ("EUR", "€", "Euro", "Euros Only", 0.92, "San Marino"),
    "Sao Tome and Principe": ("STN", "Db", "São Tomé Dobra", "São Tomé Dobras Only", 22.5, "São Tomé"),
    "Senegal": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Dakar"),
    "Serbia": ("RSD", "дин.", "Serbian Dinar", "Serbian Dinars Only", 108.0, "Belgrade"),
    "Seychelles": ("SCR", "SR", "Seychellois Rupee", "Seychellois Rupees Only", 13.5, "Victoria"),
    "Sierra Leone": ("SLE", "Le", "Sierra Leonean Leone", "Sierra Leonean Leones Only", 22.5, "Freetown"),
    "Slovakia": ("EUR", "€", "Euro", "Euros Only", 0.92, "Bratislava"),
    "Slovenia": ("EUR", "€", "Euro", "Euros Only", 0.92, "Ljubljana"),
    "Solomon Islands": ("SBD", "SI$", "Solomon Islands Dollar", "Solomon Islands Dollars Only", 8.45, "Honiara"),
    "Somalia": ("SOS", "Sh.So.", "Somali Shilling", "Somali Shillings Only", 570.0, "Mogadishu"),
    "South Sudan": ("SSP", "SS£", "South Sudanese Pound", "South Sudanese Pounds Only", 130.0, "Juba"),
    "Sudan": ("SDG", "SDG", "Sudanese Pound", "Sudanese Pounds Only", 600.0, "Khartoum"),
    "Suriname": ("SRD", "Sr$", "Surinamese Dollar", "Surinamese Dollars Only", 32.0, "Paramaribo"),
    "Syria": ("SYP", "LS", "Syrian Pound", "Syrian Pounds Only", 13000.0, "Damascus"),
    "Taiwan": ("TWD", "NT$", "New Taiwan Dollar", "New Taiwan Dollars Only", 32.2, "Taipei"),
    "Tajikistan": ("TJS", "SM", "Tajikistani Somoni", "Tajikistani Somonis Only", 10.9, "Dushanbe"),
    "Tanzania": ("TZS", "TSh", "Tanzanian Shilling", "Tanzanian Shillings Only", 2600.0, "Dodoma"),
    "Timor-Leste": ("USD", "$", "US Dollar", "US Dollars Only", 1.0, "Dili"),
    "Togo": ("XOF", "CFA", "West African CFA Franc", "West African CFA Francs Only", 605.0, "Lomé"),
    "Tonga": ("TOP", "T$", "Tongan Paʻanga", "Tongan Paʻanga Only", 2.35, "Nukuʻalofa"),
    "Trinidad and Tobago": ("TTD", "TT$", "Trinidad and Tobago Dollar", "Trinidad and Tobago Dollars Only", 6.78, "Port of Spain"),
    "Tunisia": ("TND", "د.ت", "Tunisian Dinar", "Tunisian Dinars Only", 3.12, "Tunis"),
    "Turkmenistan": ("TMT", "m", "Turkmenistani Manat", "Turkmenistani Manats Only", 3.50, "Ashgabat"),
    "Tuvalu": ("AUD", "A$", "Australian Dollar", "Australian Dollars Only", 1.52, "Funafuti"),
    "Uganda": ("UGX", "USh", "Ugandan Shilling", "Ugandan Shillings Only", 3750.0, "Kampala"),
    "Uruguay": ("UYU", "$U", "Uruguayan Peso", "Uruguayan Pesos Only", 39.0, "Montevideo"),
    "Uzbekistan": ("UZS", "so'm", "Uzbekistani Som", "Uzbekistani Soms Only", 12600.0, "Tashkent"),
    "Vanuatu": ("VUV", "VT", "Vanuatu Vatu", "Vanuatu Vatus Only", 120.0, "Port Vila"),
    "Vatican City": ("EUR", "€", "Euro", "Euros Only", 0.92, "Vatican City"),
    "Venezuela": ("VES", "Bs.S", "Venezuelan Bolívar", "Venezuelan Bolívares Only", 36.5, "Caracas"),
    "Yemen": ("YER", "﷼", "Yemeni Rial", "Yemeni Rials Only", 250.0, "Sana'a"),
    "Zambia": ("ZMW", "ZK", "Zambian Kwacha", "Zambian Kwachas Only", 26.5, "Lusaka"),
    "Zimbabwe": ("ZWL", "Z$", "Zimbabwean Dollar", "Zimbabwean Dollars Only", 13.5, "Harare")
}

# =====================================================================
# 3. DYNAMIC CONFIGURATION FACTORY
# =====================================================================

def get_country_config(country_name):
    """
    Retrieves or dynamically computes a complete real estate profile for ANY country.
    Guarantees that no country ever throws KeyError or crashes.
    """
    if country_name in CUSTOM_COUNTRY_DATA:
        return CUSTOM_COUNTRY_DATA[country_name]

    if country_name in GLOBAL_METADATA_REGISTRY:
        code, sym, name, words_suffix, mult, capital = GLOBAL_METADATA_REGISTRY[country_name]
    else:
        # Generic safe fallback for arbitrary inputs
        code, sym, name, words_suffix, mult, capital = ("USD", "$", "US Dollar", "US Dollars Only", 1.0, "Capital City")

    # Dynamically scale construction rate & itemized amenities proportionally
    base_sqft = max(15, round(165.0 * mult))
    b_def = max(10000, round(350000.0 * mult))
    b_step = max(1000, round(10000.0 * mult))

    ADMIN_UNIT_LOOKUP = {
        "UAE": "Emirate", "Japan": "Prefecture", "Canada": "Province", "China": "Province",
        "South Africa": "Province", "Argentina": "Province", "Indonesia": "Province",
        "Pakistan": "Province", "Nepal": "Province", "Saudi Arabia": "Province",
        "Kuwait": "Governorate", "Oman": "Governorate", "Egypt": "Governorate",
        "UK": "Country / Region", "France": "Region", "Germany": "Federal State",
        "Italy": "Region", "Spain": "Autonomous Community / Province", "Switzerland": "Canton",
        "USA": "State", "India": "State", "Australia": "State", "Brazil": "State",
        "Mexico": "State", "Nigeria": "State", "Kenya": "County", "Bangladesh": "Division",
        "Sri Lanka": "Province"
    }
    unit_label = ADMIN_UNIT_LOOKUP.get(country_name, "State / Province / Region")

    dyn_cfg = {
        "admin_unit_name": unit_label,
        "currency": sym,
        "currency_code": code,
        "currency_name": name,
        "currency_words_suffix": words_suffix,
        "number_system": "standard",
        "rate_multiplier": mult,
        "budget_default": b_def,
        "budget_step": b_step,
        "construction_rate_sqft": base_sqft,
        "cost_bedroom": max(100, round(5000.0 * mult)),
        "cost_bathroom": max(150, round(8000.0 * mult)),
        "cost_parking": max(200, round(12000.0 * mult)),
        "cost_kitchen": max(250, round(15000.0 * mult)),
        "cost_dining": max(80, round(4000.0 * mult)),
        "cost_balcony": max(80, round(4000.0 * mult)),
        "cost_floor_extra": max(5, round(25.0 * mult)),
        "opt_costs": {
            "Swimming Pool": max(500, round(25000.0 * mult)),
            "Solar Panels": max(250, round(12000.0 * mult)),
            "Lift / Elevator": max(400, round(20000.0 * mult)),
            "Home Office": max(100, round(4500.0 * mult)),
            "Terrace Garden": max(120, round(6000.0 * mult)),
            "Garden / Open Space": max(100, round(5000.0 * mult))
        },
        "states": {
            f"{capital} Region": {
                capital: ["City Center", "Financial District", "Uptown", "Residential Suburbs", "Waterfront", "Other"]
            },
            "Central Province": {
                "Central City": ["Downtown", "Old Town", "Suburbs", "Other"]
            },
            "Northern Region": {
                "North City": ["Central Area", "Suburbs", "Other"]
            },
            "Southern Region": {
                "South City": ["Central Area", "Suburbs", "Other"]
            },
            "Other": {
                "Other City": ["Central District", "Suburbs", "Other"]
            }
        }
    }
    return dyn_cfg

# Combine full alphabetical list of all supported countries
ALL_COUNTRY_NAMES = sorted(list(set(list(CUSTOM_COUNTRY_DATA.keys()) + list(GLOBAL_METADATA_REGISTRY.keys()))))

# Prioritize prominent countries at top of selection list for rapid access
PRIORITY_COUNTRIES = [
    "India", "USA", "UK", "Canada", "Australia", "Germany", "France", "UAE", "Saudi Arabia",
    "Japan", "Singapore", "New Zealand", "Italy", "Spain", "Switzerland", "Netherlands",
    "Sweden", "Norway", "China", "South Korea", "Brazil", "South Africa", "Mexico",
    "Qatar", "Kuwait", "Oman", "Turkey", "Egypt", "Nigeria", "Kenya", "Malaysia", "Thailand"
]
ORDERED_COUNTRY_LIST = PRIORITY_COUNTRIES + [c for c in ALL_COUNTRY_NAMES if c not in PRIORITY_COUNTRIES]

# =====================================================================
# 4. NUMBER FORMATTING & NUMBER TO WORDS ENGINE
# =====================================================================

def format_currency_value(amount, country="India"):
    """
    Formats numeric figures into country-specific currency notation with proper symbols.
    """
    if amount is None or amount < 0:
        amount = 0
    amount = round(amount)
    
    cfg = get_country_config(country)
    sym = cfg.get("currency", "$")
    
    # Needs space after symbol if it consists of letters (e.g. AED 1,000, SAR 500, CHF 200)
    has_letters = any(c.isalpha() for c in sym)
    prefix = f"{sym} " if has_letters else sym

    if cfg.get("number_system") == "indian":
        s = str(amount)
        if len(s) <= 3:
            formatted_num = s
        else:
            last3 = s[-3:]
            rest = s[:-3]
            chunks = []
            while len(rest) > 2:
                chunks.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                chunks.insert(0, rest)
            formatted_num = ",".join(chunks) + "," + last3
        return f"{prefix}{formatted_num}"
    else:
        return f"{prefix}{amount:,.0f}"

def _format_chunk(n):
    if n == 0:
        return ""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    res = []
    if n >= 100:
        res.append(ones[n // 100] + " Hundred")
        n %= 100
    if n >= 20:
        res.append(tens[n // 10])
        n %= 10
    if n > 0:
        res.append(ones[n])
    return " ".join(res)

def number_to_words(amount, country="India"):
    """
    Converts numbers into exact written words adhering to the country's currency system.
    """
    amount = int(round(amount))
    cfg = get_country_config(country)
    suffix = cfg.get("currency_words_suffix", f"{cfg.get('currency_name', 'Units')} Only")

    if amount <= 0:
        return f"Zero {suffix}"

    if cfg.get("number_system") == "indian":
        parts = []
        crores = amount // 10000000
        amount %= 10000000
        lakhs = amount // 100000
        amount %= 100000
        thousands = amount // 1000
        amount %= 1000
        hundreds = amount
        
        if crores > 0:
            parts.append(f"{_format_chunk(crores)} Crore")
        if lakhs > 0:
            parts.append(f"{_format_chunk(lakhs)} Lakh")
        if thousands > 0:
            parts.append(f"{_format_chunk(thousands)} Thousand")
        if hundreds > 0:
            parts.append(_format_chunk(hundreds))
        
        words = " ".join(parts).strip()
        return f"{words} {suffix}"
    else:
        parts = []
        trillions = amount // 1000000000000
        amount %= 1000000000000
        billions = amount // 1000000000
        amount %= 1000000000
        millions = amount // 1000000
        amount %= 1000000
        thousands = amount // 1000
        amount %= 1000
        hundreds = amount

        if trillions > 0:
            parts.append(f"{_format_chunk(trillions)} Trillion")
        if billions > 0:
            parts.append(f"{_format_chunk(billions)} Billion")
        if millions > 0:
            parts.append(f"{_format_chunk(millions)} Million")
        if thousands > 0:
            parts.append(f"{_format_chunk(thousands)} Thousand")
        if hundreds > 0:
            parts.append(_format_chunk(hundreds))

        words = " ".join(parts).strip()
        return f"{words} {suffix}"

# =====================================================================
# 5. INTERNAL ML NEIGHBORHOOD MAPPING
# =====================================================================

def map_location_to_internal_neighborhood(country, state, city, area):
    """
    Maps friendly user locations (from ANY country in the world) to Kaggle Ames model
    features internally without ever surfacing raw dataset codes to the end-user.
    """
    posh_keywords = [
        "Banjara Hills", "Jubilee Hills", "Beverly Hills", "Manhattan", "Mayfair",
        "Kensington", "South Mumbai", "Juhu", "Worli", "Indiranagar", "Koramangala",
        "Altstadt", "Mitte", "Palm Jumeirah", "Downtown Dubai", "Emirates Hills",
        "Ginza", "Minato", "Shibuya", "Yorkville", "Toorak", "Camps Bay", "Jardins",
        "Polanco", "Sandton", "Recoleta", "Las Condes", "Chapinero", "Bel-Air"
    ]
    tech_prime_keywords = [
        "Hitech City", "Madhapur", "Gachibowli", "Kondapur", "Whitefield", "HSR Layout",
        "SoMa", "Mission District", "Downtown", "Canary Wharf", "Financial District",
        "Pangyo", "Cyber City", "Marina Bay", "Business Bay", "BGC"
    ]
    family_suburb_keywords = [
        "Begumpet", "Kukatpally", "Secunderabad", "Madhurawada", "MVP Colony", "Siripuram",
        "Jayanagar", "Andheri", "Pasadena", "Santa Monica", "Brooklyn", "Westminster",
        "Charlottenburg", "Arabian Ranches", "Uptown", "Suburbs"
    ]
    
    target_area = str(area).strip()
    for kw in posh_keywords:
        if kw.lower() in target_area.lower():
            return "NoRidge"
            
    for kw in tech_prime_keywords:
        if kw.lower() in target_area.lower():
            return "Somerst"
            
    for kw in family_suburb_keywords:
        if kw.lower() in target_area.lower():
            return "CollgCr"

    return "CollgCr"
