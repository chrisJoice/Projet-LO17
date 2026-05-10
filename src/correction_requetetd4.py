from pathlib import Path
import spacy

# =========================
# CONFIGURATION DES CHEMINS
# =========================
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd().parent

BULLETINS = BASE_DIR / "BULLETINS"
DATA = BASE_DIR / "data"
OUTPUT = BASE_DIR / "output"


# =========================
# CHARGEMENT DU LEXIQUE
# =========================

def charger_lexique(fichier_lemme):
    # le lexique ne comprte que les mots qui nous interesses 

    mots = set()        # lexique principal

    # lecture du lexique
    with open(fichier_lemme, "r", encoding="utf8") as f:
        for ligne in f:
            _, lemme = ligne.strip().split("\t")
            mots.add(lemme)

    # différence ensembliste
    return mots 


# ==========================================
# ANALYSE DE LA REQUETE (TOKEN + LEMME)
# ==========================================
def analyser_requete(requete : str , nlp):    # nlp = modèle spacy

    doc = nlp(requete)  # transformation en objet spaCy

    tokens = []

    for token in doc:
        if token.is_alpha:  # ignore ponctuation et chiffres
            tokens.append(token.lemma_.lower())  # token.lemma_ : pour obtenir la forme de bas du mot , exemple : chercheurs devient chercheur 
                                                # lower pour transformer en minuscule 
    return tokens


# =========================
# DISTANCE DE LEVENSHTEIN
# =========================
def distance_levenshtein(a, b):

    # on s'assure que a est le mot le plus long
    if len(a) < len(b):
        return distance_levenshtein(b, a)

    # cas de base
    if len(b) == 0:
        return len(a)

    previous_row = range(len(b) + 1)

    # calcul dynamique
    for i, c1 in enumerate(a):
        current_row = [i + 1]

        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)

            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]


# =========================
# CORRECTION D'UN MOT
# =========================
def corriger_mot(mot , lexique):

    # a) nombre → pas de correction
    if   mot.isdigit() : #nlp(mot)[0].like_num : #    # mot.like_num: 1er deuxième 1 2 2005 
        return mot

    # b) mot déjà correct
    if mot in lexique:
        return mot

    # c) génération de candidats (préfixe)
    candidats = []

    for mot_lex in lexique:
        if mot_lex.startswith(mot[:2] if len(mot) >= 2 else mot):  # filtre rapide
            candidats.append(mot_lex)

    # f) aucun candidat
    if len(candidats) == 0:
        return "[inconnu]"

    # d) un seul candidat
    if len(candidats) == 1:
        return candidats[0]

    # e) plusieurs candidats → distance minimale
    meilleur = min(candidats, key=lambda x: distance_levenshtein(mot, x))

    return meilleur


# =========================
# CORRECTION DE LA REQUETE
# =========================
def corriger_requete(requete : str , lexique , nlp): 
    
    tokens = analyser_requete(requete , nlp)

    resultat = []

    for mot in tokens:
        correction = corriger_mot(mot, lexique)
        resultat.append(correction)

    return resultat


# =========================
# MAIN (TEST)
# =========================

# nlp = spacy.load("fr_core_news_sm")

# lexique = charger_lexique(DATA/"lemmes.txt")

# while 1 :
#     print("\n______________________________________________")
#     requete = input("Tape ta requête : ")
#     resultat = corriger_requete(requete, lexique, nlp)
#     print("Correction : ", " ".join(resultat))
#     print("\n______________________________________________\n")