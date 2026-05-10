# =========================
# IMPORTS
# =========================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from urllib.request import urlopen
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os
import re
from pathlib import Path
from nltk.stem import SnowballStemmer
import spacy
import correction_requetetd4


# =========================
# VARIABLES GLOBALES
# =========================

mois_dict = {
    "janvier": "01", "février": "02", "mars": "03",
    "avril": "04", "mai": "05", "juin": "06",
    "juillet": "07", "août": "08", "septembre": "09",
    "octobre": "10", "novembre": "11", "décembre": "12"
}

# chemins
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd().parent

BULLETINS = BASE_DIR / "BULLETINS"
DATA = BASE_DIR / "data"
OUTPUT = BASE_DIR / "output"


# =========================
# EXTRACTION METADONNEES
# =========================

def extraction_metadonnees(requete):
    metadonnees = {}


    # DATE
    pattern_date = (
        r"entre le \d{1,2} \w+ \d{4} et \d{1,2} \w+ \d{4}|"
        r"entre le \d{1,2} \w+ \d{4} et le \d{1,2} \w+ \d{4}|"
        r"entre \d{1,2}/\d{1,2}/\d{4} et \d{1,2}/\d{1,2}/\d{4}|"
        r"entre \d{4} et \d{4}|"
        r"après \d{1,2}/\d{1,2}/\d{4}|"
        r"de \d{4}|"
        r"au mois de \w+ \d{4}|"
        r"du mois de \w+ \d{4}|"
        r"en \w+ \d{4}|"
        r"en \d{4}|"
        r"à partir de \d{4}|"
        r"à partir de \w+ \d{4}|"
        r"de l'année \d{4}|"
        r"après \w+ \d{4}|"
        r"qui date d'après le \d{1,2} \w+ \d{4}|"
        r"du \d{1,2} \w+ \d{4}"
    )

    resultat_date = re.findall(pattern_date, requete, re.IGNORECASE)
    metadonnees['dates'] = resultat_date[0] if resultat_date else ""

    # RUBRIQUE
    pattern_rubrique = r"(focus|horizons enseignement|en direct des laboratoires|a lire|actualité innovations|actualités innovations|événement)"
    resultat_rubrique = re.findall(pattern_rubrique, requete, re.IGNORECASE)
    metadonnees['rubrique'] = resultat_rubrique[0] if resultat_rubrique else ""

    # STRUCTUREL
    pattern_structurel = r"(avec des images|sans image|contenant le mot \w+)"
    resultat_structurel = re.findall(pattern_structurel, requete, re.IGNORECASE)
    metadonnees['structurel'] = resultat_structurel[0].split() if resultat_structurel else []

    # OPERATEURS
    pattern_operateur = r"\b(et|ou)\b"
    resultat_operateur = re.findall(pattern_operateur, requete, re.IGNORECASE)
    metadonnees['operateur'] = list(set(resultat_operateur))

    # EXCLUSION
    pattern_operateur_not = r"(?:mais pas|sans)\s+([\w\s]+)"
    resultat_operateur_not = re.findall(pattern_operateur_not, requete, re.IGNORECASE)
    metadonnees['exclusion'] = resultat_operateur_not[0].split() if resultat_operateur_not else []

    # debug
    print("---------------------------------------------")
    print("---> metadonnees ✅ <---")
    print(
        "\tdate :", metadonnees['dates'],
        "\n\trubrique :", metadonnees['rubrique'],
        "\n\toperateur :", metadonnees['operateur'],
        "\n\texclusion :", metadonnees['exclusion'],
        "\n\tstructurel :", metadonnees['structurel'],
    )
    print("---------------------------------------------")

    return metadonnees


# =========================
# EXTRACTION RESTE REQUETE
# =========================

def reste(requete : str, metadonnees : dict):
    mots_restant = requete

    for valeur in metadonnees.values():
        if isinstance(valeur, list):
            for element in valeur:
                mots_restant = mots_restant.replace(element, "")
        elif isinstance(valeur, str):
            mots_restant = mots_restant.replace(valeur, "")

    return mots_restant.strip()


# ==================
# DATE UTILS
# ==================
def convertir_date(date_str):
    """ transforme '10 avril 2012' -> '10/04/2012' """
    parts = date_str.split()
    jour = parts[0].zfill(2)
    mois = mois_dict.get(parts[1].lower(), "01")
    annee = parts[2]
    return f"{jour}/{mois}/{annee}"


def traiter_expression(expr):
    """
    transforme une expression temporelle en intervalle [in, out]
    """

    date_min = "01/01/2011"
    date_max = "01/01/2015"

    dates = {'in': date_min, 'out': date_max}

    if not expr:
        return dates

    expr = expr.strip().lower()

    #  ENTRE ─
    # "entre le 10 avril 2012 et le 5 juin 2013"  (plus spécifique)
    match = re.match(r"entre le (\d{1,2} \w+ \d{4}) et le (\d{1,2} \w+ \d{4})", expr)
    if match:
        dates['in'] = convertir_date(match.group(1))
        dates['out'] = convertir_date(match.group(2))
        return dates

    # "entre le 10 avril 2012 et 5 juin 2013"
    match = re.match(r"entre le (\d{1,2} \w+ \d{4}) et (\d{1,2} \w+ \d{4})", expr)
    if match:
        dates['in'] = convertir_date(match.group(1))
        dates['out'] = convertir_date(match.group(2))
        return dates

    # "entre 10/04/2012 et 05/06/2013"  (avant "entre années" car plus spécifique)
    match = re.match(r"entre (\d{1,2}/\d{1,2}/\d{4}) et (\d{1,2}/\d{1,2}/\d{4})", expr)
    if match:
        dates['in'], dates['out'] = match.groups()
        return dates

    # "entre 2012 et 2013"  (plus général)
    match = re.match(r"entre (\d{4}) et (\d{4})", expr)
    if match:
        dates['in'] = f"01/01/{match.group(1)}"
        dates['out'] = f"31/12/{match.group(2)}"
        return dates

    #  APRÈS ─
    # "après 10/04/2012"  (plus spécifique)
    match = re.match(r"après (\d{1,2}/\d{1,2}/\d{4})", expr)
    if match:
        dates['in'] = match.group(1)
        return dates

    # "après avril 2012"  (plus général)
    match = re.match(r"après (\w+ \d{4})", expr)
    if match:
        mois, annee = match.group(1).split()
        mois_num = mois_dict.get(mois, "01")
        dates['in'] = f"01/{mois_num}/{annee}"
        return dates

    #  À PARTIR DE 
    # "à partir de avril 2012"  (plus spécifique, avant le pattern année seule)
    match = re.match(r"à partir de ([a-zéèêùîôà]+ \d{4})", expr)
    if match:
        mois, annee = match.group(1).split()
        mois_num = mois_dict.get(mois, "01")
        dates['in'] = f"01/{mois_num}/{annee}"
        return dates

    # "à partir de 2012"  (plus général)
    match = re.match(r"à partir de (\d{4})", expr)
    if match:
        dates['in'] = f"01/01/{match.group(1)}"
        return dates

    #  AU/DU MOIS DE 
    # "au mois de avril 2012"  (plus spécifique, avec année)
    match = re.match(r"(?:au|du) mois de (\w+) (\d{4})", expr)
    if match:
        mois, annee = match.groups()
        mois_num = int(mois_dict.get(mois, "1"))
        mois_suivant = mois_num + 1 if mois_num < 12 else 1
        annee_suivante = annee if mois_num < 12 else str(int(annee) + 1)
        dates['in'] = f"01/{str(mois_num).zfill(2)}/{annee}"
        dates['out'] = f"01/{str(mois_suivant).zfill(2)}/{annee_suivante}"
        return dates

    # "au mois de avril"  (plus général, sans année)
    match = re.match(r"au mois de (\w+)", expr)
    if match:
        mois = match.group(1)
        mois_num = int(mois_dict.get(mois, "1"))
        mois_suivant = mois_num + 1 if mois_num < 12 else 1
        dates['in'] = f"01/{str(mois_num).zfill(2)}/2011"
        dates['out'] = f"01/{str(mois_suivant).zfill(2)}/2015"
        return dates

    #  EN 
    # "en avril 2012"  (plus spécifique, avec mois)
    match = re.match(r"en ([a-zéèêùîôà]+ \d{4})", expr)
    if match:
        mois, annee = match.group(1).split()
        mois_num = int(mois_dict.get(mois, "1"))
        mois_suivant = mois_num + 1 if mois_num < 12 else 1
        annee_suivante = annee if mois_num < 12 else str(int(annee) + 1)
        dates['in'] = f"01/{str(mois_num).zfill(2)}/{annee}"
        dates['out'] = f"01/{str(mois_suivant).zfill(2)}/{annee_suivante}"
        return dates

    # "en 2012"  (plus général, année seule)
    match = re.match(r"en (\d{4})", expr)
    if match:
        dates['in'] = f"01/01/{match.group(1)}"
        dates['out'] = f"31/12/{match.group(1)}"
        return dates

    #  AUTRES 
    # "de l'année 2012"
    match = re.match(r"de l'année\s+(\d{4})", expr)
    if match:
        dates['in'] = f"01/01/{match.group(1)}"
        dates['out'] = f"31/12/{match.group(1)}"
        return dates

    # "qui date d'après le 10 avril 2012"  (plus spécifique que "du")
    match = re.match(r"qui date d'après le (\d{1,2} \w+ \d{4})", expr)
    if match:
        d = convertir_date(match.group(1))
        dates['in'] = d
        return dates

    # "du 10 avril 2012"
    match = re.match(r"du (\d{1,2} \w+ \d{4})", expr)
    if match:
        d = convertir_date(match.group(1))
        dates['in'] = d
        dates['out'] = d
        return dates

    # "de 2012"  (très général, en dernier)
    match = re.match(r"de (\d{4})", expr)
    if match:
        dates['in'] = f"01/01/{match.group(1)}"
        dates['out'] = f"31/12/{match.group(1)}"
        return dates

    return dates

def recuperation_mot_cles(mots_restant  : list , antidictionnaire : str) :

    # recuperation de l'anti-dictionnaire 
    anti_mots = set()
    anti_mots.update(["article","leb","led","trouver", "traiter","rustique","retourner","titre","suer", "end","un","contenir","mot","quiz", 'je',"lem","tsv","ler","veux", "doit", "quel", "dam", "der","del", "quid", '[inconnu]',"souhaiter", "vouloir", "parler", "afficher", "cherche", "traitant", "donner"])
    with open( antidictionnaire, "r", encoding="utf8" ) as f:
        for line in f :
            x = line.split()
            anti_mots.add(x[0].strip().lower())
    
    mots_cles = set()
    for mot in mots_restant :
        mot = mot.strip().lower()
        if mot not in anti_mots :
            mots_cles.add(mot)
    
    return list(mots_cles)


# =========================
# PIPELINE PRINCIPAL
# =========================

def traitement_requete(requete):

    nlp = spacy.load("fr_core_news_sm")

    new_anti_dict = DATA/"new_antidictionnaire.txt"
    anti_dict = DATA/"antidictionnaire.txt"
    lexique = correction_requetetd4.charger_lexique(DATA/"lemmes.txt")

    metadonnees = extraction_metadonnees(requete)
    mots_restant = reste(requete, metadonnees)
    mots_restant = mots_restant.split()
    mots_filtrer = recuperation_mot_cles(mots_restant, anti_dict )
    mots_filtrer = " ".join(mots_filtrer)
    # correction / normalisation
    mots_corriger =  correction_requetetd4.corriger_requete( mots_filtrer, lexique, nlp)
    print("mots corriger : ", mots_corriger)

    mots_cles = recuperation_mot_cles(mots_corriger, new_anti_dict )
    print("mots cles : ", mots_cles)

    dates = traiter_expression(metadonnees['dates'])

    structuration = {
        'mots_cles': mots_cles,
        'rubrique': metadonnees['rubrique'],
        'operateur': [op.upper() for op in metadonnees['operateur']],
        'exclusion': metadonnees['exclusion'],
        'date_min': dates['in'],
        'date_max': dates['out']
    }

    print("---------------------------------------------")
    print("---> STRUCTURATION ✅ <---")
    print(
        "\tmots_cles :", structuration['mots_cles'],
        "\n\trubrique :", structuration['rubrique'],
        "\n\toperateur :", structuration['operateur'],
        "\n\texclusion :", structuration['exclusion'],
        "\n\tdate_min :", structuration['date_min'],
        "\n\tdate_max :", structuration['date_max']
    )
    print("---------------------------------------------")

    return structuration


# =========================
# LOOP
# =========================

# while True:
#     traitement_requete()