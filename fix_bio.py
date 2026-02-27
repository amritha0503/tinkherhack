"""Fix bio field references."""
import os

# Frontend pages: w.bio -> w.bio_text
for f in [
    r'C:\Users\Amritha\Desktop\tinkherhack\skillsync-frontend\src\pages\WorkerSearch.jsx',
    r'C:\Users\Amritha\Desktop\tinkherhack\skillsync-frontend\src\pages\WorkerDetail.jsx',
]:
    c = open(f, encoding='utf-8').read()
    c = c.replace('{w.bio}', '{w.bio_text}')
    c = c.replace('{worker.bio}', '{worker.bio_text}')
    open(f, 'w', encoding='utf-8').write(c)
    print('Fixed:', os.path.basename(f))

# Backend: save_profile should accept both bio_english and bio_text keys
path = r'C:\Users\Amritha\Desktop\tinkherhack\skillsync-backend\src\routers\ai_call.py'
c = open(path, encoding='utf-8').read()
# Handle both key names from Gemini response
old = 'worker.bio_text = profile.get("bio_text") or worker.bio_text'
new = 'worker.bio_text = profile.get("bio_english") or profile.get("bio_text") or worker.bio_text'
c = c.replace(old, new)
open(path, 'w', encoding='utf-8').write(c)
print('Fixed: ai_call.py save_profile bio field')

print('All done.')
