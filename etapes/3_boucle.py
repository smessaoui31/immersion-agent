"""Étape 3 : la boucle agentique.

À l'étape 2, Claude ne pouvait utiliser un outil qu'une fois.
Ici, on le laisse enchaîner les outils autant qu'il veut, jusqu'à
pouvoir répondre : c'est ce qui fait de lui un agent.

Lance :  python etapes/3_boucle.py
Essaie : « Il fait combien à Toulouse et à Brest ? Calcule l'écart. »

Comme avant : quand un trou est une ligne « raise NotImplementedError(...) »,
supprime-la et écris ton code à sa place. Enregistre (Ctrl+S), puis relance.
"""
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))  # pour trouver outils.py

from anthropic import Anthropic  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from outils import OUTILS, executer_outil  # noqa: E402

load_dotenv(RACINE / ".env")
if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit("Clé introuvable. Lance d'abord :  python setup_cle.py")

client = Anthropic()
MODELE = "claude-haiku-5-5"
MAX_ETAPES = 8  # garde-fou : au-delà, l'agent s'arrête
SYSTEME = (
    "Tu es un assistant de voyage. Utilise tes outils dès qu'ils sont utiles. "
    "Réponds en français, en quelques phrases."
)


def texte_de(reponse):
    return "".join(bloc.text for bloc in reponse.content if bloc.type == "text")


def agent(question):
    messages = [{"role": "user", "content": question}]
    for etape in range(1, MAX_ETAPES + 1):
        reponse = client.messages.create(
            model=MODELE, max_tokens=4000, system=SYSTEME, tools=OUTILS, messages=messages,
        )
        messages.append({"role": "assistant", "content": reponse.content})

        # TROU 1 : si Claude ne demande pas d'outil (stop_reason différent de "tool_use"),
        #          c'est sa réponse finale : renvoie son texte avec texte_de(reponse).
        #          Indice : un « if » sur reponse.stop_reason, puis return.
        #          Supprime la ligne « raise » ci-dessous et écris ton code à sa place.
        raise NotImplementedError("TROU 1 : remplace cette ligne par ton code (arrête la boucle quand Claude a fini)")

        resultats = []
        for bloc in reponse.content:
            if bloc.type == "tool_use":
                print(f"  [étape {etape}] outil {bloc.name}({bloc.input})")
                # TROU 2 : lance l'outil avec executer_outil(bloc.name, bloc.input),
                #          puis ajoute le tool_result à resultats, comme à l'étape 2.
                #          Supprime la ligne « raise » ci-dessous et écris ton code à sa place.
                raise NotImplementedError("TROU 2 : remplace cette ligne par ton code (exécute l'outil et range son résultat)")

        # TROU 3 : renvoie tous les résultats à Claude, en ajoutant à messages :
        #          {"role": "user", "content": resultats}
        #          Sans ça, Claude redemande sans fin le même outil... jusqu'au garde-fou.
        #          Supprime la ligne « raise » ci-dessous et écris ton code à sa place.
        raise NotImplementedError("TROU 3 : remplace cette ligne par ton code (renvoie les résultats à Claude)")

    return "Je m'arrête : trop d'étapes."


def main():
    print("Pose une question (Entrée vide pour quitter).")
    while True:
        question = input("\nToi > ").strip()
        if not question:
            break
        print("Agent >", agent(question))


if __name__ == "__main__":
    main()
