import json,re,html,hashlib
from pathlib import Path
from PIL import Image
root=Path(__file__).parent
projects=json.loads((root/'data.json').read_text())
lookup={x['url']:root/x['local'] for x in json.loads((root/'source-content/catalog.json').read_text())['assets'] if 'local'in x}
plans=[]
for project in projects:
 for plan in project['plans']:
  slug=plan['source'].rsplit('/',1)[-1]
  source=html.unescape((root/'source-content'/f'{slug}.html').read_text())
  urls=list(dict.fromkeys(re.findall(r'https://static.tildacdn.com/[^\s\x22\x27<>\\]+\.(?:png|jpg)',source)))
  candidates=[u for u in urls if not any(x in u for x in ['photo.png','111111.png']) and u in lookup]
  if not candidates:continue
  url=candidates[-1]
  im=Image.open(lookup[url]).convert('RGBA');bbox=im.getbbox()
  if bbox:im=im.crop(bbox)
  bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);im=bg.convert('RGB')
  im.thumbnail((1400,1400));full=root/'assets'/('floorplan-'+slug+'.webp');im.save(full,'WEBP',quality=88)
  im.thumbnail((540,540));thumb=root/'assets'/('floorplan-'+slug+'-thumb.webp');im.save(thumb,'WEBP',quality=83)
  area=re.search(r'(\d+[,.]\d+)\s*м',plan['name']).group(1).replace('.',',')
  rooms='studio' if 'студия' in plan['name'].lower() else plan['name'][0]
  label='Студия' if rooms=='studio' else rooms+'-комнатная'
  plans.append({'id':slug,'projectId':project['id'],'project':project['name'],'city':project['city'],'type':rooms,'name':label,'area':area,'image':'/assets/'+full.name,'thumb':'/assets/'+thumb.name,'source':plan['source'],'imageSource':url})
(root/'home-plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2))
print('Prepared',len(plans),'floorplans')
