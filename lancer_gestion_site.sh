#!/usr/bin/env bash
# Lanceur genere par installer_dependances.sh
# PySide6 est installe dans un virtualenv : on l'active avant de lancer.
source "/home/christophe/.venv/kit_site/bin/activate"
exec python3 "/home/christophe/Projets/Site_PrintNC/kit_site/gestion_site.py" "$@"
