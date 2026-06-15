#!/bin/bash
# =========================================================================
# generer_miniatures.sh - Atelier du Verdier
# Genere une image miniature (.jpg) pour chaque video .mp4 de l'export
# Instagram, a utiliser comme vignette cliquable dans le site de build.
# =========================================================================
# UTILISATION :
#   1. Place ce script dans le dossier qui contient tes videos (ou au-dessus)
#   2. Rends-le executable :  chmod +x generer_miniatures.sh
#   3. Lance-le :             ./generer_miniatures.sh /chemin/vers/les/videos
#      (si tu ne donnes pas de chemin, il cherche dans le dossier courant)
# =========================================================================

set -e

# Dossier source des videos (argument 1, ou dossier courant par defaut)
SRC="${1:-.}"

# Dossier de sortie des miniatures
OUT="miniatures"
mkdir -p "$OUT"

# Verifier que ffmpeg est installe
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg n'est pas installe."
    echo "Installe-le avec :"
    echo "   Debian/Ubuntu : sudo apt install ffmpeg"
    echo "   CachyOS/Arch  : sudo pacman -S ffmpeg"
    exit 1
fi

echo "Recherche des fichiers .mp4 dans : $SRC"
echo "Les miniatures seront placees dans : $OUT/"
echo ""

count=0
fail=0

# Parcourir tous les .mp4 (recursivement) du dossier source
find "$SRC" -type f -iname "*.mp4" | while read -r video; do
    nom=$(basename "$video" .mp4)
    sortie="$OUT/${nom}.jpg"

    # Sauter si la miniature existe deja
    if [ -f "$sortie" ]; then
        echo "  [deja fait] ${nom}.jpg"
        continue
    fi

    # Extraire une image a 1 seconde du debut, largeur 480px (hauteur auto),
    # qualite correcte. -ss avant -i = rapide. -frames:v 1 = une seule image.
    if ffmpeg -loglevel error -ss 00:00:01 -i "$video" \
        -frames:v 1 -vf "scale=480:-1" -q:v 4 "$sortie" 2>/dev/null; then
        echo "  [ok] ${nom}.jpg"
        count=$((count+1))
    else
        # Si l'extraction a 1s echoue (video tres courte), essayer a 0s
        if ffmpeg -loglevel error -ss 00:00:00 -i "$video" \
            -frames:v 1 -vf "scale=480:-1" -q:v 4 "$sortie" 2>/dev/null; then
            echo "  [ok-0s] ${nom}.jpg"
            count=$((count+1))
        else
            echo "  [ECHEC] $nom"
            fail=$((fail+1))
        fi
    fi
done

echo ""
echo "Termine. Miniatures dans le dossier : $OUT/"
echo "Compte les fichiers avec :  ls $OUT/ | wc -l"
