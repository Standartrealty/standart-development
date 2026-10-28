import json,re,shutil,html
from pathlib import Path
from PIL import Image
R=Path(__file__).parent; S=R/'source-content'; A=R/'assets'; A.mkdir(exist_ok=True)
c=json.loads((S/'catalog.json').read_text()); lookup={v['url']:R/v['local'] for v in c['assets'] if 'local'in v}; manifest=[]
def asset(url,name=None,width=1600):
 p=lookup.get(url)
 if not p or not p.exists():return None
 name=name or p.stem
 if p.suffix=='.svg':dest=A/(name+'.svg');shutil.copy(p,dest)
 else:
  try:
   im=Image.open(p);im.thumbnail((width,width));dest=A/(name+'.webp');im.save(dest,'WEBP',quality=86)
  except:return None
 manifest.append({'source':url,'local':'assets/'+dest.name,'use':name});return '/assets/'+dest.name
asset('https://static.tildacdn.com/tild3265-6237-4961-b831-633130366334/1_1.jpg','hero',2000)
asset('https://static.tildacdn.com/tild3831-3138-4263-b031-373963303330/123.jpg','selection')
slugs=['prominent','wellton','primorsky','grandhills','avenue','generation'];names=['Видный','Wellton','Приморский квартал','Grand Hills','Проспект','Поколение'];cities=['Дербент','Дербент','Каспийск','Каспийск','Дербент','Дербент'];years=[2029,2027,2029,2030,2026,2029];corps=[12,2,6,3,5,5]
data=[]
for slug,name,city,year,corp in zip(slugs,names,cities,years,corps):
 source=html.unescape((S/(slug+'.html')).read_text());text=(S/(slug+'.txt')).read_text(); urls=list(dict.fromkeys(re.findall(r'https://static.tildacdn.com/[^\s\x22\x27<>\\]+\.jpg',source)))
 cover=asset(urls[0],slug)
 gallery=[]
 for url in urls[:16]:
  if 'Rectangle_8564' not in url:
   dest=asset(url,width=1800)
   if dest:gallery.append(dest)
 desc=text.split('О проекте',1)[-1].split('\n\n'+str(year),1)[0].strip()
 adv=text.split('преимущества',1)[-1].split('Галерея',1)[0].split('Выберите корпус',1)[0]
 adv=re.sub(r'\[\{.*?\}\]','',adv,flags=re.S).strip()
 if len(adv)>7000:adv=''
 planlinks=[]
 for pf in S.glob('*.txt'):
  if not (pf.stem.startswith('studia') or 'roomapartment' in pf.stem):continue
  pt=pf.read_text()
  breadcrumb=pt.split('Главная /',1)[-1].split('Планировки /',1)[0].lower()
  if name.lower() in breadcrumb:planlinks.append('/'+pf.stem)
 plans=[]
 for link in planlinks:
  f=S/(link[1:]+'.html')
  if not f.exists():continue
  ps=html.unescape(f.read_text()); svgurls=list(dict.fromkeys(re.findall(r'https://static.tildacdn.com/[^\s\x22\x27<>\\]+\.(?:png|jpg)',ps)))
  candidate=[u for u in svgurls if not any(x in u for x in ['photo.png','111111.png'])]
  if not candidate:continue
  local=asset(candidate[0]); title=re.search(r'<title>(.*?)</title>',ps)
  title=html.unescape(title.group(1)) if title else link[1:]
  plans.append({'name':title,'image':local,'source':'https://standart-develop.ru'+link})
 data.append({'id':slug,'name':name,'city':city,'year':year,'corps':corp,'image':cover,'gallery':gallery,'description':desc,'advantages':adv,'plans':plans,'source':'https://standart-develop.ru/'+slug})
(R/'data.json').write_text(json.dumps(data,ensure_ascii=False))
completed=[]
completedNames=['Центральный','Империал','Большая семья','Свадебный','Свадебный 2','Мамино','Тихий берег','Гарант','Чемпион','Спортивный','Спортивный 2','Грин парк']
completedCities=['Дербент','Дербент']+['Каспийск']*10
completedYears=['2024','2021','2022','2020','2022','2024','2022','2022','','','','2024']
# Source order of the completed-home image track.
photos=['71c3a9ce7725bdfee5','5784ab8d20bd3df786','391d9687c523b63875','636ed67ac84a9b90fe','f498e37f5373832726','a2ee43d4b98c5a6238','95ca21676219cbb785','34a33e8b54f1742466','9565ad5785b70746f3','3eb482b71b1627d8c6','f5e1d7611e0fcc91eb','752ef1e5133565fbf4']
for i,(name,city,year,key) in enumerate(zip(completedNames,completedCities,completedYears,photos)):
 found=next((v for v in c['assets'] if v.get('local','').endswith(key+'.png')),None)
 im=asset(found['url'],'completed-'+str(i),1200) if found else None
 completed.append({'name':name,'city':city,'year':year,'image':im})
(R/'completed.json').write_text(json.dumps(completed,ensure_ascii=False))
(S/'usage-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Prepared',len(data),'projects',sum(len(p['plans']) for p in data),'plans',len(manifest),'assets')
