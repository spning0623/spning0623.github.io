"""Build a portable Academic Pages-derived site from Markdown and JSON."""
from pathlib import Path
from html import escape
import argparse
import json
import re
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
NAV = [
    {'key': 'about', 'label': 'Home', 'path': ''},
    {'key': 'research', 'label': 'Research', 'path': 'research/'},
    {'key': 'publications', 'label': 'Publications', 'path': 'publications/'},
    # Teaching & Service is retained as a page but temporarily hidden from navigation.
    {'key': 'cv', 'label': 'CV', 'path': 'cv/'},
]
ICONS = {
    'email': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m3 5 9 7 9-7"/>',
    'location': '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    'scholar': '<path d="m1 8 11-6 11 6-11 6Z"/><path d="M5 11v7c4 4 10 4 14 0v-7M23 8v10"/>',
    'linkedin': '<rect x="2" y="2" width="20" height="20" rx="2"/><path d="M7 10v7M11 17v-7M11 13a3 3 0 0 1 6 0v4"/><circle cx="7" cy="7" r=".8" fill="currentColor" stroke="none"/>',
    'github': '<path d="M9 20c-4 1-4-2-6-2m12 5v-4c0-1 .2-2-1-3 4 0 7-2 7-6 0-2-1-3-2-4 0-1 0-3-1-4-2 0-4 2-4 2a12 12 0 0 0-5 0S7 2 5 2c-1 1-1 3-1 4-1 1-2 2-2 4 0 4 3 6 7 6-1 1-1 2-1 3v4"/>',
    'document': '<path d="M14 2H4v20h16V8Z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
}

def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

def bibtex(p):
    kind = {'journal': 'article', 'conference': 'inproceedings', 'preprint': 'misc'}[p['category']]
    key = f"Ning{p['year']}{p['id']}"
    lines = [f'@{kind}{{{key},', '  title = {' + p['title'] + '},', '  author = {' + ' and '.join(p['authors']) + '},', f"  year = {{{p['year']}}},"]
    field = 'booktitle' if p['category'] == 'conference' else 'journal' if p['category'] == 'journal' else 'howpublished'
    lines += ['  ' + field + ' = {' + p['venue'] + '},', '  url = {' + p['url'] + '},']
    if 'doi.org/' in p['url']:
        lines.append('  doi = {' + p['url'].split('doi.org/', 1)[1] + '},')
    if p['id'] == 'M1':
        lines += ['  eprint = {2605.23051},', '  archivePrefix = {arXiv},']
    return '\n'.join(lines).rstrip(',') + '\n}'

def authors_html(p):
    return ', '.join('<strong>' + escape(a) + '</strong>' if a == 'Shupeng Ning' else escape(a) for a in p['authors'])

def selected(pubs):
    features = {
        'M1': ('duet-architecture.png', 'DUET photonic computing architecture with jointly encoded operands and differential photodetection', 'A general-purpose photonic primitive for signed, dynamic AI workloads.'),
        'J10': ('cirptc-chip.jpg', 'Wire-bonded CirPTC photonic tensor-core chip', 'Embedding structured model compression directly into photonic hardware.'),
        'J8': ('peic_review_thumb.svg', 'Photonic-electronic AI accelerator schematic with a neural network, photonic tensor core, and electronic control and memory', 'A review of photonic computing devices, accelerator architectures, and hardware–software co-design.'),
        'J4': ('biosensing.png', 'Integrated microring biosensor and microfluidic platform', 'Multiplexed antigen detection with a subwavelength-grating microring platform.'),
        'J3': ('acoustofluidics.png', 'Serpentine surface-acoustic-wave microfluidic chip', 'Reusing an acoustic field to increase cell-separation throughput in a compact chip.'),
    }
    result = []
    for id_, (image, alt, summary) in features.items():
        p = next(p for p in pubs if p['id'] == id_)
        image_class = ' class="review-thumbnail"' if id_ == 'J8' else ''
        result.append(f'<article class="selected-paper"><a href="{escape(p["url"], quote=True)}"><img{image_class} src="assets/images/{image}" alt="{alt}" loading="lazy"></a><div><h3><a href="{escape(p["url"], quote=True)}">{escape(p["title"])}</a></h3><p class="paper-venue">{escape(p["venue"])} · {p["year"]}</p><p class="paper-summary">{summary}</p><a class="paper-link" href="{escape(p["url"], quote=True)}">{"Preprint" if p["category"] == "preprint" else "Paper"} ↗</a></div></article>')
    return '\n'.join(result)

def publication_page(pubs, profile):
    top = f'<p>Publications in photonic computing, integrated photonics, and biomedical microsystems. For citation information, visit my <a href="{escape(profile["scholar"], quote=True)}">Google Scholar profile</a>.</p><p><a href="../assets/files/publications.bib" download>Download bibliography (BibTeX)</a></p>'
    top += '<div class="publication-tools"><label for="publication-search">Search publications</label><input type="search" id="publication-search" placeholder="Title, author, venue, or year" autocomplete="off"><div class="publication-filters" role="group" aria-label="Publication type">'
    for cat, label in [('all','All'), ('preprint','Preprints'), ('journal','Journals'), ('conference','Conferences')]:
        top += f'<button class="filter-button" data-category="{cat}" aria-pressed="{"true" if cat == "all" else "false"}">{label}</button>'
    top += f'</div><p class="publication-status" id="publication-status" role="status" aria-live="polite">{len(pubs)} of {len(pubs)} publications</p></div><p id="no-results" class="no-results" hidden>No publications match your search. Try another keyword or publication type.</p>'
    for category, label in [('preprint', 'Preprints'), ('journal','Journal Articles'), ('conference','Conference Papers')]:
        top += f'<section class="publication-group"><h2>{label}</h2>'
        for p in (p for p in pubs if p['category'] == category):
            query = escape(' '.join([p['title'], *p['authors'], p['citation'], str(p['year'])]).lower(), quote=True)
            top += f'<article class="publication" id="{p["id"].lower()}" data-category="{category}" data-search="{query}"><h3><span class="pub-number">[{p["id"]}]</span><a href="{escape(p["url"], quote=True)}">{escape(p["title"])}</a></h3><p class="authors">{authors_html(p)}</p><p class="paper-venue">{escape(p["citation"])}</p><div class="pub-actions"><a href="{escape(p["url"], quote=True)}">{"arXiv" if category == "preprint" else "Paper"} ↗</a><details><summary>BibTeX</summary><pre>{escape(bibtex(p))}</pre></details></div></article>'
        top += '</section>'
    return top

def build():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site-url', default=None)
    args = parser.parse_args()
    profile = json.loads((ROOT/'content/profile.json').read_text(encoding='utf-8'))
    if args.site_url:
        profile['site_url'] = args.site_url.rstrip('/')
    pubs = json.loads((ROOT/'content/publications.json').read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True)
    (OUT/'assets/files/publications.bib').write_text('\n\n'.join(bibtex(p) for p in pubs)+'\n', encoding='utf-8')
    shutil.copy2(ROOT/'LICENSE.academicpages', OUT/'LICENSE.academicpages')
    env = Environment(loader=FileSystemLoader(ROOT/'templates'), autoescape=select_autoescape(['html']))
    template = env.get_template('base.html')
    person = {'@context':'https://schema.org', '@type':'Person', 'name':profile['name'], 'url':profile['site_url'], 'jobTitle':profile['title'], 'affiliation':{'@type':'Organization','name':profile['affiliation']}, 'sameAs':[profile['scholar'], profile['linkedin']]}
    pages = [('about','Shupeng Ning','Photonics · Computing · Microsystems'), ('research','Research','From Physical Principles To Integrated Systems'), ('publications','Publications','Papers & Preprints'), ('teaching','Teaching & Service','Education · Mentoring · Community'), ('cv','Curriculum Vitae','Background & Experience')]
    for key,title,eyebrow in pages:
        base = './' if key == 'about' else '../'
        route = '/' if key == 'about' else f'/{key}/'
        dest = OUT if key == 'about' else OUT/key
        dest.mkdir(exist_ok=True)
        if key == 'publications':
            content = publication_page(pubs, profile)
        else:
            md = (ROOT/f'content/{key}.md').read_text(encoding='utf-8')
            content = markdown.markdown(md, extensions=['tables','toc','fenced_code'])
            content = content.replace('<!-- SELECTED_PUBLICATIONS -->', selected(pubs))
        rendered = template.render(profile=profile, key=key, title=title, eyebrow=eyebrow, description=profile['description'], base=base, route=route, content=content, navigation=NAV, icon=icon, structured_data=json.dumps(person, ensure_ascii=False).replace('<','\\u003c'))
        (dest/'index.html').write_text(rendered, encoding='utf-8')
    error = template.render(profile=profile, key='404', title='Page Not Found', eyebrow='404', description=profile['description'], base='/', route='/404.html', content='<p>This page may have moved. <a href="/">Return to the homepage</a> or use the navigation above.</p>', navigation=NAV, icon=icon, structured_data=json.dumps(person))
    (OUT/'404.html').write_text(error, encoding='utf-8')
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {profile["site_url"]}/sitemap.xml\n', encoding='utf-8')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{profile["site_url"]}{"/" if p[0] == "about" else "/"+p[0]+"/"}</loc></url>' for p in pages) + '</urlset>'
    (OUT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    print(f'Built {len(pages)} pages, 404 page, {len(pubs)} publications, and bibliography in {OUT}')

if __name__ == '__main__':
    build()
