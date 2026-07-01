#!/usr/bin/env python3
# =========================================================================
# remplir_durees.py - Atelier du Verdier
# Parcours le fichier videos.csv, trouve la vidéo correspondante,
# extrait sa durée avec ffprobe et l'inscrit dans la colonne "duree".
#
# UTILISATION :
#   python3 remplir_durees.py                  (cherche dans videos_sources/)
#   python3 remplir_durees.py /chemin/autres/vids (cherche dans le dossier donné)
# =========================================================================

import csv
import os
import subprocess
import sys

CSV_PATH = os.path.join('data', 'videos.csv')
DEFAULT_VIDEO_DIR = 'videos_sources'

def get_duration(file_path):
    """Retourne la durée au format MM:SS (ex: 03:45) via ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            capture_output=True, text=True, timeout=30
        )
        duration_sec = float(result.stdout.strip())
        
        minutes = int(duration_sec // 60)
        seconds = int(duration_sec % 60)
        return f"{minutes:02d}:{seconds:02d}"
    except Exception:
        return None

def main():
    video_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VIDEO_DIR
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Erreur : Fichier {CSV_PATH} introuvable.")
        sys.exit(1)
        
    if not os.path.isdir(video_dir):
        print(f"❌ Erreur : Dossier '{video_dir}' introuvable.")
        print(f"💡 Usage : python3 {sys.argv[0]} [dossier_des_videos]")
        sys.exit(1)

    # Lecture du CSV
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if 'duree' not in fieldnames:
            fieldnames.append('duree')
        
        # Nettoyage des clés None (piège Python 3.14 si virgule en fin de ligne)
        rows = [{k: v for k, v in row.items() if k is not None} for row in reader]

    updated = 0
    missing = 0
    errors = 0

    print(f"🔍 Analyse de {len(rows)} vidéos dans '{video_dir}'...\n")

    for row in rows:
        fichier = row.get('fichier', '').strip()
        if not fichier:
            continue
            
        file_path = os.path.join(video_dir, fichier)
        
        if not os.path.exists(file_path):
            missing += 1
            continue
            
        duree = get_duration(file_path)
        
        if duree:
            if row.get('duree', '').strip() != duree:
                row['duree'] = duree
                updated += 1
                print(f"  ✅ {fichier} -> {duree}")
        else:
            errors += 1
            print(f"  ⚠️  Erreur de lecture pour {fichier}")

    print(f"\n{'='*40}")
    print(f"Durées mises à jour : {updated}")
    if missing > 0: print(f"Fichiers introuvables : {missing} (vérifie le dossier)")
    if errors > 0:  print(f"Erreurs de lecture   : {errors}")
    print(f"{'='*40}")

    if updated > 0:
        with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n💾 Fichier {CSV_PATH} mis à jour avec succès.")
    else:
        print("\n✨ Aucune modification nécessaire, le fichier est déjà à jour.")

if __name__ == '__main__':
    main()
