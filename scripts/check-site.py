#!/usr/bin/env python3
"""Validate every static page, local URL, language counterpart and product schema."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
 def __init__(self,path):super().__init__();self.path=path;self.tags=[];self.ids=[];self.h1=0;self.text=[];self.skip=False
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if a.get('id'):self.ids.append(a['id'])
  if t=='h1':self.h1+=1
  if t in ('script','style'):self.skip=True
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=False
 def handle_data(self,s):
  if not self.skip and s.strip():self.text.append(re.sub(r'\s+',' ',s).strip())
def route(p):
 path='/'+p.relative_to(ROOT).as_posix()
 return path[:-10] if path.endswith('index.html') else path
pages={}
for f in ROOT.rglob('*.html'):
 p=Page(f);p.feed(f.read_text());pages[f]=p
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
for f,p in pages.items():
 r=f.relative_to(ROOT);s=f.read_text();lang=r.parts[0] if r.parts[0] in ('en','ru') else 'pl';prefix=f'{r}: '
 check(p.h1==1,prefix+'expected one h1')
 check(not [i for i,n in Counter(p.ids).items() if n>1],prefix+'duplicate IDs')
 canon=[a['href'] for t,a in p.tags if t=='link' and a.get('rel')=='canonical'];check(canon==['https://ltsmarket.pl'+route(f)],prefix+'incorrect canonical')
 alts={a.get('hreflang'):a.get('href') for t,a in p.tags if t=='link' and a.get('rel')=='alternate'};check(set(alts)=={'pl','en','ru','x-default'},prefix+'incomplete hreflang')
 check(next(a['lang'] for t,a in p.tags if t=='html')==lang,prefix+'wrong document language')
 check('googletagmanager.com/gtag/js' not in s,prefix+'unconditional analytics')
 for tag,a in p.tags:
  for key in ('href','src'):
   if not a.get(key):continue
   u=urlsplit(a[key])
   if u.scheme and not (u.scheme in ('http','https') and u.netloc=='ltsmarket.pl'):continue
   if u.netloc and u.netloc!='ltsmarket.pl':continue
   dest=(ROOT/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else (f.parent/unquote(u.path)) if u.path else f
   if dest.is_dir():dest/= 'index.html'
   check(dest.exists(),prefix+'missing '+a[key])
   if dest in pages and u.fragment:check(unquote(u.fragment) in pages[dest].ids,prefix+'missing fragment '+a[key])
  if tag=='a' and a.get('lang') in ('pl','en','ru'):check(a['href']==urlsplit(alts[a['lang']]).path,prefix+'language switch mismatch')
 for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
  try:obj=json.loads(block)
  except ValueError:errors.append(prefix+'invalid JSON-LD');continue
  if obj.get('@type')=='Product':
   check(obj['url']==canon[0],prefix+'product schema URL')
   check(obj['offers']['priceCurrency']=='PLN',prefix+'currency')
 if 'uzywane' in r.parts and r.name!='uzywane.html':
  check('"@type": "Product"' in s,prefix+'missing Product schema')
  check(len([a for t,a in p.tags if 'data-image' in a])>=6,prefix+'incomplete gallery')
# Shared chrome may differ only in active-page state and language-switch URLs.
class Chrome(HTMLParser):
 def __init__(self):super().__init__();self.signature=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  a.pop('aria-current',None)
  if 'class' in a:a['class']=' '.join(c for c in a['class'].split() if c!='is-active')
  if tag=='a' and a.get('lang') in ('pl','en','ru'):a['href']='LANGUAGE_PAGE'
  self.signature.append((tag,sorted(a.items())))
 def handle_endtag(self,tag):self.signature.append(('/'+tag,))
 def handle_data(self,text):
  if text.strip():self.signature.append(('text',re.sub(r'\s+',' ',text).strip()))
shared={}
for f in pages:
 lang=f.relative_to(ROOT).parts[0]
 if lang not in ('en','ru'):lang='pl'
 for component in ('header','footer'):
  blocks=re.findall('<'+component+r' class="site-'+component+r'"[^>]*>.*?</'+component+'>',f.read_text(),re.S)
  check(len(blocks)==1,str(f)+' expected one shared '+component)
  if not blocks:continue
  parsed=Chrome();parsed.feed(blocks[0]);key=(lang,component)
  if key not in shared:shared[key]=parsed.signature
  check(parsed.signature==shared[key],str(f)+' inconsistent '+component)
# Check supplied product facts and translations against the generated pages.
products=json.loads((ROOT/'scripts/used-products.json').read_text())
translations=json.loads((ROOT/'scripts/translations.json').read_text())
for product in products:
 for lang in ('pl','en','ru'):
  prefix=ROOT if lang=='pl' else ROOT/lang
  page=pages[prefix/'uzywane'/(product['slug']+'.html')]
  check(product['description'][lang] in page.text,str(page.path)+' incorrect product translation')
  check(product['priceLabel'] in page.text,str(page.path)+' incorrect product price')
  check(str(product['year']) in page.text if product['year'] else True,str(page.path)+' incorrect year')
for f,p in pages.items():
 lang=f.relative_to(ROOT).parts[0]
 if lang not in ('en','ru'):continue
 for text in p.text:
  if text in translations:check(translations[text][lang]==text,str(f)+' untranslated text: '+text)
for f in ROOT.rglob('site.webmanifest'):
 m=json.loads(f.read_text());check(m['lang'] in ('pl','en','ru'),str(f)+' manifest language')
 for icon in m['icons']:check((ROOT/icon['src'].lstrip('/')).is_file(),str(f)+' missing icon')
xml=ET.parse(ROOT/'sitemap.xml');locs=[e.text for e in xml.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
check(set(locs)=={'https://ltsmarket.pl'+route(f) for f in pages},'Sitemap page coverage mismatch')
check(len(locs)==len(set(locs)),'Duplicate sitemap entries')
if errors:print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(pages)} pages, shared headers/footers, local assets and anchors, reciprocal language links, metadata, galleries, JSON-LD, 3 manifests, {len(locs)} sitemap URLs.')
