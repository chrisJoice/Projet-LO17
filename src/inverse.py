# # Import

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
import math

# # Variables 

stemmer = SnowballStemmer("french")
nlp = spacy.load("fr_core_news_sm")

try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd().parent

BULLETINS = BASE_DIR / "BULLETINS"
DATA = BASE_DIR / "data"
OUTPUT = BASE_DIR / "output"


def export_index(dictionnaire, fichier):

    with open(fichier, "w", encoding="utf-8") as f:
        for mot, docs in dictionnaire.items():
            ligne = mot + "\t"
            
            for doc, freq in docs.items():
                ligne += f"{doc}:{freq} "
            ligne += "\n"

            f.write(ligne)


def fichier_inverse(corpus, balise):
    try : 
        # obtenir le code html de la page
        with open(corpus, "r", encoding = "UTF8") as f :
            html = f.read()

        # cree un objet beautifulSoup en transmettant le code html à la fonction BeautifulSoup()
        soup = BeautifulSoup(html, 'html.parser' )
        type(soup)
        dictionnaire_index = {}
        corpus = soup.corpus
        all_documents = corpus.find_all("document")
        for doc in all_documents :
            num_article = doc.article.get_text()
            # val_balise = doc.balise.get_text()    # ici comment faire pour qu'il prenne le pbalise du paramettre ?
            val_balise = doc.find(balise).get_text()
            texte = val_balise.split()
            # construction du dictionnaire qui vas contenir les mots et document du fichier inverse 
            for txt in texte :
                frequence = val_balise.count(txt)
                if frequence != 0 : 
                    if txt in dictionnaire_index :
                        if num_article not in dictionnaire_index[txt] :
                            dictionnaire_index[txt][num_article] = frequence
                    else :
                        dictionnaire_index[txt] = {num_article : frequence }

        # export du fichier inverse a partir du dictionnaire 
        fichier = DATA /f"inverse_{balise}.txt"
        export_index(dictionnaire_index, fichier) 
    
    except TypeError as e :
        print("erreur : ", e)


# ## test
corpus = OUTPUT /"corpus.xml"
fichier_inverse(corpus, "date")
fichier_inverse(corpus, "titre")
fichier_inverse(corpus, "rubrique")
fichier_inverse(corpus, "texte")