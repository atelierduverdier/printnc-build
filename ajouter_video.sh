#!/bin/bash
# =========================================================================
# ajouter_video.sh - Atelier du Verdier
#
# Ajoute une nouvelle video au site PrintNC en une seule commande :
#  1. Copie le .mp4 fourni vers un dossier de reference (videos_sources/)
#  2. Genere sa miniature (ffmpeg) dans miniatures/
#  3. Demande date / phase / lien Instagram / legende
#  4. Ajoute la ligne dans data/videos.csv
#  5. Regenere le site (generer_site.py)
#
# UTILISATION :
#   ./ajouter_video.sh /chemin/vers/la_video_telechargee.mp4
#
# Lancer ce script depuis le dossier kit_site/ (ou il est range).
# =========================================================================

set -e

# ---- Verifications de base ----
if [ -z "$1" ]; then
    echo "Utilisation : ./ajouter_video.sh /chemin/vers/video.mp4"
    exit 1
fi

VIDEO_SRC="$1"
if [ ! -f "$VIDEO_SRC" ]; then
    echo "Fichier introuvable : $VIDEO_SRC"
    exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg n'est pas installe (sudo pacman -S ffmpeg)."
    exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

MINIATURES="miniatures"
SOURCES="videos_sources"
CSV="data/videos.csv"
mkdir -p "$MINIATURES" "$SOURCES"

# ---- Nom de fichier ----
# On garde le nom d'origine du .mp4 telecharge (sert d'identifiant unique)
NOM_FICHIER="$(basename "$VIDEO_SRC")"
NOM_BASE="${NOM_FICHIER%.*}"

echo "--------------------------------------------------"
echo " Nouvelle video : $NOM_FICHIER"
echo "--------------------------------------------------"

# Copier la video source (pour archive / pourra servir si on heberge plus tard)
if [ ! -f "$SOURCES/$NOM_FICHIER" ]; then
    cp "$VIDEO_SRC" "$SOURCES/$NOM_FICHIER"
    echo "Video copiee dans $SOURCES/"
else
    echo "(deja presente dans $SOURCES/, pas recopiee)"
fi

# ---- Generer la miniature ----
MINI="$MINIATURES/${NOM_BASE}.jpg"
if [ -f "$MINI" ]; then
    echo "Miniature deja existante : $MINI (pas regeneree)"
else
    ffmpeg -loglevel error -ss 00:00:01 -i "$VIDEO_SRC" \
        -frames:v 1 -vf "scale=480:-1" -q:v 4 "$MINI" 2>/dev/null || true
    if [ -s "$MINI" ]; then
        echo "Miniature generee : $MINI"
    else
        ffmpeg -loglevel error -ss 00:00:00 -i "$VIDEO_SRC" \
            -frames:v 1 -vf "scale=480:-1" -q:v 4 "$MINI"
        if [ -s "$MINI" ]; then
            echo "Miniature generee (a 0s) : $MINI"
        else
            echo "ATTENTION : echec de generation de la miniature."
        fi
    fi
fi

# ---- Verifier si cette video est deja dans le CSV ----
if grep -q "$NOM_FICHIER" "$CSV" 2>/dev/null; then
    echo ""
    echo "ATTENTION : '$NOM_FICHIER' est deja present dans $CSV !"
    echo "Ligne(s) existante(s) :"
    grep -n "$NOM_FICHIER" "$CSV" | sed 's/^/  /'
    echo ""
    read -r -p "Ajouter quand meme une nouvelle ligne (doublon) ? [o/N] : " CONFIRM
    case "$CONFIRM" in
        o|O|oui|Oui|y|Y) echo "(ajout du doublon confirme)" ;;
        *) echo "Abandon, rien n'a ete ajoute."; exit 0 ;;
    esac
fi

# ---- Questions a l'utilisateur ----
echo ""
DATE_DEFAUT="$(date +%Y-%m-%d)"
read -r -p "Date [AAAA-MM-JJ] (defaut: $DATE_DEFAUT) : " DATE
DATE="${DATE:-$DATE_DEFAUT}"

# Normaliser la date au format AAAA-MM-JJ avec zeros (ex: 2026-6-9 -> 2026-06-09)
# Necessaire car le tri des entrees est alphabetique : sans zero, l'ordre serait faux.
if [[ "$DATE" =~ ^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})$ ]]; then
    AA="${BASH_REMATCH[1]}"
    MM=$(printf "%02d" "${BASH_REMATCH[2]}")
    JJ=$(printf "%02d" "${BASH_REMATCH[3]}")
    DATE="${AA}-${MM}-${JJ}"
else
    echo "ATTENTION : format de date non reconnu, '$DATE' utilise tel quel."
    echo "             (attendu : AAAA-MM-JJ, ex: 2026-06-09)"
fi
echo "Date retenue : $DATE"

echo ""
echo "Phase : 1) meca  2) elec  3) soft  4) laser"
read -r -p "Choix [1-4] (defaut: 1) : " PHASE_NUM
case "$PHASE_NUM" in
    2) PHASE="elec" ;;
    3) PHASE="soft" ;;
    4) PHASE="laser" ;;
    *) PHASE="meca" ;;
esac

echo ""
read -r -p "Lien Instagram (URL du reel) : " LIEN

echo ""
read -r -p "Legende / texte : " TEXTE
TEXTE="${TEXTE:-Etape de construction (video du jour)}"

# ---- Ajouter la ligne au CSV ----
# Echapper les guillemets et entourer le texte si necessaire (virgules)
CSV_TEXTE="$TEXTE"
if [[ "$CSV_TEXTE" == *","* || "$CSV_TEXTE" == *"\""* ]]; then
    CSV_TEXTE="\"$(echo "$CSV_TEXTE" | sed 's/"/""/g')\""
fi
CSV_LIEN="$LIEN"
if [[ "$CSV_LIEN" == *","* ]]; then
    CSV_LIEN="\"$CSV_LIEN\""
fi

# Le CSV existant est en CRLF : on ajoute une ligne au meme format.
# 7 champs (duree et jalon vides) pour rester aligne sur l'en-tete.
printf '%s,%s,%s,%s,%s,,\r\n' "$DATE" "$PHASE" "$NOM_FICHIER" "$CSV_LIEN" "$CSV_TEXTE" >> "$CSV"
echo ""
echo "Ligne ajoutee dans $CSV"

# ---- Regenerer le site ----
echo ""
echo "Regeneration du site..."
python3 generer_site.py

echo "--------------------------------------------------"
echo " Termine ! Verifie index.html, puis lance"
echo " goup_site.sh pour publier sur GitHub."
echo "--------------------------------------------------"
