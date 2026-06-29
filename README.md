# Kit de génération — PrintNC build log

Outils pour générer et maintenir le site journal de construction de la PrintNC.

## Contenu

```
printnc-build/                (depot GitHub, racine = site publie)
├── index.html              Site genere (NE PAS editer a la main)
├── lire_vfd.py             Outil de lecture des parametres du VFD HuangYang
├── photos/                 Photos affichees dans la documentation
├── miniatures/             Vignettes .jpg des videos
└── kit_site/               Outils de generation du site
    ├── gestion_site.py        Interface graphique Qt6 (RECOMMANDE — tout en un)
    ├── installer_dependances.sh  Installe les deps (Arch / Debian / Fedora)
    ├── ajouter_video.sh        Ajoute une video en ligne de commande (alternative)
    ├── generer_miniatures.sh   Extrait une vignette JPG de chaque video .mp4
    ├── convertir_photos.sh     Redimensionne les photos pour le web
    ├── generer_site.py         Genere index.html depuis les fichiers data/
    ├── favicon.svg             Logo du site (chapeau Orange Mecanique)
    ├── LICENSE                 Licences MIT (code) + CC BY-SA 4.0 (doc)
    ├── LISEZMOI.md             Aide-memoire rapide
    ├── data/
    │   ├── videos.csv          Liste des videos (date, phase, fichier, lien, texte)
    │   ├── maj.md               Changelog technique (onglet "Mises a jour")
    │   ├── doc.md               Documentation de la machine (onglet "Documentation")
    │   └── recit.md             Texte narratif (onglet "Le recit")
    ├── miniatures/              Vignettes .jpg generees (une par video)
    ├── photos/                  Photos (BOM, boitier, etc.)
    └── videos_sources/          Videos .mp4 sources (non versionnees)
```

> Note : `lire_vfd.py` est place a la racine du depot pour etre facilement
> trouvable et telechargeable par quiconque possede un VFD HuangYang.

---

## `gestion_site.py` — interface graphique (le plus simple)

Interface graphique (PySide6/Qt) qui regroupe **toutes** les operations dans
une seule fenetre : tableau de bord, generation du site, ajout de video,
generation de miniatures, synchronisation Git et edition des fichiers de
donnees. C'est le point d'entree recommande au quotidien.

### Installation des dependances (Arch / Debian / Fedora)

Un script d'installation automatique detecte ta distribution et installe
tout le necessaire : Python, PySide6, pyserial, ffmpeg, git + les librairies
runtime Qt (Wayland/X11).

```bash
./installer_dependances.sh
```

| Distribution | Packages installes |
| --- | --- |
| Arch / CachyOS / Manjaro | `python python-pyserial ffmpeg git python-pyside6` (pacman) |
| Debian / Ubuntu / Mint | `python3 python3-serial ffmpeg git` + PySide6 via pip (venv) |
| Fedora | `python3 python3-pyserial ffmpeg git` + `python3-pyside6` (dnf) |

> Si PySide6 n'est pas dans les depots de ta distribution (Debian, certains
> derives d'Arch), le script cree automatiquement un virtualenv dans
> `~/.venv/kit_site` et genere un lanceur `./lancer_gestion_site.sh` qu'il
> faudra utiliser a la place de `python3 gestion_site.py`.

**Dependances detaillees** :

| Dependance | Rôle | Obligatoire ? |
| --- | --- | --- |
| `python3` (>= 3.8) | interpreteur | oui |
| `PySide6` (Qt6) | interface graphique `gestion_site.py` | oui |
| `ffmpeg` | miniatures des videos (`Ajouter une video`, `Miniatures`) | oui |
| `git` | publication sur GitHub (page `Git`) | oui |
| `pyserial` | lecture VFD (`lire_vfd.py`) | non (sauf VFD) |

### Lancement (depuis le dossier `kit_site/`)

```bash
python3 gestion_site.py
# ou, si PySide6 est dans un venv :
./lancer_gestion_site.sh
```

La fenetre propose une barre laterale avec six sections :

- **Tableau de bord** — nombre de videos, mois couverts, repartition par phase
  (mecanique / electronique / LinuxCNC) et etat du depot Git (a jour, en
  avance, en retard).
- **Generer le site** — relance `generer_site.py` et (option) ouvre
  `index.html` dans le navigateur.
- **Ajouter une video** — selection du fichier, aperçu de la miniature, saisie
  de la date / phase / lien / legende, puis enchainement automatique : archive
  source, generation de la miniature (ffmpeg), ajout dans `videos.csv`,
  regeneration du site. Detection des doublons.
- **Miniatures** — genere les vignettes manquantes d'un dossier de videos.
- **Git — publier** — liste les fichiers modifies, `git pull`, et
  `commit` + `push` (avec message personnalise). Remplace l'ancien
  `goup_site.sh`.
- **Donnees** — ouvre `videos.csv`, `recit.md`, `maj.md`, `doc.md` dans ton
  editeur, avec un apercu du CSV.

Une **console** en bas affiche en temps reel les commandes lancees et leur
sortie (avec coloration des erreurs). Les taches s'executent l'une apres
l'autre, en arriere-plan, sans bloquer l'interface.

---

## `ajouter_video.sh` (alternative en ligne de commande)

Ajoute une nouvelle video au site **en une seule commande** : copie la video,
genere sa miniature, demande les informations, met a jour `videos.csv` et
regenere `index.html`. C'est la methode la plus simple pour ajouter un reel.

**Prerequis** : ffmpeg installe (voir section `generer_miniatures.sh`).

**Utilisation**

```bash
chmod +x ajouter_video.sh   # une seule fois

./ajouter_video.sh /chemin/vers/la_video_telechargee.mp4
```

**Ce que ça fait, dans l'ordre**

1. Copie le `.mp4` dans `videos_sources/` (archive locale, non versionnee).
2. Genere sa miniature dans `miniatures/` (extraction a 1s, repli a 0s si la
   video est trop courte).
3. Verifie si ce fichier est deja present dans `videos.csv` : si oui, affiche
   la/les ligne(s) existante(s) et demande confirmation avant d'ajouter un
   doublon (par defaut : abandon).
4. Demande interactivement :
   - **Date** au format `AAAA-MM-JJ` (Entree = date du jour). Une date
     incomplete comme `2026-6-9` est automatiquement normalisee en
     `2026-06-09` (necessaire pour que le tri chronologique reste correct).
   - **Phase** : `1` = meca, `2` = elec, `3` = soft (Entree = meca).
   - **Lien Instagram** : URL du reel (a copier depuis l'app/le site).
   - **Legende** : texte affiche dans la timeline (Entree = texte generique).
5. Ajoute la ligne correspondante dans `data/videos.csv`.
6. Relance `python3 generer_site.py` automatiquement.

**Exemple de session**

```
--------------------------------------------------
 Nouvelle video : 18123456789012345.mp4
--------------------------------------------------
Video copiee dans videos_sources/
Miniature generee : miniatures/18123456789012345.jpg

Date [AAAA-MM-JJ] (defaut: 2026-07-02) : 2026-7-2
Date retenue : 2026-07-02

Phase : 1) meca  2) elec  3) soft
Choix [1-3] (defaut: 1) : 3

Lien Instagram (URL du reel) : https://www.instagram.com/atelierduverdier/reel/XXXXXXXXXXX/

Legende / texte : Reglage fin du palpeur

Ligne ajoutee dans data/videos.csv

Regeneration du site...
Site genere : index.html (230 etapes, 7 mois)
--------------------------------------------------
 Termine ! Verifie index.html, puis lance
 goup_site.sh pour publier sur GitHub.
--------------------------------------------------
```

Si la video a deja ete ajoutee precedemment :

```
ATTENTION : '18123456789012345.mp4' est deja present dans data/videos.csv !
Ligne(s) existante(s) :
  231:2026-07-02,soft,18123456789012345.mp4,https://...,Reglage fin du palpeur

Ajouter quand meme une nouvelle ligne (doublon) ? [o/N] :
```
Repondre `o` pour forcer l'ajout (cas rare), ou laisser vide / `N` pour
annuler proprement.

---

## `goup_site.sh`

Envoie le site mis a jour vers GitHub (`git add` + `git commit` + `git push`).
A lancer depuis le dossier `kit_site/` une fois `index.html` regenere.

**Utilisation**

```bash
chmod +x goup_site.sh   # une seule fois

./goup_site.sh
```

Le script demande un message de commit (ou utilise un message par defaut si
on laisse vide), puis pousse sur la branche `main`.

> **Important** : ce script est different de `goup.sh` utilise pour la
> configuration LinuxCNC (depot `printnc-config`). Si `goup_site.sh`
> repond *"rien a valider, la copie de travail est propre"* alors que des
> fichiers ont ete modifies, c'est probablement que la commande a ete
> lancee depuis le mauvais dossier - verifier avec `pwd` et `git status`
> que l'on est bien dans `kit_site/` (le depot `printnc-build`).

---

## Workflow complet (nouvelle video Instagram)

```
1. Telecharger le reel (.mp4) depuis Instagram
2. ./ajouter_video.sh /chemin/vers/la_video.mp4
3. Repondre aux questions (date, phase, lien, legende)
4. Verifier index.html dans un navigateur
5. ./goup_site.sh
```

---

## `generer_miniatures.sh`

Extrait une image fixe a 1 seconde de chaque video `.mp4` et la sauvegarde en
`.jpg` dans le dossier `miniatures/`. Utilise **ffmpeg**. Saute les vignettes
deja generees (idempotent). Utile pour regenerer en masse les miniatures
(par exemple apres avoir recupere un export Instagram complet) ; pour une
video au cas par cas, preferer `ajouter_video.sh`.

**Prerequis**

```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# CachyOS / Arch
sudo pacman -S ffmpeg
```

**Utilisation**

```bash
# Vignettes des videos dans le dossier videos_sources/
./generer_miniatures.sh videos_sources/

# Ou sans argument : cherche dans le dossier courant
./generer_miniatures.sh
```

**Ce que ça fait**

- Parcourt recursivement les `.mp4` du dossier source.
- Pour chaque video, extrait une frame a `00:00:01`, redimensionnee a 480 px
  de large.
- Si la video est trop courte (echec a 1 s), essaie a `00:00:00`.
- Sortie : `miniatures/<nom_sans_extension>.jpg`

**Exemple de sortie**

```
Recherche des fichiers .mp4 dans : videos_sources/
Les miniatures seront placees dans : miniatures/

  [ok] 17867331942452959.jpg
  [deja fait] 18027183161788717.jpg
  [ok] 18109292998673295.jpg
  ...
Termine. Miniatures dans le dossier : miniatures/
```

---

## `generer_site.py`

Genere `index.html` - le site complet - a partir de `data/videos.csv`.
Tout le HTML, le CSS et le JavaScript sont produits par ce seul script.
Aucune dependance externe : Python 3 standard uniquement.

**Utilisation**

```bash
python3 generer_site.py
# -> produit index.html dans le dossier courant
```

**Sources lues**

| Fichier           | Role                                              |
| ----------------- | ------------------------------------------------- |
| `data/videos.csv` | Une ligne par video (obligatoire)                  |
| `data/maj.md`     | Changelog affiche dans l'onglet "Mises a jour"     |
| `data/doc.md`     | Documentation affichee dans l'onglet "Documentation" |
| `data/recit.html` | Texte narratif affiche dans l'onglet "Le recit"    |

**Format de `data/videos.csv`**

```
date,phase,fichier,lien,texte
2026-01-16,meca,17867331942452959.mp4,https://www.instagram.com/.../reel/DTkQUOqiPvb/,Description de l'etape
```

| Colonne   | Valeurs possibles                                            |
| --------- | -------------------------------------------------------------|
| `date`    | `AAAA-MM-JJ` (toujours avec les zeros, ex: `09` pas `9`)     |
| `phase`   | `meca` · `elec` · `soft`                                     |
| `fichier` | nom du `.mp4` (doit avoir une miniature dans `miniatures/`)  |
| `lien`    | URL publique du reel Instagram                               |
| `texte`   | legende affichee dans la timeline                            |

> Avec `ajouter_video.sh`, le format de la date et l'absence de doublon
> sont verifies automatiquement. En cas d'edition manuelle du CSV, veiller
> a garder le zero initial (`2026-06-09`, pas `2026-6-9`) pour que le tri
> chronologique reste correct.

**Ajouter un nouveau mois**

Le script cree automatiquement l'onglet du mois. Pour lui donner un titre et
une description, ajouter une entree dans le dictionnaire `mois_info` en haut
du script :

```python
'2026-07': {'nom': 'Juillet 2026', 'titre': 'Mon titre', 'desc': 'Ma description.'},
```

---

## GitHub Pages

Fichiers a publier : `index.html` + `miniatures/` + `photos/` (si des photos sont ajoutees)

Fichiers a **ne pas versionner** (voir `.gitignore`) :

```
videos_sources/
__pycache__/
```

Les videos `.mp4` n'ont pas a etre hebergees sur GitHub - seules les
vignettes et les liens Instagram sont necessaires au site.

---

## Inserer des photos dans la documentation

Les photos s'inserent dans `data/doc.md` avec la syntaxe markdown standard.
Le convertisseur les transforme en blocs `<figure>` avec legende.

**1. Preparer les photos** (redimensionner avant upload — les photos de
telephone font souvent 5-10 Mo, trop lourd pour GitHub) :

```bash
sudo pacman -S imagemagick   # si pas encore installe
convert photo_originale.jpg -resize 1400x -quality 80 photos/nom.jpg
```

**2. Creer le dossier et y deposer les photos**

```bash
mkdir -p ~/Projets/Site_PrintNC/kit_site/photos
cp photo.jpg ~/Projets/Site_PrintNC/kit_site/photos/
```

**3. Inserer dans `data/doc.md`** a l'endroit voulu :

```markdown
## Boitier electrique

![Description de la photo](photos/nom_du_fichier.jpg)

Suite du texte...
```

Le texte entre crochets `[...]` devient la legende affichee sous la photo.

**4. Regenerer et publier**

```bash
python3 generer_site.py
./goup_site.sh
```

GitHub Pages sert automatiquement le dossier `photos/` — aucune
configuration supplementaire.

> Conseil : viser 1200-1500 px de large en JPEG qualite 80% — suffisant
> pour l'affichage web, raisonnable en poids (100-300 Ko par photo).

**Clic pour agrandir (lightbox)** : les photos dans la documentation sont
automatiquement cliquables. Un clic affiche la photo en grand sur fond
sombre. Pour fermer : clic sur le fond, ou touche Echap.

---

## Points importants dans la documentation

Dans `data/doc.md`, tout paragraphe commencant par `**Point important`,
`**Important`, `**Attention` ou `**Note` est automatiquement mis en
evidence avec un fond orange et une bordure coloree.

```markdown
**Point important — mon sujet** : mon explication ici.
```

Pas de HTML necessaire, juste du markdown — le convertisseur s'en charge.

---

## Syntaxe markdown supportee dans `data/doc.md`

| Syntaxe | Resultat |
| ------- | -------- |
| `# Titre` | Section depliable (accordeon) |
| `## Sous-titre` | Sous-titre orange a l'interieur d'une section |
| `**texte**` | Gras |
| `` `code` `` | Code inline orange |
| ` ``` ... ``` ` | Bloc de code (fond sombre) |
| `- item` | Liste a puces |
| `\| col \| col \|` | Tableau (avec liens et gras dans les cellules) |
| `![legende](photos/nom.jpg)` | Photo cliquable avec legende |
| `> texte` | Citation / note en italique |
| `**Point important...**` | Bloc mis en evidence (fond orange) |

---

## `lire_vfd.py` — Lecture des paramètres du VFD HuangYang

Outil pour lire **tous les paramètres** d'un variateur de fréquence
HuangYang (Huanyang) directement via la liaison RS485, sans avoir à les
recopier un par un depuis le petit écran du VFD.

Le script communique en **HYComm**, le protocole série propriétaire de
HuangYang. C'est un point important : ces VFD n'utilisent **pas** le Modbus
RTU standard, donc une bibliothèque Modbus classique (comme minimalmodbus)
ne fonctionne pas avec eux. Le script implémente directement les bonnes
trames HYComm et décode les réponses (longueur variable selon que la valeur
tient sur 1 ou 2 octets).

**Prérequis**

```bash
pip3 install pyserial --break-system-packages
```

**Utilisation** (sur le Raspberry Pi, LinuxCNC ARRÊTÉ) :

```bash
python3 lire_vfd.py
```

> Important : arrêter LinuxCNC avant de lancer le script. Tant que LinuxCNC
> tourne, le composant `hy_vfd` occupe le port série et le script ne peut
> pas s'y connecter.

**Ce que fait le script**

1. Interroge les paramètres PD000 à PD189 du VFD en HYComm.
2. Valide chaque réponse par son CRC16 et par l'écho du numéro de paramètre
   (évite les valeurs parasites).
3. Convertit les valeurs brutes en unités lisibles (Hz, V, A, tr/min...)
   pour les paramètres connus.
4. Affiche le résultat et le sauvegarde dans `vfd_parametres.txt`.

**Configuration en haut du script** (à adapter si besoin) :

```python
PORT    = '/dev/ttyAMA2'   # Pi 5 = ttyAMA2, Pi 4 = ttyAMA3
BAUD    = 9600
ADRESSE = 0x01
```

Les paramètres lus sont documentés dans la section « Paramètres du VFD »
de la documentation du site (onglet Documentation).

---

## Licences

Ce depot utilise deux licences complementaires, selon la nature des fichiers :

| Quoi | Licence | Copyleft ? |
| --- | --- | --- |
| Scripts (Python, shell) | **MIT (Expat)** | Non — libre d'utilisation, y compris dans un projet ferme |
| Documentation, designs, contenus (Markdown, HTML, CSS, favicon, photos, textes redactionnels) | **CC BY-SA 4.0** | Oui — toute modification doit etre partagee sous la meme licence |

**En pratique :**

- Tu peux utiliser les scripts (`gestion_site.py`, `generer_site.py`,
  `ajouter_video.sh`, etc.) librement, meme dans un projet commercial ou
  proprietaire (licence MIT).
- Tu peux reprendre la documentation, les designs du site, les textes et
  les photos, mais toute version modifiee doit rester publiee sous
  **CC BY-SA 4.0** (partage dans les memes conditions, attribution
  obligatoire).

Voir le fichier [LICENSE](LICENSE) pour le texte integral des deux licences.
