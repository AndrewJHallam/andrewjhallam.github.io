#!/usr/bin/env python3
"""Build a compact, single-page academic website. Standard library only."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parent
profile = json.loads((ROOT / 'profile.json').read_text())
publications = sorted(json.loads((ROOT / 'publications.json').read_text()), key=lambda p: -p['year'])

def e(value):
    return escape(str(value), quote=True)

def author_line(text):
    return re.sub(r'(Andrew Hallam|A\. Hallam)', r'<strong>\1</strong>', e(text))

def publication(p):
    preprint = 'Preprint · ' if p['status'] == 'preprint' else ''
    arxiv = f' · <a href="{e(p["arxiv"])}">arXiv</a>' if p.get('arxiv') and p['arxiv'] != p['url'] else ''
    return f'''<li id="{e(p['id'])}"><a class="paper-title" href="{e(p['url'])}">{e(p['title'])}</a>
    <p class="authors">{author_line(p['authors'])}</p>
    <p class="citation">{preprint}<em>{e(p['venue'])}</em> ({p['year']}){arxiv}</p></li>'''

def document(title, body, missing=False):
    person = json.dumps({'@context':'https://schema.org', '@type':'Person', 'name':profile['name'], 'jobTitle':profile['role'], 'url':profile['site_url'], 'image':profile['site_url']+'/andrew-hallam.jpg', 'worksFor':{'@type':'Organization','name':'EPCC, University of Edinburgh'}, 'sameAs':[profile['scholar'],profile['arxiv'],profile['linkedin'],profile['github']]}).replace('</','<\\/')
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{'<base href="/">' if missing else ''}<title>{e(title)}</title>
<meta name="description" content="Andrew Hallam, Quantum Fellow at EPCC, University of Edinburgh. Research in tensor networks, quantum many-body physics, and quantum information.">
<link rel="canonical" href="{e(profile['site_url'])}/"><meta name="theme-color" content="#fafafa">
<meta property="og:type" content="website"><meta property="og:title" content="Andrew Hallam | Quantum Fellow"><meta property="og:description" content="Tensor networks, quantum many-body dynamics, and quantum information. EPCC, University of Edinburgh."><meta property="og:image" content="{e(profile['site_url'])}/andrew-hallam.jpg">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css?v=20261021d">
<script type="application/ld+json">{person}</script></head><body><a class="skip-link" href="#main">Skip to content</a>
<div class="page"><header class="site-header"><h1><a href="index.html">Andrew Hallam</a></h1><p class="subtitle">Quantum Fellow · EPCC, University of Edinburgh</p><nav aria-label="Main navigation"><a href="index.html#about">About</a><a href="index.html#research">Research</a><a href="index.html#publications">Publications</a><a href="index.html#contact">Contact</a></nav></header>
<main id="main">{body}</main><footer>© 2026 Andrew Hallam <span>Updated {e(profile['updated'])}</span></footer></div></body></html>'''

career = ''.join(f'<li><span class="career-date">{e(x["dates"])}</span><span>{e(x["title"])}, {e(x["institution"])}</span></li>' for x in profile['appointments'])
career += ''.join(f'<li><span class="career-date">{e(x["dates"])}</span><span>{e(x["degree"])}, {e(x["institution"])}</span></li>' for x in profile['education'])
research = ''.join(f'<li><strong>{e(t["title"])}.</strong> {e(t["short"])}</li>' for t in profile['themes'])
papers = ''.join(publication(p) for p in publications)
teaching = ''.join(f'<p>{e(x)}</p>' for x in profile['teaching'])
body = f'''
<section id="about" class="about"><div class="about-copy"><p class="intro">I am a Quantum Fellow at <a href="https://www.epcc.ed.ac.uk/">EPCC</a>, University of Edinburgh. My research connects quantum many-body physics, tensor networks, and quantum information.</p><p>{e(profile['intro'])}</p><h2>Career</h2><ul class="career">{career}</ul></div><figure class="portrait"><img src="andrew-hallam.jpg" alt="Andrew Hallam" width="1200" height="1597" fetchpriority="high"><figcaption><a href="{e(profile['scholar'])}">Google Scholar</a><span aria-hidden="true"> · </span><a href="{e(profile['arxiv'])}">arXiv</a><span aria-hidden="true"> · </span><a href="{e(profile['linkedin'])}">LinkedIn</a></figcaption></figure></section>
<section id="research"><h2>Research</h2><p>{e(profile['research_intro'])}</p><ul class="research-list">{research}</ul></section>
<section id="publications"><h2>Publications &amp; preprints</h2><p>A list of my research papers is below. You can also find my work on <a href="{e(profile['arxiv'])}">arXiv</a> and <a href="{e(profile['scholar'])}">Google Scholar</a>.</p><ol class="publications">{papers}</ol></section>
<section id="teaching"><h2>Teaching &amp; supervision</h2>{teaching}<p>I have also organised quantum theory and non-equilibrium seminars, helped organise academic conferences, and contributed to the University of Leeds Reach for Excellence programme.</p></section>
<section id="contact"><h2>Contact</h2><p>EPCC, University of Edinburgh<br><a href="mailto:{e(profile['email'])}">{e(profile['email'])}</a><br><a href="mailto:{e(profile['alternate_email'])}">{e(profile['alternate_email'])}</a></p><p class="profile-links"><a href="{e(profile['scholar'])}">Google Scholar</a><a href="{e(profile['arxiv'])}">arXiv</a><a href="{e(profile['github'])}">GitHub</a><a href="{e(profile['linkedin'])}">LinkedIn</a></p></section>'''

(ROOT/'index.html').write_text(document('Andrew Hallam | Quantum Fellow',body),encoding='utf-8')
(ROOT/'404.html').write_text(document('Page not found | Andrew Hallam','<section><h2>Page not found</h2><p>This page may have moved. <a href="index.html">Return to my homepage</a>.</p></section>',missing=True),encoding='utf-8')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+e(profile['site_url'])+'/</loc></url></urlset>\n')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+profile['site_url']+'/sitemap.xml\n')
(ROOT/'.nojekyll').touch()
print(f'Built single-page website with {len(publications)} publications and a custom 404 page.')
