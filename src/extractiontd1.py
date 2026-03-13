# import
from bs4 import BeautifulSoup
from pathlib import Path
import os

# Extraction de la date
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
    un = fichier.stem
    numeroArticle = un.replace("BULLETINS/", "")
    
    return numeroArticle

#Extraction du numéro de la rubrique

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


#Extraction du numéro de la rubrique

def recuperation_texte(fichier):
    try :
        # obtenir le code html de la page
        with open(fichier, "r", encoding = "UTF8") as f :
            html = f.read()

        # cree un objet beautifulSoup en transmettant le code html à la fonction BeautifulSoup()
        soup = BeautifulSoup(html, 'html.parser' )
        type(soup)

        # récuperer l'element 
        texte = ""
        racine = soup.body.div.table
        all_tr_niveau1 = racine.find_all("tr")
        tr_niveau1 = all_tr_niveau1[6]
        all_tr_niveau2 = tr_niveau1.td.table.find_all("tr")
        tr_niveau2 = all_tr_niveau2[2].td
        all_span = tr_niveau2.find_all("span")
        # recuperer tout les span. l'element qui caractérise le fait qu'un span soit un texte  est sa class qui est = style95
        for span in all_span:

            if span.get("class") == ["style95"]:
                texte = span.get_text() + " " + texte

        return texte
    
    except Exception as e:
        print("fichier", fichier , "erreur: ", e)
        return None
    

#Extraction du texte

def recuperation_auteur(fichier):
    # obtenir le code html de la page
    with open(fichier, "r", encoding = "UTF8") as f :
        html = f.read()

    # cree un objet beautifulSoup en transmettant le code html à la fonction BeautifulSoup()
    soup = BeautifulSoup(html, 'html.parser' )
    type(soup)

    # récuperer l'element 

    racine = soup.body.div.table
    all_span = racine.find_all("span")
    ligne = 0
    # parcourir le tableau all span jusqu'a trouver index du texte rédacteur : l'auteur est situé à l'indice suivant 
    for index, span in enumerate(all_span):
        if span.get_text().strip() == "Rédacteur :" or span.get_text().strip() == "Rédacteurs :" :
            ligne = index + 1
            break
    if ligne != 0:
        span = all_span[ligne]
        texte = span.get_text()
        traitement = [x.strip() for x in texte.split("-")]
        # print ("texte : ", texte)
        # print(traitement)
        # ça ne fonctionne plus si on change de redacteur, du coup faut essayer de revoir 
        if len(traitement)>2 :
            resultat = traitement[1] + "-" + traitement[2]
            return resultat
        else :
            print ("traitement < 2")
            return fichier
    print ("pas de ligne")
    return fichier

#Extraction des images 

def recuperation_images(fichier):

    try :
        # obtenir le code html de la page
        with open(fichier, "r", encoding = "UTF8") as f :
            html = f.read()

        # cree un objet beautifulSoup en transmettant le code html à la fonction BeautifulSoup()
        soup = BeautifulSoup(html, 'html.parser' )
        type(soup)

        # récuperer l'element 
        images = {}
        racine = soup.body.div.table
        all_tr_niveau1 = racine.find_all("tr")
        tr_niveau1 = all_tr_niveau1[6]
        all_tr_niveau2 = tr_niveau1.td.table.find_all("tr")
        tr_niveau2 = all_tr_niveau2[2].td
        all_div = tr_niveau2.find_all("div")
        # recuperer les images, les mettres dans un dictionnaire. chaque dictionnaire pocede une un url et une description
        for index, div in enumerate(all_div):
            images[f"image_{index}"] = {"url" : div.img.get("src"), "description": div.span.get_text()}

        return images
    except Exception as e:
        print("fichier", fichier , "erreur: ", e)
        return None
    

# Extraction du contact
def recuperation_information_contact(fichier):
    try : 
        # obtenir le code html de la page
        with open(fichier, "r", encoding = "UTF8") as f :
            html = f.read()

        # cree un objet beautifulSoup en transmettant le code html à la fonction BeautifulSoup()
        soup = BeautifulSoup(html, 'html.parser' )
        type(soup)

        # récuperer l'element 

        racine = soup.body.div.table
        all_span = racine.find_all("span")
        ligne = 0
        # parcourir le tableau all span jusqu'a trouver index du texte rédacteur : l'auteur est situé à l'indice suivant 
        for index, span in enumerate(all_span):
            if span.get_text().strip() == "Pour en savoir plus, contacts :" or span.get_text().strip() == "Rédacteurs :Pour en savoir plus, contact :" :
                ligne = index + 1
                break
        if ligne != 0:
            span = all_span[ligne]
            resultat = span.get_text()
            return resultat
        print ("pas de ligne")
        return fichier
    except Exception as e:
        print("fichier: ", fichier , "erreur: ", e)
        return None

#Partie XML pour un fichier

from bs4 import BeautifulSoup

def formationxml(fichier):
    date=extraire_date(fichier)
    numéroBul=extraire_numéroBul(fichier)
    numéroArticle=extraire_numéroArticle(fichier)
    titre = extraire_titre(fichier)
    rubrique = recuperation_rubrique(fichier)
    texte = recuperation_texte(fichier)
    auteur = recuperation_auteur(fichier)
    images = recuperation_images(fichier)
    contacts = recuperation_information_contact(fichier)
    xml = "<document>\n"
    xml += "<date>" + date + "</date>\n"
    xml += "<bulletin>" + numéroBul + "</bulletin>\n"
    xml += "<article>" + numéroArticle + "</article>\n"
    xml += "<titre>" + titre + "</titre>\n"
    xml += "<rubrique>" + rubrique + "</rubrique>\n"
    xml += "<texte>" + texte + "</texte>\n"
    xml += "<auteur>" + auteur + "</auteur>\n"
    if len(images) != 0 :
        xml += "<images>\n"
        for image in images :
            xml += "<image>\n"
            xml += "<urlImage>" + images[image]["url"] + "</urlImage>\n"
            xml += "<legendeImage>" + images[image]["description"] + "</legendeImage>\n"
            xml += "<image>\n"
        xml += "<images>\n"
    xml += "<contacts>" + contacts + "</contacts>\n"

    xml += "</document>\n"

    return xml

# Ecriture dans le corpus , pour l'ensemble des fichiers 

BASE_DIR = Path(__file__).resolve().parent.parent
BULLETINS = BASE_DIR / "BULLETINS"
OUTPUT = BASE_DIR / "output"

def ecriture_corpus():

    xml = "<corpus>\n"

    for fichier in BULLETINS.glob("*.htm"):
        print("Traitement :", fichier)

        doc = formationxml(fichier)

        xml += doc

    xml += "</corpus>"

    with open(OUTPUT / "corpus.xml", "w", encoding="utf8") as f:
        f.write(xml)

    print("ok")




