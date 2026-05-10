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
import math 


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
    if nb_colonnes > 1:
        with open(file_name, "w", encoding="utf8") as f:
            for element in liste_finale:
                line = ""
                for i in range(nb_colonnes):
                    line += f"{element[i]}\t"
                line += "\n"
                f.write(line)

    elif nb_colonnes == 1:
        with open(file_name, "w", encoding="utf8") as f:
            for element in liste_finale:
                line = f"{element}\n"
                f.write(line)

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


def frequence_apparition(fichier,output_file) :

    with open(fichier, "r", encoding="utf8") as f:
            tf = {}
            for ligne in f:

                ligne = ligne.strip()           # enlever \n

                parties = ligne.split("\t")     # séparer

                doc = parties[0]       
                token = parties[1]

                cle = (doc, token)

                if cle not in tf:
                    tf[cle] = 1
                else:
                        tf[cle] = tf[cle] + 1
    # export 
    with open(output_file, "w", encoding="utf8") as f:
        for (doc, token), freq in tf.items():
            f.write(doc + "\t" + token + "\t" + str(freq) + "\n")
    print(f"successful exportation of --> {output_file} --> ✅")

def coefficients_idft(fichier,output_file) : 
    
    docs = set() # set permet de creer un ensemble d'éléments uniques(pas de doublons)
    df = {}
    idf = {}
    with open(fichier, "r", encoding="utf8") as f: # lemme c'est l'expor de extraction spyci

        for ligne in f:

            doc, token = ligne.strip().split("\t") # on supprime le \n et on separe , doc contient l'identifiant et token le token

            docs.add(doc) # on met les identifiants dans docs (sans les doublons) 

            if token not in df:
                df[token] = set()

            df[token].add(doc)   

    N = len(docs) 
    for token in df:

        dft = len(df[token])

        idf[token] = math.log10(N / dft)

    with open(output_file, "w", encoding="utf8") as f:
        for token, valeur in idf.items():
            f.write(token + "\t" + str(valeur) + "\n")

    print(f"successful exportation of --> {output_file} --> ✅")


def coefficients_tf_idft(file_idft, file_tftd, output_file): # fonction bryan
    # lecture des tf
    with open(DATA/file_idft, "r", encoding="utf8") as f:
        lignes_idf = f.readlines()

    # lecture des idf
    with open(DATA/file_tftd, "r", encoding="utf8") as f:
        lignes_tf = f.readlines()

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
    export(output_file, 3, tfxidf) # export bryan
    print(f"successful exportation of --> {output_file} --> ✅")

# construction du nouvel anti dictionaire 
def anti_dictionnaire(fichier, seuil_min , seuil_max, output_file): # fchier_tfxidf
    print(seuil_min, seuil_max)
    with open(fichier, 'r', encoding="utf8") as f :
        lines = f.readlines()
    
    # anti dictionnaire 
    liste_semi_finale = []
    for line in lines :
        coef = float(line.split()[2])
        token = line.split()[1]
        if  coef < seuil_min or coef > seuil_max :
            liste_semi_finale.append(token)

    # suppression de doublons 
    liste_finale = list(set(liste_semi_finale))

    # Ecriture dans le fichier 
    export(output_file, 1, liste_finale)

    print(f"successful exportation of --> {output_file} --> ✅")


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

def corpus_filtrer(corpus,antidictionnaire,output_file):
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
        champs = ["texte", "titre" , "legendeImage"]

        for champ in champs:

            balise = doc.find(champ)

            if balise:
                nouveau = substitue(balise.text,antidictionnaire )
                balise.string = nouveau

    # Sauvegarder le nouveau corpus
    with open(output_file, "w", encoding="utf8") as f:
        f.write(str(soup))
    print(f"successful exportation of --> {output_file} --> ✅")


# =========================
# DETERMINATION DES SEUILS
# =========================

def determination_seuils(fichier_tfxidf, seuil_min,seuil_max,  courbe = False ):

    #" je récupère les mots et les tfxidf"
    dict_tfxidf = {}
    with open(fichier_tfxidf, "r", encoding="utf-8") as f :
        for line in f :
            element = line.strip().split()
            dict_tfxidf[element[1]] = float(element[2])

    # je range par ordre decroissant de tfxidf
    dict_tfxidf = dict(sorted(dict_tfxidf.items(), key=lambda x: x[1], reverse=True)) 

    # je remplie mes liste pour mon graphe 
    rangs = []
    scores = []
    for index, (mot, score ) in enumerate(dict_tfxidf.items()) :
        rangs.append(index)
        scores.append(score)
    
    plt.plot(rangs, scores)

    plt.xlabel("rangs des mots")
    plt.ylabel("TF-IDF")
    plt.title("DISTRIBUTION DES MOTS PAR SCORE DE TF-IDF")

    # determination automatique des seuil
    # seuil_min = np.percentile(scores, pourcentage) # seuil en desous duquel on trouve 5 % des mots de tf-idf les plus faible 
    # seuil_max = np.percentile(scores, 100-pourcentage) # seuil au dessus duquel on trouve 5 % des mots de tf-idf les plus elevés

    # affichage des seuil sur le graphe 
    plt.axhline(y = seuil_min ,color = "red", label = "Seuil min")
    plt.axhline(y = seuil_max ,color = "green" ,label = "Seuil max")

        # comptages
    # nb_inf_min = sum(s < seuil_min for s in scores)

    # nb_entre = sum(seuil_min <= s <= seuil_max for s in scores)

    # nb_sup_max = sum(s > seuil_max for s in scores)

    # nb_total = len(scores)

    # print("seuil min :", seuil_min)
    # print("seuil max :", seuil_max)

    # print("inférieur min :", nb_inf_min)
    # print("entre min/max :", nb_entre)
    # print("supérieur max :", nb_sup_max)
    # print("total :", nb_total)

    # affichage 
    if courbe == True :
        plt.grid()
        plt.legend()
        plt.show()

    return seuil_min, seuil_max


#################################################
# TESTES
#################################################

def execution():
    fichier = DATA / "tokens.txt"
    chemin = OUTPUT/"corpus.xml"
    output_tf = DATA/"tf1.txt"
    output_idf = DATA/"idf.txt"
    output_tfxidf = DATA/"tfxidf.txt"
    anti_dic = DATA/"antidictionnaire.txt"
    c_filtrer = OUTPUT/"corpus_filtrer.xml"
    segmente(chemin)
    frequence_apparition(fichier,output_tf)
    coefficients_idft(fichier,output_idf)
    coefficients_tf_idft(output_idf, output_tf, output_tfxidf )
    seuil_min,seuil_max = 0.75, 25 
    # seuil_min, seuil_max = determination_seuils(output_tfxidf, seuil_min, seuil_max, True)
    anti_dictionnaire(output_tfxidf,seuil_min, seuil_max,anti_dic  )
    corpus_filtrer(chemin, anti_dic, c_filtrer)

