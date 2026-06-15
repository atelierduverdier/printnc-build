# Kit de generation du site PrintNC — Atelier du Verdier

Ce dossier permet de regenerer ton site de construction (printnc-build.html)
et surtout d'y AJOUTER de nouvelles videos toi-meme.

## Contenu du dossier

    generer_site.py        Le script qui fabrique le site
    data/videos.csv        La liste de toutes tes videos (a editer)
    data/recit.html        Le texte du recit (modifiable)
    miniatures/            (a placer ici) les images des videos
    printnc-build.html     Le site genere (resultat)

## Ajouter de nouvelles videos (nouveaux reels Instagram)

### 1. Recuperer les nouvelles videos
Refais un export Instagram (Parametres > Vos informations > Telecharger),
ou recupere juste les nouveaux fichiers .mp4 et leur lien.

### 2. Generer les miniatures des nouvelles videos
Lance le script generer_miniatures.sh sur le dossier des nouvelles videos.
Il ne traite que les nouvelles (saute celles deja faites). Copie les
nouvelles images .jpg dans le dossier miniatures/ de ce kit.

### 3. Ajouter les lignes au CSV
Ouvre data/videos.csv (avec un tableur ou un editeur de texte).
Ajoute une ligne par video, avec ces colonnes :

    date,phase,fichier,lien,texte

- date   : format AAAA-MM-JJ (ex: 2026-07-15)
- phase  : meca, elec ou soft (mecanique / electronique / LinuxCNC)
- fichier: nom du .mp4 (ex: 18012345678901234.mp4)
- lien   : URL Instagram du reel (https://www.instagram.com/.../reel/.../)
- texte  : la legende / description affichee

Si tu ajoutes un nouveau mois (juillet, aout...), le script cree
automatiquement son onglet. Pour lui donner un beau titre, ouvre
generer_site.py et ajoute une ligne dans le dictionnaire mois_info
(suis le modele des mois existants). Sinon, l'onglet apparaitra quand meme
avec le nom du mois.

### 4. Regenerer le site
Dans ce dossier, lance :

    python3 generer_site.py

Ca recree printnc-build.html avec les nouvelles videos.

### 5. Mettre en ligne
Pousse printnc-build.html (renomme index.html) et le dossier miniatures/
sur ton depot GitHub Pages.

## Modifier le recit

Edite data/recit.html. Utilise les classes suivantes :
- <h3 class="recit-h">Titre de chapitre</h3>
- <p class="recit-p">Un paragraphe.</p>
- <p class="recit-cite">Une citation en italique.</p>

Puis relance python3 generer_site.py.

## Besoin d'aide ?

Tu peux toujours revenir voir Claude avec ce dossier (le CSV et le site)
pour faire des modifications plus poussees (design, nouvelles sections, etc.).

## Ajouter une entree dans l'onglet "Mises a jour"

L'onglet "Mises a jour" est le changelog technique, groupe par date (le plus
recent en haut). Il se modifie dans le fichier data/maj.md (format markdown).

Regles simples :
- Une ligne commencant par "# " = une DATE (ex: "# 15 juillet 2026")
- Une ligne commencant par "## " = un TITRE de modification
- Le texte normal = description
- Pour un bloc de code, entoure-le de trois accents graves :
      ```
      net exemple ...
      ```
- Pour du code dans une phrase : entoure-le d'un accent grave : `comme ceci`

Pour ajouter une nouvelle date, ajoute un bloc EN HAUT du fichier (le plus
recent en premier), sur le modele des dates existantes.

Puis relance :  python3 generer_site.py

## Modifier l'onglet "Documentation"

L'onglet "Documentation" est la doc de reference de la machine (fiche
technique, cablage, configuration, utilisation, maintenance, depannage).
Il se modifie dans data/doc.md (format markdown, comme les mises a jour).

Syntaxe :
- "# " = une grande SECTION (ex: "# Maintenance")
- "## " = un sous-titre
- texte normal = paragraphe
- `code inline` entre accents graves
- bloc de code entre ``` ... ```
- tableau : lignes entre barres verticales, exemple :
      | Colonne A | Colonne B |
      |-----------|-----------|
      | valeur 1  | valeur 2  |

Complete-la petit a petit. Puis relance :  python3 generer_site.py

## Ajouter une nouvelle video facilement (recommande)

Plutot que d'editer data/videos.csv a la main et de generer la miniature
separement, utilise le script tout-en-un :

    chmod +x ajouter_video.sh        (une seule fois)
    ./ajouter_video.sh /chemin/vers/la_video_telechargee.mp4

Le script :
1. Copie la video dans videos_sources/ (archive)
2. Genere sa miniature dans miniatures/
3. Te demande : date (defaut = aujourd'hui), phase (meca/elec/soft),
   lien Instagram, legende
4. Ajoute la ligne dans data/videos.csv
5. Relance generer_site.py automatiquement

Ensuite, verifie index.html puis lance goup_site.sh pour publier.

Flux complet pour une nouvelle video Instagram :
1. Telecharge le reel avec ton extension navigateur
2. ./ajouter_video.sh /chemin/vers/le_fichier.mp4
3. Reponds aux 4 questions (lien = copie depuis Instagram)
4. ./goup_site.sh
