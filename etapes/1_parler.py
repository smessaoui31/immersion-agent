"""Étape 1 : parler à Claude.

Objectif : tenir une conversation de plusieurs tours avec Claude.
Lance :  python etapes/1_parler.py

Complète les TROUS dans l'ordre. Quand un trou est une ligne
« raise NotImplementedError(...) », supprime-la et écris ton code à sa place,
en suivant le commentaire juste au-dessus. Enregistre (Ctrl+S), puis relance :
le programme te dit quel trou il te reste à faire.

Défi final : dis-lui ton prénom, puis demande-lui comment tu t'appelles.
"""
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit("Clé introuvable. Lance d'abord :  python setup_cle.py")

client = Anthropic()
MODELE = "claude-haiku-5-5"

# TROU 1 : décris en une ou deux phrases qui est ton assistant et comment il parle.
#          Exemple : "Tu es un pirate qui répond en trois phrases au plus."
SYSTEME = "À COMPLÉTER"


def demander(messages):
    """Envoie tout l'historique à Claude et renvoie le texte de sa réponse."""
    reponse = client.messages.create(
        model=MODELE,
        max_tokens=4000,
        system=SYSTEME,
        messages=messages,
    )
    return "".join(bloc.text for bloc in reponse.content if bloc.type == "text")


def discuter(messages, question):
    """Ajoute la question à l'historique, obtient la réponse et l'ajoute aussi."""
    # TROU 2 : ajoute la question à la liste messages.
    #          Format d'un message : {"role": "user", "content": question}
    #          En Python, on ajoute un élément à une liste avec : ma_liste.append(element)
    #          Supprime la ligne « raise » ci-dessous et écris ton code à sa place.
    raise NotImplementedError("TROU 2 : remplace cette ligne par ton code (ajoute la question à messages)")

    reponse = demander(messages)

    # TROU 3 : ajoute la réponse de Claude à messages, avec le rôle "assistant".
    #          Même principe qu'au TROU 2. Sans cette ligne, Claude oublie tout
    #          d'un tour à l'autre : une fois que tout marche, mets-la en commentaire pour voir !
    #          Supprime la ligne « raise » ci-dessous et écris ton code à sa place.
    raise NotImplementedError("TROU 3 : remplace cette ligne par ton code (ajoute la réponse de Claude à messages)")

    return reponse


def main():
    if SYSTEME == "À COMPLÉTER":
        sys.exit("Commence par le TROU 1 : donne un rôle à ton assistant dans SYSTEME.")
    messages = []
    print("Discute avec Claude (Entrée vide pour quitter).")
    while True:
        question = input("\nToi > ").strip()
        if not question:
            break
        print("Claude >", discuter(messages, question))


if __name__ == "__main__":
    main()
