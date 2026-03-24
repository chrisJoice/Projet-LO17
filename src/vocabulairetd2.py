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


#################################################
# CHEMAINS 
#################################################

try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd().parent

BULLETINS = BASE_DIR / "BULLETINS"
DATA = BASE_DIR / "data"
OUTPUT = BASE_DIR / "output"

#################################################
# FONCTIONS DE TRAITEMENT DE FICHIER
#################################################

# export des résultats
def export(file_name, nb_colonnes, liste_finale):
    if nb_colonnes > 1 :
        with open(file_name, "w") as f:
            for element in liste_finale :
                line = ""
                for i in range(nb_colonnes) :
                    line = line + f"{element[i]} \t" 
                line = line + " \n"
                f.writelines(line)
    if nb_colonnes == 1 :
        with open(file_name, "w") as f:
            for element in liste_finale :
                line = f"{element} \t" 
                f.writelines(line)

def segmente(corpus):
    with open(corpus , "r" , encoding="utf8") as c:
        contenu = c.read()

    tokens = []
    soup = BeautifulSoup(contenu , "html.parser")

    documents = soup.find_all("document")

    for doc in documents:

        id_document = doc.find("article").text
        titre = doc.find("titre").text
        texte = doc.find("texte").text

        texte_total = titre + " " + texte

        token = re.findall(r"\b\w+\b", texte_total.lower())

        for mot in token:
            tokens.append([id_document , mot])
            
    #export des fichiers
    export(DATA/"tokens.txt", 2, tokens)


def frequenced_apparition(fichier):

    # construction du dictionnaire de fichier  
    dictionnaire = {}
    with open(fichier, "r") as f:
        for ligne in f:
            ligne_element = ligne.split()

            if not ligne_element:
                continue

            if ligne_element[0] in dictionnaire:
                dictionnaire[ligne_element[0]].append(ligne_element[1])
            else:
                dictionnaire[ligne_element[0]] = []
                dictionnaire[ligne_element[0]].append(ligne_element[1])
    print(dictionnaire)
    # construction le la liste de liste contenant le id_document le token tftd
    liste_tftd  = []
    for dict in dictionnaire :
        for token in dictionnaire[dict] :
            tftd = dictionnaire[dict].count(token)
            cle = [dict, token, tftd ]
            if cle not in liste_tftd :
                liste_tftd.append(cle)

    # ecriture dans le fichier
    export(DATA/"frequence_tftd.txt", 3, liste_tftd)

def coefficients_idft(fichier):
    # construciton d'un ditionnaire dont les elements au niveau 1 sont les mots .
    # au niveau 2 on a une liste de id de documents dans les quelles on trouve ses mots 
    # {'pomme': ['1'], 'chaise': ['2']}
    dictionnaire = {}
    liste_document = []
    with open(fichier, "r") as f:
        for ligne in f:
            ligne_element = ligne.split()

            if not ligne_element:
                continue

            #construction de la liste de documents 
            liste_document.append(ligne_element[0])

            if ligne_element[1] in dictionnaire and ligne_element[0] not in dictionnaire[ligne_element[1]] :
                dictionnaire[ligne_element[1]].append(ligne_element[0])
            else:
                dictionnaire[ligne_element[1]] = []
                dictionnaire[ligne_element[1]].append(ligne_element[0])
   
        print(dictionnaire)
    N  = len(list(set(liste_document)))
    # construction le la liste de liste contenant le token idft
    liste_idft  = []
    for token in dictionnaire :
        dft = len(dictionnaire[token])
        idft = np.log10(N / dft)
        cle = [ token , round(idft,4) ]
        if cle not in liste_idft :
            liste_idft.append(cle)
    
    # ecriture dans le fichier
    export(DATA/"coeffecient_idft.txt", 2, liste_idft)


def coefficients_tf_idft(file_idft, file_tftd): # fonction bryan
    # lecture des tf
    with open(DATA/file_idft, "r", encoding="utf8") as f:
        lignes_tf = f.readlines()

    # lecture des idf
    with open(DATA/file_tftd, "r", encoding="utf8") as f:
        lignes_idf = f.readlines()

    tfxidf = []
    #  étape 1 : créer un dictionnaire des idf
    idf_dict = {}

    for ligne in lignes_idf:
        ligne = ligne.strip()
        parties = ligne.split("\t")
        token = parties[0]
        idf = float(parties[1])
        idf_dict[token] = idf

    #  étape 2 : calcul du tf-idf
    for ligne in lignes_tf:
        ligne = ligne.strip()
        parties = ligne.split("\t")

        doc = parties[0]
        token = parties[1]
        tf = float(parties[2])

        if token in idf_dict:
            idf = idf_dict[token]
            cle = [doc, token, tf * idf]
            if cle not in tfxidf :  # unicité bryan 
                tfxidf.append(cle)
    # étape 3 : écriture dans le fichier
    export(DATA/"fichier_tf_idft.txt", 3, tfxidf) # export bryan

def substitue(texte, fichier_substitution):
    subs = {}

    with open(fichier_substitution, "r", encoding="utf8") as f:
        for ligne in f:
            parties = ligne.strip().split("\t")
            mot = parties[0]
            if len(parties) > 1:
                remplace = parties[1]
            else:
                remplace = ""
            subs[mot] = remplace
    # découper le mot
    mots = re.findall(r"\b\w+\b", texte.lower())
    resultat = []
    for mot in mots:
        if mot in subs:
            if subs[mot] != "":
                resultat.append(subs[mot])
            # sinon supprimé
        else:
            resultat.append(mot)

    return " ".join(resultat)
    
def corpus_filtrer1(corpus,antidictionnaire):
    # Lire le corpus XML
    with open(OUTPUT/corpus, "r", encoding="utf8") as f:
        contenu = f.read()

    #Parser le XML
    soup = BeautifulSoup(contenu, "html.parser")

    #Trouver tous les documents
    documents = soup.find_all("document")

    #Parcourir chaque document
    for doc in documents:

        # Liste des balises à nettoyer
        champs = ["texte", "titre" , "rubrique" , "legendeImage"]

        for champ in champs:

            balise = doc.find(champ)

            if balise:
                nouveau = substitue(balise.text, DATA/antidictionnaire) # j'ai mis antidictionnaire comme variable 
                balise.string = nouveau

    # Sauvegarder le nouveau corpus
    with open(OUTPUT/"corpus_filtre.xml", "w", encoding="utf8") as f:
        f.write(str(soup))


def anti_dictionnaire(fichier, seuil_min , seuil_max):
    with open(fichier, 'r') as f :
        lines = f.readlines()
    
    # anti dictionnaire 
    liste_semi_finale = []
    for line in lines :
        coef = float(line.split()[3])
        token = line.split()[0]
        if  coef < seuil_min and coef > seuil_max :
            liste_semi_finale.append(token)

    # suppression de doublons 
    liste_finale = list(set(liste_semi_finale))

    # Ecriture dans le fichier 
    export(DATA/"frequence_tftd.txt", 1, liste_finale)


#################################################
# FONCTIONS DE TRAITEMENT DE FICHIER
#################################################
def courbe_analytique(fichier, id_doc):
    with open(fichier, 'r') as f :
        lines = f.readlines()
    # frequence vas collecter collecter les données
    frequence = {}

    # le id document c'est pour specifier le document dont on cherche les mots
    if id_doc == 0 :
        for line in lines :
            if float(line.split()[2]) > 20 :
                frequence[line.split()[0]] = float(line.split()[2])
    if id_doc != 0 :
        for line in lines :
            if int(line.split()[1]) == id_doc :
                frequence[line.split()[0]] = float(line.split()[2])
        
    plt.bar(frequence.keys(), frequence.values())
    print("taille :", len(frequence))
    print(frequence)
    plt.show()


#################################################
# TESTES
#################################################
fichier = DATA / "tokens.txt"
chemin = DATA/"corpus.xml"
segmente(chemin)
frequenced_apparition(fichier)
coefficients_idft(DATA/"frequence_tftd.txt")
coefficients_tf_idft(DATA/"coeffecient_idft.txt", OUTPUT/"frequence_tftd.txt" )
# testes de la courbe
fichier = OUTPUT/"fichier_tf_idft.txt"
courbe_analytique(fichier, 0)