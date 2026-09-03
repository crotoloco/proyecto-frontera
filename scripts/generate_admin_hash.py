#!/usr/bin/env python
"""
Genera un hash de contraseña para ADMIN_PASS usando werkzeug.
Uso:
	python scripts/generate_admin_hash.py "mi_contraseña"
O interactivo sin argumento.
"""
from werkzeug.security import generate_password_hash
import sys

if len(sys.argv) > 1:
	pwd = sys.argv[1]
else:
	pwd = input('Contraseña a hashear: ')

print(generate_password_hash(pwd))
