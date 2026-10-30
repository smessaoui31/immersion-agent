"""Les outils de ton agent.

Un outil, ce sont deux choses :
  1. une fonction Python qui fait le travail ;
  2. une fiche, dans OUTILS, qui explique à Claude à quoi sert l'outil
     et quelles informations lui donner.

Pour ajouter un outil :
  1. écris (ou copie depuis outils_bonus.py) la fonction ;
  2. ajoute sa fiche dans la liste OUTILS ;
  3. inscris la fonction dans le dictionnaire FONCTIONS.
"""
import ast
import operator

import requests

DELAI = 10  # secondes avant d'abandonner un appel réseau


def appeler(url, params=None, headers=None):
    """Appelle un service web et renvoie sa réponse JSON."""
    reponse = requests.get(url, params=params, headers=headers, timeout=DELAI)
    reponse.raise_for_status()
    return reponse.json()


# ---------- Outil 1 : la météo (Open-Meteo, gratuit, sans clé) ----------

def meteo(ville):
    """Météo actuelle et du jour pour une ville."""
    geo = appeler(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ville, "count": 1, "language": "fr"},
    )
    if not geo.get("results"):
        return f"Ville introuvable : {ville}"
    lieu = geo["results"][0]
    donnees = appeler(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lieu["latitude"],
            "longitude": lieu["longitude"],
            "current": "temperature_2m,wind_speed_10m,precipitation",
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_probability_max",
            "timezone": "auto",
            "forecast_days": 1,
        },
    )
    maintenant = donnees["current"]
    jour = donnees["daily"]
    return (
        f"{lieu['name']} ({lieu.get('country', '?')}) : "
        f"{maintenant['temperature_2m']} °C, vent {maintenant['wind_speed_10m']} km/h, "
        f"pluie {maintenant['precipitation']} mm. "
        f"Aujourd'hui : de {jour['temperature_2m_min'][0]} à {jour['temperature_2m_max'][0]} °C, "
        f"risque de pluie {jour['precipitation_probability_max'][0]} %."
    )


# ---------- Outil 2 : la calculatrice ----------

OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluer(noeud):
    """Évalue l'expression morceau par morceau, sans jamais exécuter de code."""
    if isinstance(noeud, ast.Constant) and type(noeud.value) in (int, float):
        return noeud.value
    if isinstance(noeud, ast.BinOp) and type(noeud.op) in OPERATIONS:
        gauche, droite = _evaluer(noeud.left), _evaluer(noeud.right)
        if isinstance(noeud.op, ast.Pow) and abs(droite) > 100:
            raise ValueError("puissance trop grande")
        return OPERATIONS[type(noeud.op)](gauche, droite)
    if isinstance(noeud, ast.UnaryOp) and type(noeud.op) in OPERATIONS:
        return OPERATIONS[type(noeud.op)](_evaluer(noeud.operand))
    raise ValueError("seuls les nombres, + - * / ** et les parenthèses sont acceptés")


def calcul(expression):
    """Calcule une expression simple, ex. (300 - 120) / 3."""
    try:
        resultat = _evaluer(ast.parse(expression.replace(",", "."), mode="eval").body)
        if isinstance(resultat, float):
            resultat = round(resultat, 2)
            if resultat.is_integer():
                resultat = int(resultat)
        return str(resultat)
    except ZeroDivisionError:
        return "Calcul impossible : division par zéro"
    except (ValueError, SyntaxError, TypeError, OverflowError) as erreur:
        return f"Calcul impossible : {erreur}"


# ---------- Les fiches lues par Claude ----------

OUTILS = [
    {
        "name": "meteo",
        "description": (
            "Donne la météo actuelle et celle du jour pour une ville : température, "
            "vent, pluie. À utiliser dès qu'une question dépend du temps qu'il fait."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ville": {"type": "string", "description": "Nom de la ville, ex. Toulouse"},
            },
            "required": ["ville"],
        },
    },
    {
        "name": "calcul",
        "description": (
            "Calcule une expression mathématique (+ - * / ** et parenthèses). "
            "À utiliser pour tout calcul, même simple, plutôt que de calculer de tête."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Expression à calculer, ex. (300 - 120) / 3"},
            },
            "required": ["expression"],
        },
    },
]

# Le nom de chaque fiche, relié à la fonction Python qui fait le travail
FONCTIONS = {
    "meteo": meteo,
    "calcul": calcul,
}


def executer_outil(nom, arguments):
    """Lance l'outil demandé par Claude et renvoie toujours du texte."""
    fonction = FONCTIONS.get(nom)
    if fonction is None:
        return f"Outil inconnu : {nom}"
    try:
        return str(fonction(**arguments))
    except Exception as erreur:  # Claude lit l'erreur et peut corriger sa demande
        return f"Erreur de l'outil {nom} : {erreur}"
