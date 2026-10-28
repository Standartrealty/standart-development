import json, subprocess, urllib.parse, hashlib
from pathlib import Path

root=Path(__file__).parent/'source-content'
target=root/'documents';target.mkdir(exist_ok=True)
base='https://cloud-api.yandex.net/v1/disk/public/resources'
key='https://disk.yandex.ru/d/COMrmb4nRX_0Bg'
catalog=[]
def get(url):return subprocess.check_output(['curl','-fLsS','--max-time','40',url])
def walk(path='/'):
    url=base+'?'+urllib.parse.urlencode({'public_key':key,'path':path,'limit':100})
    data=json.loads(get(url))
    for item in data.get('_embedded',{}).get('items',[]):
        if item['type']=='dir':walk(item['path'])
        else:
            record={'name':item['name'],'path':item['path'],'source':key,'size':item.get('size'),'type':item.get('mime_type')}
            if item.get('file'):
                dest=target/(hashlib.sha256(item['path'].encode()).hexdigest()[:12]+'-'+item['name'])
                try:dest.write_bytes(get(item['file']));record['local']=str(dest.relative_to(root.parent))
                except Exception as error:record['error']=str(error)
            catalog.append(record)
walk()
(root/'documents-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
print('Saved',sum('local'in x for x in catalog),'of',len(catalog),'documents')
