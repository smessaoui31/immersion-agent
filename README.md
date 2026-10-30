# Immersion : ton premier agent IA

Pendant deux jours, tu vas programmer un **agent** : un assistant qui ne se contente pas de répondre, mais qui utilise de vrais outils (météo, Wikipédia, recettes...) pour aller chercher l'information avant de répondre.

Tout se passe dans ton navigateur. Rien à installer sur ton ordinateur.

## 1. Démarrer (lundi matin, 1h maximum)

1. En haut de cette page : **Use this template**, puis **Create a new repository**. Choisis ton compte, donne un nom, coche **Private**, puis **Create repository**.
2. Dans ton nouveau dépôt : bouton vert **Code**, onglet **Codespaces**, puis **Create codespace on main**. Attends 2 à 3 minutes : l'éditeur s'ouvre dans ton navigateur.
3. Dans le terminal, en bas de l'écran, tape :
   ```
   python setup_cle.py
   ```
   Colle la clé écrite sur ta carte. Rien ne s'affiche pendant que tu colles : c'est normal.
4. Puis :
   ```
   python verifier.py
   ```
   Quand tu lis **Installation OK**, c'est gagné.

Ton Codespace se met en veille après 30 minutes sans activité, par exemple au déjeuner. Pour le retrouver : [github.com/codespaces](https://github.com/codespaces). Tes fichiers sont conservés.

## 2. Jour 1 : trois étapes guidées

| Étape | Commande | Ce que tu apprends |
| --- | --- | --- |
| 1 | `python etapes/1_parler.py` | Parler à Claude et lui faire garder le fil de la conversation |
| 2 | `python etapes/2_outil.py` | Donner un outil à Claude : la météo |
| 3 | `python etapes/3_boucle.py` | La boucle : Claude enchaîne les outils tout seul |

Chaque fichier contient des **TROUS** à compléter, dans l'ordre. Lance le programme : il te dit lequel il te reste à faire.

## 3. Ton projet : `agent.py`

`agent.py` est un agent complet qui marche déjà, avec deux outils : la météo et une calculatrice. Lance-le :

```
python agent.py
```

Puis transforme-le en **ton** agent :

1. **Change son rôle** : modifie `SYSTEME` dans `agent.py`.
2. **Ajoute tes outils** dans `outils.py`, en trois gestes. Exemple avec les infos sur un pays :

   ```python
   # Geste 1 : en haut de outils.py, importe la fonction
   from outils_bonus import infos_pays

   # Geste 2 : dans la liste OUTILS, ajoute sa fiche
   {
       "name": "infos_pays",
       "description": "Donne la capitale, les langues, la monnaie et la population d'un pays. À utiliser pour toute question sur un pays.",
       "input_schema": {
           "type": "object",
           "properties": {"pays": {"type": "string", "description": "Nom du pays, ex. Portugal"}},
           "required": ["pays"],
       },
   },

   # Geste 3 : dans FONCTIONS, relie le nom à la fonction
   "infos_pays": infos_pays,
   ```

   La **description** est le plus important : c'est grâce à elle que Claude sait quand utiliser l'outil.

**Fonctions prêtes à l'emploi** dans `outils_bonus.py` (à toi d'écrire leur fiche) :

| Thème | Fonctions |
| --- | --- |
| Assistant voyage | `infos_pays(pays)` |
| Coach de révision | `resume_wikipedia(sujet)` |
| Chef cuisinier | `recettes_avec(ingredient)`, `detail_recette(id_recette)` (ingrédients en anglais) |
| Veille tech | `actus_tech(nombre)` |
| Maître du jeu | `lancer_des(nombre, faces)` |
| Pour tous | `ecrire_fichier(nom, contenu)`, `lire_fichier(nom)` (dans le dossier `donnees/`) |

Tu peux aussi écrire ta propre fonction : n'importe quelle fonction Python qui renvoie du texte peut devenir un outil.

## 4. Les paliers

| Palier | Ce que fait ton agent | Comment savoir que c'est réussi |
| --- | --- | --- |
| **Socle** | Un rôle personnalisé, au moins 2 outils dont un de ton thème | Il répond juste à 3 questions de ton thème, dont une qui demande 2 outils |
| **Avancé** | Il se souvient des conversations, et demande ta permission avant d'agir | Après redémarrage, il se souvient ; il n'écrit aucun fichier sans ton « oui » |
| **Expert** | Il confie une partie du travail à un second agent, et tu mesures sa qualité | 5 questions de test automatiques, un taux de réussite, le coût de chaque question |

Pistes pour l'**Avancé** :
- **Mémoire** : sors la liste `messages` de la fonction `agent()` pour la garder d'une question à l'autre, puis sauvegarde-la dans un fichier.
- **Permission** : avant de lancer un outil qui écrit, demande `input("Claude veut écrire ce fichier. OK ? (o/n) ")`.

Pistes pour l'**Expert** :
- **Sous-agent** : un outil dont la fonction appelle elle-même Claude, avec un autre rôle (par exemple un correcteur).
- **Évaluation** : une liste de 5 questions avec les mots attendus dans la réponse, et le pourcentage de réussite.
- **Coût** : `reponse.usage.input_tokens` et `reponse.usage.output_tokens`, multipliés par 0,10 $ et 0,50 $ par million de tokens.

## 5. Bon à savoir sur le modèle

Le modèle utilisé est `claude-haiku-5-5`. Beaucoup de tutoriels en ligne ont été écrits pour des modèles plus anciens. Avec celui-ci :

- **N'ajoute pas** `temperature`, `top_p` ni `top_k` : le modèle renvoie une erreur 400.
- La liste `messages` doit toujours **finir par un message `user`**.
- Chaque demande d'outil (`tool_use`) doit recevoir sa réponse (`tool_result`) dans le message suivant, sinon : erreur 400.
- Claude réfléchit parfois avant de répondre : sa réponse peut contenir des blocs `thinking`. On n'affiche que les blocs `text`.
- Garde les conversations sous 100 000 tokens : au-delà, le prix est multiplié par 5.

| Erreur | Ce qu'elle veut dire |
| --- | --- |
| 400 | Ta requête est mal formée : relis la liste ci-dessus |
| 401 | Clé refusée : relance `python setup_cle.py` |
| 429 | Trop de demandes : attends une minute |

## 6. Les règles du jeu

- **Ta clé est personnelle.** Elle reste dans le fichier `.env`, qui n'est jamais envoyé sur GitHub. Ne la colle nulle part ailleurs.
- **Bloqué ? Demande à trois camarades** avant d'appeler un encadrant. Expliquer, c'est aussi apprendre.
- **Sauvegarde ton travail sur GitHub**, au moins à la fin de chaque journée :
  ```
  git add -A
  git commit -m "Mon agent"
  git push
  ```

## Crédits

Données météo : [Open-Meteo](https://open-meteo.com) (CC BY 4.0). Résumés : [Wikipédia](https://fr.wikipedia.org) (CC BY-SA 4.0). Pays : [REST Countries](https://restcountries.com). Recettes : [TheMealDB](https://www.themealdb.com). Actualités : [Hacker News](https://news.ycombinator.com).
