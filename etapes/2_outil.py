"""Étape 2 : donner un outil à Claude.

Claude ne peut pas consulter internet tout seul. On lui donne un outil :
une fonction Python (meteo, dans outils.py) et une fiche qui la décrit.
Quand Claude veut s'en servir, il nous le demande, on lance la fonction
et on lui renvoie le résultat.

Lance :  python etapes/2_outil.py
"""
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))  # pour trouver outils.py

from anthropic import Anthropic  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from outils import meteo  # noqa: E402

load_dotenv(RACINE / ".env")
if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit("Clé introuvable. Lance d'abord :  python setup_cle.py")

client = Anthropic()
MODELE = "claude-haiku-5-5"
SYSTEME = "Tu es un assistant météo. Réponds en français, en deux phrases au plus."

FICHE_METEO = {
    "name": "meteo",
    # TROU 1 : explique à Claude, en une phrase, ce que fait cet outil et quand s'en servir.
    #          C'est grâce à cette phrase qu'il saura qu'il peut l'utiliser.
    "description": "À COMPLÉTER",
    "input_schema": {
        "type": "object",
        "properties": {
            "ville": {"type": "string", "description": "Nom de la ville, ex. Toulouse"},
        },
        "required": ["ville"],
    },
}


def texte_de(reponse):
    return "".join(bloc.text for bloc in reponse.content if bloc.type == "text")


def repondre(question):
    messages = [{"role": "user", "content": question}]
    reponse = client.messages.create(
        model=MODELE, max_tokens=4000, system=SYSTEME, tools=[FICHE_METEO], messages=messages,
    )
    print(f"  (Claude s'arrête pour la raison : {reponse.stop_reason})")
    if reponse.stop_reason != "tool_use":
        return texte_de(reponse)

    # Claude demande un outil : on garde sa demande dans l'historique
    messages.append({"role": "assistant", "content": reponse.content})

    resultats = []
    for bloc in reponse.content:
        # TROU 2 : reponse.content contient plusieurs blocs (réflexion, texte, outil...).
        #          Passe au bloc suivant (avec continue) si son type n'est pas "tool_use".
        raise NotImplementedError("TROU 2 : ne garde que les blocs de type tool_use")

        print(f"  [outil] {bloc.name}({bloc.input})")
        resultat = meteo(**bloc.input)  # on lance vraiment la fonction Python

        # TROU 3 : range le résultat dans la liste resultats, sous cette forme :
        #          {"type": "tool_result", "tool_use_id": bloc.id, "content": resultat}
        raise NotImplementedError("TROU 3 : range le résultat de l'outil dans resultats")

    # On renvoie tous les résultats à Claude, qui peut enfin répondre
    messages.append({"role": "user", "content": resultats})
    reponse = client.messages.create(
        model=MODELE, max_tokens=4000, system=SYSTEME, tools=[FICHE_METEO], messages=messages,
    )
    return texte_de(reponse)


def main():
    if FICHE_METEO["description"] == "À COMPLÉTER":
        sys.exit("Commence par le TROU 1 : décris l'outil météo pour Claude.")
    question = input("Question météo > ").strip() or "Je prends un parapluie à Toulouse aujourd'hui ?"
    print("Claude >", repondre(question))


if __name__ == "__main__":
    main()
