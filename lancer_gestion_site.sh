#!/usr/bin/env bash
# Lanceur genere par installer_dependances.sh
# PySide6 est installe dans un virtualenv : on l'active avant de lancer.
VENV_DIR="/home/christophe/.venv/kit_site"
if [ ! -d "$VENV_DIR" ]; then
    echo "Erreur : virtualenv introuvable dans $VENV_DIR"
    echo "Relance : ./installer_dependances.sh"
    exit 1
fi
source "$VENV_DIR/bin/activate"
exec python3 "/home/christophe/Projets/Site_PrintNC/kit_site/gestion_site.py" "$@"
