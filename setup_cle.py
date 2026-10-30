"""Enregistre ta clé Claude dans le fichier .env (à faire une seule fois).

Lance :  python setup_cle.py
Colle la clé écrite sur ta carte. Rien ne s'affiche pendant que tu colles : c'est normal.
Le fichier .env reste dans ton Codespace : il n'est jamais envoyé sur GitHub.
"""
import re
import sys
from getpass import getpass
from pathlib import Path

FICHIER_ENV = Path(__file__).resolve().parent / ".env"
NOM = "ANTHROPIC_API_KEY"
FORME = re.compile(r"^sk-ant-[A-Za-z0-9_-]{20,}$")


def cle_valide(cle):
    """Vérifie que la clé a la forme d'une clé Claude (sans l'envoyer nulle part)."""
    return bool(FORME.match(cle))


def enregistrer_cle(cle, chemin=None):
    """Écrit la clé dans .env, en remplaçant l'ancienne s'il y en avait une."""
    chemin = Path(chemin or FICHIER_ENV)
    lignes = []
    if chemin.exists():
        lignes = [ligne for ligne in chemin.read_text(encoding="utf-8").splitlines()
                  if not ligne.startswith(f"{NOM}=")]
    lignes.append(f"{NOM}={cle}")
    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    chemin.chmod(0o600)  # lisible par toi seul


def main():
    print("Colle la clé écrite sur ta carte, puis appuie sur Entrée.")
    print("(Rien ne s'affiche pendant que tu colles : c'est normal.)")
    for _ in range(3):
        cle = getpass("Clé > ").strip().strip("\"'").strip()
        if cle_valide(cle):
            enregistrer_cle(cle)
            print("Clé enregistrée. Étape suivante :  python verifier.py")
            return
        print("Cette clé ne ressemble pas à une clé Claude : elle doit commencer par sk-ant-. Réessaie.")
    sys.exit("Trois essais ratés : demande de l'aide à un encadrant.")


if __name__ == "__main__":
    main()
