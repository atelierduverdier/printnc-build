#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =========================================================================
# gestion_site.py - Atelier du Verdier
#
# Interface graphique (PySide6 / Qt6) pour gerer le site PrintNC :
#   - Tableau de bord (stats, repartition, etat git)
#   - Generer le site (index.html) a partir du CSV + markdown
#   - Ajouter une video (archive source + miniature ffmpeg + ligne CSV + regen)
#   - Generer les miniatures en lot
#   - Git : status / pull / commit + push (depot GitHub Pages)
#   - Donnees : ouvrir/editer les fichiers sources, apercu du CSV
#
# Aucune dependance externe : PySide6 (deja installee), ffmpeg, git.
#
# UTILISATION :
#   python3 gestion_site.py
#
# Tous les chemins (CSV, miniatures, depot git...) sont relatifs au dossier
# ou se trouve ce script (kit_site/).
# =========================================================================

import csv
import os
import sys
import shutil
import tempfile
import subprocess
import functools
from collections import Counter, deque

from PySide6.QtCore import (
    Qt, QProcess, QProcessEnvironment, QDate, QTimer, QUrl, QByteArray, QRectF, Signal, QObject,
    QMimeData
)
from PySide6.QtGui import (
    QFont, QColor, QPixmap, QIcon, QTextCursor, QPainter, QDesktopServices, QPalette,
    QDropEvent, QDragEnterEvent, QDragMoveEvent
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QPlainTextEdit,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QStackedWidget,
    QFrame, QProgressBar, QStatusBar, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QSplitter, QSlider, QDialog,
    QDialogButtonBox
)
# Aperçu intégré optionnel : WebEngine peut manquer (paquet séparé sur Arch :
# python-pyside6-WebEngine). Import protégé => repli sur ouverture navigateur.
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE = True
except ImportError:
    QWebEngineView = None
    WEBENGINE = False

# --------------------------------------------------------------------------
#  Configuration & theme (palette reprise du site PrintNC : dark + orange)
# --------------------------------------------------------------------------
KIT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_REL = os.path.join('data', 'videos.csv')
CSV_PATH = os.path.join(KIT_DIR, CSV_REL)
SITE_OUT = os.path.join(KIT_DIR, 'index.html')
GEN_SCRIPT = os.path.join(KIT_DIR, 'generer_site.py')
MINI_DIR = os.path.join(KIT_DIR, 'miniatures')
SRC_DIR = os.path.join(KIT_DIR, 'videos_sources')
FAVICON = os.path.join(KIT_DIR, 'favicon.svg')

PHASE_LABEL = {'meca': 'Mecanique', 'elec': 'Electronique', 'soft': 'LinuxCNC'}
PHASE_FROM_LABEL = {v: k for k, v in PHASE_LABEL.items()}
PHASE_COLORS = {'meca': '#378ADD', 'elec': '#EF9F27', 'soft': '#1D9E75'}

APP_ORANGE = '#e8821e'

QSS = """
* {
    font-family: 'Inter','Segoe UI','DejaVu Sans','Sans';
    font-size: 13px;
}
QMainWindow, QWidget#central, QWidget#page { background: #13110e; }

/* ---- Sidebar ---- */
QWidget#sidebar { background: #1c1916; border-right: 1px solid #332d24; }
QPushButton#nav {
    text-align: left; padding: 11px 16px; border: none; border-radius: 8px;
    background: transparent; color: #a89e8c; font-size: 14px; font-weight: 500;
}
QPushButton#nav:hover { background: rgba(232,130,30,.12); color: #f0ebe2; }
QPushButton#nav:checked {
    background: rgba(232,130,30,.18); color: #e8821e; font-weight: 600;
}
QLabel#brand { color: #e8821e; font-size: 17px; font-weight: 700; }
QLabel#brandsub { color: #6b6356; font-size: 11px; }

/* ---- Titres de page ---- */
QLabel#pageTitle { color: #f0ebe2; font-size: 23px; font-weight: 700; }
QLabel#pageSub { color: #a89e8c; font-size: 13px; }
QLabel#h2 { color: #e8821e; font-size: 15px; font-weight: 600; }
QLabel#muted { color: #a89e8c; }
QLabel#faint { color: #6b6356; font-size: 12px; }

/* ---- Cartes ---- */
QFrame#card, QFrame#statCard {
    background: #1c1916; border: 1px solid #332d24; border-radius: 12px;
}
QLabel#statN { color: #e8821e; font-size: 30px; font-weight: 700; }
QLabel#statL { color: #6b6356; font-size: 11px; letter-spacing: 1px; }

/* ---- Boutons ---- */
QPushButton {
    background: #1c1916; border: 1px solid #332d24; border-radius: 8px;
    color: #f0ebe2; padding: 9px 16px;
}
QPushButton:hover { border-color: #e8821e; }
QPushButton:disabled { color: #4a443b; border-color: #2a251f; background: #18150f; }
QPushButton#primary {
    background: #e8821e; border-color: #e8821e; color: #13110e; font-weight: 600;
}
QPushButton#primary:hover { background: #ff9a3c; border-color: #ff9a3c; }
QPushButton#primary:disabled { background: #5a3a16; border-color: #5a3a16; color: #2a251f; }

/* ---- Champs ---- */
QLineEdit, QComboBox, QDateEdit {
    background: #13110e; border: 1px solid #332d24; border-radius: 8px;
    color: #f0ebe2; padding: 8px 10px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus { border-color: #e8821e; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background: #1c1916; border: 1px solid #332d24;
    selection-background-color: rgba(232,130,30,.25); color: #f0ebe2;
}
QDateEdit::up-button, QDateEdit::down-button { width: 0; border: none; }

/* ---- Console ---- */
QPlainTextEdit#console {
    background: #0d0b09; border: 1px solid #332d24; border-radius: 8px;
    color: #d8cfc0;
    font-family: 'JetBrains Mono','Cascadia Code','Consolas','Monaco','monospace';
    font-size: 12px;
}

/* ---- Tableau ---- */
QTableWidget {
    background: #13110e; border: 1px solid #332d24; border-radius: 8px;
    gridline-color: #332d24; color: #f0ebe2;
    selection-background-color: rgba(232,130,30,.25); outline: 0;
}
QHeaderView::section {
    background: #1c1916; color: #e8821e; border: none;
    border-bottom: 1px solid #332d24; padding: 6px 10px; font-weight: 600;
}
QTableWidget::item { padding: 5px 8px; }

/* ---- Liste fichiers git ---- */
QListWidget#gitFiles {
    background: #13110e; border: 1px solid #332d24; border-radius: 8px;
    color: #f0ebe2; outline: 0;
}
QListWidget#gitFiles::item { padding: 5px 8px; }

/* ---- Texte general ---- */
QLabel { color: #d8cfc0; }
QCheckBox { color: #d8cfc0; }

/* ---- Divers ---- */
QProgressBar {
    background: #13110e; border: 1px solid #332d24; border-radius: 6px;
    text-align: center; color: #f0ebe2; max-height: 14px;
}
QProgressBar::chunk { background: #e8821e; border-radius: 5px; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #13110e; width: 11px; margin: 0; }
QScrollBar::handle:vertical { background: #332d24; border-radius: 5px; min-height: 28px; }
QScrollBar::handle:vertical:hover { background: #4a443b; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }
QStatusBar { background: #1c1916; color: #6b6356; border-top: 1px solid #332d24; }
QStatusBar::item { border: none; }
QSplitter::handle { background: #332d24; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }
"""


# =========================================================================
#  Runner : file de taches asynchrones (commandes externes + callbacks Py).
#  Une seule tache s'execute a la fois, dans l'ordre d'empilement.
#  - Les commandes (git/ffmpeg/python) tournent dans un QProcess.
#  - Les callbacks Python (then()) s'executent dans le thread GUI, entre
#    deux commandes : pratique pour enchaîner "ecrire le CSV puis regen".
# =========================================================================
class Runner(QObject):
    line = Signal(str)          # une ligne de sortie (cmd/out/err detecte auto)
    busy_changed = Signal(bool) # occupation globale (pour la barre de progression)

    def __init__(self, console):
        super().__init__()
        self.console = console
        self._queue = deque()   # de taches : ('cmd', ...) ou ('py', callable)
        self._proc = None
        self._busy = False
        self._halt_on_error = False  # command en cours doit bloquer la file ?

    @property
    def busy(self):
        return self._busy

    # -- Empilement ------------------------------------------------------
    def cmd(self, command, args=None, cwd=KIT_DIR, title=None, env=None,
            halt_on_error=False):
        """Empile une commande externe.

        Si halt_on_error=True et que la commande echoue (code de sortie != 0),
        le reste de la file est vide : les taches suivantes (push, regen...)
        ne s'executeront pas. Pratique pour eviter de pousser sur une base
        git cassee apres un pull/rebase qui n'a pas abouti."""
        self._queue.append(('cmd', command, args or [], cwd, title, env,
                            halt_on_error))
        self._pump()

    def then(self, func, title=None):
        """Empile un callback Python execute dans le thread GUI, apres les
        taches deja empilees. func recoit le Runner (utile pour injecter
        des taches via inject())."""
        self._queue.append(('py', func, title))
        self._pump()

    def inject(self, command, args=None, cwd=KIT_DIR, title=None, env=None,
               halt_on_error=False):
        """Insere une commande juste apres la tache courante (en tete de la
        file restante). Utilisable depuis un callback then()."""
        self._queue.appendleft(('cmd', command, args or [], cwd, title, env,
                                halt_on_error))

    def clear(self):
        self._queue.clear()

    # -- Pompage ---------------------------------------------------------
    def _set_busy(self, b):
        if b != self._busy:
            self._busy = b
            self.busy_changed.emit(b)

    def _pump(self):
        if self._proc is not None:
            return  # une commande tourne deja ; elle rappellera _pump a la fin
        if not self._queue:
            self._set_busy(False)
            return
        self._set_busy(True)
        task = self._queue.popleft()
        if task[0] == 'py':
            _, func, title = task
            if title:
                self.console.append(f"──── {title} ────", 'title')
            try:
                func(self)
            except Exception as e:   # ne jamais casser la file
                self.console.append(f"(erreur callback : {e})", 'err')
            # enchainement immediat
            QTimer.singleShot(0, self._pump)
        else:
            _, command, args, cwd, title, env, halt_on_error = task
            self._halt_on_error = halt_on_error
            if title:
                self.console.append(f"──── {title} ────", 'title')
            self.console.append(f"$ {command} {' '.join(args)}", 'cmd')
            self._proc = QProcess()
            self._proc.setProcessChannelMode(QProcess.MergedChannels)
            if env is not None:
                self._proc.setProcessEnvironment(env)
            self._proc.setWorkingDirectory(cwd)
            self._proc.readyReadStandardOutput.connect(self._read_out)
            self._proc.finished.connect(self._finished)
            self._proc.start(command, args)

    def _read_out(self):
        if not self._proc:
            return
        data = bytes(self._proc.readAllStandardOutput()).decode('utf-8', 'replace')
        for ln in data.splitlines():
            self.console.append(ln)

    def _finished(self, code, _status):
        halt = False
        if code != 0:
            self.console.append(f"(code de sortie : {code})", 'err')
            if self._halt_on_error:
                # La commande demandait d'arreter la file en cas d'echec :
                # on jette le reste (push, regen...) pour ne pas pousser sur
                # une base cassee. L'utilisateur corrige puis relance.
                halt = True
        self._halt_on_error = False
        self._proc = None
        if halt:
            n = len(self._queue)
            self._queue.clear()
            self.console.append(
                f"(file interrompue : {n} tache(s) annulee(s) "
                f"apres cet echec)", 'err')
            self._set_busy(False)
        else:
            QTimer.singleShot(0, self._pump)


# =========================================================================
#  ConsoleWidget : logs colores + bouton effacer
# =========================================================================
class ConsoleWidget(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setObjectName('console')
        self.setReadOnly(True)
        self.setMaximumBlockCount(5000)

    def append(self, text, kind=None):
        if kind is None:
            low = text.lower()
            if text.startswith('$ '):
                kind = 'cmd'
            elif text.startswith('────'):
                kind = 'title'
            elif any(w in low for w in ('erreur', 'error', 'fatal',
                                        'echec', 'failed', 'refus')):
                kind = 'err'
            else:
                kind = 'out'
        color = {'out': '#d8cfc0', 'cmd': '#a89e8c',
                 'title': APP_ORANGE, 'err': '#ff7a55'}[kind]
        self.moveCursor(QTextCursor.End)
        fmt = self.currentCharFormat()
        fmt.setForeground(QColor(color))
        fmt.setFontWeight(QFont.Bold if kind == 'title' else QFont.Normal)
        self.setCurrentCharFormat(fmt)
        self.appendPlainText(text)


# =========================================================================
#  Helpers UI
# =========================================================================
def lire_videos():
    if not os.path.exists(CSV_PATH):
        return []
    out = []
    with open(CSV_PATH, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get('date'):
                out.append(r)
    return out


def _champ_csv(v):
    """Echappe un champ CSV selon RFC 4180 (guillemets doubles) : on quote
    uniquement si le champ contient une virgule, un guillemet ou un saut de
    ligne."""
    v = v or ''
    if ',' in v or '"' in v or '\n' in v:
        return '"' + v.replace('"', '""') + '"'
    return v


def _ligne_csv(date, phase, fichier, lien, texte, duree='', jalon=''):
    return ','.join(_champ_csv(x) for x in [date, phase, fichier, lien, texte, duree, jalon])


def ecrire_ligne_csv(date, phase, fichier, lien, texte, duree='', jalon=''):
    """Ajoute une ligne au CSV en respectant le format CRLF d'origine et
    l'echappement RFC 4180 (guillemets doubles)."""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    ligne = _ligne_csv(date, phase, fichier, lien, texte, duree, jalon)
    # Garantit un CRLF avant la nouvelle ligne si le fichier existe deja et
    # ne se termine pas par un saut de ligne (lecture simple, sans rouvrir
    # le fichier en ecriture simultanement).
    prefixe = ''
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        with open(CSV_PATH, 'rb') as chk:
            chk.seek(0, 2)
            if chk.tell() > 0:
                chk.seek(max(0, chk.tell() - 2))
                if chk.read(2) != b'\r\n':
                    prefixe = '\r\n'
    with open(CSV_PATH, 'a', encoding='utf-8', newline='') as f:
        if prefixe:
            f.write(prefixe)
        f.write(ligne + '\r\n')


def ecrire_videos_csv(rows):
    """Reecrit tout le CSV videos.csv a partir d'une liste de dicos {date,
    phase, fichier, lien, texte, duree, jalon}. L'ordre des lignes est indifferent car
    generer_site.py retri par date au chargement.

    Sauvegarde preventive en .bak : le CSV est l'unique source de donnees,
    on ne veut jamais le perdre sur une ecriture cassee."""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if os.path.exists(CSV_PATH):
        shutil.copy2(CSV_PATH, CSV_PATH + '.bak')
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        f.write('date,phase,fichier,lien,texte,duree,jalon\r\n')
        for r in rows:
            f.write(_ligne_csv(r.get('date', ''), r.get('phase', ''),
                               r.get('fichier', ''), r.get('lien', ''),
                               r.get('texte', ''), r.get('duree', ''),
                               r.get('jalon', '')) + '\r\n')


def label_muted(text, min_w=110):
    l = QLabel(text)
    l.setObjectName('muted')
    l.setMinimumWidth(min_w)
    return l


def load_svg_icon(path, size=64, fallback_emoji='🖨'):
    """Charge un fichier SVG et retourne un QPixmap carree de taille x taille.
    Le SVG est rendu en conservant ses proportions, puis centre dans le
    carre (avec un fond transparent autour), ce qui evite l'effet
    d'aplatissement."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            data = QByteArray(f.read())
        renderer = QSvgRenderer(data)
        if not renderer.isValid():
            return None
        # Rendre le SVG a sa taille naturelle dans un pixmap assez grand
        # pour ne pas perdre de resolution
        orig = renderer.defaultSize()
        # Pixmap final carre
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)
        painter = QPainter(pm)
        # Calculer le rect de destination qui respecte les proportions
        aspect = orig.width() / max(1, orig.height())
        margin = 4  # petit degagement dans le carre
        avail = size - margin * 2
        if aspect >= 1:
            w = avail
            h = int(avail / aspect)
        else:
            h = avail
            w = int(avail * aspect)
        x = (size - w) // 2
        y = (size - h) // 2
        renderer.render(painter, QRectF(x, y, w, h))
        painter.end()
        return pm
    except Exception:
        return None


def section_card(parent_layout, title=None):
    """Ajoute une carte QFrame au layout parent et retourne son QVBoxLayout."""
    card = QFrame()
    card.setObjectName('card')
    cl = QVBoxLayout(card)
    cl.setContentsMargins(20, 18, 20, 18)
    cl.setSpacing(12)
    if title:
        t = QLabel(title)
        t.setObjectName('h2')
        cl.addWidget(t)
    parent_layout.addWidget(card)
    return cl


def run_git_sync(args, timeout=10):
    """Lance git de facon synchrone (pour des lectures rapides comme le
    status). Retourne (stdout, returncode)."""
    try:
        p = subprocess.run(['git', '-C', KIT_DIR] + args,
                           capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip(), p.returncode
    except Exception:
        return '', 1


@functools.lru_cache(maxsize=1)
def upstream_ref():
    """Retourne la reference upstream (ex. 'origin/main') de la branche
    courante, derivee dynamiquement plutot que codée en dur. Repli sur
    'origin/main' si aucune branche amont n'est configuree (ex. depot neuf)
    ou si git echoue. Le cache evite de relancer git a chaque refresh."""
    ref, code = run_git_sync(['rev-parse', '--abbrev-ref', '@{u}'])
    if code == 0 and ref:
        return ref
    return 'origin/main'


# =========================================================================
#  PAGE : Tableau de bord
# =========================================================================
class DashboardPage(QWidget):
    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        self.phase_bars = {}
        self.stat_labels = {}
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(self._title("Tableau de bord",
                                   "Vue d'ensemble du site et de l'etat du depot GitHub."))

        # --- Stats ---
        grid = QGridLayout()
        grid.setSpacing(12)
        root.addLayout(grid)
        for i, (key, label) in enumerate([
                ('videos', 'Videos'), ('mois', 'Mois couverts'),
                ('meca', 'Mecanique'), ('elec', 'Electronique'),
                ('soft', 'LinuxCNC'), ('git', 'Etat Git')]):
            card = QFrame()
            card.setObjectName('statCard')
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(2)
            n = QLabel('–')
            n.setObjectName('statN')
            l = QLabel(label)
            l.setObjectName('statL')
            cl.addWidget(n)
            cl.addWidget(l)
            grid.addWidget(card, i // 3, i % 3)
            self.stat_labels[key] = n

        # --- Repartition par phase ---
        c1 = section_card(root, "Repartition par phase")
        for key in ('meca', 'elec', 'soft'):
            row = QHBoxLayout()
            row.setSpacing(10)
            dot = QLabel('●')
            dot.setStyleSheet(f'color:{PHASE_COLORS[key]}; font-size:14px;')
            lbl = QLabel(PHASE_LABEL[key])
            lbl.setStyleSheet('color:#f0ebe2; min-width:95px;')
            bar_bg = QFrame()
            bar_bg.setFixedHeight(16)
            # Le remplissage est dessine via un gradient CSS lineaire : on
            # controle la largeur du segment orange via le stop de couleur.
            # fond sombre par defaut (0%)
            bar_bg.setStyleSheet(
                'background:#13110e; border-radius:4px;')
            pct = QLabel('0%')
            pct.setStyleSheet('color:#6b6356; min-width:42px;')
            pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(dot)
            row.addWidget(lbl)
            row.addWidget(bar_bg, 1)
            row.addWidget(pct)
            c1.addLayout(row)
            self.phase_bars[key] = (bar_bg, pct)   # (cadre, etiquette %)

        # --- Etat git ---
        c2 = section_card(root, "Depot Git")
        gitrow = QHBoxLayout()
        gitrow.setSpacing(14)
        self.lbl_branch = QLabel("Branche : –")
        self.lbl_ab = QLabel("Local / distant : –")
        self.lbl_last = QLabel("Dernier commit : –")
        for w in (self.lbl_branch, self.lbl_ab, self.lbl_last):
            w.setObjectName('muted')
            gitrow.addWidget(w, 1)
        c2.addLayout(gitrow)

        b = QPushButton("🔄  Actualiser les statistiques")
        b.setObjectName('primary')
        b.clicked.connect(self.refresh)
        c2.addWidget(b)

        root.addStretch(1)

    def _title(self, title, sub):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(4)
        t = QLabel(title)
        t.setObjectName('pageTitle')
        s = QLabel(sub)
        s.setObjectName('pageSub')
        s.setWordWrap(True)
        l.addWidget(t)
        l.addWidget(s)
        return w

    def refresh(self):
        vids = lire_videos()
        n = len(vids)
        phases = Counter(v.get('phase', 'meca') for v in vids)
        mois = set(v['date'][:7] for v in vids if v.get('date'))
        self.stat_labels['videos'].setText(str(n))
        self.stat_labels['mois'].setText(str(len(mois)))
        self.stat_labels['meca'].setText(str(phases.get('meca', 0)))
        self.stat_labels['elec'].setText(str(phases.get('elec', 0)))
        self.stat_labels['soft'].setText(str(phases.get('soft', 0)))
        # Barres
        total = max(1, n)
        for key in ('meca', 'elec', 'soft'):
            bar_bg, pct_lbl = self.phase_bars[key]
            val = phases.get(key, 0)
            pct = int(round(val / total * 100))
            pct_lbl.setText(f'{pct}%')
            # Remplissage via un gradient lineaire CSS : segment de couleur
            # jusqu'a pct%, puis fond sombre. Infailible, aligne a gauche.
            color = PHASE_COLORS[key]
            bar_bg.setStyleSheet(
                'border-radius:4px;'
                f'background: qlineargradient(x1:0, y1:0, x2:1, y2:0,'
                f' stop:0 {color}, stop:{pct/100:.3f} {color},'
                f' stop:{pct/100:.3f} #13110e, stop:1 #13110e);')
        # Git (synchrone, rapide)
        br, _ = run_git_sync(['rev-parse', '--abbrev-ref', 'HEAD'])
        ab, _ = run_git_sync(['rev-list', '--left-right', '--count',
                              f'{upstream_ref()}...HEAD'])
        last, _ = run_git_sync(['log', '-1', '--oneline'])
        ahead = behind = '0'
        if ab:
            parts = ab.split()
            if len(parts) >= 2:
                behind, ahead = parts[0], parts[1]
        ab_txt = 'a jour' if ahead == '0' and behind == '0' \
            else f'{behind} a recuperer, {ahead} a publier'
        self.stat_labels['git'].setText(
            '✓ a jour' if ahead == '0' and behind == '0'
            else f'⇣{behind} ⇡{ahead}')
        self.lbl_branch.setText(f"Branche : {br or '–'}")
        self.lbl_ab.setText(f"Local / distant : {ab_txt}")
        self.lbl_last.setText(f"Dernier commit : {last or '–'}")


# =========================================================================
#  PAGE : Generer le site
# =========================================================================
class GenererPage(QWidget):
    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        self.web_view = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        t = QLabel("Generer le site")
        t.setObjectName('pageTitle')
        s = QLabel("Regenere index.html a partir de data/videos.csv et des "
                   "fichiers markdown (recit, maj, doc).")
        s.setObjectName('pageSub')
        s.setWordWrap(True)
        root.addWidget(t)
        root.addWidget(s)

        c = section_card(root, "Generation")
        info = QLabel(
            f"<b>Script :</b> <code style='color:{APP_ORANGE}'>generer_site.py</code><br>"
            f"<b>Sortie :</b> <code style='color:{APP_ORANGE}'>index.html</code><br>"
            f"<b>Sources :</b> <code style='color:{APP_ORANGE}'>data/videos.csv</code>, "
            f"<code style='color:{APP_ORANGE}'>data/recit.md</code>, "
            f"<code style='color:{APP_ORANGE}'>data/maj.md</code>, "
            f"<code style='color:{APP_ORANGE}'>data/doc.md</code>")
        info.setTextFormat(Qt.RichText)
        c.addWidget(info)

        self.chk_open = QCheckBox(
            "Ouvrir le site dans le navigateur apres generation")
        self.chk_open.setChecked(False)
        c.addWidget(self.chk_open)

        row = QHBoxLayout()
        self.btn_gen = QPushButton("⚙  Generer le site")
        self.btn_gen.setObjectName('primary')
        self.btn_gen.clicked.connect(self.generate)
        self.btn_preview = QPushButton("🔄  Rafraichir l'apercu")
        row.addWidget(self.btn_gen)
        row.addWidget(self.btn_preview)
        row.addStretch(1)
        c.addLayout(row)

        # Aperçu intégré : QWebEngineView si disponible, sinon fallback
        preview_card = section_card(root, "Apercu du site")
        if WEBENGINE and QWebEngineView:
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(300)
            preview_card.addWidget(self.web_view)
            QTimer.singleShot(500, self._load_preview)  # chargement differe
            self.btn_preview.clicked.connect(self._on_preview_click)
        else:
            lbl = QLabel(
                "Apercu integre indisponible.\n"
                "Installe le paquet <code>python-pyside6-WebEngine</code> "
                "(Arch/CachyOS) ou utilise le bouton ci-dessus pour ouvrir "
                "le site dans le navigateur.")
            lbl.setTextFormat(Qt.RichText)
            lbl.setWordWrap(True)
            lbl.setStyleSheet('color:#a89e8c; padding:30px;')
            lbl.setAlignment(Qt.AlignCenter)
            preview_card.addWidget(lbl)
            self.btn_preview.setText("👁  Ouvrir dans le navigateur")
            self.btn_preview.clicked.connect(self.open_site)

    def _load_preview(self):
        if self.web_view and os.path.exists(SITE_OUT):
            self.web_view.setUrl(QUrl.fromLocalFile(SITE_OUT))

    def _on_preview_click(self):
        if self.web_view:
            self._load_preview()
        else:
            self.open_site()

    def generate(self):
        if not os.path.exists(GEN_SCRIPT):
            QMessageBox.warning(self, "Script absent", f"Introuvable :\n{GEN_SCRIPT}")
            return
        self.runner.cmd('python3', [GEN_SCRIPT], cwd=KIT_DIR,
                        title="Generation du site")
        # Recharger l'apercu WebEngine apres generation
        if self.web_view:
            self.runner.then(lambda _r: self._load_preview())
        if self.chk_open.isChecked():
            self.runner.then(lambda _r: self._maybe_open())
        self.runner.console.append("Generation lancee.", 'title')

    def refresh(self):
        """Met a jour l'etat de la page (presence d'index.html)."""
        if hasattr(self, 'web_view') and self.web_view:
            self._load_preview()

    def _maybe_open(self):
        if os.path.exists(SITE_OUT):
            QDesktopServices.openUrl(QUrl.fromLocalFile(SITE_OUT))

    def open_site(self):
        if not os.path.exists(SITE_OUT):
            QMessageBox.information(self, "Pas encore genere",
                                    "index.html n'existe pas encore. "
                                    "Genere le site d'abord.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(SITE_OUT))


# =========================================================================
#  PAGE : Ajouter une video
# =========================================================================
class VideoPage(QWidget):
    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        self.video_path = None
        self.thumb_seconds = 1.0      # instant de la vignette, reglable
        self.video_duration = None    # duree en secondes (via ffprobe)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        t = QLabel("Ajouter une video")
        t.setObjectName('pageTitle')
        s = QLabel("Ajoute un reel en une seule operation : archive de la "
                   "source, miniature (ffmpeg), ligne dans le CSV, puis "
                   "regeneration du site.")
        s.setObjectName('pageSub')
        s.setWordWrap(True)
        root.addWidget(t)
        root.addWidget(s)

        # 1. Fichier
        c1 = section_card(root, "1. Fichier video")
        row = QHBoxLayout()
        self.edit_file = QLineEdit()
        self.edit_file.setPlaceholderText("Selectionne un fichier video (.mp4, .mov...)...")
        self.edit_file.setReadOnly(True)
        btn_pick = QPushButton("📁  Choisir...")
        btn_pick.clicked.connect(self.pick_file)
        row.addWidget(self.edit_file, 1)
        row.addWidget(btn_pick)
        c1.addLayout(row)

        self.preview_lbl = QLabel("Pas d'aperçu")
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setFixedHeight(160)
        self.preview_lbl.setStyleSheet(
            'background:#13110e; border-radius:8px; border:1px solid #332d24;'
            ' color:#6b6356;')
        c1.addWidget(self.preview_lbl)

        # Curseur pour choisir l'instant de la vignette
        seek_row = QHBoxLayout()
        seek_row.addWidget(label_muted("Instant vignette", min_w=110))
        self.slider_seek = QSlider(Qt.Horizontal)
        self.slider_seek.setRange(0, 100)   # en dixiemes de seconde
        self.slider_seek.setValue(int(self.thumb_seconds * 10))
        self.slider_seek.setEnabled(False)  # actif une fois une video chargee
        self.slider_seek.valueChanged.connect(self._on_seek_changed)
        seek_row.addWidget(self.slider_seek, 1)
        self.lbl_seek = QLabel("0:01.0")
        self.lbl_seek.setMinimumWidth(56)
        self.lbl_seek.setStyleSheet('color:#a89e8c;')
        seek_row.addWidget(self.lbl_seek)
        self.btn_refresh_preview = QPushButton("🔄")
        self.btn_refresh_preview.setToolTip("Rafraichir l'aperçu")
        self.btn_refresh_preview.setFixedWidth(38)
        self.btn_refresh_preview.setEnabled(False)
        self.btn_refresh_preview.clicked.connect(self._refresh_preview)
        seek_row.addWidget(self.btn_refresh_preview)
        c1.addLayout(seek_row)

        # Drag & drop accepte sur toute la page
        self.setAcceptDrops(True)

        # 2. Details
        c2 = section_card(root, "2. Details")
        g = QGridLayout()
        g.setHorizontalSpacing(14)
        g.setVerticalSpacing(10)
        g.addWidget(label_muted("Date"), 0, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        g.addWidget(self.date_edit, 0, 1)
        g.addWidget(label_muted("Phase"), 0, 2)
        self.combo_phase = QComboBox()
        for label in ('Mecanique', 'Electronique', 'LinuxCNC'):
            self.combo_phase.addItem(label)
        g.addWidget(self.combo_phase, 0, 3)
        g.addWidget(label_muted("Lien Instagram"), 1, 0)
        self.edit_lien = QLineEdit()
        self.edit_lien.setPlaceholderText("https://www.instagram.com/.../reel/.../")
        g.addWidget(self.edit_lien, 1, 1, 1, 3)
        g.addWidget(label_muted("Legende"), 2, 0)
        self.edit_texte = QLineEdit()
        self.edit_texte.setPlaceholderText("Etape de construction (video du jour)")
        g.addWidget(self.edit_texte, 2, 1, 1, 3)
        c2.addLayout(g)

        self.chk_archive = QCheckBox(
            "Archiver aussi la video source dans videos_sources/ "
            "(recommande ; dossier ignore par git)")
        self.chk_archive.setChecked(True)
        c2.addWidget(self.chk_archive)

        self.chk_jalon = QCheckBox("Marquer comme jalon (etape cle — mise en evidence dans la timeline)")
        c2.addWidget(self.chk_jalon)

        # 3. Action
        c3 = section_card(root, "3. Ajouter")
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName('muted')
        self.lbl_status.setWordWrap(True)
        c3.addWidget(self.lbl_status)
        self.btn_add = QPushButton("➕  Ajouter et regenerer")
        self.btn_add.setObjectName('primary')
        self.btn_add.clicked.connect(self.do_add)
        c3.addWidget(self.btn_add)

        root.addStretch(1)
        self._update_add_state()

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une video", os.path.expanduser('~'),
            "Videos (*.mp4 *.mov *.avi *.mkv);;Tous les fichiers (*)",
            "", QFileDialog.Option.DontUseNativeDialog)
        if path:
            self._load_video(path)

    def _load_video(self, path):
        """Commun a pick_file et au drag & drop : charge la video, detecte sa
        duree (ffprobe) et genere l'aperçu à l'instant courant."""
        self.video_path = path
        self.edit_file.setText(path)
        # Duree via ffprobe (best-effort : repli sur 10 s si absent/echec)
        self.video_duration = self._probe_duration(path)
        duree = self.video_duration if self.video_duration else 10.0
        self.slider_seek.setRange(0, max(1, int(duree * 10)))
        self.slider_seek.setValue(int(min(self.thumb_seconds, duree) * 10))
        self.slider_seek.setEnabled(True)
        self.btn_refresh_preview.setEnabled(True)
        self._update_seek_label()
        self._show_preview(path)
        self._update_add_state()

    def _probe_duration(self, path):
        """Retourne la duree de la video en secondes (float) via ffprobe,
        ou None si ffprobe est absent ou echoue."""
        if not shutil.which('ffprobe'):
            return None
        try:
            p = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', path],
                capture_output=True, text=True, timeout=20)
            return float(p.stdout.strip())
        except Exception:
            return None

    @staticmethod
    def _fmt_seek(t):
        """Formate un instant en secondes pour l'affichage et pour ffmpeg."""
        m, s = divmod(float(t), 60)
        return f"{int(m)}:{s:04.1f}"

    def _fmt_seek_ffmpeg(self, t):
        """Formate un instant au format HH:MM:SS.mmm pour l'option -ss."""
        t = max(0.0, float(t))
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}"

    def _on_seek_changed(self, _val):
        self.thumb_seconds = self.slider_seek.value() / 10.0
        self._update_seek_label()

    def _update_seek_label(self):
        self.lbl_seek.setText(self._fmt_seek(self.thumb_seconds))

    def _refresh_preview(self):
        if self.video_path:
            self._show_preview(self.video_path)

    def _show_preview(self, path, t=None):
        if t is None:
            t = self.thumb_seconds
        fd, tmp = tempfile.mkstemp(suffix='.jpg', prefix='_printnc_preview_')
        os.close(fd)
        try:
            subprocess.run(
                ['ffmpeg', '-y', '-loglevel', 'error',
                 '-ss', self._fmt_seek_ffmpeg(t),
                 '-i', path, '-frames:v', '1', '-vf', 'scale=320:-1',
                 '-q:v', '4', tmp],
                check=True, capture_output=True, timeout=20)
            if os.path.exists(tmp):
                pix = QPixmap(tmp)
                if not pix.isNull():
                    self.preview_lbl.setPixmap(
                        pix.scaledToHeight(158, Qt.SmoothTransformation))
                    return
        except Exception:
            pass
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass
        self.preview_lbl.setText("Aperçu indisponible")

    def _update_add_state(self):
        ok = bool(self.video_path) and os.path.exists(self.video_path or '')
        self.btn_add.setEnabled(ok and not self.runner.busy)

    def do_add(self):
        if not self.video_path or not os.path.exists(self.video_path):
            QMessageBox.warning(self, "Aucune video",
                                "Choisis d'abord un fichier video.")
            return
        if not shutil.which('ffmpeg'):
            QMessageBox.warning(self, "ffmpeg manquant",
                                "Installe ffmpeg :\n  sudo pacman -S ffmpeg")
            return

        nom_fichier = os.path.basename(self.video_path)
        nom_base = os.path.splitext(nom_fichier)[0]
        date = self.date_edit.date().toString('yyyy-MM-dd')
        phase = PHASE_FROM_LABEL[self.combo_phase.currentText()]
        lien = self.edit_lien.text().strip()
        texte = self.edit_texte.text().strip() or \
            "Etape de construction (video du jour)"
        jalon = 'oui' if self.chk_jalon.isChecked() else ''
        duree = ''
        if self.video_duration:
            m, s = divmod(int(self.video_duration), 60)
            duree = f'{m:02d}:{s:02d}'

        # Doublon ? Teste la colonne 'fichier' exacte (pas une sous-chaîne
        # dans tout le CSV, qui ferait des faux positifs sur les légendes).
        deja = False
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, encoding='utf-8') as _f:
                deja = any(r.get('fichier') == nom_fichier
                           for r in csv.DictReader(_f) if r.get('date'))
        if deja:
            rep = QMessageBox.question(
                self, "Doublon potentiel",
                f"'{nom_fichier}' semble deja present dans le CSV.\n"
                "Ajouter quand meme une nouvelle ligne ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if rep != QMessageBox.Yes:
                return

        self.lbl_status.setText("Traitement en cours... (voir la console)")
        self.btn_add.setEnabled(False)

        mini = os.path.join(MINI_DIR, f'{nom_base}.jpg')
        os.makedirs(MINI_DIR, exist_ok=True)

        # --- Enchainement ordonne via la file ---
        # 1) archive optionnelle
        if self.chk_archive.isChecked():
            os.makedirs(SRC_DIR, exist_ok=True)
            dest = os.path.join(SRC_DIR, nom_fichier)
            if not os.path.exists(dest):
                self.runner.cmd('cp', [self.video_path, dest], cwd=KIT_DIR,
                                title=f"Archive de {nom_fichier}")

        # 2) miniature a l'instant choisi (si pas deja faite)
        if not os.path.exists(mini):
            self.runner.cmd('ffmpeg',
                            ['-y', '-loglevel', 'error',
                             '-ss', self._fmt_seek_ffmpeg(self.thumb_seconds),
                             '-i', self.video_path, '-frames:v', '1',
                             '-vf', 'scale=480:-1', '-q:v', '4', mini],
                            cwd=KIT_DIR,
                            title=f"Generation de la miniature ({self._fmt_seek(self.thumb_seconds)})")
            # fallback a 0 s si la miniature n'existe toujours pas
            def _fallback(_r, v=self.video_path, m=mini):
                if not os.path.exists(m):
                    _r.inject('ffmpeg',
                              ['-y', '-loglevel', 'error', '-ss', '00:00:00',
                               '-i', v, '-frames:v', '1', '-vf', 'scale=480:-1',
                               '-q:v', '4', m],
                              cwd=KIT_DIR, title="Miniature (fallback a 0 s)")
            self.runner.then(_fallback)

        # 3) ajout de la ligne CSV (callback Python, avant la regen)
        def _add_csv(_r):
            ecrire_ligne_csv(date, phase, nom_fichier, lien, texte, duree, jalon)
            _r.console.append(f"Ligne ajoutee dans {CSV_REL}", 'title')
        self.runner.then(_add_csv, title="Ajout dans videos.csv")

        # 4) regeneration du site
        self.runner.cmd('python3', [GEN_SCRIPT], cwd=KIT_DIR,
                        title="Regeneration du site")

        # 5) fin : reinit UI + rafraichir
        def _done(_r):
            self.lbl_status.setText("✓ Video ajoutee et site regenere.")
            self.video_path = None
            self.edit_file.clear()
            self.preview_lbl.clear()
            self.preview_lbl.setText("Pas d'aperçu")
            self.edit_lien.clear()
            self.edit_texte.clear()
            self.chk_jalon.setChecked(False)
            self.slider_seek.setEnabled(False)
            self.btn_refresh_preview.setEnabled(False)
            self._update_add_state()
        self.runner.then(_done, title="Termine")

    # ---- Drag & drop d'un fichier video sur la page ----
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and self._video_urls(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls() and self._video_urls(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = self._video_urls(event.mimeData())
        if urls:
            self._load_video(urls[0].toLocalFile())
            event.acceptProposedAction()
        else:
            event.ignore()

    @staticmethod
    def _video_urls(mime: QMimeData):
        """Filtre les URLs du mimeData pour ne garder que les fichiers video."""
        exts = ('.mp4', '.mov', '.avi', '.mkv')
        return [u for u in mime.urls()
                if u.isLocalFile()
                and os.path.splitext(u.toLocalFile())[1].lower() in exts]


# =========================================================================
#  PAGE : Miniatures (lot)
# =========================================================================
class MiniaturesPage(QWidget):
    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        self._src_dir = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        t = QLabel("Generer les miniatures")
        t.setObjectName('pageTitle')
        s = QLabel("Genere une vignette .jpg (480 px de large, a 1 s du debut) "
                   "pour chaque video d'un dossier. Les miniatures deja "
                   "existantes sont sautees.")
        s.setObjectName('pageSub')
        s.setWordWrap(True)
        root.addWidget(t)
        root.addWidget(s)

        c = section_card(root, "Dossier source")
        row = QHBoxLayout()
        self.edit_dir = QLineEdit()
        self.edit_dir.setPlaceholderText("Dossier contenant les videos...")
        self.edit_dir.setReadOnly(True)
        btn = QPushButton("📁  Choisir le dossier...")
        btn.clicked.connect(self.pick_dir)
        row.addWidget(self.edit_dir, 1)
        row.addWidget(btn)
        c.addLayout(row)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName('muted')
        c.addWidget(self.lbl_count)

        self.btn_gen = QPushButton("🎬  Generer les miniatures manquantes")
        self.btn_gen.setObjectName('primary')
        self.btn_gen.clicked.connect(self.run)
        self.btn_gen.setEnabled(False)
        c.addWidget(self.btn_gen)

        root.addStretch(1)

    def pick_dir(self):
        d = QFileDialog.getExistingDirectory(
            self, "Dossier des videos", os.path.expanduser('~'),
            QFileDialog.Option.DontUseNativeDialog)
        if d:
            self._src_dir = d
            self.edit_dir.setText(d)
            self._refresh_count()

    def _list_videos(self, d):
        out = []
        for dirpath, _dirs, files in os.walk(d):
            for f in files:
                if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    out.append(os.path.join(dirpath, f))
        return out

    def _refresh_count(self):
        mp4 = self._list_videos(self._src_dir)
        manquantes = [v for v in mp4
                      if not os.path.exists(os.path.join(
                          MINI_DIR, os.path.splitext(os.path.basename(v))[0] + '.jpg'))]
        self.lbl_count.setText(
            f"{len(mp4)} video(s) trouvee(s) — {len(manquantes)} miniature(s) "
            f"a generer.")
        self.btn_gen.setEnabled(len(manquantes) > 0 and not self.runner.busy)

    def run(self):
        if not self._src_dir:
            return
        os.makedirs(MINI_DIR, exist_ok=True)
        n = 0
        for v in self._list_videos(self._src_dir):
            base = os.path.splitext(os.path.basename(v))[0]
            mini = os.path.join(MINI_DIR, base + '.jpg')
            if os.path.exists(mini):
                continue
            self.runner.cmd('ffmpeg',
                            ['-y', '-loglevel', 'error', '-ss', '00:00:01',
                             '-i', v, '-frames:v', '1', '-vf', 'scale=480:-1',
                             '-q:v', '4', mini],
                            cwd=KIT_DIR, title=f"Miniature {base}.jpg")
            n += 1
        if n == 0:
            self.runner.console.append("Aucune miniature a generer.", 'title')
        else:
            self.runner.then(lambda _r: self._refresh_count(),
                             title=f"{n} miniature(s) generee(s)")

    def refresh(self):
        """Met a jour le compteur de miniatures manquantes."""
        self._refresh_count()


# =========================================================================
#  PAGE : Git — publier
# =========================================================================
class GitPage(QWidget):
    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        t = QLabel("Git — publication")
        t.setObjectName('pageTitle')
        s = QLabel("Synchronise le site avec le depot GitHub "
                   "(atelierduverdier/printnc-build, GitHub Pages).")
        s.setObjectName('pageSub')
        s.setWordWrap(True)
        root.addWidget(t)
        root.addWidget(s)

        # Etat
        c1 = section_card(root, "Etat du depot")
        self.lbl_status = QLabel("Branche : –   |   Local/distant : –")
        self.lbl_status.setObjectName('muted')
        self.lbl_status.setWordWrap(True)
        c1.addWidget(self.lbl_status)
        c1.addWidget(label_muted("Fichiers modifies (non commites) :", min_w=0))
        self.files = QListWidget()
        self.files.setObjectName('gitFiles')
        self.files.setMinimumHeight(120)
        c1.addWidget(self.files)
        btn_refresh = QPushButton("🔄  Actualiser")
        btn_refresh.clicked.connect(self.refresh)
        c1.addWidget(btn_refresh)

        # Pull
        c2 = section_card(root, "Recuperer (pull)")
        c2.addWidget(QLabel(
            "Recupere les derniers changements du distant (origin). Utile si "
            "tu as modifie le site depuis une autre machine."))
        self.btn_pull = QPushButton("⬇  git pull")
        self.btn_pull.clicked.connect(self.pull)
        c2.addWidget(self.btn_pull)

        # Commit & push
        c3 = section_card(root, "Publier (commit + push)")
        c3.addWidget(label_muted("Message de commit :", min_w=0))
        self.edit_msg = QLineEdit()
        self.edit_msg.setPlaceholderText("Ex : Ajout des videos de juillet 2026")
        c3.addWidget(self.edit_msg)
        self.chk_push = QCheckBox("Pousser vers GitHub apres le commit (git push)")
        self.chk_push.setChecked(True)
        c3.addWidget(self.chk_push)
        row = QHBoxLayout()
        self.btn_commit = QPushButton("✅  Committer")
        self.btn_commit.clicked.connect(self.commit)
        self.btn_push = QPushButton("⬆  git push")
        self.btn_push.clicked.connect(self.push)
        row.addWidget(self.btn_commit)
        row.addWidget(self.btn_push)
        row.addStretch(1)
        c3.addLayout(row)

        root.addStretch(1)

    def refresh(self):
        """Remplit la liste des fichiers modifies et l'etat branche/ahead-behind
        via des appels git synchrones (rapides)."""
        out, _ = run_git_sync(['status', '--short'])
        self.files.clear()
        for line in out.splitlines():
            line = line.rstrip()
            if not line:
                continue
            item = QListWidgetItem(line)
            st = line[:2]
            color = ('#ff7a55' if 'D' in st else
                     '#e8821e' if 'M' in st else
                     '#1D9E75' if ('?' in st or 'A' in st) else '#a89e8c')
            item.setForeground(QColor(color))
            self.files.addItem(item)
        if self.files.count() == 0:
            it = QListWidgetItem("✓ Aucun fichier modifie — copie de travail propre")
            it.setForeground(QColor('#1D9E75'))
            self.files.addItem(it)

        br, _ = run_git_sync(['rev-parse', '--abbrev-ref', 'HEAD'])
        ab, _ = run_git_sync(['rev-list', '--left-right', '--count',
                              f'{upstream_ref()}...HEAD'])
        ahead = behind = '0'
        if ab:
            parts = ab.split()
            if len(parts) >= 2:
                behind, ahead = parts[0], parts[1]
        ab_txt = 'a jour' if ahead == '0' and behind == '0' \
            else f'{behind} a recuperer, {ahead} a publier'
        self.lbl_status.setText(f"Branche : {br or '–'}   |   Local/distant : {ab_txt}")

    def pull(self):
        self.runner.cmd('git', ['pull'], cwd=KIT_DIR, title="git pull")
        self.runner.then(lambda _r: self.refresh())

    def commit(self):
        msg = self.edit_msg.text().strip()
        if not msg:
            QMessageBox.warning(self, "Message vide", "Ecris un message de commit.")
            return
        self.runner.cmd('git', ['add', '-A'], cwd=KIT_DIR, title="git add -A")
        self.runner.cmd('git', ['commit', '-m', msg], cwd=KIT_DIR,
                        title=f"git commit : {msg}")
        if self.chk_push.isChecked():
            self._enqueue_push()
        self.runner.then(lambda _r: self.refresh(), title="Commit termine")
        self.edit_msg.clear()

    def push(self):
        self._enqueue_push()
        self.runner.then(lambda _r: self.refresh())

    def _enqueue_push(self):
        env = QProcessEnvironment.systemEnvironment()
        env.insert('GIT_TERMINAL_PROMPT', '0')  # pas de prompt interactif
        # Récupère d'abord les changements distants (--rebase = historique
        # linéaire). Si le pull échoue (ex. divergence avec conflits),
        # halt_on_error empêche le push : on ne pousse jamais sur une base
        # désynchronisée, qui serait de toute façon rejetée en non-fast-forward.
        self.runner.cmd('git', ['pull', '--rebase'], cwd=KIT_DIR,
                        title="git pull --rebase (synchro avant push)",
                        env=env, halt_on_error=True)
        self.runner.cmd('git', ['push'], cwd=KIT_DIR, title="git push", env=env)


# =========================================================================
#  DIALOGUE : Edition / suppression d'une video
# =========================================================================
class EditVideoDialog(QDialog):
    """Dialogue dedie pour modifier ou supprimer une video existante.
    Pre-rempli avec les champs actuels de la video selectionnee."""

    def __init__(self, parent, video_row):
        """video_row : dict avec cles date, phase, fichier, lien, texte."""
        super().__init__(parent)
        self.setWindowTitle("Modifier la video")
        self.setMinimumWidth(520)
        self.video_row = dict(video_row)  # copie
        self._supprime = False

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Fichier (lecture seule, indicatif)
        g = QGridLayout()
        g.setHorizontalSpacing(12)
        g.setVerticalSpacing(10)
        g.addWidget(label_muted("Fichier"), 0, 0)
        lbl_fic = QLabel(self.video_row.get('fichier', ''))
        lbl_fic.setStyleSheet('color:#a89e8c;')
        g.addWidget(lbl_fic, 0, 1)

        # Date
        g.addWidget(label_muted("Date"), 1, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        d = self.video_row.get('date', '')
        if d:
            qdate = QDate.fromString(d, 'yyyy-MM-dd')
            if qdate.isValid():
                self.date_edit.setDate(qdate)
        g.addWidget(self.date_edit, 1, 1)

        # Phase
        g.addWidget(label_muted("Phase"), 2, 0)
        self.combo_phase = QComboBox()
        for label in ('Mecanique', 'Electronique', 'LinuxCNC'):
            self.combo_phase.addItem(label)
        phase = self.video_row.get('phase', 'meca')
        if phase in PHASE_LABEL:
            self.combo_phase.setCurrentText(PHASE_LABEL[phase])
        g.addWidget(self.combo_phase, 2, 1)

        # Lien Instagram
        g.addWidget(label_muted("Lien Instagram"), 3, 0)
        self.edit_lien = QLineEdit(self.video_row.get('lien', ''))
        self.edit_lien.setPlaceholderText("https://www.instagram.com/.../reel/.../")
        g.addWidget(self.edit_lien, 3, 1)

        # Legende
        g.addWidget(label_muted("Legende"), 4, 0)
        self.edit_texte = QLineEdit(self.video_row.get('texte', ''))
        self.edit_texte.setPlaceholderText("Etape de construction (video du jour)")
        g.addWidget(self.edit_texte, 4, 1)

        layout.addLayout(g)
        layout.addStretch(1)

        # Boutons
        bbox = QHBoxLayout()
        bbox.addStretch(1)
        self.btn_suppr = QPushButton("🗑  Supprimer cette video")
        self.btn_suppr.setStyleSheet(
            'background:#5c2020; color:#ff9999; padding:6px 16px; '
            'border-radius:6px; font-weight:bold;')
        self.btn_suppr.clicked.connect(self._on_supprimer)
        bbox.addWidget(self.btn_suppr)

        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.clicked.connect(self.reject)
        bbox.addWidget(self.btn_annuler)

        self.btn_valider = QPushButton("✓  Valider")
        self.btn_valider.setObjectName('primary')
        self.btn_valider.clicked.connect(self._on_valider)
        bbox.addWidget(self.btn_valider)
        layout.addLayout(bbox)

    def _on_supprimer(self):
        rep = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Supprimer la video et ses fichiers associes ?\n\n"
            f"Fichier : {self.video_row.get('fichier', '')}\n"
            f"Miniature et archive source seront aussi supprimees si "
            f"elles existent.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if rep == QMessageBox.Yes:
            self._supprime = True
            self.accept()

    def _on_valider(self):
        self.video_row['date'] = self.date_edit.date().toString('yyyy-MM-dd')
        self.video_row['phase'] = PHASE_FROM_LABEL[
            self.combo_phase.currentText()]
        self.video_row['lien'] = self.edit_lien.text().strip()
        self.video_row['texte'] = self.edit_texte.text().strip()
        self._supprime = False
        self.accept()

    @property
    def supprime(self):
        return self._supprime


# =========================================================================
#  PAGE : Donnees (fichiers editables + apercu CSV)
# =========================================================================
class DonneesPage(QWidget):
    DATA_FILES = [
        ('data/videos.csv', 'Videos',
         'Liste de toutes les videos (date, phase, fichier, lien, texte).'),
        ('data/recit.md', 'Recit', "Le recit long format (onglet « Le recit »)."),
        ('data/maj.md', 'Mises a jour',
         "Le changelog technique (onglet « Mises a jour »)."),
        ('data/doc.md', 'Documentation',
         "La doc de reference (onglet « Documentation »)."),
    ]

    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        t = QLabel("Donnees du site")
        t.setObjectName('pageTitle')
        s = QLabel("Ouvre et modifie les fichiers sources avec ton editeur, "
                   "puis regenere le site.")
        s.setObjectName('pageSub')
        s.setWordWrap(True)
        root.addWidget(t)
        root.addWidget(s)

        c = section_card(root, "Fichiers sources")
        for rel, nom, desc in self.DATA_FILES:
            row = QHBoxLayout()
            row.setSpacing(12)
            ic = QLabel('📄')
            ic.setStyleSheet('font-size:20px;')
            txt = QLabel(
                f"<b style='color:#f0ebe2'>{nom}</b> &nbsp; "
                f"<span style='color:#a89e8c'>{desc}</span><br>"
                f"<code style='color:{APP_ORANGE}; font-size:11px'>{rel}</code>")
            txt.setTextFormat(Qt.RichText)
            row.addWidget(ic)
            row.addWidget(txt, 1)
            btn = QPushButton("✎  Ouvrir")
            btn.clicked.connect(lambda _c, r=rel: self.open_file(r))
            row.addWidget(btn)
            c.addLayout(row)

        c.addWidget(self._sep())
        c.addWidget(label_muted("Apercu de videos.csv :", min_w=0))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ['Date', 'Phase', 'Fichier', 'Lien', 'Texte'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(220)
        self.table.doubleClicked.connect(self._edit_selected)
        c.addWidget(self.table)

        # Boutons d'action sur la video selectionnee
        rb = QHBoxLayout()
        rb.addStretch(1)
        self.btn_edit = QPushButton("✎  Modifier")
        self.btn_edit.clicked.connect(self._edit_selected)
        rb.addWidget(self.btn_edit)
        self.btn_suppr = QPushButton("🗑  Supprimer")
        self.btn_suppr.clicked.connect(self._delete_selected)
        rb.addWidget(self.btn_suppr)
        self.btn_regen = QPushButton("⚙  Regenerer le site")
        self.btn_regen.setObjectName('primary')
        self.btn_regen.clicked.connect(self.regen)
        rb.addWidget(self.btn_regen)
        c.addLayout(rb)

        root.addStretch(1)

    def _sep(self):
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setStyleSheet('background:#332d24; max-height:1px; border:none;')
        return f

    def open_file(self, rel):
        path = os.path.join(KIT_DIR, rel)
        if not os.path.exists(path):
            QMessageBox.information(self, "Fichier absent", path)
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def regen(self):
        self.runner.cmd('python3', [GEN_SCRIPT], cwd=KIT_DIR,
                        title="Regeneration du site")
        self.runner.then(lambda _r: self.refresh_table())

    def refresh_table(self):
        vids = lire_videos()[:200]  # limiter l'apercu
        self.table.setRowCount(len(vids))
        for i, v in enumerate(vids):
            vals = [v.get('date', ''), v.get('phase', ''), v.get('fichier', ''),
                    v.get('lien', ''), v.get('texte', '')]
            for j, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if j == 1 and val in PHASE_COLORS:
                    item.setForeground(QColor(PHASE_COLORS[val]))
                self.table.setItem(i, j, item)

    def _selected_video_key(self):
        """Retourne la cle (date, fichier) de la video selectionnee dans
        la table, ou None si aucune selection. On identifie par cle plutot
        que par rang car la table est plafonnee a 200 lignes."""
        row = self.table.currentRow()
        if row < 0:
            return None
        item_date = self.table.item(row, 0)
        item_fic = self.table.item(row, 2)
        if not item_date or not item_fic:
            return None
        return (item_date.text(), item_fic.text())

    def _edit_selected(self):
        key = self._selected_video_key()
        if not key:
            QMessageBox.information(self, "Aucune selection",
                                    "Selectionne une video dans le tableau.")
            return
        # Trouver la ligne correspondante dans le CSV complet (pas juste les
        # 200 premieres affichees)
        all_vids = lire_videos()
        video = None
        for v in all_vids:
            if v.get('date') == key[0] and v.get('fichier') == key[1]:
                video = v
                break
        if not video:
            QMessageBox.warning(self, "Video introuvable",
                                "Impossible de trouver cette video dans le CSV.")
            return
        dlg = EditVideoDialog(self, video)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if dlg.supprime:
            self._delete_video(video, all_vids)
        else:
            # Mettre a jour la ligne dans la liste
            for v in all_vids:
                if v.get('date') == key[0] and v.get('fichier') == key[1]:
                    v.update(dlg.video_row)
                    break
            ecrire_videos_csv(all_vids)
            self.runner.console.append("Video modifiee dans videos.csv", 'title')
            self.regen()

    def _delete_selected(self):
        key = self._selected_video_key()
        if not key:
            QMessageBox.information(self, "Aucune selection",
                                    "Selectionne une video dans le tableau.")
            return
        all_vids = lire_videos()
        video = None
        for v in all_vids:
            if v.get('date') == key[0] and v.get('fichier') == key[1]:
                video = v
                break
        if not video:
            return
        rep = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Supprimer la video et ses fichiers associes ?\n\n"
            f"Fichier : {video.get('fichier', '')}\n"
            f"Miniature et archive source seront aussi supprimees.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if rep == QMessageBox.Yes:
            self._delete_video(video, all_vids)

    def _delete_video(self, video, all_vids):
        """Supprime une video : ligne CSV + miniature + archive source."""
        fic = video.get('fichier', '')
        base = os.path.splitext(fic)[0] if fic else ''
        # Retirer la ligne du CSV
        all_vids = [v for v in all_vids
                     if not (v.get('date') == video.get('date')
                             and v.get('fichier') == video.get('fichier'))]
        ecrire_videos_csv(all_vids)
        self.runner.console.append(f"Video supprimee : {fic}", 'title')
        # Supprimer la miniature si elle existe
        mini = os.path.join(MINI_DIR, f'{base}.jpg')
        if os.path.exists(mini):
            os.remove(mini)
            self.runner.console.append(f"Miniature supprimee : {mini}", 'title')
        # Supprimer l'archive source si elle existe
        src = os.path.join(SRC_DIR, fic)
        if os.path.exists(src):
            os.remove(src)
            self.runner.console.append(f"Archive source supprimee : {src}", 'title')
        # Regen + refresh
        self.regen()


# =========================================================================
#  Fenetre principale
# =========================================================================
class MainWindow(QMainWindow):
    NAV = [
        ('dashboard', '🏠', 'Tableau de bord'),
        ('generer', '⚙', 'Generer le site'),
        ('video', '➕', 'Ajouter une video'),
        ('miniatures', '🎬', 'Miniatures'),
        ('git', '⎇', 'Git — publier'),
        ('donnees', '📄', 'Donnees'),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atelier du Verdier — Gestion du site PrintNC")
        self.resize(1120, 760)
        self.setMinimumSize(960, 640)

        # Console (construite en premier : les pages l'utilisent via le runner)
        self.console = ConsoleWidget()

        # Runner partage
        self.runner = Runner(self.console)

        central = QWidget()
        central.setObjectName('central')
        self.setCentralWidget(central)
        cl = QVBoxLayout(central)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        splitter = QSplitter(Qt.Vertical)
        cl.addWidget(splitter)

        top = QWidget()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)
        tl.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.pages = {
            'dashboard': DashboardPage(self.runner),
            'generer': GenererPage(self.runner),
            'video': VideoPage(self.runner),
            'miniatures': MiniaturesPage(self.runner),
            'git': GitPage(self.runner),
            'donnees': DonneesPage(self.runner),
        }
        for p in self.pages.values():
            p.setObjectName('page')
            p.setAttribute(Qt.WA_StyledBackground, True)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(p)
            scroll.setFrameShape(QFrame.NoFrame)
            self.stack.addWidget(scroll)
        tl.addWidget(self.stack, 1)
        splitter.addWidget(top)
        splitter.addWidget(self._build_console_pane())
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([560, 200])

        # Barre d'etat
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.lbl_busy = QLabel("Pret")
        sb.addWidget(self.lbl_busy)
        sb.addPermanentWidget(self.progress)

        # Runner -> UI
        self.runner.busy_changed.connect(self._on_busy)

        self.switch_page('dashboard')

        # Verifications initiales (differées pour laisser la fenêtre s'afficher)
        QTimer.singleShot(200, self._check_prereq)
        QTimer.singleShot(350, self.refresh_all)

    # ---- Sidebar ----
    def _build_sidebar(self):
        side = QWidget()
        side.setObjectName('sidebar')
        side.setFixedWidth(236)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(16, 22, 16, 16)
        sl.setSpacing(6)

        # --- En-tete : favicon (haut a gauche) + titre ---
        head = QHBoxLayout()
        head.setSpacing(12)
        logo = QLabel()
        logo_size = 64
        pix = load_svg_icon(FAVICON, size=logo_size * 2)  # rendu 2x pour netteté
        if pix is not None and not pix.isNull():
            logo.setPixmap(pix.scaled(
                logo_size, logo_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
            logo.setFixedSize(logo_size, logo_size)
        else:
            logo.setText("🖨")
            logo.setStyleSheet('color:#e8821e; font-size:40px;')
            logo.setFixedSize(logo_size, logo_size)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(
            'border:1px solid #332d24; border-radius:12px;'
            ' background:#13110e; padding:2px;')
        titles = QVBoxLayout()
        titles.setSpacing(0)
        brand = QLabel("PrintNC")
        brand.setObjectName('brand')
        sub = QLabel("Atelier du Verdier")
        sub.setObjectName('brandsub')
        titles.addWidget(brand)
        titles.addWidget(sub)
        head.addWidget(logo)
        head.addLayout(titles)
        head.addStretch(1)
        sl.addLayout(head)
        sl.addSpacing(18)

        self.nav_buttons = {}
        for key, icon, label in self.NAV:
            b = QPushButton(f"  {icon}   {label}")
            b.setObjectName('nav')
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _c=False, k=key: self.switch_page(k))
            sl.addWidget(b)
            self.nav_buttons[key] = b
        sl.addStretch(1)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet('background:#332d24; max-height:1px; border:none;')
        sl.addWidget(sep)
        info = QLabel(
            f"<div style='color:#6b6356; font-size:11px'>Dossier :<br>"
            f"<code style='color:#a89e8c'>{KIT_DIR}</code></div>")
        info.setTextFormat(Qt.RichText)
        info.setWordWrap(True)
        sl.addWidget(info)

        # --- Mention licences (discrète, en bas) ---
        licence = QLabel(
            "<div style='color:#4a443b; font-size:10px'>"
            "Logiciel libre — © 2026 Atelier du Verdier<br>"
            "<b style='color:#6b6356'>Code :</b> MIT · "
            "<b style='color:#6b6356'>Doc & designs :</b> CC BY-SA 4.0"
            "</div>")
        licence.setTextFormat(Qt.RichText)
        licence.setWordWrap(True)
        licence.setOpenExternalLinks(False)
        licence.setCursor(Qt.PointingHandCursor)
        licence.setToolTip(
            "Licences du projet PrintNC — Atelier du Verdier\n\n"
            "Code source (scripts Python, shell) :\n"
            "  Licence MIT (Expat)\n"
            "  Utilisation, modification et redistribution libres,\n"
            "  y compris dans des projets propriétaires.\n\n"
            "Documentation, designs et contenus :\n"
            "  Licence Creative Commons BY-SA 4.0 (CC BY-SA 4.0)\n"
            "  Partage et modification libres, mais les dérivés\n"
            "  doivent être publiés sous la même licence.\n\n"
            "Voir les fichiers LICENSE et LISEZMOI.md livrés avec le kit.")
        sl.addSpacing(8)
        sl.addWidget(licence)
        return side

    # ---- Console ----
    def _build_console_pane(self):
        wrap = QWidget()
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(28, 8, 28, 14)
        wl.setSpacing(6)
        head = QHBoxLayout()
        t = QLabel("Console")
        t.setObjectName('h2')
        clr = QPushButton("Effacer")
        clr.setStyleSheet('padding:3px 12px; font-size:11px;')
        clr.setCursor(Qt.PointingHandCursor)
        clr.clicked.connect(self.console.clear)
        head.addWidget(t)
        head.addStretch(1)
        head.addWidget(clr)
        wl.addLayout(head)
        wl.addWidget(self.console)
        return wrap

    # ---- Navigation ----
    def switch_page(self, key):
        if key not in self.pages:
            return
        idx = list(self.pages.keys()).index(key)
        self.stack.setCurrentIndex(idx)
        for k, b in self.nav_buttons.items():
            b.setChecked(k == key)
        page = self.pages[key]
        if key == 'dashboard':
            page.refresh()
        elif key == 'generer':
            page.refresh()
        elif key == 'donnees':
            page.refresh_table()
        elif key == 'video':
            page._update_add_state()
        elif key == 'miniatures':
            page.refresh()
        elif key == 'git':
            page.refresh()

    # ---- Runner callbacks ----
    def _on_busy(self, busy):
        self.progress.setVisible(busy)
        self.lbl_busy.setText("Traitement en cours..." if busy else "Pret")
        if 'video' in self.pages:
            self.pages['video']._update_add_state()
        if 'miniatures' in self.pages and self.pages['miniatures']._src_dir:
            self.pages['miniatures'].btn_gen.setEnabled(not busy)

    def refresh_all(self):
        for key, page in self.pages.items():
            if key == 'dashboard':
                page.refresh()
            elif key == 'donnees':
                page.refresh_table()
            elif key == 'git':
                page.refresh()

    # ---- Prerequis ----
    def _check_prereq(self):
        warnings = []
        if not os.path.exists(GEN_SCRIPT):
            warnings.append(f"generer_site.py introuvable ({GEN_SCRIPT})")
        if not os.path.exists(CSV_PATH):
            warnings.append(f"data/videos.csv introuvable ({CSV_PATH})")
        if not shutil.which('ffmpeg'):
            warnings.append("ffmpeg absent — installe-le : sudo pacman -S ffmpeg")
        if not shutil.which('git'):
            warnings.append("git absent — installe-le : sudo pacman -S git")
        self.console.append("Verification des prerequis :", 'title')
        if warnings:
            for w in warnings:
                self.console.append("  ⚠ " + w, 'err')
        else:
            self.console.append("  ✓ python, ffmpeg et git sont presents.")
        self.console.append(f"Dossier de travail : {KIT_DIR}", 'cmd')
        self.console.append("Astuce : utilise la barre de navigation a gauche "
                            "pour acceder aux differentes fonctions.", 'out')


# =========================================================================
#  Point d'entree
# =========================================================================
def _filtrer_warnings_qt():
    """Filtre les warnings SVG de Qt (favicon Inkscape avec <tspan> imbriques
    que QtSvg n'aime pas mais qui n'empechent pas le rendu). Evite de polluer
    le terminal. Le prefixe 'qt.svg' est la categorie (ctx.category), pas
    dans le message lui-meme."""
    from PySide6.QtCore import qInstallMessageHandler

    def _handler(mode, ctx, msg):
        cat = ctx.category if ctx is not None else ''
        # Warning d'analyse SVG du favicon (benins, le rendu marche)
        if cat == 'qt.svg':
            return
        if any(s in msg for s in ('Could not add child element',
                                  'Could not parse node',
                                  'qt.svg')):
            return
        print(msg, file=sys.stderr)

    qInstallMessageHandler(_handler)


def _palette_sombre(app):
    """Applique une palette sombre a toute l'application.

    La feuille de style QSS ne couvre pas les dialogues natifs (QFileDialog,
    QMessageBox) : ils suivent par defaut le theme systeme (souvent clair),
    ce qui donne un contraste casse (texte clair sur fond clair, ou inverse).
    Une palette sombre garantit un rendu coherent partout.
    """
    p = QPalette()

    def col(h):  # raccourci de saisie
        c = QColor()
        c.setNamedColor(h)
        return c

    # Fenetres / fonds
    p.setColor(QPalette.Window, col('#13110e'))
    p.setColor(QPalette.Base, col('#13110e'))          # champs de saisie, listes
    p.setColor(QPalette.AlternateBase, col('#1c1916'))
    p.setColor(QPalette.ToolTipBase, col('#1c1916'))
    p.setColor(QPalette.ToolTipText, col('#f0ebe2'))

    # Texte
    p.setColor(QPalette.WindowText, col('#f0ebe2'))
    p.setColor(QPalette.Text, col('#f0ebe2'))
    p.setColor(QPalette.ButtonText, col('#f0ebe2'))
    p.setColor(QPalette.PlaceholderText, col('#6b6356'))
    p.setColor(QPalette.BrightText, col('#ff7a55'))

    # Boutons
    p.setColor(QPalette.Button, col('#1c1916'))
    p.setColor(QPalette.Shadow, col('#000000'))

    # Selection + accent (orange PrintNC)
    p.setColor(QPalette.Highlight, col('#e8821e'))
    p.setColor(QPalette.HighlightedText, col('#13110e'))
    p.setColor(QPalette.Link, col('#e8821e'))
    p.setColor(QPalette.LinkVisited, col('#c46a10'))

    # Rols "desactives"
    p.setColor(QPalette.Disabled, QPalette.WindowText, col('#6b6356'))
    p.setColor(QPalette.Disabled, QPalette.Text, col('#6b6356'))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, col('#6b6356'))

    app.setPalette(p)


def main():
    app = QApplication(sys.argv)
    _filtrer_warnings_qt()
    app.setApplicationName("Gestion site PrintNC")
    app.setStyleSheet(QSS)
    _palette_sombre(app)
    # Icone de fenetre = favicon du site
    icon_pm = load_svg_icon(FAVICON, size=128)
    if icon_pm and not icon_pm.isNull():
        app.setWindowIcon(QIcon(icon_pm))
    f = QFont()
    f.setFamilies(['Inter', 'Segoe UI', 'DejaVu Sans', 'Sans'])
    f.setPointSize(10)
    app.setFont(f)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
