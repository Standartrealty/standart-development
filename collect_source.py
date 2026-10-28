import concurrent.futures, hashlib, json, re, urllib.request, subprocess, html
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).parent / 'source-content'
ROOT.mkdir(exist_ok=True)
BASE = 'https://standart-develop.ru/'
class Extract(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.links=[]; self.assets=set(); self.skip=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag in ('script','style'): self.skip+=1
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        for key in ('src','data-original','data-src','poster','data-bg','data-content-cover-bg'):
            value=a.get(key,'')
            if value.startswith(('https://','//')) and not value.split('?')[0].endswith(('.js','.css')): self.assets.add(value)
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip(): self.text.append(data.strip())
def fetch(url):
    return subprocess.check_output(['curl','-fLsS','--max-time','40',url],stderr=subprocess.DEVNULL)
pages=['','company','projects','prominent','wellton','avenue','generation','grandhills','primorsky','privacy','robots.txt','sitemap.xml']
records=[]; assets={}; queue=list(pages); visited=set()
while queue:
    slug=queue.pop(0)
    if slug in visited:continue
    visited.add(slug); url=urljoin(BASE,slug); name=(slug.strip('/').replace('/','_') or 'home')
    try:
        raw=fetch(url); path=ROOT/(name if name.endswith(('.txt','.xml')) else name+'.html'); path.write_bytes(raw)
        record={'url':url,'local':str(path.relative_to(ROOT.parent)),'type':'source page'}
        decoded=html.unescape(raw.decode('utf-8','replace'))
        if name.endswith('.xml'):
            for loc in re.findall(r'<loc>(.*?)</loc>',decoded):
                parsed=urlparse(loc)
                if parsed.netloc=='standart-develop.ru':queue.append(parsed.path.strip('/'))
        if path.suffix=='.html':
            p=Extract();p.feed(decoded); (ROOT/(name+'.txt')).write_text('\n\n'.join(p.text));record['links']=p.links
            for asset in p.assets:assets.setdefault(asset,[]).append(url)
            for link in p.links:
                parsed=urlparse(urljoin(url,link))
                if parsed.netloc=='standart-develop.ru' and parsed.path.strip('/') not in visited:queue.append(parsed.path.strip('/'))
            for asset in re.findall(r'https://[^\s\x22\x27<>\\]+\.(?:mp4|webm|pdf|jpg|png|jpeg|svg|webp)(?:\?[^\s\x22\x27<>\\]*)?',decoded):assets.setdefault(asset,[]).append(url)
        records.append(record); print('PAGE',url,flush=True)
    except Exception as error:records.append({'url':url,'error':str(error)});print('ERROR',url,str(error),flush=True)
(ROOT/'assets').mkdir(exist_ok=True)
def save_asset(item):
    url,sources=item; url=url if not url.startswith('//') else 'https:'+url
    ext=Path(urlparse(url).path).suffix.lower()
    if ext not in ('.jpg','.jpeg','.png','.svg','.webp','.gif','.mp4','.webm','.pdf','.ico'):return {'url':url,'sources':sources,'status':'link only; unsupported asset type'}
    filename=hashlib.sha256(url.encode()).hexdigest()[:18]+ext; path=ROOT/'assets'/filename
    try:
        if not path.exists():path.write_bytes(fetch(url))
        return {'url':url,'local':str(path.relative_to(ROOT.parent)),'sources':sorted(set(sources)),'bytes':path.stat().st_size,'use':'Review visually before selecting for new website'}
    except Exception as error:return {'url':url,'sources':sources,'error':str(error)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    media=list(pool.map(save_asset,assets.items()))
(ROOT/'catalog.json').write_text(json.dumps({'pages':records,'assets':media},ensure_ascii=False,indent=2))
print('DONE',len(records),'pages',len(media),'assets',sum('local' in x for x in media),'saved',flush=True)
