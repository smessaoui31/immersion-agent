"""Des fonctions prêtes à l'emploi pour ton thème.

Ici, il n'y a que les fonctions : pas de fiches pour Claude.
Pour en utiliser une dans ton agent :
  1. importe-la dans outils.py, ex. :  from outils_bonus import infos_pays
  2. écris sa fiche dans OUTILS (nom, description, paramètres) ;
  3. inscris-la dans FONCTIONS.
Écrire une bonne fiche, c'est ton travail : c'est elle qui fait que
Claude utilise l'outil au bon moment.
"""
import random
import re
from pathlib import Path
from urllib.parse import quote

import requests

DELAI = 10  # secondes avant d'abandonner un appel réseau
ENTETES = {"User-Agent": "ImmersionAgentIA/1.0 (atelier Holberton School)"}
DOSSIER = Path(__file__).resolve().parent / "donnees"


def _appeler(url, params=None):
    """Appelle un service web. Renvoie None si la page n'existe pas (erreur 404)."""
    reponse = requests.get(url, params=params, headers=ENTETES, timeout=DELAI)
    if reponse.status_code == 404:
        return None
    reponse.raise_for_status()
    return reponse.json()


def _couper(texte, limite=1500):
    return texte if len(texte) <= limite else texte[:limite] + "…"


# ---------- Voyage : infos sur un pays (REST Countries) ----------

def infos_pays(pays):
    """Capitale, langues, monnaie et population d'un pays (nom en français ou en anglais)."""
    donnees = _appeler(
        f"https://restcountries.com/v3.1/translation/{quote(pays.strip())}",
        params={"fields": "name,translations,capital,currencies,languages,population"},
    )
    if not donnees:
        return f"Pays introuvable : {pays}"
    p = donnees[0]
    nom = p.get("translations", {}).get("fra", {}).get("common") or p["name"]["common"]
    capitale = ", ".join(p.get("capital", [])) or "?"
    langues = ", ".join(p.get("languages", {}).values()) or "?"
    monnaies = ", ".join(f"{m['name']} ({m.get('symbol', '?')})" for m in p.get("currencies", {}).values()) or "?"
    population = f"{p.get('population', 0):,}".replace(",", " ")
    return f"{nom} : capitale {capitale}, langue(s) {langues}, monnaie {monnaies}, {population} habitants."


# ---------- Révision : résumé Wikipédia ----------

def resume_wikipedia(sujet):
    """Résumé de l'article Wikipédia en français sur un sujet."""
    titre = sujet.strip().replace(" ", "_")
    donnees = _appeler(f"https://fr.wikipedia.org/api/rest_v1/page/summary/{quote(titre)}")
    if not donnees:
        return f"Aucun article Wikipédia pour : {sujet}"
    if donnees.get("type") == "disambiguation":
        return f"« {sujet} » a plusieurs sens : précise ta recherche."
    return f"{donnees['title']} : {_couper(donnees.get('extract', ''))}"


# ---------- Cuisine : recettes (TheMealDB) ----------

def recettes_avec(ingredient):
    """Jusqu'à 5 recettes contenant un ingrédient, à donner en anglais (egg, chicken, tomato)."""
    donnees = _appeler(
        "https://www.themealdb.com/api/json/v1/1/filter.php",
        params={"i": ingredient.strip().lower().replace(" ", "_")},
    )
    plats = (donnees or {}).get("meals")
    if not plats:
        return (f"Aucune recette avec « {ingredient} ». "
                "Astuce : l'ingrédient doit être en anglais (egg, chicken, tomato).")
    liste = " ; ".join(f"{plat['strMeal']} (id {plat['idMeal']})" for plat in plats[:5])
    return f"Recettes avec {ingredient} : {liste}"


def detail_recette(id_recette):
    """Ingrédients et étapes d'une recette, à partir de son id."""
    donnees = _appeler("https://www.themealdb.com/api/json/v1/1/lookup.php", params={"i": id_recette})
    plats = (donnees or {}).get("meals")
    if not plats:
        return f"Recette introuvable : {id_recette}"
    plat = plats[0]
    ingredients = []
    for n in range(1, 21):
        nom = (plat.get(f"strIngredient{n}") or "").strip()
        dose = (plat.get(f"strMeasure{n}") or "").strip()
        if nom:
            ingredients.append(f"{dose} {nom}".strip())
    return (f"{plat['strMeal']}. Ingrédients : {', '.join(ingredients)}. "
            f"Étapes : {_couper(plat.get('strInstructions', ''))}")


# ---------- Veille tech : actualités (Hacker News) ----------

def actus_tech(nombre=5):
    """Les articles les plus populaires du moment sur Hacker News (10 au maximum)."""
    nombre = max(1, min(int(nombre), 10))
    identifiants = _appeler("https://hacker-news.firebaseio.com/v0/topstories.json") or []
    lignes = []
    for identifiant in identifiants[:nombre]:
        article = _appeler(f"https://hacker-news.firebaseio.com/v0/item/{identifiant}.json")
        if not article:
            continue
        lien = article.get("url") or f"https://news.ycombinator.com/item?id={identifiant}"
        lignes.append(f"{len(lignes) + 1}. {article['title']} ({article.get('score', 0)} points) {lien}")
    return "\n".join(lignes) or "Aucune actualité disponible."


# ---------- Jeu : lancer de dés ----------

def lancer_des(nombre=1, faces=6):
    """Lance des dés et donne chaque résultat et le total."""
    nombre, faces = int(nombre), int(faces)
    if not (1 <= nombre <= 20 and 2 <= faces <= 100):
        return "Il faut entre 1 et 20 dés, de 2 à 100 faces."
    tirages = [random.randint(1, faces) for _ in range(nombre)]
    return f"Dés : {', '.join(map(str, tirages))}. Total : {sum(tirages)}."


# ---------- Fichiers : mémoire, inventaire, liste de courses ----------

NOM_AUTORISE = re.compile(r"^[A-Za-z0-9_-][A-Za-z0-9_.-]*$")


def _chemin(nom):
    """Chemin du fichier dans le dossier donnees/, ou None si le nom est dangereux."""
    if not NOM_AUTORISE.match(nom or ""):
        return None
    return DOSSIER / nom


def ecrire_fichier(nom, contenu):
    """Écrit (ou remplace) un fichier texte dans le dossier donnees/."""
    chemin = _chemin(nom)
    if chemin is None:
        return f"Nom de fichier refusé : {nom}"
    DOSSIER.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")
    return f"Fichier {nom} enregistré ({len(contenu)} caractères)."


def lire_fichier(nom):
    """Lit un fichier texte du dossier donnees/."""
    chemin = _chemin(nom)
    if chemin is None:
        return f"Nom de fichier refusé : {nom}"
    if not chemin.exists():
        return f"Fichier introuvable : {nom}"
    return chemin.read_text(encoding="utf-8")
