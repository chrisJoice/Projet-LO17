# =========================
# IMPORTS
# =========================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
# pour afficher facilement les graphiques 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os
import re
from pathlib import Path
from nltk.stem import SnowballStemmer
import spacy
import traitement_requete


# =========================
# CONFIGURATION DES CHEMINS
# =========================

# configuration des chemins 
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd().parent

BULLETINS = BASE_DIR / "BULLETINS"
DATA = BASE_DIR / "data"
OUTPUT = BASE_DIR / "output"


# =========================
# CHARGEMENT INDEX INVERSE
# =========================

def charger_index(fichier):
    """
    transforme les fichiers inverses en dictionnaire 

    """

    index = {}

    with open(fichier, "r", encoding="utf-8") as f:

        for ligne in f:

            ligne = ligne.strip()

            if not ligne:
                continue

            # séparer mot et reste
            mot, docs_str = ligne.split("\t")

            docs = {}

            # séparer les doc:freq
            for element in docs_str.split():

                doc, freq = element.split(":")

                docs[doc] = int(freq)

            index[mot] = docs

    return index


# =========================
# CONSTRUCTION REQUETE LOGIQUE
# =========================

def construire_requete(structure):
    #initialisation de l'operateur 

    mots = structure['mots_cles']
    operateur = structure['operateur'][0].upper() if len(structure['operateur']) > 0 else ['ET']
    exclus = structure.get('exclus', [])
    sep = " OR " if operateur == "OU" else " AND "
    base = sep.join(mots)
    requete = base
    if exclus:
        excl = " AND ".join(f"NOT {m}" for m in exclus)
        requete = f"{base} AND {excl}"
    
    print("construction de la requete --> ✅  ",requete)
    return requete


# =========================
# EXECUTION REQUETE SUR INDEX
# =========================

def executer_requete(requete, index):

    # détecter opérateur principal
    if " AND " in requete:
        morceaux = requete.split(" AND ")
        operateur = "AND"
    elif " OR " in requete:
        morceaux = requete.split(" OR ")
        operateur = "OR"
    else:
        morceaux = [requete]
        operateur = None

    inclus = []
    exclus = []

    # séparer inclus / exclus
    for m in morceaux:
        m = m.strip()
        if m.startswith("NOT "):
            exclus.append(m.replace("NOT ", ""))
        else:
            inclus.append(m)

    # sets de documents
    docs_inclus = [set(index[m].keys()) for m in inclus if m in index]
    docs_exclus = set()
    for m in exclus:
        if m in index:
            docs_exclus |= set(index[m].keys())

    if not docs_inclus:
        return {}
    print ("\tdocs_inclus -->", docs_inclus )
    # AND / OR
    if operateur == "AND":
        docs_final = set.intersection(*docs_inclus)
    elif operateur == "OR":
        docs_final = set.union(*docs_inclus)
    else:
        docs_final = docs_inclus[0]

    # appliquer exclusion
    docs_final = docs_final - docs_exclus

    # score (somme des fréquences)
    resultat = {}
    for doc in docs_final:
        score = 0
        for mot in inclus:
            if mot in index and doc in index[mot]:
                score += index[mot][doc]
        resultat[doc] = score

    return resultat


# =========================
# INTERSECTION MULTIPLE
# =========================

def intersection_multiple(dicts):
    if not dicts:
        return {}

    # intersection des clés
    docs_communs = set(dicts[0].keys())

    for d in dicts[1:]:
        docs_communs &= set(d.keys())

    # somme des fréquences
    resultat = {}

    for doc in docs_communs:
        resultat[doc] = sum(d[doc] for d in dicts)

    return resultat


# =========================
# MOTEUR DE RECHERCHE
# =========================

def moteur():

    # traitement de la requete 
    structure = traitement_requete.traitement_requete()

    # recupération des fichier inverse 
    inverse_date = charger_index(DATA/"inverse_date.txt")
    inverse_rubrique = charger_index(DATA/"inverse_rubrique.txt")
    inverse_texte = charger_index(DATA/"inverse_texte.txt")
    inverse_titre = charger_index(DATA/"inverse_titre.txt")

    # recuperation des bons document
    # initialisation 
    docs_date = {}
    docs_rubrique = {}
    docs_texte = {}
    docs_titre = {}
    # 1. filtre sur les dates
    if inverse_date :
        for cle in inverse_date :
            date_doc = pd.to_datetime(cle, format="mixed", dayfirst=True, errors="coerce")
            date_min = pd.to_datetime(structure['date_min'], format="mixed", dayfirst=True, errors="coerce")
            date_max = pd.to_datetime(structure['date_max'], format="mixed", dayfirst=True, errors="coerce")
            if date_doc is not pd.NaT and date_min <= date_doc <= date_max:

                for doc, freq in list(inverse_date[cle].items()) : 
                    docs_date[doc] = freq
        print("filtre date ok ✅ ")
    # 2. filtre rubrique (hyphothèse il y a une seul rubrique dans la requette )
    if inverse_rubrique :
        for cle in inverse_rubrique :
            for mot in structure['rubrique'] :
                if mot == cle :
                    for doc, freq in list(inverse_rubrique[cle].items()) : 
                        docs_rubrique[doc] = freq
        print("filtre rubrique ok ✅ ")
    # 3. filtre texte
    if inverse_texte :
        req = construire_requete(structure)
        docs_texte = executer_requete(req,inverse_texte)
        print("filtre texte ok ✅ ")

    if inverse_titre :
        req = construire_requete(structure)
        docs_titre = executer_requete(req,inverse_titre)
        print("filtre titre ok ✅ ")
        
    # on recupère les dictionnaires non vide 
    liste_docs = [d for d in [docs_date, docs_rubrique, docs_texte, docs_titre] if d]
    resultat_final = intersection_multiple(liste_docs)

    # classe par ordre décroissant 
    resultat_final = dict(sorted(resultat_final.items(), key=lambda x: x[1], reverse=True))
    
    # affichage des resultats 
    print("documents chercher ---> ✅  ")
    print("\t ## ",resultat_final)
    return resultat_final


# =========================
# EXECUTION
# =========================
                
while 1 :
    resultat = moteur()