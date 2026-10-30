"""Vérifie que tout est prêt pour l'atelier.

Lance :  python verifier.py
Si tout va bien, il affiche « Installation OK » et une première réponse de Claude.
Sinon, il explique quoi corriger sur chaque ligne marquée [!!].
"""
import importlib.util
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
FICHIER_ENV = RACINE / ".env"
MODELE = "claude-haiku-5-5"
ENTETES = {"User-Agent": "ImmersionAgentIA/1.0 (atelier Holberton School)"}

SERVICES = [
    ("Open-Meteo (météo)", "https://api.open-meteo.com/v1/forecast?latitude=43.6&longitude=1.44&current=temperature_2m"),
    ("Wikipédia (résumés)", "https://fr.wikipedia.org/api/rest_v1/page/summary/Toulouse"),
    ("REST Countries (pays)", "https://restcountries.com/v3.1/translation/france?fields=name"),
    ("TheMealDB (recettes)", "https://www.themealdb.com/api/json/v1/1/filter.php?i=egg"),
    ("Hacker News (actualités)", "https://hacker-news.firebaseio.com/v0/topstories.json"),
]


def verifier_python(version=None):
    version = tuple((version or sys.version_info)[:2])
    texte = f"Python {version[0]}.{version[1]}"
    if version >= (3, 10):
        return True, texte
    return False, f"{texte} : il faut la version 3.10 ou plus récente."


def verifier_paquets():
    paquets = [("anthropic", "anthropic"), ("requests", "requests"), ("dotenv", "python-dotenv")]
    manquants = [nom for module, nom in paquets if importlib.util.find_spec(module) is None]
    if manquants:
        return False, f"Il manque {', '.join(manquants)} : lance  pip install -r requirements.txt"
    return True, "anthropic, requests et python-dotenv sont installés"


def verifier_cle():
    try:
        from dotenv import load_dotenv
        load_dotenv(FICHIER_ENV)
    except ImportError:
        pass
    cle = os.getenv("ANTHROPIC_API_KEY", "")
    if not cle:
        return False, "Clé introuvable : lance  python setup_cle.py"
    from setup_cle import cle_valide
    if not cle_valide(cle):
        return False, "La clé ne ressemble pas à une clé Claude (elle doit commencer par sk-ant-) : relance  python setup_cle.py"
    return True, f"Clé trouvée ({cle[:10]}…)"


def verifier_claude(client):
    import anthropic

    try:
        reponse = client.messages.create(
            model=MODELE,
            max_tokens=1000,
            messages=[{"role": "user", "content": (
                "Souhaite la bienvenue, en une phrase, à quelqu'un qui va "
                "programmer son premier agent IA aujourd'hui."
            )}],
        )
    except anthropic.AuthenticationError:
        return False, "Clé refusée par Anthropic : vérifie-la avec  python setup_cle.py, ou demande une autre clé."
    except anthropic.PermissionDeniedError:
        return False, "Cette clé n'a pas accès à Claude : préviens un encadrant."
    except anthropic.NotFoundError:
        return False, f"Modèle introuvable ({MODELE}) : préviens un encadrant."
    except anthropic.RateLimitError:
        return False, "Trop de demandes, ou plafond de dépense atteint : attends une minute, puis préviens un encadrant."
    except anthropic.APIStatusError as erreur:
        return False, f"Erreur de l'API Claude ({erreur.status_code}) : réessaie dans une minute."
    except anthropic.APIConnectionError:
        return False, "Impossible de joindre Claude : vérifie ta connexion internet."
    texte = "".join(bloc.text for bloc in reponse.content if bloc.type == "text").strip()
    return True, texte or "Claude répond."


def verifier_services():
    import requests

    resultats = []
    for nom, url in SERVICES:
        try:
            reponse = requests.get(url, headers=ENTETES, timeout=5)
            ok = reponse.status_code == 200
            resultats.append((nom, ok, "joignable" if ok else f"erreur {reponse.status_code}"))
        except requests.RequestException:
            resultats.append((nom, False, "injoignable"))
    return resultats


def afficher(ok, nom, detail):
    print(f"  [{'OK' if ok else '!!'}] {nom} : {detail}")


def main():
    print("Vérification de ton installation\n")
    essentiels = [
        ("Python", verifier_python()),
        ("Paquets", verifier_paquets()),
        ("Clé Claude", verifier_cle()),
    ]
    for nom, (ok, detail) in essentiels:
        afficher(ok, nom, detail)
    pret = all(ok for _, (ok, _) in essentiels)

    if pret:
        import anthropic
        ok, detail = verifier_claude(anthropic.Anthropic())
        afficher(ok, "Réponse de Claude", detail)
        pret = ok

    print("\nServices utilisés par les outils :")
    services = verifier_services()
    for nom, ok, detail in services:
        afficher(ok, nom, detail)
    if not all(ok for _, ok, _ in services):
        print("  Un service injoignable n'empêche pas de commencer : seul l'outil qui l'utilise ne marchera pas.")

    if pret:
        print("\nInstallation OK. Passe à l'étape 1 :  python etapes/1_parler.py")
        return 0
    print("\nIl reste un problème : corrige les lignes marquées [!!], puis relance  python verifier.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
