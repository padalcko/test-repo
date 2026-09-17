#!/usr/bin/env python3
"""Build static PL/EN/RU pages using the current Polish design, with no runtime translation.
Run from any directory: python3 scripts/build-site.py
Product source: https://github.com/padalcko/ltsmarket/blob/main/assets/js/used-products.js
Snapshot retrieved 2026-09-17. Photos are this site's original local assets.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import escape, unescape
import json, re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
BASE='https://ltsmarket.pl'
LANGS=('pl','en','ru')
D=json.loads((ROOT/'scripts/translations.json').read_text())
PRODUCTS=json.loads((ROOT/'scripts/used-products.json').read_text())
def norm(s):return re.sub(r'\s+',' ',s).strip()
def add(pl,en,ru):D[pl]={'en':en,'ru':ru}
for row in [
 ('Katalog urządzeń używanych','Pre-owned equipment catalogue','Каталог б/у оборудования'),
 ('Sprawdzone urządzenia używane | LTS Market','Inspected pre-owned equipment | LTS Market','Проверенное б/у оборудование | LTS Market'),
 ('Sprawdzone urządzenia używane po serwisie Laser Tech Service. Zdjęcia, opisy i ceny aparatów dostępnych w LTS Market.','Inspected pre-owned equipment serviced by Laser Tech Service. Photos, descriptions and prices at LTS Market.','Проверенное б/у оборудование после сервиса Laser Tech Service. Фото, описания и цены аппаратов LTS Market.'),
 ('Urządzenia używane','Pre-owned equipment','Б/у оборудование'),
 ('gotowe do pracy','ready to use','готовое к работе'),
 ('Poznaj urządzenia po serwisie Laser Tech Service. Zobacz rzeczywiste zdjęcia, sprawdź parametry i zapytaj o aktualną dostępność.','Explore equipment serviced by Laser Tech Service. View actual photos, check specifications and ask about current availability.','Ознакомьтесь с аппаратами после сервиса Laser Tech Service. Посмотрите реальные фото, характеристики и уточните наличие.'),
 ('Zobacz ofertę','View equipment','Смотреть предложения'),
 ('Rok produkcji','Year of manufacture','Год выпуска'),
 ('Stan','Condition','Состояние'),
 ('Nie podano','Not specified','Не указан'),
 ('Zapytaj o dostępność','Ask about availability','Уточнить наличие'),
 ('Wróć do katalogu','Back to catalogue','Вернуться в каталог'),
 ('Galeria produktu','Product gallery','Галерея аппарата'),
 ('Cena i dostępność do potwierdzenia przy kontakcie.','Please confirm price and availability when contacting us.','Уточняйте цену и наличие при обращении.'),
 ('Informacje o prywatności | LTS Market','Privacy information | LTS Market','Информация о конфиденциальности | LTS Market'),
 ('Informacje o formularzach, usługach zewnętrznych i ustawieniach prywatności LTS Market.','Information about forms, external services and LTS Market privacy settings.','Информация о формах, внешних сервисах и настройках конфиденциальности LTS Market.'),
 ('Kontakt w sprawie danych','Data enquiries','Вопросы о данных'),
 ('Pytania dotyczące danych osobowych możesz kierować na sales@ltsmarket.pl. Podawaj wyłącznie informacje potrzebne do obsługi zapytania.','Send personal data enquiries to sales@ltsmarket.pl. Only provide information needed to handle your enquiry.','Вопросы о персональных данных направляйте на sales@ltsmarket.pl. Указывайте только информацию, необходимую для ответа на запрос.'),
 ('Formularze kontaktowe','Contact forms','Контактные формы'),
 ('Formularze nie mają obecnie podłączonego systemu wysyłki. Wypełnienie formularza nie oznacza wysłania wiadomości. Skontaktuj się telefonicznie lub e-mailem.','The forms currently have no sending service connected. Completing a form does not send a message. Please contact us by phone or email.','Система отправки форм пока не подключена. Заполнение формы не отправляет сообщение. Свяжитесь с нами по телефону или электронной почте.'),
 ('Usługi zewnętrzne','External services','Внешние сервисы'),
 ('Strona korzysta z Google Fonts i osadzonych map Google. Załadowanie tych zasobów wymaga połączenia z dostawcą, który może otrzymać adres IP oraz informacje o przeglądarce.','The site uses Google Fonts and embedded Google Maps. Loading these resources connects to the provider, which may receive your IP address and browser information.','Сайт использует Google Fonts и встроенные карты Google. Загрузка этих ресурсов устанавливает соединение с провайдером, который может получить IP-адрес и сведения о браузере.'),
 ('Opcjonalna analityka','Optional analytics','Необязательная аналитика'),
 ('Google Analytics uruchamia się tylko po Twojej zgodzie. Wybór jest zapisywany lokalnie w przeglądarce. Możesz go zmienić w ustawieniach prywatności w stopce.','Google Analytics runs only with your consent. Your choice is stored locally in your browser. You can change it through the privacy settings in the footer.','Google Analytics запускается только с вашего согласия. Выбор сохраняется локально в браузере. Его можно изменить в настройках конфиденциальности внизу страницы.'),
]:add(*row)
for p in PRODUCTS:
 for key in ('description','condition','service','categoryLabel'):
  add(p[key]['pl'],p[key]['en'],p[key]['ru'])
 add(p['name']['pl']+' — urządzenie używane | LTS Market',p['name']['en']+' — pre-owned equipment | LTS Market',p['name']['ru']+' — б/у оборудование | LTS Market')
 for i in range(1,20):add(f"{p['name']['pl']} — zdjęcie {i}",f"{p['name']['en']} — photo {i}",f"{p['name']['ru']} — фото {i}")
def path_for(page,lang):return ('/' if lang=='pl' else '/'+lang+'/')+('' if page=='index.html' else page)
def img(p):return f"/assets/img/uzywane/{p['slug']}/{p['slug']}-01.webp"
def cards(dark=True):
 return ''.join(f'''<a class="product-card{' product-card--dark' if dark else ''}" href="/uzywane/{p['slug']}.html"><div class="product-card__image"><img src="{img(p)}" alt="{escape(p['name']['pl'])}" loading="lazy"></div><div class="product-card__body"><h3>{p['name']['pl']}</h3><p class="product-card__description">{p['description']['pl']}</p><p class="product-card__price">{p['priceLabel']}</p><span class="product-card__link">Zobacz szczegóły <span aria-hidden="true">→</span></span></div></a>''' for p in PRODUCTS)
def shell(main):
 s=(ROOT/'scripts/templates/nowe.html.in').read_text()
 s=re.sub(r'<main\b[^>]*>.*?</main>',lambda m:main,s,flags=re.S)
 s=s.replace('</head>','<link rel="stylesheet" href="/css/uzywane.css">\n</head>')
 return s
catalog=shell('''<main id="main-content"><section class="nowe-hero used-hero--text"><div class="container nowe-hero__container"><div class="nowe-hero__content"><p class="section-label">LTS Market</p><h1 class="nowe-hero__title">Urządzenia używane <span>gotowe do pracy</span></h1><p class="nowe-hero__description">Poznaj urządzenia po serwisie Laser Tech Service. Zobacz rzeczywiste zdjęcia, sprawdź parametry i zapytaj o aktualną dostępność.</p><div class="nowe-hero__actions"><a class="button button--primary" href="#oferta">Zobacz ofertę</a><a class="button button--outline-light" href="/kontakt.html">Porozmawiaj z doradcą</a></div></div></div></section><section class="products-section products-section--light" id="oferta"><div class="container"><header class="section-heading"><span class="section-label">Sprawdzone</span><h2>Katalog urządzeń używanych</h2></header><div class="product-grid">'''+cards(dark=False)+'''</div></div></section></main>''')
(ROOT/'uzywane.html').write_text(catalog)
for p in PRODUCTS:
 slug=p['slug'];name=p['name']['pl'];photos=sorted((ROOT/f'assets/img/uzywane/{slug}').glob('*.webp'))
 thumbs=''.join(f'<button type="button" data-image="/{f.relative_to(ROOT).as_posix()}" aria-pressed="{str(i==1).lower()}"><img src="/{f.relative_to(ROOT).as_posix()}" alt="{name} — zdjęcie {i}" loading="lazy"></button>' for i,f in enumerate(photos,1))
 main=f'''<main id="main-content" class="used-detail"><div class="container"><nav class="used-breadcrumbs" aria-label="Główna nawigacja"><a href="/">Market</a><span aria-hidden="true">/</span><a href="/uzywane.html">Używane urządzenia</a><span aria-hidden="true">/</span><span>{name}</span></nav><article class="nowe-product"><div class="nowe-product__visual" data-gallery><a class="used-gallery__main" href="{img(p)}"><img data-gallery-main src="{img(p)}" alt="{name} — zdjęcie 1" fetchpriority="high"></a><div class="used-gallery__thumbnails" role="group" aria-label="Galeria produktu">{thumbs}</div></div><div class="nowe-product__content"><p class="section-label">{p['categoryLabel']['pl']}</p><div class="nowe-product__heading"><h1>{name}</h1><p class="nowe-product__price">{p['priceLabel']}</p></div><p class="nowe-product__lead">{p['description']['pl']}</p><div class="nowe-specs"><div><span>Rok produkcji</span><strong>{p['year'] or 'Nie podano'}</strong></div><div><span>Stan</span><strong>{p['condition']['pl']}</strong></div><div><span>Serwis</span><strong>{p['service']['pl']}</strong></div></div><p class="nowe-product__lead">Cena i dostępność do potwierdzenia przy kontakcie.</p><div class="nowe-hero__actions"><a class="button button--primary" href="/kontakt.html?product={slug}#contact-form">Zapytaj o dostępność</a><a class="button button--outline" href="/uzywane.html">Wróć do katalogu</a></div></div></article></div></main>'''
 page=shell(main).replace('</body>','<script src="/js/uzywane.js" defer></script></body>')
 (ROOT/'uzywane').mkdir(exist_ok=True);(ROOT/f'uzywane/{slug}.html').write_text(page)
privacy_sections=[('Kontakt w sprawie danych','Pytania dotyczące danych osobowych możesz kierować na sales@ltsmarket.pl. Podawaj wyłącznie informacje potrzebne do obsługi zapytania.'),('Formularze kontaktowe','Formularze nie mają obecnie podłączonego systemu wysyłki. Wypełnienie formularza nie oznacza wysłania wiadomości. Skontaktuj się telefonicznie lub e-mailem.'),('Usługi zewnętrzne','Strona korzysta z Google Fonts i osadzonych map Google. Załadowanie tych zasobów wymaga połączenia z dostawcą, który może otrzymać adres IP oraz informacje o przeglądarce.'),('Opcjonalna analityka','Google Analytics uruchamia się tylko po Twojej zgodzie. Wybór jest zapisywany lokalnie w przeglądarce. Możesz go zmienić w ustawieniach prywatności w stopce.')]
(ROOT/'polityka-prywatnosci.html').write_text(shell('<main id="main-content" class="used-detail"><div class="container"><h1>Informacje o prywatności</h1>'+''.join(f'<section class="nowe-intro"><h2>{h}</h2><p class="nowe-financing__copy">{t}</p></section>' for h,t in privacy_sections)+'<p><a href="https://policies.google.com/privacy">Google Privacy</a></p></div></main>'))
# Repair missing routes and images while keeping the original home layout.
s=(ROOT/'scripts/templates/index.html.in').read_text()
start=s.index('<div class="product-grid product-grid--dark">')
depth=0
for m in re.finditer(r'<div\b[^>]*>|</div>',s[start:]):
 depth+= -1 if m[0]=='</div>' else 1
 if depth==0:
  s=s[:start]+'<div class="product-grid product-grid--dark">'+cards()+'</div>'+s[start+m.end():];break
(ROOT/'index.html').write_text(s)
PAGES=['index.html','nowe.html','leasing.html','kontakt.html','uzywane.html','polityka-prywatnosci.html']+[f"uzywane/{p['slug']}.html" for p in PRODUCTS]
class Localize(HTMLParser):
 def __init__(self,lang,page):super().__init__(convert_charrefs=False);self.lang=lang;self.page=page;self.out=[];self.skip=[]
 def tr(self,s):return D.get(norm(unescape(s)),{}).get(self.lang,s)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('script','style'):self.skip.append(tag)
  if tag=='html':a['lang']=self.lang
  for k in ('alt','title','placeholder','aria-label'):
   if k in a:a[k]=self.tr(a[k])
  if tag=='meta' and (a.get('name') in ('description','keywords','twitter:title','twitter:description') or a.get('property') in ('og:title','og:description')):a['content']=self.tr(a['content'])
  for key in ('href','src','action'):
   v=a.get(key,'')
   if v.startswith(('assets/','css/','js/')):a[key]='/'+v
  if tag=='a':
   href=a.get('href','')
   if a.get('lang') in LANGS:
    target=a['lang'];a['href']=path_for(self.page,target)
    cls=a.get('class','').split();cls=[c for c in cls if c!='is-active']
    if target==self.lang:cls.append('is-active');a['aria-current']='page'
    else:a.pop('aria-current',None)
    a['class']=' '.join(cls)
   elif href.startswith('/') and not href.startswith(('//', '/assets/')):
    if href=='/blog/':a['href']='https://lasertechservice.pl/blog/'
    else:
     if href.startswith('/nowe/'):href='/nowe.html#'+Path(href).stem
     a['href']=('' if self.lang=='pl' else '/'+self.lang)+href
   if 'desktop-nav__link' in a.get('class',''):
    cls=[c for c in a['class'].split() if c!='is-active']
    current='uzywane.html' if self.page.startswith('uzywane/') else self.page
    if a.get('href')==path_for(current,self.lang):cls.append('is-active');a['aria-current']='page'
    else:a.pop('aria-current',None)
    a['class']=' '.join(cls)
  self.out.append('<'+tag+''.join(' '+k+(('="'+escape(v,quote=True)+'"') if v is not None else '') for k,v in a.items())+'>')
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
 def handle_endtag(self,t):
  if self.skip and t==self.skip[-1]:self.skip.pop()
  self.out.append('</'+t+'>')
 def handle_data(self,s):
  if self.skip:self.out.append(s);return
  t=self.tr(s)
  if t!=s:
   pre=re.match(r'^\s*',s)[0];post=re.search(r'\s*$',s)[0];s=pre+escape(t)+post
  self.out.append(s)
 def handle_comment(self,s):self.out.append('<!--'+s+'-->')
 def handle_decl(self,s):self.out.append('<!'+s+'>')
 def handle_entityref(self,s):self.out.append('&'+s+';')
 def handle_charref(self,s):self.out.append('&#'+s+';')
def metadata(s,page,lang,title,desc,image):
 s=re.sub(r'<title>.*?</title>','',s,flags=re.S)
 s=re.sub(r'<link\b(?=[^>]*rel="(?:canonical|alternate|icon|apple-touch-icon|manifest)")[^>]*>','',s,flags=re.S)
 s=re.sub(r'<meta\b(?=[^>]*(?:name="(?:description|keywords|twitter:[^"]+)"|property="og:[^"]+"))[^>]*>','',s,flags=re.S)
 title=D.get(norm(title),{}).get(lang,title);desc=D.get(norm(desc),{}).get(lang,desc)
 url=BASE+path_for(page,lang);locale={'pl':'pl_PL','en':'en_GB','ru':'ru_RU'}[lang]
 meta=f'<title>{escape(title)}</title>\n<meta name="description" content="{escape(desc,quote=True)}">\n<link rel="canonical" href="{url}">\n'
 for l in LANGS:meta+=f'<link rel="alternate" hreflang="{l}" href="{BASE+path_for(page,l)}">\n'
 meta+=f'<link rel="alternate" hreflang="x-default" href="{BASE+path_for(page,"pl")}">\n'
 for k,v in {'type':'product' if page.startswith('uzywane/') else 'website','locale':locale,'site_name':'LTS Market','title':title,'description':desc,'url':url,'image':BASE+image}.items():meta+=f'<meta property="og:{k}" content="{escape(v,quote=True)}">\n'
 for k,v in {'card':'summary_large_image','title':title,'description':desc,'image':BASE+image}.items():meta+=f'<meta name="twitter:{k}" content="{escape(v,quote=True)}">\n'
 meta+=f'<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png"><link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"><link rel="icon" type="image/svg+xml" sizes="any" href="/favicon.svg"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="manifest" href="{path_for("site.webmanifest",lang)}">\n'
 return s.replace('</head>',meta+'</head>')
for page in PAGES:
 source=ROOT/'scripts/templates'/(page+'.in')
 if page=='index.html' or not source.exists():source=ROOT/page
 s=source.read_text().replace('całej Poli.','całej Polski.')
 # Every page uses the same shared header/footer before localization.
 for component in ('header','footer'):
  markup=(ROOT/'scripts/templates'/(component+'.html.in')).read_text().strip()
  s=s.replace('<!-- SITE_'+component.upper()+' -->',markup)

 s=s.replace('assets/img/uzywane/ellisys-plus.webp','assets/img/uzywane/ellisys-plus/ellisys-plus-01.webp')
 # Replace unconditional analytics with a shared consent-controlled script.
 s=re.sub(r'<script\b[^>]*src="https://www.googletagmanager.com/gtag/js[^>]*>\s*</script>','',s,flags=re.S)
 s=re.sub(r'<script>\s*window.dataLayer.*?</script>','',s,flags=re.S)
 if '/js/privacy.js' not in s:s=s.replace('</body>','<script src="/js/privacy.js" defer></script></body>')
 title=norm(re.search(r'<title>(.*?)</title>',s,re.S)[1])
 desc=re.search(r'<meta\s+name="description"\s+content="([^"]+)"',s)[1]
 image='/assets/img/hero-lts-market.jpg'
 if page=='uzywane.html':title='Sprawdzone urządzenia używane | LTS Market';desc='Sprawdzone urządzenia używane po serwisie Laser Tech Service. Zdjęcia, opisy i ceny aparatów dostępnych w LTS Market.';image=img(PRODUCTS[2])
 if page=='polityka-prywatnosci.html':title='Informacje o prywatności | LTS Market';desc='Informacje o formularzach, usługach zewnętrznych i ustawieniach prywatności LTS Market.'
 product=next((p for p in PRODUCTS if page==f"uzywane/{p['slug']}.html"),None)
 if product:title=product['name']['pl']+' — urządzenie używane | LTS Market';desc=product['description']['pl'];image=img(product)
 # Product/catalogue/privacy shells must not retain the new-equipment schema.
 if page not in ('index.html','nowe.html','leasing.html','kontakt.html'):s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
 for lang in LANGS:
  parser=Localize(lang,page);parser.feed(s);out=''.join(parser.out)
  def localize_schema(value):
   if isinstance(value,dict):return {k:localize_schema(v) for k,v in value.items()}
   if isinstance(value,list):return [localize_schema(v) for v in value]
   if isinstance(value,str):
    if value.startswith(BASE+'/') and lang!='pl':return BASE+'/'+lang+value[len(BASE):]
    return D.get(norm(value),{}).get(lang,value)
   return value
  out=re.sub(r'<script type="application/ld\+json">(.*?)</script>',lambda m:'<script type="application/ld+json">'+json.dumps(localize_schema(json.loads(m[1])),ensure_ascii=False)+'</script>',out,flags=re.S)
  out=metadata(out,page,lang,title,desc,image)
  flag={'pl':'🇵🇱','en':'🇬🇧','ru':'🇷🇺'}[lang]
  out=re.sub(r'(<button\b[^>]*id="language-button"[^>]*>).*?(</button>)',lambda m:m[1]+f'<span aria-hidden="true">{flag}</span><span>{lang.upper()}</span><span class="language-switcher__chevron" aria-hidden="true">▾</span>'+m[2],out,flags=re.S)
  # Shared JS translates its live messages through a small per-language dictionary.
  if lang!='pl':
   out=out.replace('src="/js/main.js"',f'src="/{lang}/js/main.js"').replace('src="/js/kontakt.js"',f'src="/{lang}/js/kontakt.js"')
  if product:
   schema={'@context':'https://schema.org','@type':'Product','name':product['name'][lang],'description':product['description'][lang],'image':[BASE+'/'+f.relative_to(ROOT).as_posix() for f in sorted((ROOT/f"assets/img/uzywane/{product['slug']}").glob('*.webp'))],'url':BASE+path_for(page,lang),'itemCondition':'https://schema.org/UsedCondition','offers':{'@type':'Offer','price':product['price'],'priceCurrency':'PLN','itemCondition':'https://schema.org/UsedCondition','url':BASE+path_for(page,lang),'seller':{'@type':'Organization','name':'LTS Market'}}}
   out=out.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script></head>')
  target=ROOT/('' if lang=='pl' else lang)/page;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(re.sub(r"\n{3,}", "\n\n", "\n".join(line.rstrip() for line in out.splitlines()))+"\n")
# Separate translated JS retains the original behavior without runtime text replacement.
for lang in ('en','ru'):
 for name in ('main.js','kontakt.js'):
  js=(ROOT/'js'/name).read_text()
  for pl,translations in D.items():js=js.replace(json.dumps(pl,ensure_ascii=False),json.dumps(translations[lang],ensure_ascii=False))
  target=ROOT/lang/'js'/name;target.parent.mkdir(exist_ok=True);target.write_text(js)
for lang in LANGS:
 manifest={'id':path_for('index.html',lang),'name':'LTS Market','short_name':'LTS Market','description':D['Profesjonalne urządzenia dla branży beauty. Nowe, używane, leasing i wsparcie techniczne.'].get(lang,'Profesjonalne urządzenia dla branży beauty. Nowe, używane, leasing i wsparcie techniczne.'),'lang':lang,'start_url':path_for('index.html',lang),'scope':'/','display':'standalone','background_color':'#050d14','theme_color':'#050d14','icons':[{'src':f'/web-app-manifest-{size}x{size}.png','sizes':f'{size}x{size}','type':'image/png','purpose':'any'} for size in (192,512)]}
 (ROOT/('' if lang=='pl' else lang)/'site.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');ET.register_namespace('xhtml','http://www.w3.org/1999/xhtml')
xml=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
for page in PAGES:
 for lang in LANGS:
  node=ET.SubElement(xml,'{http://www.sitemaps.org/schemas/sitemap/0.9}url');ET.SubElement(node,'{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text=BASE+path_for(page,lang)
  for alt in (*LANGS,'x-default'):ET.SubElement(node,'{http://www.w3.org/1999/xhtml}link',{'rel':'alternate','hreflang':alt,'href':BASE+path_for(page,'pl' if alt=='x-default' else alt)})
ET.indent(xml);ET.ElementTree(xml).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
print(f'Built {len(PAGES)*3} pages, 3 manifests and sitemap.xml')
