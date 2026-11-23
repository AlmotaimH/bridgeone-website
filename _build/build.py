from urllib.parse import quote
#!/usr/bin/env python3
"""BridgeOne site builder.
Edit text in _build/i18n.js, the home template in _build/index.tpl.html,
articles in _build/articles/*.html, then run:  python3 _build/build.py
It regenerates every page in English, French (/fr/) and Arabic (/ar/).
"""
import json, subprocess, re, html, os, glob

B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
V = '73'
SITE = 'https://bridge-one.ca/'
CO = 'https://www.linkedin.com/company/110901315/'
ME = 'https://www.linkedin.com/in/almotaimh/'
BOOK = 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ0aO-BlcStGVecBihE2OnPBUyP5SknhKZ5tUgFDl0L_cGZ54JCzUtOTi8MWzA1suHI3szzGr0B9'
NL = 'https://www.linkedin.com/newsletters/bridging-the-gap-7508783536003420161/'
T = json.loads(subprocess.check_output(['node', '-e',
    "global.window={};require('%s/i18n.js');console.log(JSON.stringify(window.BO_I18N))" % B]))
def _strip(o):
    if isinstance(o, dict): return {k: _strip(v) for k, v in o.items()}
    if isinstance(o, list): return [_strip(v) for v in o]
    if isinstance(o, str): return re.sub(r'\s*[→←]$', '', o)
    return o
T = _strip(T)
LANGS = {'EN': ('en', 'ltr', ''), 'FR': ('fr', 'ltr', 'fr/'), 'AR': ('ar', 'rtl', 'ar/')}
MONTHS = {
 'EN': ['January','February','March','April','May','June','July','August','September','October','November','December'],
 'FR': ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'],
 'AR': ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']}

def esc(s): return html.escape(s, quote=False)
def att(s): return html.escape(s, quote=True)
def g(L, key):
    v = T[L]
    for k in key.split('.'):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v
def fdate(L, iso):
    y, m, d = [int(x) for x in iso.split('-')]
    mn = MONTHS[L][m-1]
    return f'{mn} {d}, {y}' if L == 'EN' else f'{d} {mn} {y}'
def write(path, s):
    p = os.path.join(R, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

def langs_html(L, file):
    out = '<div class="langs" role="group" aria-label="Language">'
    for code, label, extra in [('EN', 'EN', ''), ('FR', 'FR', ''), ('AR', 'ع', ' lang="ar" aria-label="العربية"')]:
        cur = ' aria-current="true"' if code == L else ''
        out += f'<a href="/{LANGS[code][2]}{file}" hreflang="{LANGS[code][0]}"{extra}{cur}>{label}</a>'
    return out + '</div>'

def head(L, title, desc, file, alt=True, extra='', ogtype='website', og='assets/og-image.jpg'):
    lang, d, pre = LANGS[L]
    url = SITE + pre + file
    fonts = 'family=Montserrat:wght@400..800'
    if L == 'AR': fonts += '&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700'
    alts = ''
    if alt:
        for c in LANGS:
            alts += f'<link rel="alternate" hreflang="{LANGS[c][0]}" href="{SITE}{LANGS[c][2]}{file}">\n'
        alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{file}">\n'
    return f'''<!doctype html>
<html lang="{lang}" dir="{d}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{att(desc)}">
<meta name="theme-color" content="#020A1F">
<link rel="canonical" href="{url}">
{alts}<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{att(title)}">
<meta property="og:description" content="{att(desc)}">
<meta property="og:image" content="{SITE}{og}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icon-32.png">
<link rel="apple-touch-icon" href="/assets/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<script>document.documentElement.classList.add("js")</script>
<link rel="stylesheet" href="/styles.css?v={V}">
<script data-goatcounter="https://bridgeone.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
{extra}</head>
'''

BURGER = '<button class="burger" type="button" aria-label="Menu" aria-expanded="false"><svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14" stroke="#E8E2D4" stroke-width="2" stroke-linecap="round"/></svg></button>'
TOTOP = '<button class="to-top" type="button" aria-label="Back to top"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M4 11l5-5 5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>'
LI_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="3" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M7 10v7M7 7v.01M11 17v-7M11 13c0-2 1.500-3 3-3s3 1 3 3v4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'

def header(L, file, cur='', home=False):
    pre = '/' + LANGS[L][2]
    base = '' if home else pre
    def a(h, key, k):
        c = ' aria-current="page"' if k == cur else ''
        return f'<a href="{h}"{c}>{esc(g(L, key))}</a>'
    links = a(pre, 'nav.home', 'h') + a(base + '#services', 'nav.services', 's') + a(base + '#decisions', 'nav.dec', 'd') + a(base + '#approach', 'nav.approach', 'a') + a(base + '#why', 'nav.results', 'w') + a(pre + 'insights.html', 'nav.insights', 'i')
    return f'''<a class="skip" href="#main">{esc(g(L, "skip"))}</a>
<header class="hdr">
<div class="wrap">
<a class="brand" href="{pre}" aria-label="BridgeOne"><img src="/assets/logo-sm.png" alt="" width="54" height="34"><span>BRIDGEONE</span></a>
<nav class="nav" aria-label="Main">{links}{a(base + '#contact', 'nav.contact', 'c')}</nav>
<div class="hdr-r">{langs_html(L, file)}<a class="btn btn-gold" href="{BOOK}" target="_blank" rel="noopener">{esc(g(L, "nav.cta"))}</a>{BURGER}</div>
</div>
<nav class="mnav" aria-label="Mobile">{links}<a class="btn btn-gold" href="{BOOK}" target="_blank" rel="noopener">{esc(g(L, "nav.cta"))}</a></nav>
</header>
'''

def inner_header(L, file, cur=''):
    return '<body>\n' + header(L, file, cur)

def footer(L):
    pre = '/' + LANGS[L][2]
    return f'''<footer class="ftr"><img class="ftr-wm" src="/assets/logo-mark.png" alt="" aria-hidden="true" loading="lazy"><div class="wrap">
<div class="ftr-cta"><div><b>{esc(g(L, "band.title"))}</b></div><a class="btn btn-gold" href="{pre}#contact">{esc(g(L, "band.cta"))}</a></div>
<div class="top">
<div class="col main"><a class="brand" href="{pre}"><img src="/assets/logo-sm.png" alt="" width="54" height="34"><span>BRIDGEONE</span></a><span class="motto">{esc(g(L, "motto"))}</span>
<p style="margin:0;max-width:360px;line-height:1.6">{esc(g(L, "footer.tag"))}</p></div>
<nav class="col" aria-label="Footer"><b>{esc(g(L, "footer.company"))}</b><a href="{pre}#about">{esc(g(L, "footer.about"))}</a><a href="{pre}#services">{esc(g(L, "nav.services"))}</a><a href="{pre}bridgeone-os.html">BridgeOne OS</a><a href="{pre}insights.html">{esc(g(L, "nav.insights"))}</a><a href="{pre}#contact">{esc(g(L, "nav.contact"))}</a></nav>
<div class="col"><b>{esc(g(L, "nav.contact"))}</b><a href="tel:+16473355647" dir="ltr">+1 (647) 335-5647</a><a href="mailto:info@bridge-one.ca" dir="ltr">info@bridge-one.ca</a><span>{esc(g(L, "contact.hours"))}</span></div>
<nav class="col" aria-label="Legal"><b>{esc(g(L, "footer.legal"))}</b><a href="{pre}privacy.html">{esc(g(L, "footer.privacy"))}</a><a href="{CO}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:8px">{LI_ICON}LinkedIn</a></nav>
</div>
<div class="bot"><span>{esc(g(L, "footer.copy"))}</span><span>{esc(g(L, "contact.loc"))}</span></div>
</div>
</footer>
{TOTOP}
<script src="/main.js?v={V}"></script>
</body>
</html>
'''

def inner_footer(L): return footer(L)

# ---------- Articles ----------
def clean_body(b):
    b = b.replace('<h3>', '<h2>').replace('</h3>', '</h2>')
    lines = b.strip().split('\n'); out = []; i = 0
    def run(pred, tag, strip):
        nonlocal i
        items = []
        while i < len(lines) and pred(lines[i]):
            items.append('<li>' + strip(lines[i]) + '</li>'); i += 1
        out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
    bul = lambda l: l.startswith('<p>• ')
    num = lambda l: re.match(r'<p>\d+\. ', l) is not None
    while i < len(lines):
        l = lines[i]
        if bul(l): run(bul, 'ul', lambda x: x[len('<p>• '):-len('</p>')])
        elif num(l) and i + 1 < len(lines) and num(lines[i+1]): run(num, 'ol', lambda x: re.sub(r'^<p>\d+\. ', '', x)[:-len('</p>')])
        else: out.append(l); i += 1
    b = '\n'.join(out)
    b = re.sub(r'(<h2>References</h2>\n)<ul>', r'\1<ul class="refs">', b)
    b = b.replace('<p class="ref">', '<p class="refp">')
    return b

def load_articles():
    arts = []
    for f in sorted(glob.glob(B + '/articles/*.html')):
        raw = open(f, encoding='utf-8').read(); meta, body = raw.split('\n---\n', 1)
        m = dict(l.split(': ', 1) for l in meta.strip().split('\n'))
        arts.append(dict(title=m['TITLE'], date=m['DATE'], slug=m['SLUG'], source=m.get('SOURCE', ''), dek=m['DEK'],
                         read=m['READ'], cat=m.get('CAT', 'Leadership'), body=clean_body(body)))
    arts.sort(key=lambda a: a['date'])
    n = 0
    for a in arts:
        if a['source']: n += 1; a['ed'] = n
        else: a['ed'] = 0
    return arts

# Edition covers and posters (assets/ed). cover = 16:9 image; posters = (file, alt)
VIS = {
 'leadership-is-a-practice-not-a-position': ('e1', 'Edition 1 cover: Leadership is a practice, not a position, with a rising staircase of nine principles',
   [('e1-principles', 'Infographic: nine principles across three pillars, lead yourself, lead with others and make a difference')]),
 'the-weight-leaders-carry': ('e2', 'Edition 2 cover: The Weight Leaders Carry, with a pressure curve across a leader\'s first years',
   [('e2-weights', 'Infographic: the six weights leaders carry and the turning point for each')]),
 'why-good-leaders-misread-people': ('e3', 'Edition 3 cover: Why Good Leaders Misread People, showing what happened versus what you believe',
   [('e3-perception', 'Poster: Same facts, different realities, with the Johari window and how perception errors form'),
    ('e3-personality', 'Poster: Personality is if-then, not a label, with the HEXACO model and how situations trigger behaviour')]),
 'why-people-stop-trying': ('e4', 'Edition 4 cover: Why people stop trying, with the motivation and learning loop',
   [('e4-guide', 'Field guide: the motivation and learning loop, where it breaks, a team check-up and a 30-day playbook'),
    ('e4-motivation', 'Poster: Pay matters, meaning shapes effort, with the motivation spectrum'),
    ('e4-learning', 'Poster: One in three feedback interventions can make it worse, and where feedback should point')]),
 'the-influence-triangle': ('e5', 'Edition 5 cover: The Influence Triangle of power, conflict and communication, with voice in the middle',
   [('e5-guide', 'Field guide: find the weak corner of the influence triangle, a two-minute check-up and a 30-day playbook'),
    ('e5-power', 'Poster: Your title buys compliance, trust earns commitment, with the five bases of power'),
    ('e5-conflict', 'Poster: Fight about the work, never the person, with five ways to handle conflict'),
    ('e5-communication', 'Poster: What you meant isn\'t what they heard, with the tapping experiment')]),
 'from-answers-to-questions': ('e6', 'Edition 6 cover: From Answers to Questions, with a double-diamond diagram of Goal, Reality, Options and Will',
   [('e6-guide', 'Field guide: technical versus adaptive problems, a double-diamond diagnosis map, a team check-up and a 30-day playbook'),
    ('e6-coaching', 'Poster: The best leaders ask before they answer, with coaching effect sizes from Theeboom, Beersma and van Vianen (2014)'),
    ('e6-creative', 'Poster: First, think alone, then think together, with about 56 ideas from brainstorming groups versus 103 from people working alone first')]),
}
def cover_of(a): return VIS.get(a['slug'])
ARTS = load_articles()
LATEST = [a for a in ARTS if a['source']][-1]

def article_page(a, prev, nxt):
    L = 'EN'; file = f'insights/{a["slug"]}.html'
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": a['title'], "description": a['dek'],
                     "datePublished": a['date'], "inLanguage": "en",
                     "author": ({"@type": "Person", "name": "Hossam Almotaim", "url": ME} if a["source"] else {"@type": "Organization", "name": "BridgeOne Inc.", "url": SITE}),
                     "publisher": {"@type": "Organization", "name": "BridgeOne Inc.", "url": SITE},
                     "mainEntityOfPage": SITE + file}, ensure_ascii=False)
    h = head(L, f'{a["title"]} | BridgeOne Inc.', a['dek'], file, alt=False, ogtype='article',
             extra=f'<script type="application/ld+json">{ld}</script>\n', og=(f'assets/ed/{cover_of(a)[0]}-cover-og.jpg' if cover_of(a) else 'assets/og-image.jpg'))
    v = cover_of(a); cov = gal = ''
    if v:
        k, calt, posters = v
        cov = f'<figure class="cover"><img src="/assets/ed/{k}-cover.jpg" alt="{att(calt)}" width="1600" height="900" fetchpriority="high"></figure>'
        items = ''.join(f'<a class="pv" href="/assets/ed/{f}.jpg" target="_blank" rel="noopener"><img src="/assets/ed/{f}.jpg" alt="{att(t)}" width="1080" height="1350" loading="lazy"></a>' for f, t in posters)
        gal = f'<section class="visuals" aria-labelledby="vis-h"><h2 id="vis-h">Visual summary</h2><p>Save or share the posters from this edition. Select one to open it full size.</p><div class="pvs">{items}</div></section>'
    hdr = inner_header(L, 'insights.html', 'i').replace('<header class="hdr">', '<div class="progress" aria-hidden="true"></div>\n<header class="hdr">')
    eyebrow = f'Bridging the Gap, edition {a["ed"]}' if a['ed'] else a['cat']
    src = ''
    if a['source']:
        src = f'''<aside class="orig"><p>This edition of <strong>Bridging the Gap</strong> was first published on LinkedIn on {fdate(L, a["date"])}.</p>
<div><a class="btn btn-gold" href="{NL}" target="_blank" rel="noopener">Subscribe on LinkedIn</a><a class="btn btn-ghost" href="{a["source"]}" target="_blank" rel="noopener">Join the discussion on LinkedIn</a></div></aside>'''
    nav = '<nav class="pn" aria-label="More editions">'
    nav += f'<a href="/insights/{prev["slug"]}.html"><span>Previous edition</span><b>{esc(prev["title"])}</b></a>' if prev else '<span></span>'
    nav += f'<a href="/insights/{nxt["slug"]}.html" style="text-align:end"><span>Next edition</span><b>{esc(nxt["title"])}</b></a>' if nxt else '<span></span>'
    nav += '</nav>'
    share = SITE + file
    if a['source']:
        who = f'<img class="avatar" src="/assets/founder-sm.jpg?v=7" alt="" width="56" height="56"><div style="display:flex;flex-direction:column;font-size:15px"><strong><a href="{ME}" target="_blank" rel="noopener" style="color:#020A1F;text-decoration:none">Hossam Almotaim</a></strong>'
    else:
        who = '<img class="avatar logo-av" src="/assets/logo-mark.png" alt="" width="56" height="56"><div style="display:flex;flex-direction:column;font-size:15px"><strong style="color:#020A1F">BridgeOne</strong>'
    return h + hdr + f'''<main id="main"><article class="article">
<a class="back" href="/insights.html">All editions</a>
<p class="kicker">{esc(eyebrow)}</p>
<h1>{esc(a["title"])}</h1>
<p class="dek">{esc(a["dek"])}</p>
<div class="byline">{who}<span style="color:#5A6870"><time datetime="{a["date"]}">{fdate(L, a["date"])}</time>, {a["read"]} min read</span></div></div>
{cov}<div class="prose">
{a["body"]}
</div>
{gal}{src}
<div class="band"><h2>Want help putting ideas like these into practice in your organization?</h2><a class="btn btn-gold btn-lg" href="/#contact">Book a free consultation</a></div>
<div class="share"><span>Share</span>
<a class="btn btn-ghost" href="https://www.linkedin.com/sharing/share-offsite/?url={quote(share, safe="")}" target="_blank" rel="noopener">LinkedIn</a>
<button class="btn btn-ghost" type="button" data-copy data-copied="Link copied">Copy link</button></div>
{nav}
</article></main>
''' + inner_footer(L)

INS = {
 'EN': dict(title='Insights | BridgeOne Inc.', eyebrow='Insights', h1='Bridging the Gap',
            p='Every edition of Bridging the Gap, the leadership newsletter by BridgeOne founder Hossam Almotaim, published here and on LinkedIn.',
            all='All editions', ed='Edition', read='min read', note='', sub_h='Never miss an edition', sub_p='Bridging the Gap is published on LinkedIn. Subscribe there to get each new edition as it comes out.', go='Read the edition'),
 'FR': dict(title='Analyses | BridgeOne Inc.', eyebrow='Analyses', h1='Bridging the Gap',
            p='Toutes les éditions de Bridging the Gap, l’infolettre sur le leadership de Hossam Almotaim, fondateur de BridgeOne, publiées ici et sur LinkedIn.',
            all='Toutes les éditions', ed='Édition', read='min de lecture', note='Les articles sont publiés en anglais.', sub_h='Ne manquez aucune édition', sub_p='Bridging the Gap est publiée sur LinkedIn. Abonnez-vous pour recevoir chaque nouvelle édition dès sa parution.', go='Lire l’édition'),
 'AR': dict(title='رؤى | BridgeOne Inc.', eyebrow='رؤى', h1='Bridging the Gap',
            p='جميع إصدارات Bridging the Gap، نشرة القيادة التي يكتبها Hossam Almotaim مؤسس BridgeOne، تُنشر هنا وعلى لينكدإن.',
            all='جميع الإصدارات', ed='الإصدار', read='دقائق قراءة', note='المقالات منشورة باللغة الإنجليزية.', sub_h='لا تفوّت أي إصدار', sub_p='تُنشر Bridging the Gap على لينكدإن. اشترك هناك ليصلك كل إصدار جديد فور صدوره.', go='اقرأ الإصدار'),
}

def feature_card(L, a, label, go):
    return f'''<a class="feature" href="/insights/{a["slug"]}.html" hreflang="en">
{('<div class="art has-cover"><img src="/assets/ed/' + cover_of(a)[0] + '-cover.jpg" alt="" width="1600" height="900" loading="lazy"></div>') if cover_of(a) else ('<div class="art"><div class="lockup" aria-hidden="true"><img src="/assets/logo-mark.png" alt=""><span class="lk-name">BRIDGEONE</span><span class="lk-rule"></span><span class="lk-tag">' + esc(g(L, "motto")) + '</span></div></div>')}
<div class="tx"><span class="meta">{esc(label)}, <time datetime="{a["date"]}">{fdate(L, a["date"])}</time></span>
<h3 lang="en" dir="ltr">{esc(a["title"])}</h3>
<p lang="en" dir="ltr">{esc(a["dek"])}</p>
<span class="go">{esc(go)}</span></div>
</a>
'''

def ed_rows(L, arts, readw):
    rows = ''
    for a in arts:
        num = str(a['ed']) if a['ed'] else '<img src="/assets/logo-sm.png" alt="" width="30" height="19">'
        th = f'<img class="th" src="/assets/ed/{cover_of(a)[0]}-cover-sm.jpg" alt="" width="640" height="360" loading="lazy">' if cover_of(a) else ''
        rows += f'''<a class="ed{' has-th' if th else ''}" href="/insights/{a["slug"]}.html" hreflang="en">{th}<span class="n" aria-hidden="true">{num}</span>
<span class="meta"><time datetime="{a["date"]}">{fdate(L, a["date"])}</time>, {a["read"]} {readw}</span><b lang="en" dir="ltr">{esc(a["title"])}</b><span class="dk" lang="en" dir="ltr">{esc(a["dek"])}</span></a>
'''
    return rows

def insights_page(L):
    P = INS[L]
    rows = ed_rows(L, [x for x in ARTS if x is not LATEST], P['read'])
    note = f'<p class="note">{esc(P["note"])}</p>' if P['note'] else ''
    return head(L, P['title'], P['p'], 'insights.html') + inner_header(L, 'insights.html', 'i') + f'''<main id="main">
<section class="phero"><div class="wrap">
<p class="kicker">{esc(P["eyebrow"])}</p>
<h1>{esc(P["h1"])}</h1>
<p>{esc(P["p"])}</p>
</div></section>
<section class="sec" style="padding-top:72px"><div class="wrap">
{note}{feature_card(L, LATEST, g(L, "insights.featured"), P["go"])}
<div class="mast" style="margin:88px 0 0;grid-template-columns:1fr"><h2 style="font-size:clamp(28px,3.2vw,40px)">{esc(P["all"])}</h2></div>
<div class="eds">
{rows}</div>
</div></section>
<section class="sec fog" style="padding:80px 0"><div class="wrap subscribe">
<div><h2>{esc(P["sub_h"])}</h2><p>{esc(P["sub_p"])}</p></div>
<a class="btn btn-gold btn-lg" href="{NL}" target="_blank" rel="noopener">{esc(g(L, "news.btn"))}</a>
</div></section>
</main>
''' + inner_footer(L)

PRIV = {
 'EN': dict(t='Privacy policy', up='Last updated: November 22, 2026', secs=[
  (None, 'BridgeOne Inc. (“BridgeOne”, “we”) respects your privacy. This policy explains what personal information we collect through this website and how we use it, in line with Canada’s Personal Information Protection and Electronic Documents Act (PIPEDA).'),
  ('What we collect', 'When you use our contact form, call or email us, or book a consultation, we collect the details you provide, such as your name, email address, company and message.'),
  ('How we use it', 'We use your information only to respond to your enquiry and provide our services. We do not sell your personal information.'),
  ('How long we keep it', 'We keep your information only as long as we need it to respond to you, deliver our services and meet legal or contractual obligations, then delete it.'),
  ('Service providers', 'We use trusted providers to host this website, deliver contact-form messages, handle consultation bookings and run our email. They handle your information only on our behalf, and some may process it outside Canada. Our newsletter, Bridging the Gap, is published on LinkedIn, and subscriptions are managed by LinkedIn under its own privacy policy.'),
  ('Tools on this site', 'The business health check, the decision check and the BridgeOne OS demo run entirely in your browser. Nothing you enter in them is sent to us or saved.'),
  ('Website statistics', 'We use GoatCounter to count page visits. It does not use cookies or collect personal information, and we see only totals such as which pages were viewed and which country or website visitors came from.'),
  ('Your choices', 'You can ask to access, correct or delete your information at any time by emailing {e}.'),
  ('Contact', 'Hossam Almotaim, Founder, is responsible for privacy at BridgeOne. Questions about this policy? Email {e}.')]),
 'FR': dict(t='Politique de confidentialité', up='Dernière mise à jour : 22 novembre 2026', secs=[
  (None, 'BridgeOne Inc. (« BridgeOne », « nous ») respecte votre vie privée. La présente politique explique quels renseignements personnels nous recueillons par l’entremise de ce site Web et comment nous les utilisons, conformément à la Loi sur la protection des renseignements personnels et les documents électroniques (LPRPDE) du Canada.'),
  ('Ce que nous recueillons', 'Lorsque vous utilisez notre formulaire de contact, nous appelez ou nous écrivez, ou réservez une consultation, nous recueillons les renseignements que vous fournissez, comme votre nom, votre adresse courriel, votre entreprise et votre message.'),
  ('Comment nous les utilisons', 'Nous utilisons vos renseignements uniquement pour répondre à votre demande et fournir nos services. Nous ne vendons pas vos renseignements personnels.'),
  ('Durée de conservation', 'Nous conservons vos renseignements seulement le temps nécessaire pour vous répondre, fournir nos services et respecter nos obligations légales ou contractuelles, puis nous les supprimons.'),
  ('Fournisseurs de services', 'Nous faisons appel à des fournisseurs de confiance pour héberger ce site, acheminer les messages du formulaire, gérer les réservations de consultation et nos courriels. Ils traitent vos renseignements uniquement en notre nom, et certains peuvent les traiter à l’extérieur du Canada. Notre infolettre, Bridging the Gap, est publiée sur LinkedIn; les abonnements sont gérés par LinkedIn selon sa propre politique de confidentialité.'),
  ('Outils sur ce site', 'Le diagnostic d’entreprise, le diagnostic des décisions et la démo BridgeOne OS fonctionnent entièrement dans votre navigateur. Rien de ce que vous y saisissez ne nous est transmis ni n’est conservé.'),
  ('Statistiques du site', 'Nous utilisons GoatCounter pour compter les visites des pages. Il n’utilise pas de témoins (cookies) et ne recueille aucun renseignement personnel; nous ne voyons que des totaux, comme les pages consultées et le pays ou le site d’où viennent les visiteurs.'),
  ('Vos choix', 'Vous pouvez demander en tout temps à consulter, à corriger ou à supprimer vos renseignements en écrivant à {e}.'),
  ('Nous joindre', 'Hossam Almotaim, fondateur, est responsable de la protection des renseignements personnels chez BridgeOne. Des questions sur cette politique? Écrivez à {e}.')]),
 'AR': dict(t='سياسة الخصوصية', up='آخر تحديث: 22 نوفمبر 2026', secs=[
  (None, 'تحترم BridgeOne Inc. («BridgeOne» أو «نحن») خصوصيتك. توضّح هذه السياسة المعلومات الشخصية التي نجمعها عبر هذا الموقع وكيف نستخدمها، وفقًا لقانون حماية المعلومات الشخصية والوثائق الإلكترونية الكندي (PIPEDA).'),
  ('ما الذي نجمعه', 'عند استخدامك نموذج التواصل أو اتصالك بنا أو مراسلتنا أو حجز استشارة، نجمع البيانات التي تقدّمها، مثل اسمك وبريدك الإلكتروني وشركتك ورسالتك.'),
  ('كيف نستخدمها', 'نستخدم معلوماتك فقط للرد على استفسارك وتقديم خدماتنا. نحن لا نبيع معلوماتك الشخصية.'),
  ('مدة الاحتفاظ', 'نحتفظ بمعلوماتك فقط للمدة اللازمة للرد عليك وتقديم خدماتنا والوفاء بالتزاماتنا القانونية أو التعاقدية، ثم نحذفها.'),
  ('مزوّدو الخدمات', 'نستعين بمزوّدين موثوقين لاستضافة هذا الموقع وإيصال رسائل نموذج التواصل وإدارة حجوزات الاستشارات وبريدنا الإلكتروني. يتعاملون مع معلوماتك نيابةً عنا فقط، وقد يعالجها بعضهم خارج كندا. تُنشر نشرتنا Bridging the Gap على لينكدإن، وتُدار الاشتراكات فيها من قِبل لينكدإن وفق سياسة الخصوصية الخاصة به.'),
  ('الأدوات على هذا الموقع', 'يعمل فحص الأعمال وفحص القرارات والعرض التجريبي لـ BridgeOne OS بالكامل داخل متصفحك، ولا يُرسَل إلينا أو يُحفَظ أي شيء تُدخله فيها.'),
  ('إحصاءات الموقع', 'نستخدم GoatCounter لعدّ زيارات الصفحات. لا يستخدم ملفات تعريف الارتباط (الكوكيز) ولا يجمع أي معلومات شخصية، ولا نرى إلا أرقامًا إجمالية مثل الصفحات التي تمت زيارتها والبلد أو الموقع الذي جاء منه الزوار.'),
  ('خياراتك', 'يمكنك في أي وقت طلب الاطلاع على معلوماتك أو تصحيحها أو حذفها بمراسلتنا على {e}.'),
  ('تواصل معنا', 'المؤسس Hossam Almotaim هو المسؤول عن الخصوصية في BridgeOne. لديك أسئلة عن هذه السياسة؟ راسلنا على {e}.')]),
}
def privacy_page(L):
    P = PRIV[L]; e = '<a href="mailto:info@bridge-one.ca" dir="ltr">info@bridge-one.ca</a>'; body = ''
    for h2, p in P['secs']:
        if h2: body += f'<h2>{esc(h2)}</h2>\n'
        body += '<p>' + esc(p).replace('{e}', e) + '</p>\n'
    return head(L, f'{P["t"]} | BridgeOne Inc.', P['secs'][0][1][:150], 'privacy.html') + inner_header(L, 'privacy.html') + f'''<main id="main"><article class="article">
<h1>{esc(P["t"])}</h1>
<p style="color:#5A6870">{esc(P["up"])}</p>
<div class="prose">
{body}</div></article></main>
''' + inner_footer(L)

# ---------- Home ----------
def home_page(L):
    tpl = open(B + '/index.tpl.html', encoding='utf-8').read()
    body = tpl.replace('{{LANGS}}', langs_html(L, ''))
    recent = [x for x in ARTS if x['source'] and x is not LATEST][-3:]
    body = body.replace('{{LATEST}}', feature_card(L, LATEST, g(L, 'insights.featured'), g(L, 'insights.go')))
    body = body.replace('{{EDITIONS}}', ed_rows(L, recent, INS[L]['read']))
    body = body.replace('{{DOS}}', '/' + LANGS[L][2] + 'bridgeone-os.html').replace('{{BOOK}}', BOOK).replace('{{ME}}', ME).replace('{{NL}}', NL).replace('{{FAIL}}', att(g(L, 'contact.fail'))).replace('data-fail=', 'data-sending="' + att(g(L, 'contact.sending')) + '" data-mailbtn="' + att(g(L, 'contact.mailbtn')) + '" data-fail=')
    body = body.replace('<a class="skip" href="#main" data-i18n="skip"></a>\n<header', '<header')
    hs = body.index('<header'); he = body.index('</header>') + len('</header>')
    body = body[:hs] + header(L, '', home=True).split('\n', 1)[1].rstrip('\n') + body[he:]
    body = body.replace('<body>\n', '<body>\n' + f'<a class="skip" href="#main">{esc(g(L, "skip"))}</a>\n', 1)
    body = body.replace('{{FOOTER}}', footer(L))
    body = body.replace('data-clock>', 'data-clock data-city="' + att(g(L,'clock.city')) + '" data-open="' + att(g(L,'clock.open')) + '" data-closed="' + att(g(L,'clock.closed')) + '" data-pairs="' + att(json.dumps(g(L,'pairs'), ensure_ascii=False)) + '">',1)
    def rep(m):
        try: v = g(L, m.group(1))
        except Exception: raise SystemExit('missing text: ' + m.group(1))
        return f'{m.group(0)[:-1]}{esc(v)}<'
    body = re.sub(r'data-i18n="([\w.]+)"[^>]*>(?=<)', lambda m: m.group(0) if False else rep2(m, L), body)
    ld = json.dumps({"@context": "https://schema.org", "@type": "ProfessionalService", "name": "BridgeOne Inc.", "slogan": "Excellence With Purpose",
        "url": SITE, "logo": SITE + "assets/icon-512.png", "description": g('EN', 'meta.desc'), "telephone": "+1-647-335-5647", "email": "info@bridge-one.ca",
        "areaServed": "Greater Toronto Area, Ontario, Canada", "address": {"@type": "PostalAddress", "addressRegion": "ON", "addressCountry": "CA"},
        "openingHours": "Mo-Th 10:00-19:00", "sameAs": [CO],
        "founder": {"@type": "Person", "name": "Hossam Almotaim", "sameAs": ME}}, ensure_ascii=False)
    return head(L, g(L, 'meta.title'), g(L, 'meta.desc'), '', extra=f'<script type="application/ld+json">{ld}</script>\n') + body

def rep2(m, L):
    key = m.group(1)
    try: v = g(L, key)
    except Exception: raise SystemExit('missing text: ' + key)
    if not isinstance(v, str): raise SystemExit('not text: ' + key)
    return m.group(0) + esc(v)


# ---------- BridgeOne OS product page ----------
PORT = {'EN': ('One system, four portals', "Start with the portal you need and add the others when you're ready. They share the same data, so a sales forecast that sets tomorrow's roster also sets stock orders and the cash plan.", 'Every engagement starts with an assessment and baseline.', [('People Portal', 'Our HR Portal and staff scheduling in one place, for HR and operations managers', ['Staff rosters built from hourly demand and your labour target', 'Labour cost and overtime control within employment standards', 'HR answers and step-by-step decision guides, by province', 'Online HR requests with approval chains, target times and automatic checks against employee records', 'Letters and forms on your letterhead, ready to issue']), ('Stock & Supply Portal', 'For operations, buying and merchandising teams', ['Reorder points and safety stock for every item and location', 'Transfers between locations before new orders', 'Markdown plans and promotion checks that protect margin']), ('Franchise & Network Portal', 'For franchisors, area managers and multi-unit operators', ['Scorecards that compare every location', 'Go or no-go checks for new locations', 'Franchise fee and franchisee health checks']), ('Executive View', 'For the CEO, COO, CFO and owners', ['Thirteen-week cash and buying plan', 'Monthly scorecard against the baseline', 'Decision log: who approved what, and what happened next'])]), 'FR': ('Un système, quatre portails', 'Commencez par le portail dont vous avez besoin et ajoutez les autres quand vous êtes prêt. Ils partagent les mêmes données : la prévision de ventes qui fixe l’horaire de demain fixe aussi les commandes et le plan de trésorerie.', 'Chaque mandat commence par une évaluation et un point de départ.', [('Portail Personnel', 'Notre portail RH et les horaires réunis, pour les gestionnaires RH et des opérations', ['Horaires bâtis à partir de la demande horaire et de votre cible de main-d’œuvre', 'Contrôle du coût de main-d’œuvre et des heures supplémentaires selon les normes du travail', 'Réponses RH et guides de décision étape par étape, par province', 'Demandes RH en ligne avec circuits d’approbation, délais cibles et vérification automatique des dossiers des employés', 'Lettres et formulaires à votre en-tête, prêts à remettre']), ('Portail Stocks et approvisionnement', 'Pour les équipes des opérations, des achats et de la mise en marché', ['Points de commande et stocks de sécurité pour chaque article et emplacement', 'Transferts entre emplacements avant toute nouvelle commande', 'Plans de démarque et vérification des promotions qui protègent la marge']), ('Portail Franchises et réseau', 'Pour les franchiseurs, directeurs régionaux et exploitants multi-unités', ['Tableaux comparatifs de chaque emplacement', 'Vérification « go ou no-go » des nouveaux emplacements', 'Analyse des redevances et de la santé des franchisés']), ('Vue de la direction', 'Pour le PDG, le chef de l’exploitation, le chef des finances et les propriétaires', ['Plan de trésorerie et d’achats sur treize semaines', 'Bilan mensuel par rapport au point de départ', 'Journal des décisions : qui a approuvé quoi, et ce qui a suivi'])]), 'AR': ('نظام واحد وأربع بوابات', 'ابدأ بالبوابة التي تحتاجها وأضف الباقي عندما تكون مستعدًا. تتشارك البوابات البيانات نفسها، فتوقّع المبيعات الذي يحدد جدول الغد يحدد أيضًا طلبات المخزون وخطة النقد.', 'يبدأ كل تعاون بتقييم وخط أساس.', [('بوابة الموارد البشرية', 'بوابة الموارد البشرية وجداول الموظفين في مكان واحد، لمديري الموارد البشرية والعمليات', ['جداول موظفين مبنية على الطلب في كل ساعة وعلى هدف تكلفة العمالة', 'ضبط تكلفة العمالة والعمل الإضافي ضمن معايير العمل', 'إجابات الموارد البشرية وأدلة قرار خطوة بخطوة حسب المقاطعة', 'طلبات موارد بشرية إلكترونية بمسارات اعتماد ومُهل مستهدفة وتحقق تلقائي من سجلات الموظفين', 'خطابات ونماذج على ترويسة شركتك جاهزة للإصدار']), ('بوابة المخزون والإمداد', 'لفرق العمليات والمشتريات والتسويق التجاري', ['نقاط إعادة الطلب ومخزون الأمان لكل صنف وفرع', 'نقل المخزون بين الفروع قبل أي طلب جديد', 'خطط تخفيض وفحص للعروض يحميان الهامش']), ('بوابة الامتياز والشبكة', 'لمانحي الامتياز ومديري المناطق ومشغّلي الفروع المتعددة', ['بطاقات أداء تقارن كل الفروع', 'فحص «نعم أم لا» للمواقع الجديدة', 'تحليل رسوم الامتياز وصحة أصحاب الفروع']), ('الرؤية التنفيذية', 'للرئيس التنفيذي ومدير العمليات والمدير المالي والملاك', ['خطة نقد ومشتريات لثلاثة عشر أسبوعًا', 'بطاقة أداء شهرية مقارنة بخط الأساس', 'سجل القرارات: من اعتمد ماذا، وما الذي حدث بعدها'])])}
DOS = {
 'EN': dict(title='BridgeOne OS | Decision tools for multi-location businesses',
  desc='BridgeOne OS turns your sales, staff, stock and cash data into weekly decisions your managers approve. Four portals for multi-location businesses.',
  kick='BridgeOne OS', h1='Better everyday decisions across every location',
  lead='BridgeOne OS is our own decision system for businesses with several locations. It brings four portals, People, Stock & Supply, Franchise & Network and an Executive View, onto the data you already have, with clear weekly recommendations. Your managers approve them, and we measure the results with you every month.',
  demo='Try the live demo', book='Book a free call', demoNote='The demo uses a fictional five-location business and runs entirely in your browser.',
  forT='Built for businesses with more than one location', forL=['Retail chains and specialty stores','Cafés, restaurants and food service groups','Franchise networks, for franchisors and multi-unit franchisees','Service businesses with several branches or clinics'],
  modT='Seven tools, one weekly rhythm', mods=[
   ('Assessment and baseline','We look at how each decision is made today and put a dollar value on the gaps, so you know where to start.'),
   ('Staff roster and labour cost','Hourly demand becomes the staff each hour needs, then shifts that cover it at the lowest cost within your rules and employment standards.'),
   ('Stock, reorder and transfers','A safety stock and reorder point for every item at every location, with transfers from locations that have too much before anything new is ordered.'),
   ('Pricing, promotions and markdowns','Week-by-week markdown plans that protect margin, and a quick check on whether a promotion is worth running.'),
   ('Buying and cash plan','Thirteen weeks of cash in and out, with purchase orders timed so cash stays above the floor you set.'),
   ('Location and franchise decisions','A scorecard that compares every location, a go or no-go check for new sites, and a fee check for franchise networks.'),
   ('Decision log and monthly scorecard','Every recommendation, who approved it and what happened next, reviewed against the baseline each month.')],
  howT='How it works', how=[
   ('Assess','A free call, then a two to three week audit of your numbers and how decisions are made today.'),
   ('Set up','We connect the data you already keep, from your point of sale, payroll, inventory and accounting exports or spreadsheets, and set the rules with you.'),
   ('Decide weekly','Managers get recommendations they can approve, adjust or reject, each with a plain explanation of why.'),
   ('Measure monthly','We compare results with the baseline, refine the rules and decide what to improve next.')],
  diffT='What makes it different', diff=[
   ('Explainable','Every recommendation shows the reason and the numbers behind it. Nothing is a black box.'),
   ('Your rules, your call','Your service levels, wage rules, cash floor and approval roles. People decide; the tools advise.'),
   ('Starts with what you have','No new software to buy on day one. We begin with your exports and work alongside your payroll (ADP or another), point of sale and accounting.'),
   ('Run with you','BridgeOne runs the assessment and works with your team directly, so the tools fit how your business really operates.')],
  pkgT='Ways to work together', pkgs=[
   ('Decision assessment','2 to 4 weeks','Baseline, maturity score and a ranked list of opportunities with estimated value.'),
   ('Decision sprint','6 to 8 weeks','One or two tools set up on your data, with your managers trained and the first results measured.'),
   ('BridgeOne OS with coaching','Monthly','All the tools you need, weekly recommendations and a monthly scorecard review with BridgeOne.'),
   ('Licensed copy','Annual','Your own branded copy of BridgeOne OS, with roles and approvals, maintained by BridgeOne.')],
  lic='Each portal can be licensed as your own branded copy, with roles and approvals, maintained and updated by BridgeOne.',
  sign='Every stage ends with a named deliverable and clear acceptance criteria. The next stage starts only when you sign it off.',
  hc='A short call to name the 3 decisions worth fixing first and the portal to start with.',
  ctaT='See what better decisions are worth in your business', ctaP='Start with a free 30-minute call. We’ll tell you honestly whether BridgeOne OS fits.',
  note='Results depend on your data and how consistently recommendations are applied. Figures in the demo are illustrative.'),
 'FR': dict(title='BridgeOne OS | Outils de décision pour entreprises multisites',
  desc='BridgeOne OS transforme vos données en décisions hebdomadaires que vos gestionnaires approuvent. Quatre portails pour les entreprises multisites.',
  kick='BridgeOne OS', h1='De meilleures décisions au quotidien, dans chaque emplacement',
  lead='BridgeOne OS est le système de décision conçu par BridgeOne pour les entreprises qui comptent plusieurs emplacements. Il réunit quatre portails (Personnel, Stocks et approvisionnement, Franchises et réseau, et une Vue de la direction) sur les données dont vous disposez déjà, avec des recommandations hebdomadaires claires. Vos gestionnaires les approuvent, et nous mesurons les résultats avec vous chaque mois.',
  demo='Essayer la démo', book='Réserver un appel gratuit', demoNote='La démo utilise une entreprise fictive de cinq emplacements et fonctionne entièrement dans votre navigateur (en anglais).',
  forT='Conçu pour les entreprises de plus d’un emplacement', forL=['Chaînes de détail et boutiques spécialisées','Cafés, restaurants et groupes de restauration','Réseaux de franchises, franchiseurs et franchisés multi-unités','Entreprises de services avec plusieurs succursales ou cliniques'],
  modT='Sept outils, un rythme hebdomadaire', mods=[
   ('Évaluation et point de départ','Nous examinons comment chaque décision est prise aujourd’hui et chiffrons les écarts, pour savoir par où commencer.'),
   ('Horaires et coût de main-d’œuvre','La demande horaire devient le personnel requis à chaque heure, puis des quarts qui la couvrent au moindre coût, selon vos règles et les normes du travail.'),
   ('Stocks, réapprovisionnement et transferts','Un stock de sécurité et un point de commande pour chaque article à chaque emplacement, avec des transferts depuis les emplacements en surplus avant toute nouvelle commande.'),
   ('Prix, promotions et démarques','Des plans de démarque semaine par semaine qui protègent la marge, et une vérification rapide de la rentabilité d’une promotion.'),
   ('Achats et trésorerie','Treize semaines d’entrées et de sorties de fonds, avec des commandes planifiées pour garder la trésorerie au-dessus du seuil fixé.'),
   ('Emplacements et franchises','Un tableau comparatif de chaque emplacement, une vérification « go ou no-go » pour un nouveau site et une analyse des redevances pour les réseaux de franchises.'),
   ('Journal des décisions et bilan mensuel','Chaque recommandation, qui l’a approuvée et ce qui a suivi, comparé chaque mois au point de départ.')],
  howT='Comment ça fonctionne', how=[
   ('Évaluer','Un appel gratuit, puis un audit de deux à trois semaines de vos chiffres et de vos façons de décider.'),
   ('Mettre en place','Nous relions les données que vous avez déjà (exportations de caisse, de paie, d’inventaire et de comptabilité, ou tableurs) et fixons les règles avec vous.'),
   ('Décider chaque semaine','Vos gestionnaires reçoivent des recommandations à approuver, ajuster ou refuser, chacune expliquée simplement.'),
   ('Mesurer chaque mois','Nous comparons les résultats au point de départ, affinons les règles et choisissons la prochaine amélioration.')],
  diffT='Ce qui le distingue', diff=[
   ('Explicable','Chaque recommandation montre sa raison et les chiffres qui la justifient. Aucune boîte noire.'),
   ('Vos règles, votre décision','Vos niveaux de service, règles salariales, seuil de trésorerie et rôles d’approbation. Les personnes décident; les outils conseillent.'),
   ('Part de ce que vous avez','Aucun logiciel à acheter au départ. Nous partons de vos exportations et travaillons avec votre paie (ADP ou autre), votre caisse et votre comptabilité.'),
   ('Mené avec vous','BridgeOne réalise l’évaluation et travaille directement avec votre équipe, pour que les outils collent à votre réalité.')],
  pkgT='Façons de travailler ensemble', pkgs=[
   ('Évaluation décisionnelle','2 à 4 semaines','Point de départ, score de maturité et liste priorisée des occasions avec leur valeur estimée.'),
   ('Sprint décisionnel','6 à 8 semaines','Un ou deux outils mis en place sur vos données, gestionnaires formés et premiers résultats mesurés.'),
   ('BridgeOne OS avec accompagnement','Mensuel','Tous les outils utiles, des recommandations hebdomadaires et un bilan mensuel avec BridgeOne.'),
   ('Copie sous licence','Annuel','Votre propre copie de BridgeOne OS à vos couleurs, avec rôles et approbations, maintenue par BridgeOne.')],
  lic='Chaque portail peut être offert sous licence comme copie à vos couleurs, avec rôles et approbations, maintenue et mise à jour par BridgeOne.',
  sign='Chaque étape se termine par un livrable précis et des critères d’acceptation clairs. L’étape suivante ne commence qu’après votre approbation.',
  hc='Un court appel pour cibler les 3 décisions à corriger en premier et le portail par lequel commencer.',
  ctaT='Découvrez ce que valent de meilleures décisions pour votre entreprise', ctaP='Commencez par un appel gratuit de 30 minutes. Nous vous dirons franchement si BridgeOne OS vous convient.',
  note='Les résultats dépendent de vos données et de l’application constante des recommandations. Les chiffres de la démo sont illustratifs.'),
 'AR': dict(title='BridgeOne OS | أدوات قرار للشركات متعددة الفروع',
  desc='يحوّل BridgeOne OS بيانات المبيعات والموظفين والمخزون والنقد إلى توصيات أسبوعية يعتمدها مديروك: جداول الموظفين، ونقل المخزون، والتخفيضات، وخطط الشراء، وقرارات الفروع.',
  kick='BridgeOne OS', h1='قرارات يومية أفضل في كل فرع',
  lead='BridgeOne OS هو نظام القرار الذي صمّمته BridgeOne للشركات التي تدير أكثر من فرع. يجمع أربع بوابات، الموارد البشرية والمخزون والإمداد والامتياز والشبكة والرؤية التنفيذية، على البيانات المتوفرة لديك أصلًا، مع توصيات أسبوعية واضحة. يعتمدها مديروك، ونقيس النتائج معك كل شهر.',
  demo='جرّب العرض التجريبي', book='احجز مكالمة مجانية', demoNote='يستخدم العرض التجريبي شركة وهمية لديها خمسة فروع، ويعمل بالكامل داخل متصفحك (باللغة الإنجليزية).',
  forT='مصمَّم للشركات التي لديها أكثر من فرع', forL=['سلاسل التجزئة والمتاجر المتخصصة','المقاهي والمطاعم ومجموعات الأغذية','شبكات الامتياز التجاري، للمانحين وأصحاب الفروع المتعددة','شركات الخدمات ذات الفروع أو العيادات المتعددة'],
  modT='سبع أدوات وإيقاع أسبوعي واحد', mods=[
   ('التقييم وخط الأساس','ندرس كيف يُتخذ كل قرار اليوم ونقدّر قيمة الفجوات بالأرقام، لتعرف من أين تبدأ.'),
   ('جداول الموظفين وتكلفة العمالة','يتحول الطلب في كل ساعة إلى عدد الموظفين المطلوب، ثم إلى ورديات تغطيه بأقل تكلفة ضمن قواعدك ومعايير العمل.'),
   ('المخزون وإعادة الطلب والنقل','مخزون أمان ونقطة إعادة طلب لكل صنف في كل فرع، مع نقل الفائض من فرع إلى آخر قبل أي طلب جديد.'),
   ('التسعير والعروض والتخفيضات','خطط تخفيض أسبوعية تحمي الهامش، وفحص سريع لمعرفة ما إذا كان العرض يستحق التنفيذ.'),
   ('الشراء والتدفق النقدي','ثلاثة عشر أسبوعًا من التدفقات النقدية الداخلة والخارجة، مع توقيت أوامر الشراء ليبقى النقد فوق الحد الأدنى الذي تحدده.'),
   ('قرارات الفروع والامتياز','بطاقة أداء تقارن كل الفروع، وفحص «نعم أم لا» للمواقع الجديدة، وتحليل للرسوم في شبكات الامتياز.'),
   ('سجل القرارات وبطاقة الأداء الشهرية','كل توصية، ومن اعتمدها، وما حدث بعدها، مع مراجعة شهرية مقارنة بخط الأساس.')],
  howT='كيف يعمل', how=[
   ('التقييم','مكالمة مجانية، ثم تدقيق لمدة أسبوعين إلى ثلاثة لأرقامك وطريقة اتخاذ القرارات اليوم.'),
   ('الإعداد','نربط البيانات التي تحتفظ بها أصلًا من نقاط البيع والرواتب والمخزون والمحاسبة أو جداول البيانات، ونضع القواعد معك.'),
   ('قرارات أسبوعية','يحصل المديرون على توصيات يمكنهم اعتمادها أو تعديلها أو رفضها، مع شرح واضح لسبب كل توصية.'),
   ('قياس شهري','نقارن النتائج بخط الأساس، ونحسّن القواعد، ونحدد الخطوة التالية.')],
  diffT='ما الذي يميّزه', diff=[
   ('قابل للتفسير','كل توصية تعرض سببها والأرقام التي تستند إليها، دون أي صندوق أسود.'),
   ('قواعدك وقرارك','مستويات الخدمة وقواعد الأجور والحد الأدنى للنقد وأدوار الاعتماد كلها لك. الناس يقررون والأدوات تنصح.'),
   ('يبدأ بما لديك','لا حاجة لشراء برنامج جديد في البداية. نبدأ بملفاتك الحالية ونعمل مع نظام الرواتب لديك (ADP أو غيره) ونقاط البيع والمحاسبة.'),
   ('ننفّذه معك','تجري BridgeOne التقييم وتعمل مع فريقك مباشرة، لتناسب الأدوات طريقة عمل شركتك فعلًا.')],
  pkgT='طرق العمل معًا', pkgs=[
   ('تقييم القرارات','من أسبوعين إلى 4 أسابيع','خط أساس ودرجة نضج وقائمة مرتبة بالفرص وقيمتها التقديرية.'),
   ('سبرنت القرارات','من 6 إلى 8 أسابيع','إعداد أداة أو أداتين على بياناتك، وتدريب المديرين، وقياس النتائج الأولى.'),
   ('BridgeOne OS مع المتابعة','شهري','كل الأدوات التي تحتاجها، وتوصيات أسبوعية، ومراجعة شهرية لبطاقة الأداء مع BridgeOne.'),
   ('نسخة مرخّصة','سنوي','نسختك الخاصة من BridgeOne OS بهويتك، مع الأدوار والاعتمادات، وتتولى BridgeOne صيانتها.')],
  lic='يمكن ترخيص كل بوابة كنسخة خاصة بهويتك، مع الأدوار والاعتمادات، وتتولى BridgeOne صيانتها وتحديثها.',
  sign='تنتهي كل مرحلة بمخرَج محدد ومعايير قبول واضحة، ولا تبدأ المرحلة التالية إلا بعد اعتمادك له.',
  hc='مكالمة قصيرة لتحديد أهم 3 قرارات تستحق المعالجة أولًا والبوابة التي نبدأ بها.',
  ctaT='اكتشف قيمة القرارات الأفضل في شركتك', ctaP='ابدأ بمكالمة مجانية مدتها 30 دقيقة، وسنخبرك بصراحة إن كان BridgeOne OS مناسبًا لك.',
  note='تعتمد النتائج على بياناتك ومدى الالتزام بتطبيق التوصيات. الأرقام في العرض التجريبي توضيحية.'),
}
def dos_page(L):
    P = DOS[L]; f = 'bridgeone-os.html'
    li = ''.join(f'<li>{esc(x)}</li>' for x in P['forL'])
    pt, pp, pa, pl = PORT[L]
    mods = ''.join(f'<article class="tile dos-m"><span class="dos-who">{esc(w)}</span><h3>{esc(t)}</h3><ul>' + ''.join(f'<li>{esc(x)}</li>' for x in items) + '</ul></article>' for t, w, items in pl)
    how = ''.join(f'<li><b><span class="dos-l">{esc(x[0])}</span> {esc(x[1])}</b><span>{esc(x[2])}</span></li>' for x in g(L, 'dec.steps'))
    pkgs = [list(x) for x in g(L, 'dec.pkgs')]; pkgs[0][2] = P['hc']
    diff = ''.join(f'<div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in P['diff'])
    pk = ''.join(f'<article class="tile dx-pk{" dx-feat" if i == 2 else ""}"><span class="dx-dur">{esc(x[1])}</span><h3>{esc(x[0])}</h3><p>{esc(x[2])}</p></article>' for i, x in enumerate(pkgs))
    ld = json.dumps({"@context": "https://schema.org", "@type": "Service", "name": "BridgeOne OS", "serviceType": "Decision support for multi-location businesses",
        "provider": {"@type": "ProfessionalService", "name": "BridgeOne Inc.", "url": SITE}, "areaServed": "Canada", "description": P['desc'], "url": SITE + LANGS[L][2] + f}, ensure_ascii=False)
    return head(L, P['title'], P['desc'], f, extra=f'<script type="application/ld+json">{ld}</script>\n') + inner_header(L, f, 'd') + f'''<main id="main">
<section class="phero dos-hero"><div class="wrap">
<p class="kicker">{esc(P["kick"])}</p>
<h1>{esc(P["h1"])}</h1>
<p>{esc(P["lead"])}</p>
<div class="dos-cta"><a class="btn btn-gold btn-lg" href="/bridgeone-os/demo.html">{esc(P["demo"])}</a><a class="btn btn-glass btn-lg" href="{BOOK}" target="_blank" rel="noopener">{esc(P["book"])}</a></div>
<p class="dos-dn">{esc(P["demoNote"])}</p>
</div></section>
<section class="sec" style="padding-top:72px"><div class="wrap">
<div class="glass dos-for"><h2>{esc(P["forT"])}</h2><ul>{li}</ul></div>
<div class="sh" style="margin-top:80px"><h2>{esc(pt)}</h2><p>{esc(pp)}</p></div>
<div class="dos-mods dos-ports">{mods}</div>
<p class="dos-lic">{esc(pa)}</p>
<div class="sh" style="margin-top:80px"><h2>{esc(g(L, "dec.stepsT"))}</h2></div>
<ol class="dos-how">{how}</ol>
<p class="dos-lic">{esc(P["sign"])}</p>
<div class="sh" style="margin-top:80px"><h2>{esc(P["diffT"])}</h2></div>
<div class="dos-diff">{diff}</div>
<div class="sh" style="margin-top:80px"><h2>{esc(P["pkgT"])}</h2></div>
<div class="dx-pkgs">{pk}</div>
<p class="dos-lic">{esc(P["lic"])}</p>
<p class="dos-note">{esc(P["note"])}</p>
</div></section>
<section class="sec fog" style="padding:80px 0"><div class="wrap subscribe">
<div><h2>{esc(P["ctaT"])}</h2><p>{esc(P["ctaP"])}</p></div>
<div class="dos-cta" style="margin:0"><a class="btn btn-gold btn-lg" href="{BOOK}" target="_blank" rel="noopener">{esc(P["book"])}</a><a class="btn btn-glass btn-lg" href="/bridgeone-os/demo.html">{esc(P["demo"])}</a></div>
</div></section>
</main>
''' + inner_footer(L)



# ---------- Redirects from the old Decision OS addresses (renamed Nov 22, 2026) ----------
def redirect_stub(target):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>BridgeOne OS</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{target.lstrip('/')}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}"+location.hash)</script></head>
<body><p><a href="{target}">BridgeOne OS</a></p></body></html>
'''

# ---------- Write everything ----------
for L in LANGS:
    pre = LANGS[L][2]
    write(pre + 'index.html', home_page(L))
    write(pre + 'insights.html', insights_page(L))
    write(pre + 'privacy.html', privacy_page(L))
    write(pre + 'bridgeone-os.html', dos_page(L))
    write(pre + 'decision-os.html', redirect_stub('/' + pre + 'bridgeone-os.html'))
for i, a in enumerate(ARTS):
    write(f'insights/{a["slug"]}.html', article_page(a, ARTS[i-1] if i else None, ARTS[i+1] if i + 1 < len(ARTS) else None))
first = [a for a in ARTS if not a['source']]
if first:
    to = f'/insights/{first[0]["slug"]}.html'
    write('article.html', f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{SITE[:-1]}{to}"><meta http-equiv="refresh" content="0; url={to}"></head><body><a href="{to}">This article has moved.</a></body></html>\n')
urls = []
for L in LANGS:
    for f in ['', 'bridgeone-os.html', 'insights.html', 'privacy.html']: urls.append(SITE + LANGS[L][2] + f)
urls.append(SITE + 'bridgeone-os/demo.html')
urls += [SITE + f'insights/{a["slug"]}.html' for a in ARTS]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
s = open(R + '/404.html').read(); write('404.html', re.sub(r'styles\.css\?v=\d+', f'styles.css?v={V}', s))
print('built', len(urls), 'pages; latest:', LATEST['title'])
