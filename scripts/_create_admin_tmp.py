#!/usr/bin/env python
import secrets
import importlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from werkzeug.security import generate_password_hash

# import db module
db = importlib.import_module('centro_control.db')
# ensure users table
try:
	db.init_user_table()
except Exception as e:
	print('INIT_ERR', e)

pwd = secrets.token_urlsafe(12)
ph = generate_password_hash(pwd)
try:
	uid = db.create_user('admin', ph, True)
	print('CREATED', uid, pwd)
except Exception as e:
	print('ERROR', e)
