# CLAUDE.md

Ce qui doit être vrai à chaque session sur ce dépôt.

## Ce que c'est

Le **site journal de construction** de la PrintNC (Atelier du Verdier), statique,
publié par **GitHub Pages** sur le domaine porté par `CNAME` —
**`atelierduverdier.fr`**. La racine du dépôt *est* le site publié : `index.html`,
les ressources (`photos/`, `miniatures/`, favicons) et l'outillage de génération
vivent tous ici.

## La règle d'or : `index.html` est ENGENDRÉ, jamais édité à la main

`index.html` est fabriqué par **`generer_site.py`** à partir des fichiers de
`data/`. Une retouche à la main est écrasée à la génération suivante — et pire,
elle survit juste assez longtemps pour qu'on la croie acquise. Pour changer le
site, on modifie la source dans `data/`, puis on régénère :

```bash
python3 generer_site.py
```

Il écrit `index.html` dans le dossier courant et annonce `Site genere : …`.

Commiter `data/…` **et** l'`index.html` régénéré **ensemble**.

## Où vit le contenu (`data/`)

`generer_site.py` (voir `construire()`) assemble la page à partir de :

* **`videos.csv`** — la chronologie, une ligne par vidéo :
  `date, phase, fichier, lien, texte, duree, jalon`.
  Les dates doivent être en `AAAA-MM-JJ` **avec les zéros** (`2026-06-09`, pas
  `2026-6-9`) : sinon le tri chronologique se dérègle.
  La phase vaut `meca`, `elec`, `soft` ou `laser`.
* **`mois.json`** — titres et descriptions des mois de la chronologie.
* **`maj.md`** → onglet « Mises à jour ». Journal des changements, **la plus
  récente en premier** (`# JJ mois AAAA — titre`, puis des sections `##`).
* **`doc.md`** → onglet « Documentation » (documentation de la machine).
* **`recit.md`** → onglet « Le récit ».
* **`glossaire.md`** → onglet « Glossaire ».

## Deux valeurs recopiées qui vieilliront

Les libellés et les couleurs des quatre phases sont écrits **deux fois** :
`phase_info` dans `generer_site.py` (ligne 22) et `PHASE_LABEL` / `PHASE_COLORS`
dans `gestion_site.py` (lignes 70-72). Ils concordent aujourd'hui. Ajouter une
phase ou changer une couleur d'un seul côté ne produit **aucune erreur** : le
site et l'interface de gestion se mettent simplement à raconter deux choses
différentes. Toucher les deux, toujours.

`lire_vfd.py` est ici une **copie octet pour octet** de celui du dépôt
`lire-vfd-huanyang`, gardée là pour être trouvable. Il n'a rien à voir avec le
site. Le corriger ici seulement, c'est le laisser faux là-bas.

## Le Markdown est lu par des convertisseurs maison, pas par CommonMark

Chaque onglet a son propre analyseur écrit à la main dans `generer_site.py` :
seul un sous-ensemble de Markdown est rendu.

| Convertisseur | Pour |
|---|---|
| `markdown_vers_html` | `maj.md` |
| `markdown_vers_html_doc` (ancres de titres, tableaux) | `doc.md`, `glossaire.md` |
| `markdown_vers_html_recit` | `recit.md` |

En ajoutant du contenu, **reprendre les tournures Markdown déjà présentes dans
ce fichier-là** : titres `#/##/###`, `**gras**`, `` `code` ``, listes `-`,
tableaux `|` dans doc et glossaire, liens `[texte](url)`. Ne pas supposer qu'une
syntaxe exotique passe — lire le convertisseur concerné, ou régénérer et
chercher le résultat dans `index.html`. Le gabarit HTML de la page est la chaîne
`MODELE` dans `generer_site.py`.

## Outillage

* **`gestion_site.py`** — interface PySide6/Qt6, l'outil du quotidien : tableau
  de bord, génération, ajout de vidéo, miniatures, publication Git, édition des
  données. Se lance d'ici par `python3 gestion_site.py`, ou par
  `./lancer_gestion_site.sh` si PySide6 est dans le venv `~/.venv/kit_site`.
  Le `README.md` donne l'installation.
* **`ajouter_video.sh <fichier.mp4>`** — en ligne de commande : archive la
  vidéo, fabrique la miniature (ffmpeg), ajoute la ligne à `videos.csv`,
  régénère.
* **`generer_miniatures.sh`** — les miniatures manquantes.
* **`remplir_durees.py`** — remplit les durées des vidéos.
* **`installer_dependances.sh`** — les dépendances selon la distribution.

## Publier, c'est tourné vers l'extérieur

`git push` **met le site en ligne** (GitHub Pages par `CNAME`). Il n'y a pas de
préproduction. Commiter librement, mais **demander avant de pousser**, sauf
consigne contraire. Pour prévisualiser, il suffit d'ouvrir l'`index.html`
engendré dans un navigateur.
