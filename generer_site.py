#!/usr/bin/env python3
# =========================================================================
# generer_site.py - Atelier du Verdier
# Genere le site "PrintNC build log" (index.html) a partir du
# fichier data/videos.csv. Pour ajouter une video : ajoute une ligne au
# CSV, genere sa miniature, et relance ce script.
# =========================================================================
# UTILISATION :
#   python3 generer_site.py
# Produit : index.html (dans le dossier courant)
# =========================================================================

import csv, os, re, json
from collections import Counter

CSV = os.path.join('data', 'videos.csv')
SORTIE = 'index.html'
DATE_DEBUT = '2026-01-16'       # date du premier montage
DATE_NAISSANCE = '2026-06-29'   # date du dernier copeau — stat "age de la machine"
DUREE_CONSTRUCTION = 6          # mois de construction — stat fixe

phase_info = {
    'meca': {'label': 'Mecanique',    'color': '#378ADD', 'bg': 'rgba(55,138,221,.12)'},
    'elec': {'label': 'Electronique', 'color': '#EF9F27', 'bg': 'rgba(239,159,39,.12)'},
    'soft': {'label': 'LinuxCNC',     'color': '#1D9E75', 'bg': 'rgba(29,158,117,.12)'},
    'laser': {'label': 'Laser',       'color': '#C44A31', 'bg': 'rgba(196,74,49,.12)'},
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


def slugify(s):
    import unicodedata
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:50]


SHARE_SVG = '<svg viewBox="0 0 24 24" width="13" height="13"><path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/></svg>'


def markdown_vers_html_recit(md):
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
                alt, url = esc(m.group(1)), m.group(2)
                out.append(f'<figure class="doc-photo"><img src="{url}" alt="{alt}" loading="lazy"><figcaption>{alt}</figcaption></figure>')
        elif ln.strip():
            txt = esc(ln.strip())
            txt = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', txt)
            out.append(f'<p class="recit-p">{txt}</p>')
    return '\n'.join(out)


def markdown_vers_html(md):
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
        elif ln.startswith('# '):
            out.append(f'<div class="maj-date-sep">{esc(ln[2:].strip())}</div>')
        elif ln.startswith('## '):
            out.append(f'<h3 class="maj-titre">{esc(ln[3:].strip())}</h3>')
        elif ln.lstrip().startswith('|') and ln.rstrip().endswith('|'):
            tbl = [ln]
            while i + 1 < len(lignes) and lignes[i+1].lstrip().startswith('|'):
                i += 1
                tbl.append(lignes[i])
            rows = []
            for k, trow in enumerate(tbl):
                cells = [c.strip() for c in trow.strip().strip('|').split('|')]
                if all(set(c) <= set('-: ') for c in cells): continue
                tag = 'th' if k == 0 else 'td'
                cells_html = ''.join(f'<{tag}>{esc(c)}</{tag}>' for c in cells)
                rows.append(f'<tr>{cells_html}</tr>')
            out.append('<table class="doc-table">' + ''.join(rows) + '</table>')
        elif ln.strip().startswith('!['):
            import re as _re
            m = _re.match(r'!\[([^\]]*)\]\(([^)]+)\)', ln.strip())
            if m:
                alt, url = m.group(1), m.group(2)
                out.append(f'<figure class="doc-photo"><img src="{url}" alt="{alt}" loading="lazy"><figcaption>{alt}</figcaption></figure>')
        elif ln.strip():
            para = [esc(ln.strip())]
            while (i + 1 < len(lignes) and lignes[i+1].strip()
                   and not lignes[i+1].startswith(('#', '```'))
                   and not lignes[i+1].lstrip().startswith('|')):
                i += 1
                para.append(esc(lignes[i].strip()))
            txt = ' '.join(para)
            import re as _re
            txt = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', txt)
            txt = _re.sub(r'`([^`]+)`', r'<code>\1</code>', txt)
            txt = _re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', txt)
            out.append(f'<p class="maj-desc">{txt}</p>')
        i += 1
    return '\n'.join(out)


def markdown_vers_html_doc(md, prefix='doc'):
    import re as _re
    sections = _re.split(r'\n(?=# )', '\n' + md)
    out = []
    slug_counts = {}
    for section in sections:
        if not section.strip(): continue
        lignes = section.split('\n')
        titre_raw, titre, contenu_lignes = '', '', []
        for ln in lignes:
            if ln.startswith('# ') and not titre_raw:
                titre_raw = ln[2:].strip()
                titre = esc(titre_raw)
            else:
                contenu_lignes.append(ln)
        contenu_html = _convertir_contenu_doc('\n'.join(contenu_lignes))
        if titre_raw:
            base_slug = prefix + '-' + slugify(titre_raw)
            slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1
            slug = base_slug if slug_counts[base_slug] == 1 else f'{base_slug}-{slug_counts[base_slug]}'
            share = f'<button class="share-btn" onclick="copyAnchor(\'{slug}\')" title="Copier le lien">{SHARE_SVG}</button>'
            out.append(f'<details class="doc-section" id="{slug}"><summary class="doc-section-titre">{titre}{share}</summary><div class="doc-section-corps">{contenu_html}</div></details>')
        else:
            out.append(contenu_html)
    return '\n'.join(out)


def _render_cell(txt):
    import re as _re
    def rpl_lien(m): return f'<a href="{m.group(2)}" target="_blank" rel="noopener">{esc(m.group(1))}</a>'
    txt = _re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rpl_lien, txt)
    txt = _re.sub(r'\*\*([^*]+)\*\*', lambda m: f'<strong>{esc(m.group(1))}</strong>', txt)
    txt = _re.sub(r'`([^`]+)`', lambda m: f'<code>{esc(m.group(1))}</code>', txt)
    return txt


def _convertir_contenu_doc(md):
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
                code.append(esc(lignes[i])); i += 1
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
                i += 1; tbl.append(lignes[i])
            rows = []
            for k, trow in enumerate(tbl):
                raw = trow.strip().strip('|')
                cells = [c.strip() for c in raw.split('|')]
                if all(set(c) <= set('-: ') for c in cells): continue
                tag = 'th' if k == 0 else 'td'
                cells_html = ''.join(f'<{tag}>{_render_cell(c)}</{tag}>' for c in cells)
                rows.append(f'<tr>{cells_html}</tr>')
            out.append('<table class="doc-table">' + ''.join(rows) + '</table>')
        elif ln.strip().startswith('!['):
            m = _re.match(r'!\[([^\]]*)\]\(([^)]+)\)', ln.strip())
            if m:
                alt, url = esc(m.group(1)), m.group(2)
                out.append(f'<figure class="doc-photo"><img src="{url}" alt="{alt}" loading="lazy"><figcaption>{alt}</figcaption></figure>')
            else:
                out.append(f'<p class="maj-desc">{esc(ln.strip())}</p>')
        elif ln.strip().startswith('- ') or ln.strip().startswith('* '):
            items = []
            while i < len(lignes) and (lignes[i].strip().startswith('- ') or lignes[i].strip().startswith('* ')):
                item_txt = lignes[i].strip()[2:]
                item_txt = _re.sub(r'`([^`]+)`', r'<code>\1</code>', esc(item_txt))
                item_txt = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item_txt)
                items.append(f'<li>{item_txt}</li>'); i += 1
            out.append('<ul class="doc-liste">' + ''.join(items) + '</ul>')
            continue
        elif ln.strip():
            para = [esc(ln.strip())]
            while (i + 1 < len(lignes) and lignes[i+1].strip()
                   and not lignes[i+1].startswith(('#', '```', '>'))
                   and not lignes[i+1].lstrip().startswith('|')
                   and not lignes[i+1].strip().startswith(('- ', '* ', '!['))):
                i += 1; para.append(esc(lignes[i].strip()))
            txt = ' '.join(para)
            txt = _re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', txt)
            txt = _re.sub(r'`([^`]+)`', r'<code>\1</code>', txt)
            txt = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', txt)
            txt_lower = txt.lower()
            if txt_lower.startswith('<strong>point important') or txt_lower.startswith('<strong>important') or txt_lower.startswith('<strong>attention') or txt_lower.startswith('<strong>note'):
                out.append(f'<p class="doc-important">{txt}</p>')
            else:
                out.append(f'<p class="maj-desc">{txt}</p>')
        i += 1
    return '\n'.join(out)


def construire():
    jalons = charger()
    counts = Counter(j['date'][:7] for j in jalons)

    # --- CHARGEMENT EXTERNE DES MOIS ---
    mois_info = {}
    json_path = os.path.join('data', 'mois.json')
    if os.path.exists(json_path):
        with open(json_path, encoding='utf-8') as f:
            mois_info = json.load(f)

    # --- STATISTIQUES DYNAMIQUES ---
    nb_mois = len(set(j['date'][:7] for j in jalons))
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
        '\n    </div>\n    <div class="tabs tabs-mois" id="tabs-mois" style="display:none;">\n' +
        '\n'.join(onglets_mois)
    )

    # --- GENERATION DES BLOCS TIMELINE ---
    blocks = []
    cur = None
    date_count = {}
    for j in jalons:
        m = j['date'][:7]
        if m != cur:
            cur = m
            nom_defaut = f"{mois_onglet.get(m[5:7], m)} {m[:4]}"
            mi = mois_info.get(m, {'nom': nom_defaut, 'titre': '', 'desc': ''})
            share_mois = f'<button class="share-btn" onclick="copyAnchor(\'{m}\')" title="Copier le lien vers ce mois">{SHARE_SVG}</button>'
            blocks.append(f'''    <section class="month" data-month="{m}">
      <div class="mhead">
        <div class="mnom">{mi.get('nom', nom_defaut)}{share_mois}</div>
        <h2 class="mtitre">{mi.get('titre', '')}</h2>
        <p class="mdesc">{mi.get('desc', '')} <span class="mcount">{counts[m]} etapes</span></p>
      </div>
    </section>''')

        pi = phase_info.get(j['phase'], phase_info['meca'])
        # (x or '') : DictReader renvoie None pour les colonnes absentes
        # (vieilles lignes a 5 champs sans duree/jalon)
        lien = (j.get('lien') or '').strip()
        fnoext = j['fichier'].replace('.mp4', '') if j.get('fichier') else ''
        duree = (j.get('duree') or '').strip()
        is_jalon = (j.get('jalon') or '').strip().lower() in ('oui', '1', 'true')

        if fnoext:
            article_id = f'v-{fnoext}'
        else:
            date_count[j['date']] = date_count.get(j['date'], 0) + 1
            article_id = f'v-{j["date"]}-{date_count[j["date"]]}'
        share_vid = f'<button class="share-btn" onclick="copyAnchor(\'{article_id}\')" title="Copier le lien vers cette étape">{SHARE_SVG}</button>'

        vid = ''
        if lien and fnoext:
            duree_badge = f'<span class="vid-duration">{esc(duree)}</span>' if duree else ''
            vid = (f'<a class="vid-thumb" href="{lien}" target="_blank" rel="noopener" title="Voir la video">'
                   f'{duree_badge}'
                   f'<img src="miniatures/{fnoext}.jpg" loading="lazy" alt="Miniature {date_fr(j["date"])}" '
                   f'onerror="this.parentNode.classList.add(\'noimg\')">'
                   f'<span class="overlay"><span class="play">&#9654;</span></span></a>')
        elif lien:
            vid = f'<a class="vid" href="{lien}" target="_blank" rel="noopener"><span class="play">&#9654;</span> Voir la video</a>'

        texte = j.get('texte', '') or 'Etape de construction (video du jour)'
        texte = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', texte)
        texte = re.sub(r'(?<!["\'>])(https?://[^\s<]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', texte)

        class_item = 'item milestone' if is_jalon else 'item'

        blocks.append(f'''    <article class="{class_item}" id="{article_id}" data-phase="{j['phase']}" data-month="{m}">
      <div class="dot" style="background:{pi['color']}"></div>
      <div class="content">
        <div class="meta"><span class="date">{date_fr(j['date'])}</span><span class="tag" style="background:{pi['bg']};color:{pi['color']}">{pi['label']}</span>{share_vid}</div>
        <p class="text">{texte}</p>
        {vid}
      </div>
    </article>''')

    # Mises a jour, Documentation, Recit, Glossaire
    maj_html = ''
    mp = os.path.join('data', 'maj.md')
    if os.path.exists(mp): maj_html = markdown_vers_html(open(mp, encoding='utf-8').read())

    doc_html = ''
    dp = os.path.join('data', 'doc.md')
    if os.path.exists(dp): doc_html = markdown_vers_html_doc(open(dp, encoding='utf-8').read())

    recit = ''
    rp_md = os.path.join('data', 'recit.md')
    rp_html = os.path.join('data', 'recit.html')
    if os.path.exists(rp_md): recit = markdown_vers_html_recit(open(rp_md, encoding='utf-8').read())
    elif os.path.exists(rp_html): recit = open(rp_html, encoding='utf-8').read()

    gloss_html = ''
    gp_md = os.path.join('data', 'glossaire.md')
    if os.path.exists(gp_md): gloss_html = markdown_vers_html_doc(open(gp_md, encoding='utf-8').read(), prefix='gloss')

    n = len(jalons)
    html = MODELE.replace('__ONGLETS__', onglets)
    html = html.replace('__BLOCKS__', '\n'.join(blocks))
    html = html.replace('__RECIT__', recit)
    html = html.replace('__MAJ__', maj_html)
    html = html.replace('__DOC__', doc_html)
    html = html.replace('__GLOSS__', gloss_html)
    _mois_fr = ['', 'jan.', 'fév.', 'mars', 'avr.', 'mai', 'juin',
                'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
    _d = DATE_DEBUT.split('-')
    date_debut_fr = f"{int(_d[2])} {_mois_fr[int(_d[1])]} {_d[0]}"
    _f = DATE_NAISSANCE.split('-')
    date_fin_fr = f"{int(_f[2])} {_mois_fr[int(_f[1])]} {_f[0]}"
    html = html.replace('__N__', str(n))
    html = html.replace('__DUREE_CONSTRUCTION__', str(DUREE_CONSTRUCTION))
    html = html.replace('__DATE_DEBUT_FR__', date_debut_fr)
    html = html.replace('__DATE_FIN_FR__', date_fin_fr)
    html = html.replace('__DATE_NAISSANCE__', DATE_NAISSANCE)
    open(SORTIE, 'w', encoding='utf-8').write(html)
    print(f"Site genere : {SORTIE} ({n} etapes, {nb_mois} mois)")


MODELE = '''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PrintNC &mdash; Journal de construction | Atelier du Verdier</title>
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<meta name="description" content="Construction complète d'une fraiseuse CNC PrintNC : journal vidéo, documentation technique (BOM, câblage, LinuxCNC, VFD), récit et configuration open source.">
<meta name="author" content="Atelier du Verdier">
<meta property="og:type" content="website">
<meta property="og:title" content="PrintNC — Journal de construction | Atelier du Verdier">
<meta property="og:description" content="Construction complète d'une fraiseuse CNC PrintNC, open source.">
<meta property="og:image" content="https://atelierduverdier.github.io/printnc-build/photos/printnc.jpg">
<meta name="twitter:card" content="summary_large_image">
<script data-goatcounter="https://atelierduverdier.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script>
  window.addEventListener('load', function() {
    var r = new XMLHttpRequest();
    r.addEventListener('load', function() {
      try {
        var n = JSON.parse(this.responseText).count;
        document.getElementById('compteur-visites').innerText = n;
        document.getElementById('footer-counter').hidden = false;
      } catch (e) {}
    });
    r.open('GET', 'https://atelierduverdier.goatcounter.com/counter/TOTAL.json');
    r.send();
  });
</script>
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
  .stat-dates{display:flex;flex-direction:column;gap:2px;font-size:15px;font-weight:700;line-height:1.3;}
  .stat-dates-sep{font-size:11px;color:var(--faint);font-weight:400;}
  .stat .l{font-size:13px;color:var(--faint);text-transform:uppercase;letter-spacing:1px;}
  .stat-hero .n{color:var(--orange);}
  .stat-hero .l{text-transform:none;letter-spacing:0;color:var(--muted);font-size:14px;font-style:italic;}
  .nav{position:sticky;top:0;background:rgba(19,17,14,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);z-index:10;}
  .tabs{display:flex;gap:6px;flex-wrap:wrap;padding:12px 20px 6px;}
  .tabs-mois{display:flex;gap:6px;flex-wrap:wrap;padding:4px 20px 10px;border-top:1px solid var(--line);}
  .tab-mois{font-size:13px;padding:6px 13px;}
  .tab{background:var(--surface);border:1px solid var(--line);color:var(--muted);padding:9px 16px;border-radius:8px;font-size:14px;cursor:pointer;transition:.15s;font-weight:500;}
  .tab:hover{border-color:var(--orange);color:var(--text);}
  .tab.active{background:var(--orange);border-color:var(--orange);color:#13110e;font-weight:600;}
  .tab-recit,.tab-maj,.tab-doc,.tab-gloss,.tab-accueil{border-color:var(--orange);color:var(--orange);}
  .tab-recit.active,.tab-maj.active,.tab-doc.active,.tab-gloss.active,.tab-accueil.active{background:var(--orange);color:#13110e;}
  .search-box{margin:0 20px 10px; position:relative;}
  .search-box input{width:100%;padding:8px 14px;background:var(--surface);border:1px solid var(--line);border-radius:8px;color:var(--text);font-size:14px;outline:none;transition:.15s;}
  .search-box input:focus{border-color:var(--orange);}
  .search-box input::placeholder{color:var(--faint);}
  .phases-row{display:flex;align-items:center;justify-content:space-between;padding:0 20px 10px;flex-wrap:wrap;gap:6px;}
  .phases{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
  .tab-actions{display:flex;align-items:center;gap:8px;margin-left:auto;padding:4px 0;}
  .plabel{font-size:12px;color:var(--faint);text-transform:uppercase;letter-spacing:1px;margin-right:4px;}
  .pbtn{background:transparent;border:1px solid var(--line);color:var(--muted);padding:5px 12px;border-radius:14px;font-size:13px;cursor:pointer;transition:.15s;}
  .pbtn:hover{border-color:var(--orange);color:var(--text);}
  .pbtn.active{border-color:var(--orange);color:var(--orange);}
  .copy-link-btn{background:transparent;border:1px solid var(--line);color:var(--faint);padding:4px 12px;border-radius:14px;font-size:12px;cursor:pointer;transition:.15s;}
  .copy-link-btn:hover{border-color:var(--orange);color:var(--orange);}
  .copy-ok{font-size:12px;color:var(--orange);opacity:0;transition:.3s;}
  .copy-ok.show{opacity:1;}
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
  .vid-duration{position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,.8);color:#fff;font-size:11px;padding:2px 6px;border-radius:4px;z-index:3;font-variant-numeric:tabular-nums;}
  .vid-thumb .overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.25);opacity:0;transition:.15s;}
  .vid-thumb .overlay .play{font-size:22px;color:#fff;background:rgba(232,130,30,.9);width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;padding-left:3px;}
  .vid-thumb:hover{border-color:var(--orange);}
  .vid-thumb:hover .overlay{opacity:1;}
  .vid-thumb.noimg{width:auto;border:none;}
  .vid-thumb.noimg img{display:none;}
  .vid-thumb.noimg::after{content:'\\25B6  Voir la video';display:inline-flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 14px;font-size:13px;color:var(--muted);line-height:1.4;}
  .vid-thumb.noimg .overlay{display:none;}
  .item.milestone{background:rgba(232,130,30,.05);margin:0 -20px;padding:18px 20px 18px 62px;border-left:3px solid var(--orange);border-radius:0 8px 8px 0;}
  .item.milestone .dot{width:20px;height:20px;left:2px;top:22px;}
  .item.hidden{display:none;}
  .empty{padding:40px 0;color:var(--faint);font-size:15px;text-align:center;display:none;}
#accueil, #tl, #recit, #maj, #doc, #gloss { display: none; padding: 30px 0 60px; max-width: 680px; }
#accueil.show, #tl.show, #recit.show, #maj.show, #doc.show, #gloss.show { display: block; }
  .recit-progress{position:fixed;top:0;left:0;height:3px;background:var(--orange);width:0%;z-index:20;transition:width .1s linear;pointer-events:none;}
  .recit-h{font-size:22px;color:var(--orange);margin:36px 0 14px;font-weight:700;}
  .recit-h:first-child{margin-top:8px;}
  .recit-p{font-size:16px;line-height:1.8;color:var(--text);margin-bottom:16px;}
  .recit-cite{font-size:18px;font-style:italic;color:var(--muted);border-left:3px solid var(--orange);padding-left:18px;margin:24px 0;}
  .maj-date-sep{font-size:13px;letter-spacing:2px;text-transform:uppercase;color:var(--orange);font-weight:600;margin:40px 0 18px;padding-bottom:8px;border-bottom:1px solid var(--line);}
  .maj-titre{font-size:18px;font-weight:600;color:var(--text);margin-bottom:6px;}
  .maj-desc{font-size:15px;line-height:1.7;color:var(--muted);margin-bottom:12px;}
  .maj-desc a, .doc-important a{color:var(--orange);text-decoration:none;border-bottom:1px solid var(--orange);transition:.15s;}
  .maj-desc a:hover, .doc-important a:hover{opacity:.7;}
  .maj-code{background:#0d0b09;border:1px solid var(--line);border-radius:8px;padding:14px 16px;font-family:'Consolas','Monaco',monospace;font-size:13px;line-height:1.5;color:#d8cfc0;overflow-x:auto;margin:8px 0 16px;white-space:pre;}
  .maj-desc code{background:#0d0b09;border:1px solid var(--line);border-radius:4px;padding:1px 6px;font-family:monospace;font-size:13px;color:var(--orange);}
  .doc-table{width:100%;border-collapse:collapse;margin:10px 0 18px;font-size:14px;}
  .doc-table th{background:var(--surface);color:var(--orange);text-align:left;padding:8px 12px;border:1px solid var(--line);font-weight:600;}
  .doc-table td{padding:8px 12px;border:1px solid var(--line);color:var(--muted);}
  .doc-table td a{color:var(--orange);text-decoration:none;}
  .doc-table td a:hover{text-decoration:underline;}
  .doc-section{border:1px solid var(--line);border-radius:10px;margin-bottom:12px;overflow:hidden;}
  .doc-section[open]{border-color:var(--orange);}
  .doc-section-titre{font-size:17px;font-weight:600;color:var(--text);padding:14px 18px;cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;background:var(--surface);}
  .doc-section-titre::-webkit-details-marker{display:none;}
  .doc-section-titre::after{content:'＋';color:var(--orange);font-size:18px;transition:.2s;}
  .doc-section[open] .doc-section-titre::after{content:'－';}
  .doc-section-titre:hover{color:var(--orange);}
  .doc-section-corps{padding:18px 18px 10px;border-top:1px solid var(--line);}
  .doc-sous-titre{font-size:16px;font-weight:600;color:var(--orange);margin:18px 0 10px;}
  .doc-sous-titre:first-child{margin-top:4px;}
  .doc-sous-titre-3{font-size:14px;font-weight:600;color:var(--muted);margin:12px 0 6px;}
  .doc-note{border-left:3px solid var(--orange);padding:8px 14px;color:var(--muted);font-style:italic;margin:10px 0 14px;background:var(--surface);}
  .doc-important{border-left:3px solid var(--orange);padding:10px 16px;color:var(--text);margin:14px 0 18px;background:rgba(232,130,30,.08);border-radius:0 8px 8px 0;}
  .doc-important strong{color:var(--orange);}
  .doc-liste{margin:6px 0 14px 18px;color:var(--muted);font-size:15px;line-height:1.8;}
  .doc-liste li{margin-bottom:2px;}
  .doc-liste li strong{color:var(--orange);}
  .doc-liste li code{background:#0d0b09;border:1px solid var(--line);border-radius:4px;padding:1px 6px;font-family:monospace;font-size:13px;color:var(--orange);}
  .doc-photo{margin:14px 0 20px;text-align:center;}
  .doc-photo img{max-width:100%;max-height:320px;object-fit:cover;border-radius:10px;border:1px solid var(--line);display:block;margin:0 auto;cursor:zoom-in;transition:.2s;}
  .doc-photo img:hover{border-color:var(--orange);opacity:.9;}
  .doc-photo figcaption{font-size:13px;color:var(--faint);margin-top:6px;font-style:italic;}
  #accueil{display:none;padding:24px 0 50px;}
  #accueil.show{display:block;}
  .hero{display:flex;gap:28px;align-items:center;margin-bottom:44px;flex-wrap:wrap;}
  .hero-img{width:340px;max-width:100%;border-radius:14px;border:1px solid var(--line);object-fit:cover;cursor:zoom-in;transition:.2s;}
  .hero-img:hover{border-color:var(--orange);opacity:.92;}
  .hero-text{flex:1;min-width:260px;}
  .hero-titre{font-size:30px;margin:0 0 12px;color:var(--text);font-weight:600;}
  .hero-sous{font-size:16px;color:var(--muted);line-height:1.6;margin:0 0 20px;}
  .accueil-h{font-size:20px;color:var(--orange);margin:40px 0 18px;font-weight:600;}
  .accueil-p{font-size:15px;color:var(--muted);line-height:1.6;margin:0 0 18px;}
  .accueil-p a{color:var(--orange);text-decoration:none;border-bottom:1px solid var(--orange);transition:.15s;}
  .accueil-p a:hover{opacity:.7;}
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
  .soutien{margin:32px 0 8px;text-align:center;}
  .soutien-btn{display:inline-flex;align-items:center;gap:10px;background:var(--orange);color:#13110e;font-size:15px;font-weight:700;padding:13px 24px;border-radius:10px;text-decoration:none;transition:.15s;}
  .soutien-btn:hover{transform:translateY(-2px);box-shadow:0 6px 22px -8px var(--orange);}
  .soutien-btn svg{width:20px;height:20px;fill:currentColor;}
  .soutien-note{font-size:13px;color:var(--faint);margin-top:10px;}
  .lightbox{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:1000;align-items:center;justify-content:center;cursor:zoom-out;}
  .lightbox.open{display:flex;}
  .lightbox img{max-width:90vw;max-height:90vh;object-fit:contain;border-radius:8px;box-shadow:0 0 40px rgba(0,0,0,.8);}
  .lightbox-close{position:fixed;top:18px;right:24px;font-size:32px;color:#fff;cursor:pointer;line-height:1;opacity:.7;transition:.15s;}
  .lightbox-close:hover{opacity:1;color:var(--orange);}
  .lightbox-caption{position:fixed;bottom:20px;left:0;right:0;text-align:center;color:var(--muted);font-size:14px;font-style:italic;pointer-events:none;}
  .theme-toggle{position:fixed;top:14px;right:120px;z-index:25;background:var(--surface);border:1px solid var(--line);color:var(--orange);font-size:18px;width:36px;height:36px;border-radius:50%;cursor:pointer;transition:.2s;display:flex;align-items:center;justify-content:center;}
  .theme-toggle:hover{background:var(--orange);color:#13110e;}
  .github-ribbon{position:fixed;top:0;right:0;z-index:24;width:130px;height:130px;overflow:hidden;pointer-events:none;}
  .github-ribbon a{position:absolute;display:block;width:170px;padding:7px 0;background:var(--orange);color:#13110e;font-size:12px;font-weight:700;text-align:center;text-decoration:none;letter-spacing:.5px;transform:rotate(45deg);right:-42px;top:32px;box-shadow:0 2px 6px rgba(0,0,0,.35);pointer-events:auto;transition:.2s;}
  .github-ribbon a:hover{background:#ff9a3c;}
  .back-to-top{position:fixed;bottom:30px;right:30px;width:44px;height:44px;background:var(--orange);color:#13110e;border:none;border-radius:50%;font-size:20px;cursor:pointer;opacity:0;visibility:hidden;transition:.2s;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(0,0,0,.3);z-index:20;}
  .back-to-top.show{opacity:1;visibility:visible;}
  .back-to-top:hover{transform:translateY(-3px);}
  footer{border-top:1px solid var(--line);padding:40px 0 60px;color:var(--faint);font-size:14px;text-align:center;}
  footer a{color:var(--orange);text-decoration:none;}
  .social{display:flex;justify-content:center;gap:22px;margin-bottom:18px;}
  .social a{color:var(--faint);transition:.2s;display:flex;}
  .social a:hover{color:var(--orange);transform:translateY(-2px);}
  .footer-text{font-size:13px;}
  .footer-counter{margin-top:14px;opacity:.6;transition:.2s;font-size:13px;}
  .footer-counter:hover{opacity:1;}
  .footer-counter a{color:var(--faint);}
  .footer-counter a:hover{color:var(--orange);}
  .footer-counter #compteur-visites{color:var(--orange);font-weight:600;}
  .adv-rate{max-width:22rem;margin:0 auto 28px;padding:1.1rem 1.4rem;border:1px solid var(--line);border-radius:12px;background:var(--surface);text-align:center;}
  .adv-rate__q{margin:0 0 .8rem;font-size:.95rem;font-weight:600;color:var(--text);}
  .adv-rate__btn{background:transparent;border:1px solid var(--line);color:var(--muted);padding:8px 18px;border-radius:8px;font-size:14px;font-weight:500;cursor:pointer;transition:.2s;display:inline-flex;align-items:center;gap:8px;font-family:inherit;}
  .adv-rate__btn:hover{border-color:var(--orange);color:var(--orange);transform:translateY(-1px);}
  .adv-rate__btn.is-voted{border-color:var(--orange);background:rgba(232,130,30,.12);color:var(--orange);cursor:default;pointer-events:none;}
  .adv-rate__btn svg{fill:currentColor;}
  .adv-rate__avg{margin:.6rem 0 0;font-size:.82rem;color:var(--muted);min-height:1.1em;}
  body.jour{--bg:#f5f2ee;--surface:#ede8e0;--surface2:#e0d9cf;--text:#1a1612;--muted:#5a4f44;--faint:#9a8f84;--line:#d0c8bc;--orange:#c46a10;}
  body.jour .tab{background:var(--surface);border-color:var(--line);color:var(--muted);}
  body.jour .tab:hover{border-color:var(--orange);color:var(--text);}
  body.jour .tab.active{background:var(--orange);border-color:var(--orange);color:#fff;}
  body.jour .pbtn{border-color:var(--line);color:var(--muted);}
  body.jour .pbtn.active{border-color:var(--orange);color:var(--orange);}
  body.jour .nav{background:rgba(245,242,238,.95);}
  body.jour .lightbox{background:rgba(0,0,0,.85);}
  @media print{
    .nav,.filters,.theme-toggle,.tab-actions,.recit-progress,.github-ribbon,.back-to-top,.search-box,#tl,#recit,#maj,#accueil,footer{display:none!important;}
    #doc,#gloss{display:block!important;max-width:100%!important;}
    .doc-section{border:none!important;margin-bottom:12px!important;}
    .doc-section-titre{background:none!important;border-bottom:1px solid #ccc!important;}
    .doc-section-corps{display:block!important;}
    .doc-table{font-size:11px!important;}
    a{color:#000!important;text-decoration:none!important;}
    body{background:#fff!important;color:#000!important;}
  }
  @media(max-width:600px){.theme-toggle{right:90px;}.github-ribbon{width:100px;height:100px;}.github-ribbon a{font-size:10px;width:150px;right:-40px;top:24px;}}
  @media (prefers-reduced-motion:reduce){.adv-rate__btn{transition:none;}.adv-rate__btn:hover{transform:none;}}
  .share-btn{background:none;border:none;color:var(--faint);cursor:pointer;padding:0 4px;display:inline-flex;align-items:center;transition:.15s;flex-shrink:0;vertical-align:middle;line-height:1;}
  .share-btn:hover{color:var(--orange);}
  .share-btn svg{fill:currentColor;display:block;}
  .item .share-btn,.mnom .share-btn{opacity:0;}
  .item:hover .share-btn,.mnom:hover .share-btn{opacity:1;}
  .doc-section{position:relative;}
  .doc-section .share-btn{position:absolute;top:13px;right:46px;opacity:0;}
  .doc-section:hover .share-btn{opacity:1;}
  #share-toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(8px);background:var(--orange);color:#13110e;padding:8px 18px;border-radius:8px;font-size:13px;font-weight:600;z-index:200;opacity:0;transition:.2s;pointer-events:none;}
  #share-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
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
      <div class="stat stat-hero"><div class="n">__DUREE_CONSTRUCTION__ mois</div><div class="l">de patience, d'essais et de copeaux</div></div>
      <div class="stat"><div class="n">__N__</div><div class="l">etapes video</div></div>
      <div class="stat"><div class="stat-dates"><span>__DATE_DEBUT_FR__</span><span class="stat-dates-sep">→</span><span>__DATE_FIN_FR__</span></div><div class="l">construction</div></div>
      <div class="stat"><div class="n" id="machine-age">—</div><div class="l">depuis le premier copeau</div></div>
    </div>
  </div>
</header>
<nav class="nav">
  <div class="wrap" style="padding:0;">
    <div class="tabs">
__ONGLETS__
    </div>
    <div class="search-box" id="search-box" style="display:none;">
      <input type="text" id="search-input" placeholder="Rechercher une étape, un mot-clé...">
    </div>
    <div class="phases-row" id="phases-row" style="display:none;">
      <div class="phases">
      <span class="plabel">Filtre</span>
      <button class="pbtn active" data-filter="all">Tout</button>
      <button class="pbtn" data-filter="meca">Mecanique</button>
      <button class="pbtn" data-filter="elec">Electronique</button>
      <button class="pbtn" data-filter="soft">LinuxCNC</button>
      <button class="pbtn" data-filter="laser">Laser</button>
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
<button class="back-to-top" id="back-to-top" title="Remonter en haut">↑</button>

<main class="wrap">
  <section id="accueil">
    <div class="hero">
      <img class="hero-img" src="photos/printnc.jpg" alt="PrintNC — Atelier du Verdier" onerror="this.style.display='none'">
      <div class="hero-text">
        <h1 class="hero-titre">PrintNC — Atelier du Verdier</h1>
        <p class="hero-sous">Journal de construction d'une fraiseuse CNC PrintNC, de la première pièce au premier copeau. Documentation complète, ouverte et reproductible.</p>
      </div>
    </div>
    <h2 class="accueil-h">Explorer le site</h2>
    <div class="cartes">
      <button class="carte" onclick="switchTab('recit')"><div class="carte-titre">Le récit</div><div class="carte-desc">L'histoire complète de la construction, mois par mois.</div></button>
      <button class="carte" onclick="switchTab('all')"><div class="carte-titre">Timeline</div><div class="carte-desc">Le journal vidéo quotidien, étape par étape.</div></button>
      <button class="carte" onclick="switchTab('doc')"><div class="carte-titre">Documentation</div><div class="carte-desc">BOM détaillée, câblage, configuration LinuxCNC.</div></button>
      <button class="carte" onclick="switchTab('gloss')"><div class="carte-titre">Glossaire</div><div class="carte-desc">Tous les termes techniques expliqués.</div></button>
    </div>
  </section>

  <div class="timeline" id="tl">
__BLOCKS__
    <div class="empty" id="empty">Aucune etape pour cette combinaison.</div>
  </div>
  
  <article id="recit">__RECIT__</article>
  <article id="maj">__MAJ__</article>
  <article id="doc">__DOC__</article>
  <article id="gloss">__GLOSS__</article>

  <div class="lightbox" id="lightbox">
    <span class="lightbox-close" id="lightbox-close">&times;</span>
    <img src="" id="lightbox-img" alt="">
    <div class="lightbox-caption" id="lightbox-caption"></div>
  </div>
</main>

<footer>
  <div class="wrap">
    <div class="adv-rate" id="advRate">
      <p class="adv-rate__q">Vous construisez (ou envisagez) une PrintNC ?</p>
      <button class="adv-rate__btn" id="btn-useful">
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M2 20h2c.55 0 1-.45 1-1v-9c0-.55-.45-1-1-1H2v11zm19.83-7.12c.11-.25.17-.52.17-.8V11c0-1.1-.9-2-2-2h-5.5l.92-4.65c.05-.22.02-.46-.08-.66-.23-.45-.52-.86-.88-1.22L14 2 7.59 8.41C7.21 8.79 7 9.3 7 9.83V19c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3-7.12z"/></svg>
        Oui, je me lance !
      </button>
      <p class="adv-rate__avg" id="advRateAvg"></p>
    </div>
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
      <a href="https://ko-fi.com/atelierduverdier" target="_blank" rel="noopener" title="Soutenir l'atelier sur Ko-fi" aria-label="Ko-fi">
        <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M5 3h13a3 3 0 0 1 3 3v1a4 4 0 0 1-4 4h-1.1A5 5 0 0 1 11 15H8a5 5 0 0 1-5-5V5a2 2 0 0 1 2-2zm12 6a2 2 0 0 0 2-2V6a1 1 0 0 0-1-1h-1v4zM4 19h14a1 1 0 0 1 0 2H4a1 1 0 0 1 0-2z"/></svg>
      </a>
    </div>
    <p class="footer-text">Atelier du Verdier &middot; PrintNC build log &middot; <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a></p>
    <div class="footer-counter" hidden id="footer-counter">
      <a href="https://atelierduverdier.goatcounter.com" target="_blank" rel="noopener" title="Statistiques de visite">
        <span id="compteur-visites">0</span> visites
      </a>
    </div>
  </div>
</footer>

<script>
// --- GESTION DES ONGLETS, RECHERCHE & DEEP LINKING ---
let currentMonth = 'accueil';
const tabs = document.querySelectorAll('.tab');
const sections = { accueil: document.getElementById('accueil'), tl: document.getElementById('tl'), recit: document.getElementById('recit'), maj: document.getElementById('maj'), doc: document.getElementById('doc'), gloss: document.getElementById('gloss') };
const searchBox = document.getElementById('search-box');
const tabsMois = document.getElementById('tabs-mois');
const phasesRow = document.getElementById('phases-row');
const printBtn = document.getElementById('print-btn');

function switchTab(month) {
    currentMonth = month;
    tabs.forEach(t => t.classList.toggle('active', t.dataset.month === month));
    Object.values(sections).forEach(s => s.classList.remove('show'));
    
    const showTl = (month === 'all' || month.startsWith('20'));
    if (showTl) sections.tl.classList.add('show');
    else sections.tl.classList.remove('show');
    
    if (sections[month]) sections[month].classList.add('show');

    const isTimeline = showTl;
    searchBox.style.display = isTimeline ? 'block' : 'none';
    tabsMois.style.display = isTimeline ? 'flex' : 'none';
    phasesRow.style.display = isTimeline ? 'flex' : 'none';
    printBtn.style.display = (month === 'doc' || month === 'gloss') ? 'inline-block' : 'none';

    filterTimeline();
    if (month === 'accueil') history.replaceState(null, '', window.location.pathname);
    else history.replaceState(null, '', '#' + month);
}

tabs.forEach(t => t.addEventListener('click', () => switchTab(t.dataset.month)));

// Filtres phase
document.querySelectorAll('.pbtn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.pbtn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        filterTimeline();
    });
});

function filterTimeline() {
    const activePhase = document.querySelector('.pbtn.active').dataset.filter;
    const searchQuery = document.getElementById('search-input').value.toLowerCase();
    document.querySelectorAll('.item').forEach(item => {
        const matchPhase = (activePhase === 'all' || item.dataset.phase === activePhase);
        const matchMonth = (currentMonth === 'all' || item.dataset.month === currentMonth);
        const matchSearch = !searchQuery || item.textContent.toLowerCase().includes(searchQuery);
        item.classList.toggle('hidden', !(matchPhase && matchMonth && matchSearch));
    });
    document.querySelectorAll('.month').forEach(month => {
        month.classList.toggle('hidden', month.querySelectorAll('.item:not(.hidden)').length === 0 && currentMonth !== 'all');
    });
    document.getElementById('empty').style.display = (document.querySelectorAll('.item:not(.hidden)').length === 0 && currentMonth !== 'accueil') ? 'block' : 'none';
}

document.getElementById('search-input').addEventListener('input', filterTimeline);

// Copier le lien
document.getElementById('copy-link-btn').addEventListener('click', () => {
    navigator.clipboard.writeText(window.location.href);
    const ok = document.getElementById('copy-ok');
    ok.classList.add('show');
    setTimeout(() => ok.classList.remove('show'), 2000);
});

// Bouton remonter
const backToTop = document.getElementById('back-to-top');
window.addEventListener('scroll', () => backToTop.classList.toggle('show', window.scrollY > 600));
backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// Lightbox
document.querySelectorAll('.doc-photo img, .hero-img').forEach(img => {
    img.addEventListener('click', () => {
        document.getElementById('lightbox-img').src = img.src;
        document.getElementById('lightbox-caption').innerText = img.alt;
        document.getElementById('lightbox').classList.add('open');
    });
});
document.getElementById('lightbox-close').addEventListener('click', () => document.getElementById('lightbox').classList.remove('open'));
document.getElementById('lightbox').addEventListener('click', (e) => { if (e.target === e.currentTarget) e.currentTarget.classList.remove('open'); });

// Theme jour/nuit
const toggle = document.getElementById('theme-toggle');
if (localStorage.getItem('theme') === 'jour') document.body.classList.add('jour');
toggle.innerText = document.body.classList.contains('jour') ? '🌙' : '☀';
toggle.addEventListener('click', () => {
    document.body.classList.toggle('jour');
    toggle.innerText = document.body.classList.contains('jour') ? '🌙' : '☀';
    localStorage.setItem('theme', document.body.classList.contains('jour') ? 'jour' : 'nuit');
});

// --- Bouton "Je me lance" + compteur GoatCounter ---
(function() {
    var btn = document.getElementById('btn-useful');
    var avg = document.getElementById('advRateAvg');
    if (!btn || !avg) return;

    function afficherCompteur(n, dejaVote) {
        if (n > 0) {
            avg.textContent = n + ' personne' + (n > 1 ? 's se lancent' : ' se lance') + (dejaVote ? ' (dont vous) !' : ' aussi !');
        } else if (dejaVote) {
            avg.textContent = 'Vous faites partie des premiers !';
        }
    }

    var dejaVote = !!localStorage.getItem('site_useful_voted');
    if (dejaVote) btn.classList.add('is-voted');

    fetch('https://atelierduverdier.goatcounter.com/counter/%2Fvote-utile.json')
        .then(function(r) { return r.json(); })
        .then(function(d) { afficherCompteur(parseInt(d.count, 10) || 0, dejaVote); })
        .catch(function() {});

    btn.addEventListener('click', function() {
        if (dejaVote) return;
        dejaVote = true;
        btn.classList.add('is-voted');
        localStorage.setItem('site_useful_voted', 'true');
        avg.textContent = 'Super, bonne construction !';
        if (window.goatcounter && window.goatcounter.count) {
            window.goatcounter.count({ event: true, path: '/vote-utile', title: 'Construit une PrintNC' });
        }
    });
})();

// Partage par ancre
function copyAnchor(id) {
    var url = location.origin + location.pathname + '#' + id;
    var ok = function() { showToastOk(); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(ok).catch(ok);
    } else {
        var ta = document.createElement('textarea');
        ta.value = url; ta.style.cssText = 'position:fixed;opacity:0;';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch(e) {}
        document.body.removeChild(ta); ok();
    }
}
function showToastOk() {
    var t = document.getElementById('share-toast');
    if (!t) { t = document.createElement('div'); t.id = 'share-toast'; document.body.appendChild(t); }
    t.textContent = 'Lien copié !';
    t.classList.add('show');
    clearTimeout(t._tid);
    t._tid = setTimeout(function() { t.classList.remove('show'); }, 2000);
}

// Initialisation : deep linking
(function() {
    var naissance = new Date('__DATE_NAISSANCE__');
    var now = new Date();
    var mois = (now.getFullYear() - naissance.getFullYear()) * 12 + (now.getMonth() - naissance.getMonth());
    var jours = Math.floor((now - naissance) / 86400000);
    var label;
    if (jours < 30) {
        label = jours + (jours <= 1 ? ' jour' : ' jours');
    } else if (mois < 24) {
        label = mois + ' mois';
    } else {
        var ans = Math.floor(mois / 12);
        var rm = mois % 12;
        label = ans + (ans === 1 ? ' an' : ' ans') + (rm ? ' et ' + rm + ' mois' : '');
    }
    var el = document.getElementById('machine-age');
    if (el) el.textContent = label;
})();
function initFromHash(hash) {
    if (!hash) { switchTab('accueil'); return; }
    if (hash.startsWith('v-')) {
        switchTab('all');
        setTimeout(function() {
            var el = document.getElementById(hash);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 200);
    } else if (hash.startsWith('doc-') || hash.startsWith('gloss-')) {
        switchTab(hash.startsWith('gloss-') ? 'gloss' : 'doc');
        setTimeout(function() {
            var el = document.getElementById(hash);
            if (el) { el.open = true; el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        }, 200);
    } else {
        switchTab(hash);
    }
}
initFromHash(location.hash.slice(1));
window.addEventListener('hashchange', function() { initFromHash(location.hash.slice(1)); });
</script>
</body>
</html>'''

if __name__ == '__main__':
    construire()
