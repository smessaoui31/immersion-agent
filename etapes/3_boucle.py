"""Étape 3 : la boucle agentique.

À l'étape 2, Claude ne pouvait utiliser un outil qu'une fois.
Ici, on le laisse enchaîner les outils autant qu'il veut, jusqu'à
pouvoir répondre : c'est ce qui fait de lui un agent.

Lance :  python etapes/3_boucle.py
Essaie : « Il fait combien à Toulouse et à Brest ? Calcule l'écart. »
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
        raise NotImplementedError("TROU 1 : arrête la boucle quand Claude a fini")

        resultats = []
        for bloc in reponse.content:
            if bloc.type == "tool_use":
                print(f"  [étape {etape}] outil {bloc.name}({bloc.input})")
                # TROU 2 : lance l'outil avec executer_outil(bloc.name, bloc.input),
                #          puis range le tool_result dans resultats, comme à l'étape 2.
                raise NotImplementedError("TROU 2 : exécute l'outil et range son résultat")

        # TROU 3 : renvoie tous les résultats à Claude dans un message "user".
        #          Sans ça, Claude redemande sans fin le même outil... jusqu'au garde-fou.
        raise NotImplementedError("TROU 3 : renvoie les résultats à Claude")

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
