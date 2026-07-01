#!/usr/bin/env bash
# =========================================================================
# installer_dependances.sh
# Installe toutes les dependances necessaires au kit de generation du site
# PrintNC (gestion_site.py, generer_site.py, lire_vfd.py, miniatures...).
#
# Supporte : Arch Linux (et derives), Debian/Ubuntu (et derives), Fedora.
# Detection automatique de la distribution via /etc/os-release.
#
# Dependances installees :
#   - python3            interpreteur
#   - pyside6            interface graphique Qt6 (gestion_site.py)
#   - pyserial           lecture du port serie (lire_vfd.py)
#   - ffmpeg             generation des miniatures des videos
#   - git                publication sur GitHub
#   - libs runtime Qt    libGL, glib, Wayland/X11...
#
# UTILISATION :
#   ./installer_dependances.sh
# =========================================================================

set -e

# --- Couleurs ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC}   $*"; }
info() { echo -e "${BLUE}[..]${NC}   $*"; }
warn() { echo -e "${YELLOW}[!]${NC}  $*"; }
err()  { echo -e "${RED}[ERREUR]${NC} $*"; }

# --- Resolution du dossier du script (pour le lanceur) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Detection de la distribution ---
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO="$ID"
else
    err "Impossible de detecter la distribution (/etc/os-release absent)."
    echo "    Installe manuellement : python3, PySide6, pyserial, ffmpeg, git."
    exit 1
fi

echo ""
echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE} Installation des dependances du kit site PrintNC      ${NC}"
echo -e "${BLUE}========================================================${NC}"
echo ""
info "Distribution detectee : ${PRETTY_NAME:-$DISTRO}"
echo ""

# Verifier que l'on est pas root (sudo sera demande au besoin)
if [ "$(id -u)" -eq 0 ]; then
    warn "Tu executes ce script en root. Ce n'est pas recommande."
    warn "Il vaut mieux le lancer en utilisateur normal (sudo sera demande)."
fi

# --- Verification de la version Python minimale (3.8) ---
if [ "$(python3 -c 'import sys; print(sys.version_info < (3, 8))')" = "True" ]; then
    err "Python 3.8 ou superieur est requis."
    err "Version actuelle : $(python3 --version 2>&1)"
    exit 1
fi
ok "Version Python valide : $(python3 --version 2>&1)"

# =========================================================================
#  Fonction : creer un lanceur si PySide6 est installe via venv
# =========================================================================
creer_lanceur() {
    local VENV_DIR="$1"
    local LAUNCHER="$SCRIPT_DIR/lancer_gestion_site.sh"
    cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# Lanceur genere par installer_dependances.sh
# PySide6 est installe dans un virtualenv : on l'active avant de lancer.
VENV_DIR="$VENV_DIR"
if [ ! -d "\$VENV_DIR" ]; then
    echo "Erreur : virtualenv introuvable dans \$VENV_DIR"
    echo "Relance : ./installer_dependances.sh"
    exit 1
fi
source "\$VENV_DIR/bin/activate"
exec python3 "$SCRIPT_DIR/gestion_site.py" "\$@"
EOF
    chmod +x "$LAUNCHER"
    ok "Lanceur cree : $LAUNCHER"
    echo ""
    warn "PySide6 etant dans un virtualenv, utilise desormais :"
    echo -e "    ${YELLOW}./lancer_gestion_site.sh${NC}   (au lieu de 'python3 gestion_site.py')"
}

# =========================================================================
#  ARCH LINUX (et derives : CachyOS, Manjaro, EndeavourOS...)
# =========================================================================
if [[ "$DISTRO" == "arch" || "$DISTRO" == "cachyos" || "$DISTRO" == "manjaro" \
   || "$DISTRO" == "endeavouros" || "$DISTRO" == "garuda" ]]; then

    info "Mode Arch Linux"
    echo ""

    # Paquets system disponibles dans les depots officiels (core/extra)
    info "Installation des paquets systeme via pacman..."
    sudo pacman -Sy --needed \
        python \
        python-pyserial \
        ffmpeg \
        git

    ok "Paquets de base installes (python, pyserial, ffmpeg, git)."

    # --- PySide6 ---
    # Present dans extra sur Arch ; absent de certains depots derives.
    info "Installation de PySide6..."
    if pacman -Si python-pyside6 >/dev/null 2>&1; then
        sudo pacman -S --needed python-pyside6
        ok "PySide6 installe via pacman (paquet systeme)."
        # WebEngine : optionnel, pour l'apercu integre du site
        if pacman -Si python-pyside6-WebEngine >/dev/null 2>&1; then
            sudo pacman -S --needed python-pyside6-WebEngine && \
                ok "PySide6 WebEngine installe (apercu integre du site)." || \
                warn "python-pyside6-WebEngine non installe (apercu integre " \
                     "indisponible, le site s'ouvrira dans le navigateur)."
        fi
    else
        warn "python-pyside6 absent des depots -> installation via pip (virtualenv)."
        VENV_DIR="$HOME/.venv/kit_site"
        [ -d "$VENV_DIR" ] || python3 -m venv "$VENV_DIR"
        "$VENV_DIR/bin/pip" install --upgrade pip
        "$VENV_DIR/bin/pip" install pyside6
        ok "PySide6 installe dans $VENV_DIR"
        creer_lanceur "$VENV_DIR"
    fi

# =========================================================================
#  DEBIAN / UBUNTU (et derives : Linux Mint, Pop!_OS...)
# =========================================================================
elif [[ "$DISTRO" == "debian" || "$DISTRO" == "ubuntu" || "$DISTRO" == "linuxmint" \
     || "$DISTRO" == "pop" || "$DISTRO" == "kali" ]]; then

    info "Mode Debian / Ubuntu"
    echo ""

    info "Mise a jour des listes de paquets..."
    sudo apt-get update -qq
    echo ""

    # Paquets systeme (avec libs runtime Qt pour PySide6 sous Wayland/X11)
    info "Installation des paquets systeme via apt..."
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-serial \
        ffmpeg \
        git \
        libgl1 \
        libegl1 \
        libglib2.0-0 \
        libfontconfig1 \
        libdbus-1-3 \
        libxkbcommon0 \
        qt6-wayland 2>/dev/null || true   # optionnel (Wayland)

    ok "Paquets de base installes."

    # --- PySide6 (jamais dans Debian stable, toujours via pip) ---
    info "Installation de PySide6 (via pip dans un virtualenv)..."
    VENV_DIR="$HOME/.venv/kit_site"
    [ -d "$VENV_DIR" ] || python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install pyside6
    ok "PySide6 installe dans $VENV_DIR"
    creer_lanceur "$VENV_DIR"

# =========================================================================
#  FEDORA
# =========================================================================
elif [[ "$DISTRO" == "fedora" ]]; then

    info "Mode Fedora"
    echo ""

    info "Installation des paquets systeme via dnf..."
    sudo dnf install -y \
        python3 \
        python3-pip \
        python3-virtualenv \
        python3-pyserial \
        ffmpeg \
        ffmpeg-libs \
        git \
        mesa-libGL \
        mesa-libEGL \
        glib2 \
        fontconfig \
        qt6-qtwayland 2>/dev/null || true   # optionnel (Wayland)

    ok "Paquets de base installes."

    # --- PySide6 ---
    info "Installation de PySide6..."
    if dnf info python3-pyside6 >/dev/null 2>&1; then
        sudo dnf install -y python3-pyside6
        ok "PySide6 installe via dnf (paquet systeme)."
    else
        warn "python3-pyside6 absent des depots -> installation via pip (virtualenv)."
        VENV_DIR="$HOME/.venv/kit_site"
        [ -d "$VENV_DIR" ] || python3 -m venv "$VENV_DIR"
        "$VENV_DIR/bin/pip" install --upgrade pip
        "$VENV_DIR/bin/pip" install pyside6
        ok "PySide6 installe dans $VENV_DIR"
        creer_lanceur "$VENV_DIR"
    fi

else
    echo ""
    err "Distribution '$DISTRO' non supportee par ce script."
    echo ""
    echo "    Installe manuellement ces dependances :"
    echo "      - python3  (>= 3.8)"
    echo "      - PySide6  (interface graphique Qt6)"
    echo "      - pyserial (lecture port serie)"
    echo "      - ffmpeg   (miniatures des videos)"
    echo "      - git      (publication GitHub)"
    echo ""
    echo "    Puis lance : python3 gestion_site.py"
    exit 1
fi

# =========================================================================
#  Verification finale
# =========================================================================
echo ""
echo -e "${BLUE}--------------------------------------------------------${NC}"
info "Verification des dependances..."
echo -e "${BLUE}--------------------------------------------------------${NC}"
echo ""

# Choisir le bon binaire python (venv si present)
PYTHON_BIN="python3"
if [ -x "$HOME/.venv/kit_site/bin/python3" ]; then
    PYTHON_BIN="$HOME/.venv/kit_site/bin/python3"
fi

NB_OK=0
NB_TOTAL=5

check_module() {
    # $1 = module Python, $2 = nom affichable, $3 = binaire python (optionnel)
    local bin="${3:-$PYTHON_BIN}"
    local ver
    ver=$("$bin" -c "import $1; print($1.__version__)" 2>/dev/null) || return 1
    ok "$2 OK ($ver)"
    return 0
}

check_import() {
    # $1 = module Python, $2 = nom affichable, $3 = binaire python (optionnel)
    # Ne verifie que l'import, sans lire __version__ (utile pour les sous-modules)
    local bin="${3:-$PYTHON_BIN}"
    "$bin" -c "import $1" 2>/dev/null || return 1
    ok "$2 OK"
    return 0
}

check_cmd() {
    # $1 = commande, $2 = nom affichable
    local ver
    ver=$("$1" --version 2>&1 | head -1) || return 1
    ok "$2 OK ($ver)"
    return 0
}

# Python (toujours OK puisqu'on est en train de l'utiliser)
PY_VER=$("$PYTHON_BIN" --version 2>&1)
ok "Python OK ($PY_VER)"
NB_OK=$((NB_OK + 1))

# PySide6
if check_module PySide6 "PySide6"; then
    NB_OK=$((NB_OK + 1))
fi

# PySide6 WebEngine — optionnel, pour l'apercu integre du site
if check_import PySide6.QtWebEngineWidgets "PySide6 WebEngine (optionnel)"; then
    info "Apercu integre du site disponible."
else
    warn "PySide6 WebEngine absent — l'apercu du site s'ouvrira dans le " \
         "navigateur. Pour l'activer sur Arch : sudo pacman -S " \
         "python-pyside6-WebEngine"
fi

# pyserial — verifier avec le python SYSTEME (pas le venv)
# car pyserial est installe via pacman/apt/dnf, et utilise par lire_vfd.py
if check_module serial "pyserial" "python3"; then
    NB_OK=$((NB_OK + 1))
fi

# ffmpeg
if check_cmd ffmpeg "ffmpeg"; then
    NB_OK=$((NB_OK + 1))
fi

# git
if check_cmd git "git"; then
    NB_OK=$((NB_OK + 1))
fi

echo ""
echo -e "${BLUE}--------------------------------------------------------${NC}"
if [ "$NB_OK" -eq "$NB_TOTAL" ]; then
    ok "Installation terminee : $NB_OK/$NB_TOTAL dependances presentes."
    echo ""
    info "Pour lancer l'interface graphique :"
    if [ -f "$SCRIPT_DIR/lancer_gestion_site.sh" ]; then
        echo -e "    ${GREEN}./lancer_gestion_site.sh${NC}"
    else
        echo -e "    ${GREEN}python3 gestion_site.py${NC}"
    fi
else
    warn "Installation terminee avec $NB_OK/$NB_TOTAL dependances."
    warn "Certaines dependances manquent — verifie les messages ci-dessus."
fi
echo -e "${BLUE}--------------------------------------------------------${NC}"
echo ""
