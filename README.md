# Projet LO17 — Moteur de Recherche sur l'Archive ADIT

Système d'indexation et de recherche d'information sur une archive construite à partir du site de l'ADIT (Agence pour la Diffusion de l'Information Technologique). Le moteur permet d'interroger un corpus de bulletins en langage naturel français, avec filtrage par date, rubrique et mots-clés.

---

## Table des matières

- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Dépendances](#dépendances)
- [Architecture technique](#architecture-technique)
- [Utilisation](#utilisation)
- [Description des fichiers](#description-des-fichiers)

---

## Structure du projet

```
PROJET-LO17/
│
├── BULLETINS/                  # Données d'entrée (fichiers HTML bruts)
│
├── data/                       # Données intermédiaires générées
│   ├── inverse_date.txt        # Index inversé sur les dates
│   ├── inverse_rubrique.txt    # Index inversé sur les rubriques
│   ├── inverse_texte.txt       # Index inversé sur le texte des articles
│   ├── inverse_titre.txt       # Index inversé sur les titres
│   ├── lemmes.txt              # Lexique de lemmatisation
│   ├── new_antidictionnaire.txt
│   ├── antidictionnaire.txt    # Mots vides à exclure
│   ├── tf1.txt                 # Fréquences TF
│   ├── tfxidf.txt              # Scores TF-IDF
│   └── tokens.txt
│
├── output/                     # Résultats générés
│   └── corpus_final.xml        # Corpus XML structuré
│   ├── corpus_filtrer.xml      # corpus à pres le premier filtre basé sur tfxidf des tokens
│   └── corpus.xml              # corpus original (brut)
|
├── src/                        # Code source Python
│   ├── extraction.py           # Extraction et parsing des bulletins HTML
│   ├── inverse.py              # Construction des index inversés
│   ├── moteur.py               # Moteur de recherche principal
│   ├── traitement_requete.py   # Analyse et structuration des requêtes
│   ├── correction_requetetd4.py# Correction orthographique des requêtes
│   ├── lemmatisation.py        # Lemmatisation du corpus
│   ├── vocabulairetd2.py       # Construction du vocabulaire
│   └── main.py                 # Point d'entrée principal
│
├── README.md
└── requirements.txt
```

---

## Installation

**Prérequis :** Python 3.9+

```bash
# 1. Cloner le dépôt
git clone https://github.com/chrisJoice/Projet-LO17.git
cd PROJET-LO17

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Télécharger le modèle spaCy français
python -m spacy download fr_core_news_sm
```

---

## Dépendances

| Bibliothèque | Usage |
|---|---|
| `spacy` | Lemmatisation et analyse morphologique |
| `beautifulsoup4` | Parsing HTML/XML du corpus |
| `nltk` | Stemming (SnowballStemmer) |
| `pandas` | Manipulation des dates et données |
| `numpy` | Calculs numériques |
| `matplotlib` / `seaborn` | Visualisation (optionnel) |

---

# Architecture du système

Le moteur est organisé en plusieurs étapes.

```text
Bulletins HTML
       │
       ▼
Extraction HTML
       │
       ▼
Corpus XML structuré
       │
       ▼
Calcul TF / IDF / TF-IDF
       │
       ▼
Nettoyage 
       │
       ▼
Calcul TF / IDF / TF-IDF
       │
       ▼
lemmatisation + Nettoyage
       │
       ▼
Construction index inversés
       │
       ▼
Moteur de recherche
```

---

### Stratégie de recherche

Le moteur distingue deux types de filtres :

- **Filtres durs** (date, rubrique) → intersection stricte, un document doit obligatoirement les respecter
- **Filtres de pertinence** (texte, titre) → contribuent au score, le titre compte double

---

## Utilisation

Lancer le moteur depuis le terminal :

```bash
cd src
python main.py
```

L'interface demande une requête en langage naturel français :

```
==================================================
MOTEUR DE RECHERCHE LO17
==================================================

Entrer votre requête (ou 'quit' pour quitter) :
```

Puis propose un mode de tri :

```
Mode de tri :
1 - Pertinence
2 - Date croissante
3 - Date décroissante
```

---

## Description des fichiers

### `extraction.py`
Parse les bulletins HTML bruts du dossier `BULLETINS/` et construit un corpus XML structuré (`corpus.xml`). Extrait pour chaque article : identifiant, date, titre, rubrique, texte, auteur, images et contacts.

### `vocabulairetd2.py`
Construit le vocabulaire du corpus et calcule les statistiques linguistiques :
- fréquences TF ;
- scores IDF ;
- scores TF-IDF ;
- construction de l’antidictionnaire ;
- filtrage et lemmatisation du corpus ;
- construction des index inversés.

### `traitement_requete.py`
Analyse la requête utilisateur en langage naturel. Extrait les métadonnées (dates, rubrique, opérateurs booléens, exclusions) et structure la requête pour le moteur de recherche.

### `moteur.py`
Orchestre la recherche :
- charge les index inversés ;
- applique les filtres (date, rubrique) ;
- exécute la requête sur les index texte et titre ;
- calcule les scores de pertinence ;
- trie et affiche les résultats dans l’interface terminale.

### `correction_requetetd4.py`
Corrige les fautes d’orthographe de la requête utilisateur à l’aide :
- d’un lexique construit à partir des lemmes du corpus ;
- de la distance de Levenshtein ;
- d’une normalisation par lemmatisation spaCy.

### `main.py`
Point d’entrée principal du projet. Lance l’interface terminale interactive du moteur de recherche.

---

## Auteurs

Projet réalisé par MIGUEU Bryan et TEPI Joice
