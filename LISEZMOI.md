# Kit de generation du site PrintNC — Aide-memoire

Ce dossier contient tout ce qu'il faut pour generer, mettre a jour et
publier le site journal de construction de la PrintNC.

## Installation rapide (premiere fois)

```bash
./installer_dependances.sh
```

Detecte ta distribution (Arch, Debian, Fedora) et installe Python, PySide6,
pyserial, ffmpeg et git. Voir le README.md pour le detail.

## Lancer l'interface graphique

```bash
python3 gestion_site.py
# ou, si PySide6 est dans un virtualenv :
./lancer_gestion_site.sh
```

L'interface propose six sections (barre laterale) :

| Page | Ce qu'elle fait |
| --- | --- |
| Tableau de bord | Stats (videos, mois, phases), etat Git |
| Generer le site | Regenere index.html a partir du CSV + markdown |
| Ajouter une video | Fichier + miniature ffmpeg + ligne CSV + regen |
| Miniatures | Genere les vignettes manquantes d'un dossier |
| Git — publier | git status, pull, commit + push |
| Donnees | Ouvre les fichiers sources (CSV, markdown) |

## Ajouter une video (flux complet)

### Via l'interface graphique (recommande)

1. Ouvrir `gestion_site.py`, page **Ajouter une video**
2. Choisir le fichier .mp4 (l'apercu de la miniature s'affiche)
3. Renseigner : date, phase, lien Instagram, legende
4. Cliquer **Ajouter et regenerer**
5. Page **Git — publier** → ecrire un message → **Committer**

### Via la ligne de commande (alternative)

```bash
chmod +x ajouter_video.sh        (une seule fois)
./ajouter_video.sh /chemin/vers/la_video.mp4
```

Le script demande la date, la phase, le lien et la legende, puis
regenere le site automatiquement.

## Modifier le contenu du site

| Fichier | Onglet du site | Format |
| --- | --- | --- |
| `data/videos.csv` | Timeline | CSV (date, phase, fichier, lien, texte) |
| `data/recit.md` | Le recit | Markdown |
| `data/maj.md` | Mises a jour | Markdown |
| `data/doc.md` | Documentation | Markdown |

Edite les fichiers dans ton editeur prefere, puis regenere le site.

### Ajouter un nouveau mois dans videos.csv

Si tu ajoutes des videos d'un mois qui n'existe pas encore, l'onglet est
cree automatiquement. Pour lui donner un beau titre, ouvre `generer_site.py`
et ajoute une ligne dans le dictionnaire `mois_info` (suivre le modele des
mois existants). Sinon, l'onglet apparait avec le nom du mois.

### Colonnes du CSV videos.csv

    date,phase,fichier,lien,texte

- `date`   : AAAA-MM-JJ (ex: 2026-07-15)
- `phase`  : `meca`, `elec` ou `soft`
- `fichier`: nom du .mp4 (ex: 18012345678901234.mp4)
- `lien`   : URL Instagram du reel
- `texte`  : legende affichee dans la timeline

## Generer les miniatures

Les miniatures sont des vignettes .jpg (480 px de large) extraites a 1 s
du debut de chaque video.

```bash
# Toutes les miniatures manquantes d'un dossier :
./generer_miniatures.sh /chemin/du/dossier/videos

# Ou via l'interface (page Miniatures)
```

## Publier sur GitHub Pages

Le site est heberge sur GitHub Pages via le depot
`atelierduverdier/printnc-build` (branche `main`).

Via l'interface (page **Git — publier**) :
1. Verifier que les fichiers modifies sont corrects
2. `git pull` si tu as modifie depuis une autre machine
3. Ecrire un message de commit
4. Cliquer **Committer** (le push est coche par defaut)

## Licences

| Quoi | Licence |
| --- | --- |
| Scripts Python et shell | **MIT** (libre, y compris usage commercial) |
| Documentation, designs, contenus | **CC BY-SA 4.0** (partage aux memes conditions) |

Voir le fichier `LICENSE` pour le texte integral.
