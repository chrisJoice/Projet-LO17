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

def extraire_titre(fichier):

    with open(fichier, "r", encoding="utf8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")

    titre_page = soup.title.text

    parties = titre_page.split(">")

    titre = parties[2].strip()

    return titre



#Extraction du numéro du bulletin

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

def extraire_numéroArticle(fichier):
    un = fichier.replace(".htm","")
    numeroArticle = un.replace("BULLETINS/", "")
    
    return numeroArticle


def recuperation_rubrique(fichier):
    # obtenir le code html de la page
    with open(fichier, "r", encoding = "UTF8") as f :
        html = f.read()

    # cree un objet beautifulSoup en transmettant le code html à la fonction BeautifulSoup()
    soup = BeautifulSoup(html, 'html.parser' )
    type(soup)

    # récuperer l'element 

    racine = soup.body.div.table
    all_span = racine.find_all("span")
    span = all_span[45]
    resultat = span.get_text()
    return resultat

#Partie XML pour un fichier

def formationxml(fichier):
    date=extraire_date(fichier)
    numéroBul=extraire_numéroBul(fichier)
    numéroArticle=extraire_numéroArticle(fichier)
    titre = extraire_titre(fichier)
    rubrique = recuperation_rubrique(fichier)
    
    xml = "<document>\n"
    xml += "<date>" + date + "</date>\n"
    xml += "<bulletin>" + numéroBul + "</bulletin>\n"
    xml += "<bulletin>" + numéroArticle + "</bulletin>\n"
    xml += "<titre>" + titre + "</titre>\n"
    xml += "<rubrique>" + rubrique + "</titre>\n"
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








