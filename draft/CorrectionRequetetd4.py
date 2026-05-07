from pathlib import Path
import spacy
BASE_DIR = Path.cwd().parent
BULLETINS = BASE_DIR / "BULLETINS"
OUTPUT = BASE_DIR / "output"
DATA = BASE_DIR / "data"


# 1- fonction de création de notre lexique 
def charger_lexique(fichier):

    lexique = set()

    with open(fichier, "r", encoding="utf8") as f:
        for ligne in f:
            _, lemme = ligne.strip().split("\t")
            lexique.add(lemme)

    return lexique

# 2- tokenisation et lematisation de la requete
def analyser_requete(requete, nlp):    # nlp etant le modèle spacy

    doc = nlp(requete) # spacy transforme la requete en objet analysé , doc est donc la requete découpée en tokens 

    tokens = []

    for token in doc:
        if token.is_alpha: # verifie si c'est un vrai mot ( on ignore nombre , ponctuation )
            tokens.append(token.lemma_.lower()) # token.lemma_ : pour obtenir la forme de bas du mot , exemple : chercheurs devient chercheur 
                                                # lower pour transformer en minuscule 

    return tokens

# 3 distance levenshtien
def distance_levenshtein(a, b):

    if len(a) < len(b):
        return distance_levenshtein(b, a)

    if len(b) == 0:
        return len(a)

    previous_row = range(len(b) + 1)

    for i, c1 in enumerate(a):
        current_row = [i + 1]

        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)

            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]

# correcteur de la requete 
def corriger_mot(mot, lexique):

    # a) entité (nombre)
    if mot.isdigit():
        return mot

    # b) mot correct
    if mot in lexique:
        return mot

    # c) candidats par préfixe
    candidats = [] # liste vide pour stocker les mots proches de celui de la requete

    for mot_lex in lexique:
        if mot_lex.startswith(mot[:2]): # on compare les deux premières lettres
            candidats.append(mot_lex)

    # f) aucun candidat
    if len(candidats) == 0:
        return "[inconnu]"

    # d) un seul candidat
    if len(candidats) == 1:
        return candidats[0]

    # e) plusieurs candiadats  → Levenshtein
    meilleur = min(candidats, key=lambda x: distance_levenshtein(mot, x))

    return meilleur

# correction du mot
def corriger_requete(requete, lexique, nlp) : 
    
    tokens = analyser_requete(requete, nlp)

    resultat = []

    for mot in tokens:

        correction = corriger_mot(mot, lexique)

        resultat.append(correction)

    return resultat


# main 

nlp = spacy.load("fr_core_news_sm")

# lexique = charger_lexique(DATA/"lemmes.txt")

# requete = input("Tape ta requête : ")

# resultat = corriger_requete(requete, lexique, nlp)

# print("Correction :", " ".join(resultat))