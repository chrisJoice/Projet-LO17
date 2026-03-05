# Extraction de la date
from bs4 import BeautifulSoup

def extraire_date(fichier):

    with open(fichier, "r", encoding="utf8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")

    titre_page = soup.title.text

    parties = titre_page.split(">")

    date = parties[0].strip()

    return date



# Extraction du titre
from bs4 import BeautifulSoup

def extraire_titre(fichier):

    with open(fichier, "r", encoding="utf8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")

    titre_page = soup.title.text

    parties = titre_page.split(">")

    titre = parties[2].strip()

    return titre



#Extraction du numéro du bulletin
from bs4 import BeautifulSoup

def extraire_numéroBul(fichier):

    with open(fichier, "r", encoding="utf8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")

    titre_page = soup.title.text

    parties = titre_page.split(">")

    bulletin = parties[1].strip()

    numero_bulletin = bulletin.split()[-1]
    
    return numero_bulletin



#Extraction du numéro de l'article
from bs4 import BeautifulSoup

def extraire_numéroArticle(fichier):
    un = fichier.replace(".htm","")
    numeroArticle = un.replace("BULLETINS/", "")
    
    return numeroArticle


#Partie XML pour un fichier
from bs4 import BeautifulSoup

def formationxml(fichier):
    date=extraire_date(fichier)
    numéroBul=extraire_numéroBul(fichier)
    numéroArticle=extraire_numéroArticle(fichier)
    titre = extraire_titre(fichier)
    
    xml = "<document>\n"
    xml += "<date>" + date + "</date>\n"
    xml += "<bulletin>" + numéroBul + "</bulletin>\n"
    xml += "<bulletin>" + numéroArticle + "</bulletin>\n"
    xml += "<titre>" + titre + "</titre>\n"
    xml += "</document>\n"

    return xml


# Ecriture dans le corpus , pour l'ensemble des fichiers 
import os

xml = "<corpus>\n"

for fichier in os.listdir("BULLETINS"):

    if fichier.endswith(".htm"):

        chemin = "BULLETINS/" + fichier

        doc = formationxml(chemin)

        xml += doc

xml += "</corpus>"

with open("corpus.xml", "w", encoding="utf8") as f:
    f.write(xml)








