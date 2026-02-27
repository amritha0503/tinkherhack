import urllib.request
import json

base = 'http://localhost:8000'

# 1. Languages endpoint
try:
    r = urllib.request.urlopen(f'{base}/api/ai-call/languages')
    data = json.loads(r.read())
    print('AI Call /languages OK:', [l['name'] for l in data['languages']])
except Exception as e:
    print(f'AI Call /languages FAIL: {e}')

# 2. Worker detail
try:
    r = urllib.request.urlopen(f'{base}/api/workers/search')
    workers = json.loads(r.read())['workers']
    wid = workers[0]['id']
    r2 = urllib.request.urlopen(f'{base}/api/workers/{wid}')
    w = json.loads(r2.read())
    print(f'Worker detail OK: {w.get("name")} | bio_text present: {bool(w.get("bio_text"))}')
except Exception as e:
    print(f'Worker detail FAIL: {e}')

# 3. Search with skill filter
try:
    r = urllib.request.urlopen(f'{base}/api/workers/search?skill=Plumber')
    data = json.loads(r.read())
    print(f'Search by skill OK: {data["total"]} Plumber(s) found')
except Exception as e:
    print(f'Search by skill FAIL: {e}')

# 4. Search with location filter
try:
    r = urllib.request.urlopen(f'{base}/api/workers/search?location=Kozhikode')
    data = json.loads(r.read())
    print(f'Search by location OK: {data["total"]} worker(s) in Kozhikode area')
except Exception as e:
    print(f'Search by location FAIL: {e}')

print('\nAll checks complete.')
