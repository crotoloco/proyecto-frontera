#!/usr/bin/env python
import os
import re
import webbrowser
import requests

s = requests.Session()
login_url = 'http://127.0.0.1:5000/login'

# GET login page to obtain CSRF
r = s.get(login_url)
if r.status_code != 200:
	print('GET /login failed', r.status_code)
	raise SystemExit(1)

# extract csrf token
m = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
csrf = m.group(1) if m else ''
print('csrf token found?', bool(csrf))

# read credentials from environment with sensible defaults
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin')

creds = {
	'user': ADMIN_USER,
	'password': ADMIN_PASS,
	'csrf_token': csrf,
	'next': '/dashboard.html',
}

r2 = s.post(login_url, data=creds, allow_redirects=True)
print('POST login status', r2.status_code)
print('POST response url', r2.url)
print('POST redirect history', [(h.status_code, h.headers.get('Location')) for h in r2.history])
print('Session cookies after login:', s.cookies.get_dict())

# fetch dashboard (after login)
r3 = s.get('http://127.0.0.1:5000/dashboard.html')
print('GET dashboard status', r3.status_code)
print('dashboard length', len(r3.text))
print('GET dashboard url', r3.url)
print('GET dashboard redirect history', [(h.status_code, h.headers.get('Location')) for h in r3.history])
print('First 400 chars of dashboard response:\n', r3.text[:400])

path = 'tmp_dashboard.html'
open(path, 'w', encoding='utf-8').write(r3.text)
print('wrote', path)

# open file in default browser for quick inspection
try:
	webbrowser.open(path)
	print('Opened', path, 'in default browser')
except Exception:
	pass
