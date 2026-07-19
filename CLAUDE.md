# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The **build-log website** for the PrintNC CNC (Atelier du Verdier) — a static site published via
**GitHub Pages** (custom domain in `CNAME`). This repo's root *is* the published site: `index.html`,
assets (`photos/`, `miniatures/`, favicons), and the generator tooling live here.

## The golden rule: `index.html` is GENERATED — never edit it by hand

`index.html` is built by **`generer_site.py`** from the `data/` files. Hand edits are overwritten on
the next generation. To change the site, edit the source in `data/`, then regenerate:

```bash
python3 generer_site.py     # writes index.html in the current dir; prints "Site genere : ..."
```

Then commit `data/…` **and** the regenerated `index.html` together.

## Where content lives (`data/`)

`generer_site.py` (see `construire()`) assembles the page from:

- **`videos.csv`** — the timeline (one row per video): `date, phase, fichier, lien, texte, duree, jalon`.
  Dates must be `AAAA-MM-JJ` and zero-padded (`2026-06-09`, not `2026-6-9`) or the chronological sort breaks.
  Phase: `meca` / `elec` / `soft` / `laser` (string slugs — keep `phase_info` in `generer_site.py`
  and `PHASE_LABEL`/`PHASE_COLORS` in `gestion_site.py` in sync when adding one).
- **`mois.json`** — month titles/descriptions for the timeline.
- **`maj.md`** → "Mises à jour" tab. **Changelog, newest entry first** (`# JJ mois AAAA — titre`, then `##` sections).
- **`doc.md`** → "Documentation" tab (machine documentation).
- **`recit.md`** → "Le récit" tab (narrative).
- **`glossaire.md`** → "Glossaire" tab.

## Markdown is parsed by custom, minimal converters — not full CommonMark

Each tab uses its own hand-rolled parser in `generer_site.py`, so only a subset of Markdown renders:

- `markdown_vers_html` → `maj.md`
- `markdown_vers_html_doc` (heading anchors, tables) → `doc.md` and `glossaire.md`
- `markdown_vers_html_recit` → `recit.md`

When adding content, **mirror the Markdown patterns already present in that file** (`#/##/###`
headings, `**bold**`, `` `code` ``, `-` lists, `|` tables in doc/glossaire, `[text](url)` links).
Don't assume exotic syntax works — check the relevant converter, or verify by regenerating and
grepping `index.html`. The HTML page template is the inline `MODELE` string in `generer_site.py`.

## Tooling

- **`gestion_site.py`** — PySide6/Qt6 GUI, the recommended daily tool (dashboard, generate, add
  video, thumbnails, Git publish, edit data). Launch from this dir: `python3 gestion_site.py` (or
  `./lancer_gestion_site.sh` if PySide6 is in the `~/.venv/kit_site` venv). See README.md for setup.
- **`ajouter_video.sh <file.mp4>`** — CLI: archives the video, makes a thumbnail (ffmpeg), appends to
  `videos.csv`, regenerates. **`generer_miniatures.sh`** — missing thumbnails. **`remplir_durees.py`**
  — fills video durations. **`installer_dependances.sh`** — deps per distro.
- **`lire_vfd.py`** — a HuangYang VFD parameter reader, unrelated to the site (kept here to be findable).

## Conventions

- **French** everywhere: content, UI strings, commit messages.
- Cross-project link target: the FreeCAD laser workbench is `atelierduverdier/LaserAtelier`, the machine
  config is `atelierduverdier/printnc-config`; `maj.md`/`doc.md` reference both.

## Publishing is outward-facing

`git push` publishes the site live (GitHub Pages via `CNAME`). Treat it as a publish action: commit
freely, but **confirm before pushing** unless told otherwise. Previewing is just opening the generated
`index.html` in a browser.
