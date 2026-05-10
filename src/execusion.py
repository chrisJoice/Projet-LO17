import extractiontd1
import vocabulairetd2
import lemmatisation
import inverse
import traitement_requete
import correction_requetetd4
import moteur 
from pathlib import Path
from datetime import datetime
# chemins
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd().parent

BULLETINS = BASE_DIR / "BULLETINS"
DATA = BASE_DIR / "data"
OUTPUT = BASE_DIR / "output"

# =========================
# CONSTRUIRE LES FICHIERS IMPORTANTS 
# =========================

def contruction_fichiers() :
    extractiontd1.ecriture_corpus()
    vocabulairetd2.execution()
    lemmatisation.execution()
    inverse.execution()

# =========================
# RECUPERATION INFOS DOCUMENTS
# =========================

def recuperation_infos_documents(resultats, corpus):
    """
    resultats :
        dictionnaire {article : score}

    corpus :
        fichier corpus XML
    """

    from bs4 import BeautifulSoup

    # lecture du corpus
    with open(corpus, "r", encoding="utf8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")

    documents = soup.find_all("document")

    infos_documents = {}

    # parcours du corpus
    for document in documents:

        # article = identifiant du document
        balise_article = document.find("article")

        if balise_article:

            id_document = balise_article.get_text().strip()

            # vérifier si le document est dans les résultats
            if id_document in resultats:

                # récupération des informations
                titre = document.find("titre")
                date = document.find("date")
                rubrique = document.find("rubrique")

                infos_documents[id_document] = {

                    "score": resultats[id_document],

                    "titre": titre.get_text().strip() if titre else "",

                    "date": date.get_text().strip() if date else "",

                    "rubrique": rubrique.get_text().strip() if rubrique else ""
                }

    return infos_documents

def affichage_resultats(infos_documents):

    print("\n" + "=" * 70)
    print("RESULTATS DE RECHERCHE")
    print("=" * 70)

    # parcours des documents
    for id_document, infos in infos_documents.items():

        print("\n" + "-" * 70)

        print(f"DOCUMENT  : {id_document}")

        print(f"TITRE     : {infos['titre']}")

        print(f"DATE      : {infos['date']}")

        print(f"RUBRIQUE  : {infos['rubrique']}")

        print(f"SCORE     : {infos['score']}")

        print("-" * 70)

    print("\n" + "=" * 70)
    print("FIN DES RESULTATS")
    print("=" * 70)

# =========================
# INTERFACE TERMINAL
# =========================


def interface_terminal():

    print("=" * 50)
    print("MOTEUR DE RECHERCHE LO17")
    print("=" * 50)

    corpus = OUTPUT / "corpus.xml"

    while True:

        requete = input("\nEntrer votre requête (ou 'quit' pour quitter) : ")

        if requete.lower() in ["quit", "exit", "q"]:
            print("Fermeture du moteur.")
            break

        resultats = moteur.moteur(requete)

        if not resultats:
            print("Aucun résultat trouvé.")
            continue

        # récupération des infos AVANT le tri
        infos_documents = recuperation_infos_documents(resultats, corpus)

        print("\nMode de tri :")
        print("1 - Pertinence")
        print("2 - Date croissante")
        print("3 - Date décroissante")
        choix = input("Choix : ")

        def parse_date(item):
            date_str = item[1].get("date", "")
            try:
                # format corpus : YYYY/MM/DD
                return datetime.strptime(date_str, "%Y/%m/%d")
            except ValueError:
                return datetime.min

        if choix == "1":
            infos_documents = dict(
                sorted(
                    infos_documents.items(),
                    key=lambda x: x[1]["score"],
                    reverse=True
                )
            )

        elif choix == "2":
            infos_documents = dict(
                sorted(infos_documents.items(), key=parse_date, reverse=False)
            )

        elif choix == "3":
            infos_documents = dict(
                sorted(infos_documents.items(), key=parse_date, reverse=True)
            )

        affichage_resultats(infos_documents)

contruction_fichiers()
interface_terminal()
