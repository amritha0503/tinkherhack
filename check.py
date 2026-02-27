import urllib.request
import json

try:
    r = urllib.request.urlopen('http://localhost:8000/api/workers/search')
    data = json.loads(r.read())
    print(f'Backend UP — {data["total"]} workers found')
    for w in data['workers']:
        bio = (w.get('bio_text') or '')[:60]
        print(f'  {w["name"]} | {w["skill_type"]} | trust:{w["trust_score"]} | bio:"{bio}..."')
except Exception as e:
    print(f'Backend ERROR: {e}')

try:
    r2 = urllib.request.urlopen('http://localhost:3000')
    print(f'\nFrontend UP — {r2.status} {r2.reason}')
except Exception as e:
    print(f'\nFrontend ERROR: {e}')
