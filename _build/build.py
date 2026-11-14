#!/usr/bin/env python3
"""BridgeOne site builder.
Edit text in _build/i18n.js, the home template in _build/index.tpl.html,
articles in _build/articles/*.html, then run:  python3 _build/build.py
It regenerates every page in English, French (/fr/) and Arabic (/ar/).
"""
import json, subprocess, re, html, os, glob

B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
V = '36'
SITE = 'https://bridge-one.ca/'
CO = 'https://www.linkedin.com/company/110901315/'
ME = 'https://www.linkedin.com/in/almotaimh/'
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

def head(L, title, desc, file, alt=True, extra='', ogtype='website'):
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
<meta property="og:image" content="{SITE}assets/og-image.jpg">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icon-32.png">
<link rel="apple-touch-icon" href="/assets/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<script>document.documentElement.classList.add("js")</script>
<link rel="stylesheet" href="/styles.css?v={V}">
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
    links = a(pre, 'nav.home', 'h') + a(base + '#services', 'nav.services', 's') + a(base + '#approach', 'nav.approach', 'a') + a(base + '#why', 'nav.results', 'w') + a(pre + 'insights.html', 'nav.insights', 'i')
    return f'''<a class="skip" href="#main">{esc(g(L, "skip"))}</a>
<header class="hdr">
<div class="wrap">
<a class="brand" href="{pre}" aria-label="BridgeOne"><img src="/assets/logo-sm.png" alt="" width="54" height="34"><span>BRIDGEONE</span></a>
<nav class="nav" aria-label="Main">{links}{a(base + '#contact', 'nav.contact', 'c')}</nav>
<div class="hdr-r">{langs_html(L, file)}<a class="btn btn-gold" href="{base}#contact">{esc(g(L, "nav.cta"))}</a>{BURGER}</div>
</div>
<nav class="mnav" aria-label="Mobile">{links}<a class="btn btn-gold" href="{base}#contact">{esc(g(L, "nav.cta"))}</a></nav>
</header>
'''

def inner_header(L, file, cur=''):
    return '<body>\n' + header(L, file, cur)

def footer(L):
    pre = '/' + LANGS[L][2]
    return f'''<footer class="ftr"><div class="wrap">
<div class="top">
<div class="col main"><a class="brand" href="{pre}"><img src="/assets/logo-sm.png" alt="" width="54" height="34"><span>BRIDGEONE</span></a><span class="motto">{esc(g(L, "motto"))}</span>
<p style="margin:0;max-width:360px;line-height:1.6">{esc(g(L, "footer.tag"))}</p></div>
<nav class="col" aria-label="Footer"><b>{esc(g(L, "footer.company"))}</b><a href="{pre}#about">{esc(g(L, "footer.about"))}</a><a href="{pre}#services">{esc(g(L, "nav.services"))}</a><a href="{pre}insights.html">{esc(g(L, "nav.insights"))}</a><a href="{pre}#contact">{esc(g(L, "nav.contact"))}</a></nav>
<nav class="col" aria-label="Legal"><b>{esc(g(L, "footer.legal"))}</b><a href="{pre}privacy.html">{esc(g(L, "footer.privacy"))}</a><a href="{CO}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:8px">{LI_ICON}LinkedIn</a></nav>
</div>
<div class="bot"><span>{esc(g(L, "footer.copy"))}</span><span>Greater Toronto Area, Ontario</span></div>
</div>
<div class="wordmark" aria-hidden="true">BRIDGEONE</div>
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
             extra=f'<script type="application/ld+json">{ld}</script>\n')
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
<div class="prose">
{a["body"]}
</div>
{src}
<div class="band"><h2>Want help putting ideas like these into practice in your organization?</h2><a class="btn btn-gold btn-lg" href="/#contact">Book a free consultation</a></div>
<div class="share"><span>Share</span>
<a class="btn btn-ghost" href="https://www.linkedin.com/sharing/share-offsite/?url={share}" target="_blank" rel="noopener">LinkedIn</a>
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
<div class="art"><div class="lockup" aria-hidden="true"><img src="/assets/logo-mark.png" alt=""><span class="lk-name">BRIDGEONE</span><span class="lk-rule"></span><span class="lk-tag">{esc(g(L, "motto"))}</span></div></div>
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
        rows += f'''<a class="ed" href="/insights/{a["slug"]}.html" hreflang="en"><span class="n" aria-hidden="true">{num}</span>
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
 'EN': dict(t='Privacy policy', up='Last updated: November 13, 2026', secs=[
  (None, 'BridgeOne Inc. (“BridgeOne”, “we”) respects your privacy. This policy explains what personal information we collect through this website and how we use it, in line with Canada’s Personal Information Protection and Electronic Documents Act (PIPEDA).'),
  ('What we collect', 'When you use our contact form, call or email us, or book a consultation, we collect the details you provide, such as your name, email address, company and message.'),
  ('How we use it', 'We use your information only to respond to your enquiry and provide our services. We do not sell your personal information.'),
  ('Service providers', 'We use trusted third parties to run this website, process forms and send email. They handle your information only on our behalf. Our newsletter, Bridging the Gap, is published on LinkedIn, and subscriptions are managed by LinkedIn under its own privacy policy.'),
  ('Your choices', 'You can ask to access, correct or delete your information at any time by emailing {e}.'),
  ('Contact', 'Questions about this policy? Email {e}.')]),
 'FR': dict(t='Politique de confidentialité', up='Dernière mise à jour : 13 novembre 2026', secs=[
  (None, 'BridgeOne Inc. (« BridgeOne », « nous ») respecte votre vie privée. La présente politique explique quels renseignements personnels nous recueillons par l’entremise de ce site Web et comment nous les utilisons, conformément à la Loi sur la protection des renseignements personnels et les documents électroniques (LPRPDE) du Canada.'),
  ('Ce que nous recueillons', 'Lorsque vous utilisez notre formulaire de contact, nous appelez ou nous écrivez, ou réservez une consultation, nous recueillons les renseignements que vous fournissez, comme votre nom, votre adresse courriel, votre entreprise et votre message.'),
  ('Comment nous les utilisons', 'Nous utilisons vos renseignements uniquement pour répondre à votre demande et fournir nos services. Nous ne vendons pas vos renseignements personnels.'),
  ('Fournisseurs de services', 'Nous faisons appel à des tiers de confiance pour exploiter ce site Web, traiter les formulaires et envoyer des courriels. Ils traitent vos renseignements uniquement en notre nom. Notre infolettre, Bridging the Gap, est publiée sur LinkedIn; les abonnements sont gérés par LinkedIn selon sa propre politique de confidentialité.'),
  ('Vos choix', 'Vous pouvez demander en tout temps à consulter, à corriger ou à supprimer vos renseignements en écrivant à {e}.'),
  ('Nous joindre', 'Des questions sur cette politique? Écrivez à {e}.')]),
 'AR': dict(t='سياسة الخصوصية', up='آخر تحديث: 13 نوفمبر 2026', secs=[
  (None, 'تحترم BridgeOne Inc. («BridgeOne» أو «نحن») خصوصيتك. توضّح هذه السياسة المعلومات الشخصية التي نجمعها عبر هذا الموقع وكيف نستخدمها، وفقًا لقانون حماية المعلومات الشخصية والوثائق الإلكترونية الكندي (PIPEDA).'),
  ('ما الذي نجمعه', 'عند استخدامك نموذج التواصل أو اتصالك بنا أو مراسلتنا أو حجز استشارة، نجمع البيانات التي تقدّمها، مثل اسمك وبريدك الإلكتروني وشركتك ورسالتك.'),
  ('كيف نستخدمها', 'نستخدم معلوماتك فقط للرد على استفسارك وتقديم خدماتنا. نحن لا نبيع معلوماتك الشخصية.'),
  ('مزوّدو الخدمات', 'نستعين بأطراف ثالثة موثوقة لتشغيل هذا الموقع ومعالجة النماذج وإرسال البريد الإلكتروني، وهم يتعاملون مع معلوماتك نيابةً عنا فقط. تُنشر نشرتنا Bridging the Gap على لينكدإن، وتُدار الاشتراكات فيها من قِبل لينكدإن وفق سياسة الخصوصية الخاصة به.'),
  ('خياراتك', 'يمكنك في أي وقت طلب الاطلاع على معلوماتك أو تصحيحها أو حذفها بمراسلتنا على {e}.'),
  ('تواصل معنا', 'لديك أسئلة عن هذه السياسة؟ راسلنا على {e}.')]),
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
    body = body.replace('{{ME}}', ME).replace('{{NL}}', NL).replace('{{FAIL}}', att(g(L, 'contact.fail')))
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

# ---------- Write everything ----------
for L in LANGS:
    pre = LANGS[L][2]
    write(pre + 'index.html', home_page(L))
    write(pre + 'insights.html', insights_page(L))
    write(pre + 'privacy.html', privacy_page(L))
for i, a in enumerate(ARTS):
    write(f'insights/{a["slug"]}.html', article_page(a, ARTS[i-1] if i else None, ARTS[i+1] if i + 1 < len(ARTS) else None))
first = [a for a in ARTS if not a['source']]
if first:
    to = f'/insights/{first[0]["slug"]}.html'
    write('article.html', f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{SITE[:-1]}{to}"><meta http-equiv="refresh" content="0; url={to}"></head><body><a href="{to}">This article has moved.</a></body></html>\n')
urls = []
for L in LANGS:
    for f in ['', 'insights.html', 'privacy.html']: urls.append(SITE + LANGS[L][2] + f)
urls += [SITE + f'insights/{a["slug"]}.html' for a in ARTS]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
s = open(R + '/404.html').read(); write('404.html', re.sub(r'styles\.css\?v=\d+', f'styles.css?v={V}', s))
print('built', len(urls), 'pages; latest:', LATEST['title'])
