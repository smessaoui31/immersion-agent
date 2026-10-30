"""Ton agent : le projet que tu vas personnaliser.

Lance-le avec :  python agent.py

Il fonctionne déjà avec deux outils (météo et calcul). À toi de :
  1. changer SYSTEME pour lui donner le rôle de ton thème ;
  2. lui ajouter tes propres outils dans outils.py ;
  3. viser le palier suivant (voir le README).
"""
import os
import sys
from pathlib import Path

from anthropic import Anthropic, APIError
from dotenv import load_dotenv

from outils import OUTILS, executer_outil

load_dotenv(Path(__file__).resolve().parent / ".env")
if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit("Clé introuvable. Lance d'abord :  python setup_cle.py")

client = Anthropic()
MODELE = "claude-haiku-5-5"
MAX_ETAPES = 8  # garde-fou : au-delà, l'agent s'arrête

# Personnalise ton agent ici : son rôle, son ton, ses règles.
SYSTEME = (
    "Tu es un assistant de voyage sympathique. "
    "Utilise tes outils dès qu'ils sont utiles, plutôt que de deviner. "
    "Réponds en français, en quelques phrases."
)


def texte_de(reponse):
    """Garde seulement le texte de la réponse (Claude peut aussi renvoyer sa réflexion)."""
    return "".join(bloc.text for bloc in reponse.content if bloc.type == "text")


def agent(question):
    """La boucle agentique : Claude utilise des outils jusqu'à pouvoir répondre."""
    messages = [{"role": "user", "content": question}]
    for _ in range(MAX_ETAPES):
        reponse = client.messages.create(
            model=MODELE,
            max_tokens=4000,
            system=SYSTEME,
            tools=OUTILS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": reponse.content})

        if reponse.stop_reason != "tool_use":
            return texte_de(reponse) or f"(Réponse vide, raison : {reponse.stop_reason})"

        resultats = []
        for bloc in reponse.content:
            if bloc.type == "tool_use":
                print(f"  [outil] {bloc.name}({bloc.input})")
                resultats.append({
                    "type": "tool_result",
                    "tool_use_id": bloc.id,
                    "content": executer_outil(bloc.name, bloc.input),
                })
        messages.append({"role": "user", "content": resultats})

    return "Je m'arrête : trop d'étapes."


def main():
    print("Ton agent est prêt. Pose une question (Entrée vide pour quitter).")
    try:
        while True:
            question = input("\nToi > ").strip()
            if not question:
                break
            try:
                print("Agent >", agent(question))
            except APIError as erreur:
                print("Problème avec Claude :", erreur)
    except (EOFError, KeyboardInterrupt):
        pass
    print("\nÀ bientôt !")


if __name__ == "__main__":
    main()
