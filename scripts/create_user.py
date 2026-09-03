#!/usr/bin/env python
"""
Crear usuario administrativo en la base de datos.
Uso:
	python scripts/create_user.py --username admin --password 'MiPass' --admin
Si no se pasan opciones, solicita interactivamente.
"""
import argparse
from getpass import getpass
from werkzeug.security import generate_password_hash
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from centro_control import db

parser = argparse.ArgumentParser()
parser.add_argument('--username', '-u', help='Nombre de usuario')
parser.add_argument('--password', '-p', help='Contraseña (no recomendable en la línea)')
parser.add_argument('--admin', action='store_true', help='Marcar como admin')
args = parser.parse_args()

username = args.username or input('Usuario: ')
password = args.password or getpass('Contraseña: ')
if not password:
	password = getpass('Contraseña (confirmar): ')
	if not password:
		print('Contraseña vacía, abortando')
		raise SystemExit(1)

ph = generate_password_hash(password)
uid = db.create_user(username, ph, is_admin=args.admin)
print(f'Usuario creado id={uid} username={username} admin={args.admin}')
