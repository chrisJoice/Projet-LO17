
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
import math
import vocabulairetd2


# =========================
# VARIABLES
# =========================

stemmer = SnowballStemmer("french")
nlp = spacy.load("fr_core_news_sm")

try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd().parent

BULLETINS = BASE_DIR / "BULLETINS"
DATA = BASE_DIR / "data"
OUTPUT = BASE_DIR / "output"


# # 0. Découpage du corpus 

# =========================
# INDENTATION XML
# =========================

# permet d'indenter le xml 
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


# # 1. extraction

# =========================
# EXPORT DE DONNEES
# =========================

def export(file_name, nb_colonnes, liste_finale):
    if nb_colonnes > 1:
        with open(file_name, "w", encoding="utf-8") as f:
            for element in liste_finale:
                line = ""
                for i in range(nb_colonnes):
                    line += f"{element[i]}\t"
                line += "\n"
                f.write(line)

    elif nb_colonnes == 1:
        with open(file_name, "w", encoding="utf-8") as f:
            for element in liste_finale:
                line = f"{element}\n"
                f.write(line)
                

# =========================
# EXTRACTION AVEC SPACY
# =========================

def extraction_spacy(fichier):
    try:
        # Lecture du fichier
        with open(fichier, "r", encoding="UTF-8") as f:
            html = f.read()

        # Parsing HTML/XML
        soup = BeautifulSoup(html, 'html.parser')

        liste_finale = []
        all_document = soup.find_all("document")

        if not all_document:
            print("Aucun document trouvé")
            return

        for document in all_document:
            try:
                # Article
                article_tag = document.find("article")
                article = article_tag.get_text() if article_tag else "UNKNOWN"

                # Titre
                titre_tag = document.find("titre")
                titre = titre_tag.get_text().split() if titre_tag else []

                # Texte
                texte_tag = document.find("texte")
                texte = texte_tag.get_text().split() if texte_tag else []

                # Rubrique
                rubrique_tag = document.find("rubrique")
                rubrique = rubrique_tag.get_text().split() if rubrique_tag else []

                # Fusion des contenus --> on obtient une chaine de caractère qui correspond a input de nlp
                texte_document = " ".join(texte + titre + rubrique)

                # Traitement spaCy
                doc = nlp(texte_document)

                for token in doc:
                    cle = [article, token.lemma_]
                    liste_finale.append(cle)

            except Exception as e:
                print(f"Erreur sur un document : {e}")
                continue

        # Export
        try:
            
            export(DATA / "lemme.txt", 2, liste_finale)
        except Exception as e:
            print(f"Erreur lors de l'export : {e}")

    except Exception as e:
        print("Erreur globale :", e)
        print(fichier)


# =========================
# EXTRACTION AVEC SNOWBALL
# =========================

def extraction_snowball(fichier):
    try : 
        # obtenir le code html de la page
        with open(fichier, "r", encoding = "UTF8") as f :
            html = f.read()

        # cree un objet beautifulSoup en transmettant le code html à la fonction BeautifulSoup()
        soup = BeautifulSoup(html, 'html.parser' )

        # parse 
        all_document = soup.find_all("document")
        if not all_document:
            print("Aucun document trouvé")
            return
        
        # recuperaion du texte 
        liste_finale = []
        for document in all_document:
            try:
                # Article
                article_tag = document.find("article")
                article = article_tag.get_text() if article_tag else "UNKNOWN"

                # Titre
                titre_tag = document.find("titre")
                titre = titre_tag.get_text().split() if titre_tag else []

                # Texte
                texte_tag = document.find("texte")
                texte = texte_tag.get_text().split() if texte_tag else []

                # Rubrique
                rubrique_tag = document.find("rubrique")
                rubrique = rubrique_tag.get_text().split() if rubrique_tag else []

                # Fusion des contenus --> on obtient une liste de mots qui correspond a input de stem
                texte_document = texte + titre + rubrique
                
                # traitement snowball 
                for mot in texte_document :
                    if mot.isalpha():  # verrifie si le mot n'est constituer que des lettre et pas des chiffres
                        cle = [article , mot, stemmer.stem(mot.lower())] # mot et sa racine
                        liste_finale.append(cle)
                
            except Exception as e:
                print(f"Erreur sur un document : {e}")
                continue
        
        # Export
        try:
            
            export(DATA/"Extracionsnowball.txt", 3, liste_finale)
        except Exception as e:
            print(f"Erreur lors de l'export : {e}")

        
    except Exception as e:

        print("erreur  : ", e)
        print(fichier)


# =========================
# ANALYSE DES RESULTATS
# =========================

def analyse(fichier, methode):
    with open(fichier) as f :
        lines = f.readlines()
    
    # je sépare le fichier : je met les mots brute dans une 
    # liste et les reduction dans une autres pour faciliter les traitements
    mots = []
    reductions = []
    for line in lines :
        mots.append(line.split()[0])
        reductions.append(line.split()[1])

    # nombre de mot = nombre de mot unique pour les reduction 
    # car il y a potentiellement les doublons 
    nb_mots = len(reductions)
    nb_unique = len(set(reductions))
    print( f"nombre mots pour la methode {methode} : ",nb_mots )
    print( f"nombre mots unique pour la methode {methode} : ",nb_unique )

    # taux  de perte 
    taux = (1 - (nb_unique/nb_mots))*100
    print( f"taux de perte pour la methode {methode} : ", round(taux,2) ) # roud == deux chiffres apres la virgule

    # dsitribution : frequence d'apparition
    dictionnaire = {}
    for mot in reductions :
        if mot not in dictionnaire :
            dictionnaire[mot] = reductions.count(mot)

    print("distribution : -------------")
    for mot, freq in dictionnaire.items():
        print(mot, ":", freq  )
    print("distribution : -------------")


# # Affinage de l’anti-dictionnaire

# =========================
# CONSTRUCTION CORPUS FINAL
# =========================

def construire_corpusfinal(fichier_corpusfiltré , fichier_newantidictionnaire ,fichier_corpusfinal):

    nlp = spacy.load("fr_core_news_sm")

    with open(fichier_corpusfiltré, "r", encoding="utf8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")
    documents = soup.find_all("document")

    for doc in documents:
        champs = ["titre", "texte","rubrique" , "legendeImage"]

        for champ in champs:
            balise = doc.find(champ)
            if balise:
                #lemmatisation
                doc_spacy = nlp(balise.text)
                lemmes = []
                for token in doc_spacy:
                    if token.is_alpha:
                        lemmes.append(token.lemma_.lower())

                texte_lemmatise = " ".join(lemmes)
                #appliquer substitue
                nouveau = vocabulairetd2.substitue(texte_lemmatise, fichier_newantidictionnaire)
                #remplacer dans XML
                balise.string = nouveau
                
    with open(fichier_corpusfinal, "w", encoding="utf8") as f:
        f.write(str(soup))
    print("corpus filtrer --> ✅")


# # Inverse

# =========================
# EXPORT INDEX INVERSE
# =========================

def export_index(dictionnaire, fichier):

    with open(fichier, "w", encoding="utf-8") as f:
        for mot, docs in dictionnaire.items():
            ligne = mot + "\t"
            
            for doc, freq in docs.items():
                ligne += f"{doc}:{freq} "
            ligne += "\n"

            f.write(ligne)


# ===================================
# CONSTRUCTION FICHIER INVERSE
# ======================================

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
outpout_tf = DATA/"tf1_new.txt"
outpout_idf = DATA/"idf_new.txt"
outpout_tfxidf = DATA/"tfxidf_new.txt"
extraction_spacy(OUTPUT/"corpus_filtre.xml")
extraction_snowball(OUTPUT/"corpus_filtre.xml")
fichier = DATA/"lemmes.txt"
vocabulairetd2.frequence_apparition(fichier,outpout_tf)
vocabulairetd2.coefficients_idft(fichier,outpout_idf)
vocabulairetd2.coefficients_tf_idft(outpout_idf, outpout_tf,outpout_tfxidf )
fichier_tfxidf = DATA/"tfxidf_new.txt"
new_antidictionnaire = DATA/"new_antidictionnaire.txt"
seuil_min = 0.75
seuil_max = 25
vocabulairetd2.anti_dictionnaire(fichier_tfxidf, seuil_min, seuil_max, new_antidictionnaire)
corpus_filtrer = OUTPUT/"corpus_filtre.xml"
corpus_final = OUTPUT/"corpus_final.xml"
construire_corpusfinal(corpus_filtrer, new_antidictionnaire,corpus_final)






