#!/usr/bin/env python3
# =========================================================================
# generer_site.py - Atelier du Verdier
# Genere le site "PrintNC build log" (printnc-build.html) a partir du
# fichier data/videos.csv. Pour ajouter une video : ajoute une ligne au
# CSV, genere sa miniature, et relance ce script.
# =========================================================================
# UTILISATION :
#   python3 generer_site.py
# Produit : printnc-build.html (dans le dossier courant)
# =========================================================================

import csv, os, re
from collections import Counter

CSV = os.path.join('data', 'videos.csv')
SORTIE = 'index.html'

phase_info = {
    'meca': {'label': 'Mecanique',    'color': '#378ADD', 'bg': 'rgba(55,138,221,.12)'},
    'elec': {'label': 'Electronique', 'color': '#EF9F27', 'bg': 'rgba(239,159,39,.12)'},
    'soft': {'label': 'LinuxCNC',     'color': '#1D9E75', 'bg': 'rgba(29,158,117,.12)'},
}

# Titres et descriptions par mois (modifiable librement)
mois_info = {
    '2026-01': {'nom': 'Janvier 2026',  'titre': 'Les debuts et le montage a blanc',          'desc': 'Premieres etapes de construction et essai d\'assemblage.'},
    '2026-02': {'nom': 'Fevrier 2026',  'titre': 'La saga de l\'axe Z',                        'desc': 'Plaques reimprimees, rajustees, et le cablage de la broche.'},
    '2026-03': {'nom': 'Mars 2026',     'titre': 'Mecanique finalisee, place a l\'electrique', 'desc': 'Montage du portique termine, debut du boitier electrique.'},
    '2026-04': {'nom': 'Avril 2026',    'titre': 'Mise en route... et la carte grillee',       'desc': 'Premiers mouvements sous LinuxCNC, puis un coup dur.'},
    '2026-05': {'nom': 'Mai 2026',      'titre': 'La renaissance et les reglages fins',        'desc': 'Nouvelle carte, premiere decoupe, palpeur et precision.'},
    '2026-06': {'nom': 'Juin 2026',     'titre': 'ATC, relais et interface',                   'desc': 'Accessoires, automatismes et personnalisation de QtDragon.'},
}

# Noms des mois pour les onglets (FR)
mois_onglet = {'01': 'Janvier', '02': 'Fevrier', '03': 'Mars', '04': 'Avril',
               '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Aout',
               '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Decembre'}


def date_fr(d):
    a, m, j = d.split('-')
    return f"{j}/{m}/{a}"


def charger():
    lignes = []
    with open(CSV, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if not r.get('date'):
                continue
            lignes.append(r)
    lignes.sort(key=lambda x: x['date'], reverse=True)
    return lignes


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def markdown_vers_html_recit(md):
    """Convertit recit.md en HTML avec les classes CSS du recit."""
    import re as _re
    out = []
    for ln in md.split('\n'):
        if ln.startswith('# '):
            out.append(f'<h3 class="recit-h">{esc(ln[2:].strip())}</h3>')
        elif ln.startswith('> '):
            out.append(f'<p class="recit-cite">{esc(ln[2:].strip())}</p>')
        elif ln.strip().startswith('!['):
            m = _re.match(r'!\[([^\]]*)\]\(([^)]+)\)', ln.strip())
            if m:
                alt = esc(m.group(1))
                url = m.group(2)
                out.append(f'<figure class="doc-photo"><img src="{url}" alt="{alt}" loading="lazy"><figcaption>{alt}</figcaption></figure>')
        elif ln.strip():
            txt = esc(ln.strip())
            txt = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', txt)
            out.append(f'<p class="recit-p">{txt}</p>')
    return '\n'.join(out)


def markdown_vers_html(md):
    # Convertit le changelog markdown en HTML : # = date (h2), ## = titre (h3),
    # blocs ``` = code, le reste en paragraphes.
    out = []
    lignes = md.split('\n')
    i = 0
    while i < len(lignes):
        ln = lignes[i]
        if ln.startswith('```'):
            # bloc de code jusqu'au prochain ```
            i += 1
            code = []
            while i < len(lignes) and not lignes[i].startswith('```'):
                code.append(esc(lignes[i]))
                i += 1
            out.append('<pre class="maj-code">' + '\n'.join(code) + '</pre>')
        elif ln.startswith('# '):
            out.append(f'<div class="maj-date-sep">{esc(ln[2:].strip())}</div>')
        elif ln.startswith('## '):
            out.append(f'<h3 class="maj-titre">{esc(ln[3:].strip())}</h3>')
        elif ln.lstrip().startswith('|') and ln.rstrip().endswith('|'):
            # tableau markdown : accumuler les lignes commencant par |
            tbl = [ln]
            while i + 1 < len(lignes) and lignes[i+1].lstrip().startswith('|'):
                i += 1
                tbl.append(lignes[i])
            # construire le tableau HTML
            rows = []
            for k, trow in enumerate(tbl):
                cells = [c.strip() for c in trow.strip().strip('|').split('|')]
                # ligne de separation (---) ignoree
                if all(set(c) <= set('-: ') for c in cells):
                    continue
                tag = 'th' if k == 0 else 'td'
                cells_html = ''.join(f'<{tag}>{esc(c)}</{tag}>' for c in cells)
                rows.append(f'<tr>{cells_html}</tr>')
            out.append('<table class="doc-table">' + ''.join(rows) + '</table>')
        elif ln.strip():
            # paragraphe : accumuler les lignes consecutives non vides hors code/titres/tableaux
            para = [esc(ln.strip())]
            while (i + 1 < len(lignes) and lignes[i+1].strip()
                   and not lignes[i+1].startswith(('#', '```'))
                   and not lignes[i+1].lstrip().startswith('|')):
                i += 1
                para.append(esc(lignes[i].strip()))
            txt = ' '.join(para)
            import re as _re
            txt = _re.sub(r'`([^`]+)`', r'<code>\1</code>', txt)
            out.append(f'<p class="maj-desc">{txt}</p>')
        i += 1
    return '\n'.join(out)


def markdown_vers_html_doc(md):
    # Comme markdown_vers_html mais les sections # deviennent des blocs
    # depliables <details>/<summary>. Les ## sont des sous-titres a l'interieur.
    import re as _re
    # Decouper le markdown en sections delimitees par les # (niveau 1)
    sections = _re.split(r'\n(?=# )', '\n' + md)
    out = []
    for section in sections:
        if not section.strip():
            continue
        lignes = section.split('\n')
        # Premiere ligne non vide = titre de section (#)
        titre = ''
        contenu_lignes = []
        for ln in lignes:
            if ln.startswith('# ') and not titre:
                titre = esc(ln[2:].strip())
            else:
                contenu_lignes.append(ln)
        contenu_md = '\n'.join(contenu_lignes)
        # Convertir le contenu de la section (sans les # de niveau 1)
        contenu_html = _convertir_contenu_doc(contenu_md)
        if titre:
            out.append(f'<details class="doc-section">'
                       f'<summary class="doc-section-titre">{titre}</summary>'
                       f'<div class="doc-section-corps">{contenu_html}</div>'
                       f'</details>')
        else:
            out.append(contenu_html)
    return '\n'.join(out)


def _render_cell(txt):
    """Convertit le markdown d'une cellule de tableau en HTML."""
    import re as _re
    # Liens [texte](url)
    def rpl_lien(m):
        label = esc(m.group(1))
        url = m.group(2)
        return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
    txt = _re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rpl_lien, txt)
    # Gras **texte**
    txt = _re.sub(r'\*\*([^*]+)\*\*', lambda m: f'<strong>{esc(m.group(1))}</strong>', txt)
    # Code `texte`
    txt = _re.sub(r'`([^`]+)`', lambda m: f'<code>{esc(m.group(1))}</code>', txt)
    # Echapper le reste (pas deja echappe)
    # On echappe seulement les parties sans balises HTML
    # Simple : on suppose que le reste est du texte pur apres les remplacements
    # (les URLs dans les liens ne sont pas echappees)
    return txt


def _convertir_contenu_doc(md):
    # Convertit le contenu d'une section doc (sans #, avec ##, tableaux, code)
    import re as _re
    out = []
    lignes = md.split('\n')
    i = 0
    while i < len(lignes):
        ln = lignes[i]
        if ln.startswith('```'):
            i += 1
            code = []
            while i < len(lignes) and not lignes[i].startswith('```'):
                code.append(esc(lignes[i]))
                i += 1
            out.append('<pre class="maj-code">' + '\n'.join(code) + '</pre>')
        elif ln.startswith('## '):
            out.append(f'<h3 class="doc-sous-titre">{esc(ln[3:].strip())}</h3>')
        elif ln.startswith('### '):
            out.append(f'<h4 class="doc-sous-titre-3">{esc(ln[4:].strip())}</h4>')
        elif ln.startswith('> '):
            out.append(f'<blockquote class="doc-note">{esc(ln[2:].strip())}</blockquote>')
        elif ln.lstrip().startswith('|') and ln.rstrip().endswith('|'):
            tbl = [ln]
            while i + 1 < len(lignes) and lignes[i+1].lstrip().startswith('|'):
                i += 1
                tbl.append(lignes[i])
            rows = []
            for k, trow in enumerate(tbl):
                # Decouper proprement en gerant les virgules dans les cellules
                raw = trow.strip()
                if raw.startswith('|'): raw = raw[1:]
                if raw.endswith('|'): raw = raw[:-1]
                cells = [c.strip() for c in raw.split('|')]
                # Ligne separatrice (---)
                if all(set(c) <= set('-: ') for c in cells):
                    continue
                tag = 'th' if k == 0 else 'td'
                cells_html = ''
                for c in cells:
                    # Convertir markdown dans les cellules :
                    # liens [texte](url), gras **texte**, code `texte`
                    cell = esc(c)
                    # Liens [texte](url) — apres esc, les & sont &amp; etc.
                    # On re-parse avant esc pour les liens
                    cell = _render_cell(c)
                    cells_html += f'<{tag}>{cell}</{tag}>'
                rows.append(f'<tr>{cells_html}</tr>')
            out.append('<table class="doc-table">' + ''.join(rows) + '</table>')
        elif ln.strip().startswith('!['):
            # Image markdown : ![alt](url)
            import re as _re
            m = _re.match(r'!\[([^\]]*)\]\(([^)]+)\)', ln.strip())
            if m:
                alt = esc(m.group(1))
                url = m.group(2)
                out.append(f'<figure class="doc-photo"><img src="{url}" alt="{alt}" loading="lazy"><figcaption>{alt}</figcaption></figure>')
            else:
                out.append(f'<p class="maj-desc">{esc(ln.strip())}</p>')
        elif ln.strip().startswith('- ') or ln.strip().startswith('* '):
            # liste a puces : accumuler tous les items consecutifs
            items = []
            while i < len(lignes) and (lignes[i].strip().startswith('- ') or lignes[i].strip().startswith('* ')):
                item_txt = lignes[i].strip()[2:]
                item_txt = _re.sub(r'`([^`]+)`', r'<code>\1</code>', esc(item_txt))
                item_txt = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item_txt)
                items.append(f'<li>{item_txt}</li>')
                i += 1
            out.append('<ul class="doc-liste">' + ''.join(items) + '</ul>')
            continue
        elif ln.strip():
            # Paragraphe : ne pas avaler les lignes qui sont des items de liste
            para = [esc(ln.strip())]
            while (i + 1 < len(lignes) and lignes[i+1].strip()
                   and not lignes[i+1].startswith(('#', '```', '>'))
                   and not lignes[i+1].lstrip().startswith('|')
                   and not lignes[i+1].strip().startswith('- ')
                   and not lignes[i+1].strip().startswith('* ')
                   and not lignes[i+1].strip().startswith('![')):
                i += 1
                para.append(esc(lignes[i].strip()))
            txt = ' '.join(para)
            # Liens [texte](url) AVANT les autres conversions
            txt = _re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                          r'<a href="\2" target="_blank" rel="noopener">\1</a>', txt)
            txt = _re.sub(r'`([^`]+)`', r'<code>\1</code>', txt)
            txt = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', txt)
            # Detecter les points importants/attention
            txt_lower = txt.lower()
            if txt_lower.startswith('<strong>point important') or \
               txt_lower.startswith('<strong>important') or \
               txt_lower.startswith('<strong>attention') or \
               txt_lower.startswith('<strong>note'):
                out.append(f'<p class="doc-important">{txt}</p>')
            else:
                out.append(f'<p class="maj-desc">{txt}</p>')
        i += 1
    return '\n'.join(out)


def construire():
    jalons = charger()
    counts = Counter(j['date'][:7] for j in jalons)

    # Onglets mensuels (uniques, dans l'ordre)
    mois_presents = sorted(set(j['date'][:7] for j in jalons), reverse=True)
    onglets_principaux = [
        '      <button class="tab tab-accueil active" data-month="accueil">Accueil</button>',
        '      <button class="tab" data-month="all">Timeline</button>',
        '      <button class="tab tab-recit" data-month="recit">Le récit</button>',
        '      <button class="tab tab-maj" data-month="maj">Mises à jour</button>',
        '      <button class="tab tab-doc" data-month="doc">Documentation</button>',
        '      <button class="tab tab-gloss" data-month="gloss">Glossaire</button>',
    ]
    onglets_mois = []
    for m in mois_presents:
        nom = mois_onglet.get(m[5:7], m)
        onglets_mois.append(f'      <button class="tab tab-mois" data-month="{m}">{nom}</button>')

    onglets = (
        '\n'.join(onglets_principaux) +
        '\n    </div>\n    <div class="tabs tabs-mois">\n' +
        '\n'.join(onglets_mois)
    )

    # Blocs timeline
    blocks = []
    cur = None
    for j in jalons:
        m = j['date'][:7]
        if m != cur:
            cur = m
            # Nom par defaut intelligent : "Juillet 2026" au lieu de "2026-07"
            nom_defaut = f"{mois_onglet.get(m[5:7], m)} {m[:4]}"
            mi = mois_info.get(m, {'nom': nom_defaut, 'titre': '', 'desc': ''})
            blocks.append(f'''    <section class="month" data-month="{m}">
      <div class="mhead">
        <div class="mnom">{mi['nom']}</div>
        <h2 class="mtitre">{mi['titre']}</h2>
        <p class="mdesc">{mi['desc']} <span class="mcount">{counts[m]} etapes</span></p>
      </div>
    </section>''')
        pi = phase_info.get(j['phase'], phase_info['meca'])
        lien = j.get('lien', '').strip()
        fnoext = j['fichier'].replace('.mp4', '') if j.get('fichier') else ''
        if lien and fnoext:
            vid = (f'<a class="vid-thumb" href="{lien}" target="_blank" rel="noopener" title="Voir la video">'
                   f'<img src="miniatures/{fnoext}.jpg" loading="lazy" alt="Miniature {date_fr(j["date"])}" '
                   f'onerror="this.parentNode.classList.add(\'noimg\')">'
                   f'<span class="overlay"><span class="play">&#9654;</span></span></a>')
        elif lien:
            vid = f'<a class="vid" href="{lien}" target="_blank" rel="noopener"><span class="play">&#9654;</span> Voir la video</a>'
        else:
            vid = ''
        texte = j.get('texte', '') or 'Etape de construction (video du jour)'
        # Liens markdown [texte](url)
        texte = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                       r'<a href="\2" target="_blank" rel="noopener">\1</a>', texte)
        # URLs brutes (http/https) pas deja dans une balise
        texte = re.sub(r'(?<!["\'>])(https?://[^\s<]+)',
                       r'<a href="\1" target="_blank" rel="noopener">\1</a>', texte)
        blocks.append(f'''    <article class="item" data-phase="{j['phase']}" data-month="{m}">
      <div class="dot" style="background:{pi['color']}"></div>
      <div class="content">
        <div class="meta"><span class="date">{date_fr(j['date'])}</span><span class="tag" style="background:{pi['bg']};color:{pi['color']}">{pi['label']}</span></div>
        <p class="text">{texte}</p>
        {vid}
      </div>
    </article>''')

    # Mises a jour : converties depuis data/maj.md (markdown technique)
    maj_html = ''
    mp = os.path.join('data', 'maj.md')
    if os.path.exists(mp):
        maj_html = markdown_vers_html(open(mp, encoding='utf-8').read())

    # Documentation : convertie depuis data/doc.md
    doc_html = ''
    dp = os.path.join('data', 'doc.md')
    if os.path.exists(dp):
        doc_html = markdown_vers_html_doc(open(dp, encoding='utf-8').read())

    # Recit : converti depuis data/recit.md (ou recit.html pour compatibilite)
    recit = ''
    rp_md = os.path.join('data', 'recit.md')
    rp_html = os.path.join('data', 'recit.html')
    if os.path.exists(rp_md):
        recit = markdown_vers_html_recit(open(rp_md, encoding='utf-8').read())
    elif os.path.exists(rp_html):
        recit = open(rp_html, encoding='utf-8').read()

    n = len(jalons)
    html = MODELE.replace('__ONGLETS__', onglets)
    html = html.replace('__BLOCKS__', '\n'.join(blocks))
    html = html.replace('__RECIT__', recit)
    html = html.replace('__MAJ__', maj_html)
    html = html.replace('__DOC__', doc_html)
    html = html.replace('__N__', str(n))
    open(SORTIE, 'w', encoding='utf-8').write(html)
    print(f"Site genere : {SORTIE} ({n} etapes, {len(mois_presents)} mois)")


MODELE = '''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PrintNC &mdash; Journal de construction | Atelier du Verdier</title>
<style>
  :root{--bg:#13110e;--surface:#1c1916;--text:#f0ebe2;--muted:#a89e8c;--faint:#6b6356;--orange:#e8821e;--line:#332d24;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;}
  .wrap{max-width:820px;margin:0 auto;padding:0 20px;}
  header{padding:70px 0 44px;border-bottom:1px solid var(--line);}
  .logo{max-width:200px;height:auto;margin-bottom:24px;display:block;}
  .kicker{font-size:13px;letter-spacing:3px;color:var(--orange);text-transform:uppercase;margin-bottom:14px;}
  h1{font-size:clamp(34px,6vw,56px);font-weight:700;line-height:1.05;letter-spacing:-1px;margin-bottom:18px;}
  h1 span{color:var(--orange);}
  .sub{font-size:18px;color:var(--muted);max-width:560px;}
  .stats{display:flex;gap:40px;margin-top:36px;flex-wrap:wrap;}
  .stat .n{font-size:32px;font-weight:700;}
  .stat .l{font-size:13px;color:var(--faint);text-transform:uppercase;letter-spacing:1px;}
  .nav{position:sticky;top:0;background:rgba(19,17,14,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);z-index:10;}
  .tabs{display:flex;gap:6px;flex-wrap:wrap;padding:12px 20px 6px;}
  .tabs-mois{display:flex;gap:6px;flex-wrap:wrap;padding:4px 20px 10px;border-top:1px solid var(--line);}
  .tab-mois{font-size:13px;padding:6px 13px;}
  .tab{background:var(--surface);border:1px solid var(--line);color:var(--muted);padding:9px 16px;border-radius:8px;font-size:14px;cursor:pointer;transition:.15s;font-weight:500;}
  .tab:hover{border-color:var(--orange);color:var(--text);}
  .tab.active{background:var(--orange);border-color:var(--orange);color:#13110e;font-weight:600;}
  .tab-recit{border-color:var(--orange);color:var(--orange);}
  .tab-recit.active{background:var(--orange);color:#13110e;}
  .phases-row{display:flex;align-items:center;justify-content:space-between;padding:0 20px 10px;flex-wrap:wrap;gap:6px;}
  .phases{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
  .tab-actions{display:flex;align-items:center;gap:8px;margin-left:auto;}
  .plabel{font-size:12px;color:var(--faint);text-transform:uppercase;letter-spacing:1px;margin-right:4px;}
  .pbtn{background:transparent;border:1px solid var(--line);color:var(--muted);padding:5px 12px;border-radius:14px;font-size:13px;cursor:pointer;transition:.15s;}
  .pbtn:hover{border-color:var(--orange);color:var(--text);}
  .pbtn.active{border-color:var(--orange);color:var(--orange);}
  .timeline{position:relative;padding:0 0 80px;}
  .month{padding:44px 0 4px;}
  .month.hidden{display:none;}
  .mnom{font-size:13px;letter-spacing:2px;text-transform:uppercase;color:var(--orange);margin-bottom:6px;}
  .mtitre{font-size:28px;font-weight:700;letter-spacing:-.5px;margin-bottom:8px;}
  .mdesc{font-size:15px;color:var(--muted);}
  .mcount{display:inline-block;margin-left:8px;font-size:12px;color:var(--faint);border:1px solid var(--line);padding:2px 8px;border-radius:10px;}
  .item{position:relative;padding:18px 0 12px 42px;}
  .item::before{content:'';position:absolute;left:7px;top:26px;bottom:-12px;width:2px;background:var(--line);}
  .item:last-child::before{display:none;}
  .dot{position:absolute;left:0;top:23px;width:16px;height:16px;border-radius:50%;border:3px solid var(--bg);z-index:2;}
  .meta{display:flex;align-items:center;gap:12px;margin-bottom:8px;flex-wrap:wrap;}
  .date{font-size:14px;color:var(--faint);font-variant-numeric:tabular-nums;}
  .tag{font-size:12px;padding:3px 10px;border-radius:12px;font-weight:600;}
  .text{font-size:16px;margin-bottom:12px;}
  .text a{color:var(--orange);text-decoration:none;border-bottom:1px solid var(--orange);transition:.15s;}
  .text a:hover{opacity:.7;}
  .vid{display:inline-flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 14px;font-size:13px;color:var(--muted);cursor:pointer;transition:.15s;text-decoration:none;}
  .vid:hover{border-color:var(--orange);color:var(--text);}
  .play{color:var(--orange);font-size:11px;}
  .vid-thumb{display:block;position:relative;width:200px;max-width:100%;border-radius:10px;overflow:hidden;border:1px solid var(--line);line-height:0;transition:.15s;}
  .vid-thumb img{width:100%;height:auto;display:block;}
  .vid-thumb .overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.25);opacity:0;transition:.15s;}
  .vid-thumb .overlay .play{font-size:22px;color:#fff;background:rgba(232,130,30,.9);width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;padding-left:3px;}
  .vid-thumb:hover{border-color:var(--orange);}
  .vid-thumb:hover .overlay{opacity:1;}
  .vid-thumb.noimg{width:auto;border:none;}
  .vid-thumb.noimg img{display:none;}
  .vid-thumb.noimg::after{content:'\\25B6  Voir la video';display:inline-flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 14px;font-size:13px;color:var(--muted);line-height:1.4;}
  .vid-thumb.noimg .overlay{display:none;}
  .item.hidden{display:none;}
  .empty{padding:40px 0;color:var(--faint);font-size:15px;text-align:center;display:none;}
  #recit{display:none;padding:30px 0 60px;max-width:680px;}
  .recit-progress{position:fixed;top:0;left:0;height:3px;background:var(--orange);width:0%;z-index:20;transition:width .1s linear;pointer-events:none;}
  #recit.show{display:block;}
  .recit-h{font-size:22px;color:var(--orange);margin:36px 0 14px;font-weight:700;}
  .recit-h:first-child{margin-top:8px;}
  .recit-p{font-size:16px;line-height:1.8;color:var(--text);margin-bottom:16px;}
  .recit-cite{font-size:18px;font-style:italic;color:var(--muted);border-left:3px solid var(--orange);padding-left:18px;margin:24px 0;}
  .tab-maj{border-color:var(--orange);color:var(--orange);}
  .tab-maj.active{background:var(--orange);color:#13110e;}
  #maj{display:none;padding:30px 0 60px;max-width:680px;}
  #maj.show{display:block;}
  .maj-item{border-left:2px solid var(--line);padding:0 0 24px 20px;position:relative;}
  .maj-item::before{content:'';position:absolute;left:-5px;top:4px;width:8px;height:8px;border-radius:50%;background:var(--orange);}
  .maj-meta{display:flex;align-items:center;gap:10px;margin-bottom:4px;}
  .maj-date{font-size:13px;color:var(--faint);font-variant-numeric:tabular-nums;}
  .maj-titre{font-size:18px;font-weight:600;color:var(--text);margin-bottom:6px;}
  .maj-desc{font-size:15px;line-height:1.7;color:var(--muted);margin-bottom:12px;}
  .maj-date-sep{font-size:13px;letter-spacing:2px;text-transform:uppercase;color:var(--orange);font-weight:600;margin:40px 0 18px;padding-bottom:8px;border-bottom:1px solid var(--line);}
  .maj-date-sep:first-child{margin-top:0;}
  .maj-code{background:#0d0b09;border:1px solid var(--line);border-radius:8px;padding:14px 16px;font-family:'Consolas','Monaco',monospace;font-size:13px;line-height:1.5;color:#d8cfc0;overflow-x:auto;margin:8px 0 16px;white-space:pre;}
  .maj-desc code{background:#0d0b09;border:1px solid var(--line);border-radius:4px;padding:1px 6px;font-family:monospace;font-size:13px;color:var(--orange);}
  .maj-desc a, .doc-important a{color:var(--orange);text-decoration:none;border-bottom:1px solid var(--orange);transition:.15s;}
  .maj-desc a:hover, .doc-important a:hover{opacity:.7;}
  .tab-doc{border-color:var(--orange);color:var(--orange);}
  .tab-gloss{border-color:var(--orange);color:var(--orange);}
  .tab-accueil{border-color:var(--orange);color:var(--orange);}
  .tab-accueil.active{background:var(--orange);color:#13110e;}
  /* Page accueil */
  #accueil{display:none;padding:24px 0 50px;}
  #accueil.show{display:block;}
  .hero{display:flex;gap:28px;align-items:center;margin-bottom:44px;flex-wrap:wrap;}
  .hero-img{width:340px;max-width:100%;border-radius:14px;border:1px solid var(--line);object-fit:cover;}
  .hero-text{flex:1;min-width:260px;}
  .hero-titre{font-size:30px;margin:0 0 12px;color:var(--text);font-weight:600;}
  .hero-sous{font-size:16px;color:var(--muted);line-height:1.6;margin:0 0 20px;}
  .hero-liens{display:flex;gap:10px;flex-wrap:wrap;}
  .hero-btn{display:inline-block;padding:9px 16px;background:var(--orange);color:#13110e;border-radius:8px;text-decoration:none;font-size:14px;font-weight:500;transition:.15s;}
  .hero-btn:hover{opacity:.85;}
  .hero-btn.alt{background:transparent;border:1px solid var(--orange);color:var(--orange);}
  .accueil-h{font-size:20px;color:var(--orange);margin:40px 0 18px;font-weight:600;}
  .accueil-p{font-size:15px;color:var(--muted);line-height:1.6;margin:0 0 18px;}
  .specs{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;}
  .spec{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px;}
  .spec-val{font-size:18px;color:var(--text);font-weight:600;margin-bottom:4px;}
  .spec-lbl{font-size:13px;color:var(--faint);}
  .cartes{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;}
  .carte{text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:18px;cursor:pointer;transition:.15s;font-family:inherit;}
  .carte:hover{border-color:var(--orange);transform:translateY(-2px);}
  .carte-titre{font-size:16px;color:var(--orange);font-weight:600;margin-bottom:6px;}
  .carte-desc{font-size:14px;color:var(--muted);line-height:1.5;}
  .ressources{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;}
  .ressource{display:block;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:18px;text-decoration:none;transition:.15s;}
  .ressource:hover{border-color:var(--orange);transform:translateY(-2px);}
  .ressource-titre{font-size:15px;color:var(--orange);font-weight:600;margin-bottom:6px;font-family:monospace;}
  .ressource-desc{font-size:13px;color:var(--muted);line-height:1.5;}
  .tab-gloss.active{background:var(--orange);color:#13110e;}
  .tab-doc.active{background:var(--orange);color:#13110e;}
  #doc{display:none;padding:30px 0 60px;max-width:720px;}
  #doc.show{display:block;}
  .doc-table{width:100%;border-collapse:collapse;margin:10px 0 18px;font-size:14px;}
  .doc-table th{background:var(--surface);color:var(--orange);text-align:left;padding:8px 12px;border:1px solid var(--line);font-weight:600;}
  .doc-table td{padding:8px 12px;border:1px solid var(--line);color:var(--muted);}
  .doc-section-hidden{display:none !important;}
  .doc-section{border:1px solid var(--line);border-radius:10px;margin-bottom:12px;overflow:hidden;}
  .doc-section[open]{border-color:var(--orange);}
  .doc-section-titre{font-size:17px;font-weight:600;color:var(--text);padding:14px 18px;cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;background:var(--surface);}
  .doc-section-titre::-webkit-details-marker{display:none;}
  .doc-section-titre::after{content:'＋';color:var(--orange);font-size:18px;transition:.2s;}
  .doc-section[open] .doc-section-titre::after{content:'－';}
  .doc-section-titre:hover{background:var(--surface2);color:var(--orange);}
  .doc-section-corps{padding:18px 18px 10px;border-top:1px solid var(--line);}
  .doc-sous-titre{font-size:16px;font-weight:600;color:var(--orange);margin:18px 0 10px;}
  .doc-sous-titre:first-child{margin-top:4px;}
  .doc-sous-titre-3{font-size:14px;font-weight:600;color:var(--muted);margin:12px 0 6px;}
  .doc-note{border-left:3px solid var(--orange);padding:8px 14px;color:var(--muted);font-style:italic;margin:10px 0 14px;background:var(--surface);}
  .doc-important{border-left:3px solid var(--orange);padding:10px 16px;color:var(--text);margin:14px 0 18px;background:rgba(232,130,30,.08);border-radius:0 8px 8px 0;}
  .doc-important strong{color:var(--orange);}
  .doc-table td a{color:var(--orange);text-decoration:none;}
  .doc-table td a:hover{text-decoration:underline;}
  .doc-liste{margin:6px 0 14px 18px;color:var(--muted);font-size:15px;line-height:1.8;}
  .doc-liste li{margin-bottom:2px;}
  .doc-liste li strong{color:var(--orange);}
  .doc-liste li code{background:#0d0b09;border:1px solid var(--line);border-radius:4px;padding:1px 6px;font-family:monospace;font-size:13px;color:var(--orange);}
  .doc-photo{margin:14px 0 20px;text-align:center;}
  .doc-photo img{max-width:100%;max-height:320px;object-fit:cover;border-radius:10px;border:1px solid var(--line);display:block;margin:0 auto;cursor:zoom-in;transition:.2s;}
  .doc-photo img:hover{border-color:var(--orange);opacity:.9;}
  .doc-photo figcaption{font-size:13px;color:var(--faint);margin-top:6px;font-style:italic;}
  /* Lightbox */
  .lightbox{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:1000;align-items:center;justify-content:center;cursor:zoom-out;}
  .lightbox.open{display:flex;}
  .lightbox img{max-width:90vw;max-height:90vh;object-fit:contain;border-radius:8px;box-shadow:0 0 40px rgba(0,0,0,.8);}
  .lightbox-close{position:fixed;top:18px;right:24px;font-size:32px;color:#fff;cursor:pointer;line-height:1;opacity:.7;transition:.15s;}
  .lightbox-close:hover{opacity:1;color:var(--orange);}
  .lightbox-caption{position:fixed;bottom:20px;left:0;right:0;text-align:center;color:var(--muted);font-size:14px;font-style:italic;pointer-events:none;}
  @media print{
    .nav,.filters,.theme-toggle,.tab-actions,.recit-progress,.github-ribbon,#tl,#recit,#maj,#accueil,footer{display:none!important;}
    #doc{display:block!important;max-width:100%!important;}
    .doc-section{border:none!important;margin-bottom:12px!important;}
    .doc-section-titre{background:none!important;border-bottom:1px solid #ccc!important;}
    .doc-section-corps{display:block!important;}
    .doc-table{font-size:11px!important;}
    a{color:#000!important;text-decoration:none!important;}
    body{background:#fff!important;color:#000!important;}
  }
  .tab-actions{padding:4px 20px 6px;display:flex;align-items:center;gap:8px;justify-content:flex-end;}
  .copy-link-btn{background:transparent;border:1px solid var(--line);color:var(--faint);padding:4px 12px;border-radius:14px;font-size:12px;cursor:pointer;transition:.15s;}
  .copy-link-btn:hover{border-color:var(--orange);color:var(--orange);}
  .copy-ok{font-size:12px;color:var(--orange);opacity:0;transition:.3s;}
  .copy-ok.show{opacity:1;}
  .theme-toggle{position:fixed;top:14px;right:120px;z-index:25;background:var(--surface);border:1px solid var(--line);color:var(--orange);font-size:18px;width:36px;height:36px;border-radius:50%;cursor:pointer;transition:.2s;display:flex;align-items:center;justify-content:center;}
  .theme-toggle:hover{background:var(--orange);color:#13110e;}
  /* Ruban GitHub en haut a droite */
  .github-ribbon{position:fixed;top:0;right:0;z-index:24;width:130px;height:130px;overflow:hidden;pointer-events:none;}
  .github-ribbon a{position:absolute;display:block;width:170px;padding:7px 0;background:var(--orange);color:#13110e;font-size:12px;font-weight:700;text-align:center;text-decoration:none;letter-spacing:.5px;transform:rotate(45deg);right:-42px;top:32px;box-shadow:0 2px 6px rgba(0,0,0,.35);pointer-events:auto;transition:.2s;}
  .github-ribbon a:hover{background:#ff9a3c;}
  @media(max-width:600px){.theme-toggle{right:90px;}.github-ribbon{width:100px;height:100px;}.github-ribbon a{font-size:10px;width:150px;right:-40px;top:24px;}}
  body.jour{--bg:#f5f2ee;--surface:#ede8e0;--surface2:#e0d9cf;--text:#1a1612;--muted:#5a4f44;--faint:#9a8f84;--line:#d0c8bc;--orange:#c46a10;}
  body.jour .tab{background:var(--surface);border-color:var(--line);color:var(--muted);}
  body.jour .tab:hover{border-color:var(--orange);color:var(--text);}
  body.jour .tab.active{background:var(--orange);border-color:var(--orange);color:#fff;}
  body.jour .pbtn{border-color:var(--line);color:var(--muted);}
  body.jour .pbtn.active{border-color:var(--orange);color:var(--orange);}
  body.jour .fbtn{background:var(--surface);border-color:var(--line);color:var(--muted);}
  body.jour .fbtn.active{background:var(--orange);border-color:var(--orange);color:#fff;}
  body.jour .nav{background:rgba(245,242,238,.95);}
  body.jour .lightbox{background:rgba(0,0,0,.85);}
  footer{border-top:1px solid var(--line);padding:40px 0 60px;color:var(--faint);font-size:14px;text-align:center;}
  footer a{color:var(--orange);text-decoration:none;}
  .social{display:flex;justify-content:center;gap:22px;margin-bottom:18px;}
  .social a{color:var(--faint);transition:.2s;display:flex;}
  .social a:hover{color:var(--orange);transform:translateY(-2px);}
  .footer-text{font-size:13px;}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <img class="logo" src="https://raw.githubusercontent.com/atelierduverdier/printnc-config/main/PrintNC.png" alt="Logo PrintNC Atelier du Verdier" onerror="this.style.display='none'">
    <button class="theme-toggle" id="theme-toggle" title="Mode jour/nuit">☀</button>
    <div class="kicker">Atelier du Verdier</div>
    <h1>Journal de construction</h1>
    <p class="sub">L'histoire complète d'une fraiseuse CNC construite de zero, du premier montage à blanc jusqu'à la machine pleinement fonctionnelle.</p>
    <div class="stats">
      <div class="stat"><div class="n">5</div><div class="l">mois de travail</div></div>
      <div class="stat"><div class="n">1275&times;1275</div><div class="l">surface (mm)</div></div>
      <div class="stat"><div class="n">8000</div><div class="l">mm/min</div></div>
    </div>
  </div>
</header>
<nav class="nav">
  <div class="wrap" style="padding:0;">
    <div class="tabs">
__ONGLETS__
    </div>
    <div class="phases-row">
      <div class="phases">
      <span class="plabel">Filtre</span>
      <button class="pbtn active" data-filter="all">Tout</button>
      <button class="pbtn" data-filter="meca">Mecanique</button>
      <button class="pbtn" data-filter="elec">Electronique</button>
      <button class="pbtn" data-filter="soft">LinuxCNC</button>
      </div>
      <div class="tab-actions">
        <span class="copy-ok" id="copy-ok">✓ Copié !</span>
        <button class="copy-link-btn" id="copy-link-btn" title="Copier le lien de cet onglet">🔗 Lien</button>
        <button class="copy-link-btn" id="print-btn" title="Imprimer la documentation" style="display:none;" onclick="window.print()">🖨 Imprimer</button>
      </div>
    </div>
  </div>
</nav>
<div class="github-ribbon"><a href="https://github.com/atelierduverdier" target="_blank" rel="noopener">GitHub</a></div>
<div class="recit-progress" id="recit-progress"></div>
<main class="wrap">
  <section id="accueil">
    <div class="hero">
      <img class="hero-img" src="photos/printnc.jpg" alt="PrintNC de l'Atelier du Verdier" onerror="this.style.display='none'">
      <div class="hero-text">
        <h1 class="hero-titre">PrintNC — Atelier du Verdier</h1>
        <p class="hero-sous">Journal de construction d'une fraiseuse CNC PrintNC, de la première pièce au premier copeau. Documentation complète, ouverte et reproductible.</p>
      </div>
    </div>

    <h2 class="accueil-h">Caractéristiques en un coup d'œil</h2>
    <div class="specs">
      <div class="spec"><div class="spec-val">~1275 × 1275 mm</div><div class="spec-lbl">Zone de travail (chassis)</div></div>
      <div class="spec"><div class="spec-val">8000 mm/min</div><div class="spec-lbl">Vitesse de travail X/Y</div></div>
      <div class="spec"><div class="spec-val">0.03–0.1 mm</div><div class="spec-lbl">Précision typique</div></div>
      <div class="spec"><div class="spec-val">2.2 kW</div><div class="spec-lbl">Broche G-Penny ER20</div></div>
      <div class="spec"><div class="spec-val">24000 tr/min</div><div class="spec-lbl">Vitesse broche max</div></div>
      <div class="spec"><div class="spec-val">Nema 23</div><div class="spec-lbl">Moteurs boucle fermée</div></div>
      <div class="spec"><div class="spec-val">LinuxCNC 2.9.8</div><div class="spec-lbl">QtDragon HD + FlexiHAL</div></div>
      <div class="spec"><div class="spec-val">~4046 €</div><div class="spec-lbl">Budget total du projet</div></div>
    </div>

    <h2 class="accueil-h">Explorer le site</h2>
    <div class="cartes">
      <button class="carte" onclick="document.querySelector('.tab[data-month=&quot;recit&quot;]').click()">
        <div class="carte-titre">Le récit</div>
        <div class="carte-desc">L'histoire complète de la construction, mois par mois, avec les galères et les victoires.</div>
      </button>
      <button class="carte" onclick="document.querySelector('.tab[data-month=&quot;all&quot;]').click()">
        <div class="carte-titre">Timeline</div>
        <div class="carte-desc">Le journal vidéo quotidien, étape par étape, de janvier à aujourd'hui.</div>
      </button>
      <button class="carte" onclick="document.querySelector('.tab[data-month=&quot;doc&quot;]').click()">
        <div class="carte-titre">Documentation</div>
        <div class="carte-desc">BOM détaillée, câblage, configuration LinuxCNC, paramètres VFD, maintenance.</div>
      </button>
      <button class="carte" onclick="document.querySelector('.tab[data-month=&quot;gloss&quot;]').click()">
        <div class="carte-titre">Glossaire</div>
        <div class="carte-desc">Tous les termes techniques expliqués : HAL, REMAP, VFD, G-code, tandem Y...</div>
      </button>
    </div>

    <h2 class="accueil-h">Fichiers et ressources</h2>
    <p class="accueil-p">Tout le projet est open source. Les dépôts GitHub contiennent la configuration LinuxCNC complète, les macros G-code, le code du site et l'outil de lecture du VFD :</p>
    <div class="ressources">
      <a class="ressource" href="https://github.com/atelierduverdier/printnc-config" target="_blank" rel="noopener">
        <div class="ressource-titre">printnc-config</div>
        <div class="ressource-desc">Configuration LinuxCNC : fichiers HAL, INI, macros G-code (toolchange, palpage...).</div>
      </a>
      <a class="ressource" href="https://github.com/atelierduverdier/printnc-build" target="_blank" rel="noopener">
        <div class="ressource-titre">printnc-build</div>
        <div class="ressource-desc">Le code de ce site et les outils de génération (Python, scripts).</div>
      </a>
      <a class="ressource" href="https://github.com/atelierduverdier/huanyang-vfd-reader" target="_blank" rel="noopener">
        <div class="ressource-titre">huanyang-vfd-reader</div>
        <div class="ressource-desc">Outil Python pour lire les paramètres d'un VFD Huanyang en HYComm (RS485).</div>
      </a>
    </div>
  </section>
  <div class="timeline" id="tl">
__BLOCKS__
    <div class="empty" id="empty">Aucune etape pour cette combinaison.</div>
  </div>
  <article id="recit">
__RECIT__
  </article>
  <article id="maj">
__MAJ__
  </article>
  <article id="doc">
__DOC__
  </article>
  <!-- Lightbox pour les photos de la documentation -->
  <div class="lightbox" id="lightbox">
    <span class="lightbox-close" id="lightbox-close">&times;</span>
    <img src="" id="lightbox-img" alt="">
    <div class="lightbox-caption" id="lightbox-caption"></div>
  </div>
</main>
<footer>
  <div class="wrap">
    <div class="social">
      <a href="https://www.instagram.com/atelierduverdier/" target="_blank" rel="noopener" title="Instagram" aria-label="Instagram">
        <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.05 1.8.25 2.2.42.6.22 1 .48 1.4.9.42.4.68.8.9 1.4.17.4.37 1 .42 2.2.06 1.3.07 1.7.07 4.9s0 3.6-.07 4.9c-.05 1.2-.25 1.8-.42 2.2-.22.6-.48 1-.9 1.4-.4.42-.8.68-1.4.9-.4.17-1 .37-2.2.42-1.3.06-1.7.07-4.9.07s-3.6 0-4.9-.07c-1.2-.05-1.8-.25-2.2-.42-.6-.22-1-.48-1.4-.9-.42-.4-.68-.8-.9-1.4-.17-.4-.37-1-.42-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.9c.05-1.2.25-1.8.42-2.2.22-.6.48-1 .9-1.4.4-.42.8-.68 1.4-.9.4-.17 1-.37 2.2-.42C8.4 2.2 8.8 2.2 12 2.2m0-2.2C8.7 0 8.3 0 7 .07 5.7.13 4.8.33 4.1.6c-.8.3-1.4.7-2.1 1.4C1.3 2.7.9 3.3.6 4.1.33 4.8.13 5.7.07 7 0 8.3 0 8.7 0 12s0 3.7.07 5c.06 1.3.26 2.2.53 2.9.3.8.7 1.4 1.4 2.1.7.7 1.3 1.1 2.1 1.4.7.27 1.6.47 2.9.53C8.3 24 8.7 24 12 24s3.7 0 5-.07c1.3-.06 2.2-.26 2.9-.53.8-.3 1.4-.7 2.1-1.4.7-.7 1.1-1.3 1.4-2.1.27-.7.47-1.6.53-2.9.07-1.3.07-1.7.07-5s0-3.7-.07-5c-.06-1.3-.26-2.2-.53-2.9-.3-.8-.7-1.4-1.4-2.1-.7-.7-1.3-1.1-2.1-1.4-.7-.27-1.6-.47-2.9-.53C15.7 0 15.3 0 12 0z"/><path fill="currentColor" d="M12 5.8a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zm0 10.2a4 4 0 110-8 4 4 0 010 8z"/><circle fill="currentColor" cx="18.4" cy="5.6" r="1.44"/></svg>
      </a>
      <a href="https://www.facebook.com/profile.php?id=61569899877112" target="_blank" rel="noopener" title="Facebook" aria-label="Facebook">
        <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M24 12a12 12 0 10-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.6 4.5-4.6 1.3 0 2.7.23 2.7.23v2.9h-1.5c-1.5 0-1.9.92-1.9 1.86V12h3.3l-.53 3.5h-2.8v8.4A12 12 0 0024 12z"/></svg>
      </a>
      <a href="https://www.youtube.com/@atelierduverdier" target="_blank" rel="noopener" title="YouTube" aria-label="YouTube">
        <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M23.5 6.2a3 3 0 00-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 00.5 6.2 31 31 0 000 12a31 31 0 00.5 5.8 3 3 0 002.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 002.1-2.1A31 31 0 0024 12a31 31 0 00-.5-5.8zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z"/></svg>
      </a>
    </div>
    <div class="footer-text">
      Atelier du Verdier &middot; PrintNC build log &middot; <a href="https://github.com/atelierduverdier" target="_blank" rel="noopener">GitHub</a>
    </div>
  </div>
</footer>
<script>
  let curMonth='all', curPhase='all';
  const tabs=document.querySelectorAll('.tab');
  const pbtns=document.querySelectorAll('.pbtn');
  const items=document.querySelectorAll('.item');
  const months=document.querySelectorAll('.month');
  const empty=document.getElementById('empty');
  const tl=document.getElementById('tl');
  const recit=document.getElementById('recit');
  const phasesBar=document.querySelector('.phases');
  function apply(){
    items.forEach(it=>{
      const okM=curMonth==='all'||it.dataset.month===curMonth;
      const okP=curPhase==='all'||it.dataset.phase===curPhase;
      it.classList.toggle('hidden',!(okM&&okP));
    });
    let any=false;
    months.forEach(m=>{
      const mm=m.dataset.month;
      const okM=curMonth==='all'||mm===curMonth;
      const has=[...items].some(it=>it.dataset.month===mm&&!it.classList.contains('hidden'));
      m.classList.toggle('hidden',!(okM&&has));
      if(okM&&has)any=true;
    });
    empty.style.display=any?'none':'block';
  }
  tabs.forEach(t=>t.addEventListener('click',()=>{
    tabs.forEach(x=>x.classList.remove('active'));t.classList.add('active');
    const maj=document.getElementById('maj');
    const doc=document.getElementById('doc');
    const accueil=document.getElementById('accueil');
    const moisRow=document.querySelector('.tabs-mois');
    const hideSecondary=()=>{
      if(moisRow) moisRow.style.display='none';
      document.getElementById('print-btn').style.display='none';
    };
    if(t.dataset.month==='accueil'){
      tl.style.display='none';phasesBar.style.display='none';recit.classList.remove('show');maj.classList.remove('show');doc.classList.remove('show');
      accueil.classList.add('show');
      hideSecondary();
      window.scrollTo({top:0,behavior:'smooth'});return;
    }
    accueil.classList.remove('show');
    if(t.dataset.month==='recit'){
      tl.style.display='none';phasesBar.style.display='none';maj.classList.remove('show');doc.classList.remove('show');recit.classList.add('show');
      hideSecondary();
      window.scrollTo({top:0,behavior:'smooth'});return;
    }
    if(t.dataset.month==='maj'){
      tl.style.display='none';phasesBar.style.display='none';recit.classList.remove('show');doc.classList.remove('show');maj.classList.add('show');
      hideSecondary();
      window.scrollTo({top:0,behavior:'smooth'});return;
    }
    if(t.dataset.month==='gloss'){
      tl.style.display='none';phasesBar.style.display='none';recit.classList.remove('show');maj.classList.remove('show');doc.classList.add('show');
      if(moisRow) moisRow.style.display='none';
      document.getElementById('print-btn').style.display='';
      // Ouvrir et scroller vers la section Glossaire
      let trouve=false;
      document.querySelectorAll('.doc-section').forEach(sec=>{
        const titre=sec.querySelector('.doc-section-titre');
        if(titre && titre.textContent.trim().toLowerCase().startsWith('glossaire')){
          sec.setAttribute('open','');
          trouve=true;
          setTimeout(()=>sec.scrollIntoView({behavior:'smooth',block:'start'}),60);
        }
      });
      if(!trouve) window.scrollTo({top:0,behavior:'smooth'});
      return;
    }
    if(t.dataset.month==='doc'){
      tl.style.display='none';phasesBar.style.display='none';recit.classList.remove('show');maj.classList.remove('show');doc.classList.add('show');
      if(moisRow) moisRow.style.display='none';
      document.getElementById('print-btn').style.display='';
      window.scrollTo({top:0,behavior:'smooth'});return;
    }
    // Onglets timeline (Timeline + mois)
    tl.style.display='';phasesBar.style.display='';
    recit.classList.remove('show');maj.classList.remove('show');doc.classList.remove('show');
    if(moisRow) moisRow.style.display='';
    document.getElementById('print-btn').style.display='none';
    curMonth=t.dataset.month;apply();
    window.scrollTo({top:document.querySelector('.nav').offsetTop-1,behavior:'smooth'});
  }));
  pbtns.forEach(p=>p.addEventListener('click',()=>{
    pbtns.forEach(x=>x.classList.remove('active'));p.classList.add('active');
    curPhase=p.dataset.filter;apply();
  }));

  // Barre de lecture du recit
  const recitProgress=document.getElementById('recit-progress');
  window.addEventListener('scroll',()=>{
    const recitEl=document.getElementById('recit');
    if(!recitEl.classList.contains('show')){recitProgress.style.width='0%';return;}
    const rect=recitEl.getBoundingClientRect();
    const total=recitEl.offsetHeight-window.innerHeight;
    const scrolled=Math.max(0,-rect.top);
    const pct=total>0?Math.min(100,(scrolled/total)*100):0;
    recitProgress.style.width=pct+'%';
  });
  // Copier le lien de l'onglet actif
  const copyBtn=document.getElementById('copy-link-btn');
  const copyOk=document.getElementById('copy-ok');
  copyBtn.addEventListener('click',()=>{
    const activeTab=document.querySelector('.tab.active');
    const month=activeTab?activeTab.dataset.month:'all';
    const url=window.location.href.split('#')[0]+'#'+month;
    navigator.clipboard.writeText(url).then(()=>{
      copyOk.classList.add('show');
      setTimeout(()=>copyOk.classList.remove('show'),2000);
    });
  });
  // Mode jour/nuit
  const themeBtn=document.getElementById('theme-toggle');
  const savedTheme=localStorage.getItem('theme');
  if(savedTheme==='jour'){document.body.classList.add('jour');themeBtn.textContent='🌙';}
  themeBtn.addEventListener('click',()=>{
    document.body.classList.toggle('jour');
    const isJour=document.body.classList.contains('jour');
    themeBtn.textContent=isJour?'🌙':'☀';
    localStorage.setItem('theme',isJour?'jour':'nuit');
  });
  // Lightbox pour les photos de la documentation
  const lightbox=document.getElementById('lightbox');
  const lbImg=document.getElementById('lightbox-img');
  const lbCap=document.getElementById('lightbox-caption');
  const lbClose=document.getElementById('lightbox-close');
  document.querySelectorAll('.doc-photo img').forEach(img=>{
    img.addEventListener('click',()=>{
      lbImg.src=img.src; lbImg.alt=img.alt;
      lbCap.textContent=img.alt;
      lightbox.classList.add('open');
      document.body.style.overflow='hidden';
    });
  });
  function closeLightbox(){
    lightbox.classList.remove('open');
    document.body.style.overflow='';
    lbImg.src='';
  }
  lbClose.addEventListener('click',closeLightbox);
  lightbox.addEventListener('click',e=>{if(e.target===lightbox)closeLightbox();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLightbox();});

  // Afficher la page d'accueil par defaut au chargement
  (function(){
    const tabAccueil=document.querySelector('.tab[data-month="accueil"]');
    if(tabAccueil) tabAccueil.click();
  })();
</script>
</body>
</html>'''


if __name__ == '__main__':
    construire()
