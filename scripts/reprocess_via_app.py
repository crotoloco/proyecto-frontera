#!/usr/bin/env python
import requests, re, sqlite3
from pathlib import Path
BASE='http://127.0.0.1:5000'
# get last upload id
p=Path('centro_control/centro_control.db')
conn=sqlite3.connect(str(p))
conn.row_factory=sqlite3.Row
cur=conn.cursor()
row=cur.execute('SELECT id FROM upload_history ORDER BY id DESC LIMIT 1').fetchone()
conn.close()
if not row:
	print('no uploads')
	raise SystemExit(1)
uid=row['id']
print('will reprocess upload id',uid)
# login
s=requests.Session()
r=s.get(BASE+'/login')
m=re.search(r'name="csrf_token" value="([^"]+)"', r.text)
csrf=m.group(1) if m else ''
print('csrf',bool(csrf))
creds={'user':'admin','password':'C9_w0S6FKvJAJjGv','csrf_token':csrf}
r2=s.post(BASE+'/login', data=creds)
print('login status',r2.status_code)
# post reprocess
r3=s.post(f"{BASE}/centro_control/history/{uid}/reprocess", data={'csrf_token':csrf})
print('reprocess status', r3.status_code)
print('response len', len(r3.text))
open('tmp_reprocess_response.html','w', encoding='utf-8').write(r3.text)
print('wrote tmp_reprocess_response.html')
